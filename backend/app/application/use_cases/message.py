from uuid import UUID
from typing import List
from app.domain.models import Message
from app.domain.repositories import MessageRepository, UserRepository
from app.domain.exceptions import EntityNotFoundException, FriendshipException
from app.application.dtos import MessageCreateRequest

class SendMessageUseCase:
    def __init__(self, message_repo: MessageRepository, user_repo: UserRepository):
        self.message_repo = message_repo
        self.user_repo = user_repo

    def execute(self, sender_id: UUID, request: MessageCreateRequest) -> Message:
        if sender_id == request.receiver_id:
            raise FriendshipException("You cannot send a message to yourself.")

        # Check if receiver exists
        receiver = self.user_repo.get_by_id(request.receiver_id)
        if not receiver:
            raise EntityNotFoundException("User", str(request.receiver_id))

        message = Message(
            sender_id=sender_id,
            receiver_id=request.receiver_id,
            content=request.content
        )
        return self.message_repo.add(message)

class GetChatHistoryUseCase:
    def __init__(self, message_repo: MessageRepository):
        self.message_repo = message_repo

    def execute(self, current_user_id: UUID, other_user_id: UUID) -> List[Message]:
        # Retrieve history
        messages = self.message_repo.get_conversation(current_user_id, other_user_id)
        # Mark messages received by current user from other user as read
        self.message_repo.mark_as_read(sender_id=other_user_id, receiver_id=current_user_id)
        return messages
