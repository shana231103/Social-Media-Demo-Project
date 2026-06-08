from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Dict, Any

from app.infrastructure.database.connection import get_db
from app.infrastructure.database.repositories import SQLAlchemyFriendshipRepository, SQLAlchemyUserRepository
from app.application.dtos import UserBriefResponse, FriendRequestResponse
from app.application.use_cases.friendship import (
    SendFriendRequestUseCase,
    AcceptFriendRequestUseCase,
    RemoveFriendshipUseCase,
    GetFriendsUseCase,
    GetPendingRequestsUseCase,
    SearchUsersUseCase,
    GetFriendsCountUseCase,
)
from app.domain.exceptions import FriendshipException, EntityNotFoundException
from app.domain.models import User
from app.presentation.api.dependencies import get_current_user, get_user_repository

router = APIRouter(prefix="/friendships", tags=["friendships"])

def get_friendship_repo(db: Session = Depends(get_db)) -> SQLAlchemyFriendshipRepository:
    return SQLAlchemyFriendshipRepository(db)

@router.post("/request/{friend_id}", status_code=status.HTTP_200_OK)
def send_friend_request(
    friend_id: UUID,
    current_user: User = Depends(get_current_user),
    friendship_repo: SQLAlchemyFriendshipRepository = Depends(get_friendship_repo),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
):
    use_case = SendFriendRequestUseCase(friendship_repo, user_repo)
    friendship = use_case.execute(current_user.id, friend_id)
    return {"status": friendship.status}

@router.post("/accept/{requester_id}", status_code=status.HTTP_200_OK)
def accept_friend_request(
    requester_id: UUID,
    current_user: User = Depends(get_current_user),
    friendship_repo: SQLAlchemyFriendshipRepository = Depends(get_friendship_repo),
):
    use_case = AcceptFriendRequestUseCase(friendship_repo)
    use_case.execute(current_user.id, requester_id)
    return {"message": "Friend request accepted."}

@router.delete("/remove/{friend_id}", status_code=status.HTTP_200_OK)
def remove_friendship(
    friend_id: UUID,
    current_user: User = Depends(get_current_user),
    friendship_repo: SQLAlchemyFriendshipRepository = Depends(get_friendship_repo),
):
    use_case = RemoveFriendshipUseCase(friendship_repo)
    use_case.execute(current_user.id, friend_id)
    return {"message": "Friendship/request removed."}

@router.get("/friends", response_model=List[UserBriefResponse])
def get_friends(
    current_user: User = Depends(get_current_user),
    friendship_repo: SQLAlchemyFriendshipRepository = Depends(get_friendship_repo),
):
    use_case = GetFriendsUseCase(friendship_repo)
    return use_case.execute(current_user.id)

@router.get("/requests", response_model=List[FriendRequestResponse])
def get_pending_requests(
    current_user: User = Depends(get_current_user),
    friendship_repo: SQLAlchemyFriendshipRepository = Depends(get_friendship_repo),
):
    use_case = GetPendingRequestsUseCase(friendship_repo)
    return use_case.execute(current_user.id)

@router.get("/search", response_model=List[UserBriefResponse])
def search_users(
    q: str,
    current_user: User = Depends(get_current_user),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
):
    use_case = SearchUsersUseCase(user_repo)
    return use_case.execute(q, current_user.id)

@router.get("/user/{user_id}/friends/count", response_model=int)
def get_user_friends_count(
    user_id: UUID,
    friendship_repo: SQLAlchemyFriendshipRepository = Depends(get_friendship_repo),
):
    use_case = GetFriendsCountUseCase(friendship_repo)
    return use_case.execute(user_id)
