from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

@dataclass
class User:
    username: str
    email: str
    display_name: str
    password_hash: str
    avatar_url: Optional[str] = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Tweet:
    user_id: UUID
    content: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Comment:
    tweet_id: UUID
    user_id: UUID
    content: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Friendship:
    user_id: UUID
    friend_id: UUID
    status: str  # "pending" or "accepted"
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Message:
    sender_id: UUID
    receiver_id: UUID
    content: str
    id: UUID = field(default_factory=uuid4)
    is_read: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class BrowserCookie:
    username: str
    cookies: str
    local_storage: str
    updated_at: datetime = field(default_factory=datetime.utcnow)
