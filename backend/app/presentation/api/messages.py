from fastapi import APIRouter, Depends, HTTPException, status, WebSocket
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
import json

from app.infrastructure.database.connection import get_db, SessionLocal
from app.infrastructure.database.repositories import SQLAlchemyMessageRepository, SQLAlchemyUserRepository
from app.infrastructure.websockets.connection_manager import manager
from app.infrastructure.security.auth_handler import verify_token
from app.application.dtos import MessageCreateRequest, MessageResponse
from app.application.use_cases.message import SendMessageUseCase, GetChatHistoryUseCase
from app.domain.models import User
from app.presentation.api.dependencies import get_current_user

router = APIRouter(prefix="/messages", tags=["messages"])

def get_message_repo(db: Session = Depends(get_db)) -> SQLAlchemyMessageRepository:
    return SQLAlchemyMessageRepository(db)

def get_user_repo(db: Session = Depends(get_db)) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(db)

@router.get("/history/{other_user_id}", response_model=List[MessageResponse])
def get_chat_history(
    other_user_id: UUID,
    current_user: User = Depends(get_current_user),
    message_repo: SQLAlchemyMessageRepository = Depends(get_message_repo),
):
    use_case = GetChatHistoryUseCase(message_repo)
    return use_case.execute(current_user.id, other_user_id)

@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    request: MessageCreateRequest,
    current_user: User = Depends(get_current_user),
    message_repo: SQLAlchemyMessageRepository = Depends(get_message_repo),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
):
    use_case = SendMessageUseCase(message_repo, user_repo)
    try:
        msg = use_case.execute(current_user.id, request)
        
        # Optionally send a real-time message notification over active WebSockets
        msg_payload = {
            "type": "chat_message",
            "data": {
                "id": str(msg.id),
                "sender_id": str(msg.sender_id),
                "receiver_id": str(msg.receiver_id),
                "content": msg.content,
                "is_read": msg.is_read,
                "created_at": msg.created_at.isoformat()
            }
        }
        serialized = json.dumps(msg_payload)
        await manager.send_personal_message(serialized, msg.sender_id)
        await manager.send_personal_message(serialized, msg.receiver_id)
        
        return msg
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    payload = verify_token(token)
    if not payload:
        await websocket.close(code=1008)
        return

    user_id_str = payload.get("sub")
    if not user_id_str:
        await websocket.close(code=1008)
        return

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        await websocket.close(code=1008)
        return

    # 1. Short-lived session to verify user exists on connection
    with SessionLocal() as db:
        user_repo = SQLAlchemyUserRepository(db)
        user = user_repo.get_by_id(user_id)
        if not user:
            await websocket.close(code=1008)
            return

    await manager.connect(user_id, websocket)
    try:
        while True:
            # Listen to incoming client-side WebSocket messages
            data = await websocket.receive_text()
            try:
                parsed_data = json.loads(data)
                receiver_id_str = parsed_data.get("receiver_id")
                content = parsed_data.get("content")
                if receiver_id_str and content:
                    receiver_id = UUID(receiver_id_str)
                    
                    # 2. Short-lived session per message event
                    with SessionLocal() as db:
                        user_repo = SQLAlchemyUserRepository(db)
                        message_repo = SQLAlchemyMessageRepository(db)
                        
                        send_case = SendMessageUseCase(message_repo, user_repo)
                        msg_request = MessageCreateRequest(receiver_id=receiver_id, content=content)
                        saved_msg = send_case.execute(user_id, msg_request)
                        
                        msg_payload = {
                            "type": "chat_message",
                            "data": {
                                "id": str(saved_msg.id),
                                "sender_id": str(saved_msg.sender_id),
                                "receiver_id": str(saved_msg.receiver_id),
                                "content": saved_msg.content,
                                "is_read": saved_msg.is_read,
                                "created_at": saved_msg.created_at.isoformat()
                            }
                        }
                    
                    serialized = json.dumps(msg_payload)
                    await manager.send_personal_message(serialized, user_id)
                    await manager.send_personal_message(serialized, receiver_id)
            except Exception as ex:
                try:
                    await websocket.send_text(json.dumps({"type": "error", "message": str(ex)}))
                except Exception:
                    pass
    except Exception:
        pass
    finally:
        manager.disconnect(user_id, websocket)
