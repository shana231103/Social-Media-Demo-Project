from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.infrastructure.database.connection import Base

class UserDB(Base):
    __tablename__ = "users"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    avatar_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    tweets = relationship("TweetDB", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("CommentDB", back_populates="user", cascade="all, delete-orphan")

class TweetDB(Base):
    __tablename__ = "tweets"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("UserDB", back_populates="tweets")
    comments = relationship("CommentDB", back_populates="tweet", cascade="all, delete-orphan")
    likes = relationship("LikeDB", back_populates="tweet", cascade="all, delete-orphan")

class CommentDB(Base):
    __tablename__ = "comments"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tweet_id = Column(PG_UUID(as_uuid=True), ForeignKey("tweets.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("UserDB", back_populates="comments")
    tweet = relationship("TweetDB", back_populates="comments")

class LikeDB(Base):
    __tablename__ = "likes"
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tweet_id = Column(PG_UUID(as_uuid=True), ForeignKey("tweets.id", ondelete="CASCADE"), nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint("user_id", "tweet_id"),
    )

    tweet = relationship("TweetDB", back_populates="likes")

class FriendshipDB(Base):
    __tablename__ = "friendships"
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    friend_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="pending", nullable=False)  # "pending", "accepted"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint("user_id", "friend_id"),
    )

class MessageDB(Base):
    __tablename__ = "messages"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    receiver_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
