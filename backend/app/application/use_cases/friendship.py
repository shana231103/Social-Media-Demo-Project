from uuid import UUID
from typing import List, Dict, Any
from app.domain.models import Friendship, User
from app.domain.repositories import FriendshipRepository, UserRepository
from app.domain.exceptions import FriendshipException, EntityNotFoundException

class SendFriendRequestUseCase:
    def __init__(self, friendship_repo: FriendshipRepository, user_repo: UserRepository):
        self.friendship_repo = friendship_repo
        self.user_repo = user_repo

    def execute(self, user_id: UUID, friend_id: UUID) -> Friendship:
        if user_id == friend_id:
            raise FriendshipException("You cannot send a friend request to yourself.")

        # Check if target user exists
        friend = self.user_repo.get_by_id(friend_id)
        if not friend:
            raise EntityNotFoundException("User", str(friend_id))

        existing = self.friendship_repo.get(user_id, friend_id)
        if existing:
            if existing.status == "accepted":
                raise FriendshipException("You are already friends with this user.")
            
            # If request is pending
            if existing.user_id == user_id:
                raise FriendshipException("Friend request already sent and is pending approval.")
            else:
                # Target user sent a request to current user, auto-accept it!
                self.friendship_repo.update_status(user_id, friend_id, "accepted")
                existing.status = "accepted"
                return existing

        friendship = Friendship(user_id=user_id, friend_id=friend_id, status="pending")
        return self.friendship_repo.add(friendship)

class AcceptFriendRequestUseCase:
    def __init__(self, friendship_repo: FriendshipRepository):
        self.friendship_repo = friendship_repo

    def execute(self, user_id: UUID, requester_id: UUID) -> None:
        # Check if request exists and is pending
        friendship = self.friendship_repo.get(user_id, requester_id)
        if not friendship:
            raise FriendshipException("No friend request found between these users.")

        if friendship.status == "accepted":
            raise FriendshipException("Friend request already accepted.")

        # Make sure the acceptor is indeed the one who received the request
        if friendship.friend_id != user_id:
            raise FriendshipException("You cannot accept a friend request you sent.")

        self.friendship_repo.update_status(user_id, requester_id, "accepted")

class RemoveFriendshipUseCase:
    def __init__(self, friendship_repo: FriendshipRepository):
        self.friendship_repo = friendship_repo

    def execute(self, user_id: UUID, friend_id: UUID) -> None:
        self.friendship_repo.delete(user_id, friend_id)

class GetFriendsUseCase:
    def __init__(self, friendship_repo: FriendshipRepository):
        self.friendship_repo = friendship_repo

    def execute(self, user_id: UUID) -> List[User]:
        return self.friendship_repo.get_friends(user_id)

class GetPendingRequestsUseCase:
    def __init__(self, friendship_repo: FriendshipRepository):
        self.friendship_repo = friendship_repo

    def execute(self, user_id: UUID) -> List[Dict[str, Any]]:
        return self.friendship_repo.get_pending_requests(user_id)

class SearchUsersUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(self, query: str, current_user_id: UUID) -> List[User]:
        return self.user_repo.search_users(query, current_user_id)


class GetFriendsCountUseCase:
    def __init__(self, friendship_repo: FriendshipRepository):
        self.friendship_repo = friendship_repo

    def execute(self, user_id: UUID) -> int:
        return self.friendship_repo.get_friends_count(user_id)
