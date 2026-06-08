from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List, Dict, Any
from app.domain.models import User, Tweet, Comment, Friendship, Message, BrowserCookie

class UserRepository(ABC):
    @abstractmethod
    def add(self, user: User) -> User:
        pass

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def search_users(self, query: str, exclude_user_id: UUID) -> List[User]:
        pass

class TweetRepository(ABC):
    @abstractmethod
    def add(self, tweet: Tweet) -> Tweet:
        pass

    @abstractmethod
    def get_by_id(self, tweet_id: UUID) -> Optional[Tweet]:
        pass

    @abstractmethod
    def get_feed(self, current_user_id: UUID) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: UUID, current_user_id: UUID) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_liked_by_user_id(self, user_id: UUID, current_user_id: UUID) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def add_like(self, user_id: UUID, tweet_id: UUID) -> bool:
        pass

    @abstractmethod
    def remove_like(self, user_id: UUID, tweet_id: UUID) -> bool:
        pass

    @abstractmethod
    def is_liked(self, user_id: UUID, tweet_id: UUID) -> bool:
        pass

class CommentRepository(ABC):
    @abstractmethod
    def add(self, comment: Comment) -> Comment:
        pass

    @abstractmethod
    def get_by_tweet_id(self, tweet_id: UUID) -> List[Dict[str, Any]]:
        pass

class FriendshipRepository(ABC):
    @abstractmethod
    def add(self, friendship: Friendship) -> Friendship:
        pass

    @abstractmethod
    def get(self, user_id: UUID, friend_id: UUID) -> Optional[Friendship]:
        pass

    @abstractmethod
    def update_status(self, user_id: UUID, friend_id: UUID, status: str) -> None:
        pass

    @abstractmethod
    def delete(self, user_id: UUID, friend_id: UUID) -> None:
        pass

    @abstractmethod
    def get_friends(self, user_id: UUID) -> List[User]:
        pass

    @abstractmethod
    def get_pending_requests(self, user_id: UUID) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_friends_count(self, user_id: UUID) -> int:
        pass

class MessageRepository(ABC):
    @abstractmethod
    def add(self, message: Message) -> Message:
        pass

    @abstractmethod
    def get_conversation(self, user1_id: UUID, user2_id: UUID) -> List[Message]:
        pass

    @abstractmethod
    def mark_as_read(self, sender_id: UUID, receiver_id: UUID) -> None:
        pass

class BrowserCookieRepository(ABC):
    @abstractmethod
    def save(self, cookie: BrowserCookie) -> BrowserCookie:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[BrowserCookie]:
        pass
