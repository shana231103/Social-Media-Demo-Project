from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional

class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=3, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=6)
    avatar_url: Optional[str] = None

class UserLoginRequest(BaseModel):
    username_or_email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: UUID
    username: str
    display_name: str
    avatar_url: Optional[str] = None

class UserBriefResponse(BaseModel):
    id: UUID
    username: str
    display_name: str
    avatar_url: Optional[str] = None

class TweetCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=280)

class TweetResponse(BaseModel):
    id: UUID
    content: str
    created_at: datetime
    user: UserBriefResponse
    likes_count: int
    comments_count: int
    is_liked: bool

class CommentCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=280)

class CommentResponse(BaseModel):
    id: UUID
    content: str
    created_at: datetime
    user: UserBriefResponse

class FriendRequestResponse(BaseModel):
    sender_id: UUID
    sender: UserBriefResponse
    created_at: datetime

class MessageCreateRequest(BaseModel):
    receiver_id: UUID
    content: str

class MessageResponse(BaseModel):
    id: UUID
    sender_id: UUID
    receiver_id: UUID
    content: str
    is_read: bool
    created_at: datetime
