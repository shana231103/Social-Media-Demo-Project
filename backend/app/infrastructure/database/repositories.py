from sqlalchemy.orm import Session
from sqlalchemy import func, exists, or_
from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.domain.models import User, Tweet, Comment, Friendship, Message, BrowserCookie
from app.domain.repositories import (
    UserRepository,
    TweetRepository,
    CommentRepository,
    FriendshipRepository,
    MessageRepository,
    BrowserCookieRepository,
)
from app.infrastructure.database.models import (
    UserDB,
    TweetDB,
    CommentDB,
    LikeDB,
    FriendshipDB,
    MessageDB,
    BrowserCookieDB,
)

class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_domain(self, db_user: UserDB) -> User:
        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            display_name=db_user.display_name,
            password_hash=db_user.password_hash,
            avatar_url=db_user.avatar_url,
            created_at=db_user.created_at,
        )

    def add(self, user: User) -> User:
        db_user = UserDB(
            id=user.id,
            username=user.username,
            email=user.email,
            display_name=user.display_name,
            password_hash=user.password_hash,
            avatar_url=user.avatar_url,
            created_at=user.created_at,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return self._to_domain(db_user)

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        return self._to_domain(db_user) if db_user else None

    def get_by_username(self, username: str) -> Optional[User]:
        db_user = self.db.query(UserDB).filter(UserDB.username.ilike(username)).first()
        return self._to_domain(db_user) if db_user else None

    def get_by_email(self, email: str) -> Optional[User]:
        db_user = self.db.query(UserDB).filter(UserDB.email.ilike(email)).first()
        return self._to_domain(db_user) if db_user else None

    def search_users(self, query: str, exclude_user_id: UUID) -> List[User]:
        db_users = (
            self.db.query(UserDB)
            .filter(UserDB.id != exclude_user_id)
            .filter(
                or_(
                    UserDB.username.ilike(f"%{query}%"),
                    UserDB.display_name.ilike(f"%{query}%"),
                )
            )
            .limit(10)
            .all()
        )
        return [self._to_domain(u) for u in db_users]


class SQLAlchemyTweetRepository(TweetRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_domain(self, db_tweet: TweetDB) -> Tweet:
        return Tweet(
            id=db_tweet.id,
            user_id=db_tweet.user_id,
            content=db_tweet.content,
            created_at=db_tweet.created_at,
        )

    def add(self, tweet: Tweet) -> Tweet:
        db_tweet = TweetDB(
            id=tweet.id,
            user_id=tweet.user_id,
            content=tweet.content,
            created_at=tweet.created_at,
        )
        self.db.add(db_tweet)
        self.db.commit()
        self.db.refresh(db_tweet)
        return self._to_domain(db_tweet)

    def get_by_id(self, tweet_id: UUID) -> Optional[Tweet]:
        db_tweet = self.db.query(TweetDB).filter(TweetDB.id == tweet_id).first()
        return self._to_domain(db_tweet) if db_tweet else None

    def _format_tweet_row(self, row: Any) -> Dict[str, Any]:
        return {
            "id": row.id,
            "content": row.content,
            "created_at": row.created_at,
            "user": {
                "id": row.user_id,
                "username": row.username,
                "display_name": row.display_name,
                "avatar_url": row.avatar_url,
            },
            "likes_count": row.likes_count,
            "comments_count": row.comments_count,
            "is_liked": bool(row.is_liked),
        }

    def get_feed(self, current_user_id: UUID) -> List[Dict[str, Any]]:
        # Query tweets, joining user details, likes count, comment count, and whether liked by current_user_id
        # We use a subquery/outerjoin pattern.
        # Fetching all tweets for simplicity, sorted by creation date
        rows = (
            self.db.query(
                TweetDB.id,
                TweetDB.content,
                TweetDB.created_at,
                TweetDB.user_id,
                UserDB.username,
                UserDB.display_name,
                UserDB.avatar_url,
                func.count(func.distinct(LikeDB.user_id)).label("likes_count"),
                func.count(func.distinct(CommentDB.id)).label("comments_count"),
                exists()
                .where(LikeDB.tweet_id == TweetDB.id)
                .where(LikeDB.user_id == current_user_id)
                .correlate(TweetDB)
                .label("is_liked"),
            )
            .join(UserDB, TweetDB.user_id == UserDB.id)
            .outerjoin(LikeDB, TweetDB.id == LikeDB.tweet_id)
            .outerjoin(CommentDB, TweetDB.id == CommentDB.tweet_id)
            .group_by(TweetDB.id, UserDB.id)
            .order_by(TweetDB.created_at.desc())
            .all()
        )
        return [self._format_tweet_row(r) for r in rows]

    def get_by_user_id(self, user_id: UUID, current_user_id: UUID) -> List[Dict[str, Any]]:
        rows = (
            self.db.query(
                TweetDB.id,
                TweetDB.content,
                TweetDB.created_at,
                TweetDB.user_id,
                UserDB.username,
                UserDB.display_name,
                UserDB.avatar_url,
                func.count(func.distinct(LikeDB.user_id)).label("likes_count"),
                func.count(func.distinct(CommentDB.id)).label("comments_count"),
                exists()
                .where(LikeDB.tweet_id == TweetDB.id)
                .where(LikeDB.user_id == current_user_id)
                .correlate(TweetDB)
                .label("is_liked"),
            )
            .join(UserDB, TweetDB.user_id == UserDB.id)
            .outerjoin(LikeDB, TweetDB.id == LikeDB.tweet_id)
            .outerjoin(CommentDB, TweetDB.id == CommentDB.tweet_id)
            .filter(TweetDB.user_id == user_id)
            .group_by(TweetDB.id, UserDB.id)
            .order_by(TweetDB.created_at.desc())
            .all()
        )
        return [self._format_tweet_row(r) for r in rows]

    def get_liked_by_user_id(self, user_id: UUID, current_user_id: UUID) -> List[Dict[str, Any]]:
        rows = (
            self.db.query(
                TweetDB.id,
                TweetDB.content,
                TweetDB.created_at,
                TweetDB.user_id,
                UserDB.username,
                UserDB.display_name,
                UserDB.avatar_url,
                func.count(func.distinct(LikeDB.user_id)).label("likes_count"),
                func.count(func.distinct(CommentDB.id)).label("comments_count"),
                exists()
                .where(LikeDB.tweet_id == TweetDB.id)
                .where(LikeDB.user_id == current_user_id)
                .correlate(TweetDB)
                .label("is_liked"),
            )
            .join(UserDB, TweetDB.user_id == UserDB.id)
            .join(LikeDB, TweetDB.id == LikeDB.tweet_id)
            .outerjoin(CommentDB, TweetDB.id == CommentDB.tweet_id)
            .filter(LikeDB.user_id == user_id)
            .group_by(TweetDB.id, UserDB.id)
            .order_by(TweetDB.created_at.desc())
            .all()
        )
        return [self._format_tweet_row(r) for r in rows]

    def add_like(self, user_id: UUID, tweet_id: UUID) -> bool:
        # Check if already liked
        if self.is_liked(user_id, tweet_id):
            return False
        like = LikeDB(user_id=user_id, tweet_id=tweet_id)
        self.db.add(like)
        self.db.commit()
        return True

    def remove_like(self, user_id: UUID, tweet_id: UUID) -> bool:
        like = (
            self.db.query(LikeDB)
            .filter(LikeDB.user_id == user_id, LikeDB.tweet_id == tweet_id)
            .first()
        )
        if like:
            self.db.delete(like)
            self.db.commit()
            return True
        return False

    def is_liked(self, user_id: UUID, tweet_id: UUID) -> bool:
        return (
            self.db.query(exists().where(LikeDB.user_id == user_id).where(LikeDB.tweet_id == tweet_id))
            .scalar()
        )


class SQLAlchemyCommentRepository(CommentRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_domain(self, db_comment: CommentDB) -> Comment:
        return Comment(
            id=db_comment.id,
            tweet_id=db_comment.tweet_id,
            user_id=db_comment.user_id,
            content=db_comment.content,
            created_at=db_comment.created_at,
        )

    def add(self, comment: Comment) -> Comment:
        db_comment = CommentDB(
            id=comment.id,
            tweet_id=comment.tweet_id,
            user_id=comment.user_id,
            content=comment.content,
            created_at=comment.created_at,
        )
        self.db.add(db_comment)
        self.db.commit()
        self.db.refresh(db_comment)
        return self._to_domain(db_comment)

    def get_by_tweet_id(self, tweet_id: UUID) -> List[Dict[str, Any]]:
        rows = (
            self.db.query(
                CommentDB.id,
                CommentDB.content,
                CommentDB.created_at,
                CommentDB.user_id,
                UserDB.username,
                UserDB.display_name,
                UserDB.avatar_url,
            )
            .join(UserDB, CommentDB.user_id == UserDB.id)
            .filter(CommentDB.tweet_id == tweet_id)
            .order_by(CommentDB.created_at.asc())
            .all()
        )
        return [
            {
                "id": r.id,
                "content": r.content,
                "created_at": r.created_at,
                "user": {
                    "id": r.user_id,
                    "username": r.username,
                    "display_name": r.display_name,
                    "avatar_url": r.avatar_url,
                },
            }
            for r in rows
        ]


class SQLAlchemyFriendshipRepository(FriendshipRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_domain(self, db_friendship: FriendshipDB) -> Friendship:
        return Friendship(
            user_id=db_friendship.user_id,
            friend_id=db_friendship.friend_id,
            status=db_friendship.status,
            created_at=db_friendship.created_at,
        )

    def add(self, friendship: Friendship) -> Friendship:
        db_friendship = FriendshipDB(
            user_id=friendship.user_id,
            friend_id=friendship.friend_id,
            status=friendship.status,
            created_at=friendship.created_at,
        )
        self.db.add(db_friendship)
        self.db.commit()
        self.db.refresh(db_friendship)
        return self._to_domain(db_friendship)

    def get(self, user_id: UUID, friend_id: UUID) -> Optional[Friendship]:
        db_friendship = (
            self.db.query(FriendshipDB)
            .filter(
                or_(
                    (FriendshipDB.user_id == user_id) & (FriendshipDB.friend_id == friend_id),
                    (FriendshipDB.user_id == friend_id) & (FriendshipDB.friend_id == user_id),
                )
            )
            .first()
        )
        return self._to_domain(db_friendship) if db_friendship else None

    def update_status(self, user_id: UUID, friend_id: UUID, status: str) -> None:
        db_friendship = (
            self.db.query(FriendshipDB)
            .filter(
                or_(
                    (FriendshipDB.user_id == user_id) & (FriendshipDB.friend_id == friend_id),
                    (FriendshipDB.user_id == friend_id) & (FriendshipDB.friend_id == user_id),
                )
            )
            .first()
        )
        if db_friendship:
            db_friendship.status = status
            self.db.commit()

    def delete(self, user_id: UUID, friend_id: UUID) -> None:
        db_friendship = (
            self.db.query(FriendshipDB)
            .filter(
                or_(
                    (FriendshipDB.user_id == user_id) & (FriendshipDB.friend_id == friend_id),
                    (FriendshipDB.user_id == friend_id) & (FriendshipDB.friend_id == user_id),
                )
            )
            .first()
        )
        if db_friendship:
            self.db.delete(db_friendship)
            self.db.commit()

    def get_friends(self, user_id: UUID) -> List[User]:
        # Get list of accepted friends
        # Where (user_id = user_id or friend_id = user_id) and status = 'accepted'
        friendships = (
            self.db.query(FriendshipDB)
            .filter(
                ((FriendshipDB.user_id == user_id) | (FriendshipDB.friend_id == user_id))
                & (FriendshipDB.status == "accepted")
            )
            .all()
        )

        friend_ids = []
        for f in friendships:
            if f.user_id == user_id:
                friend_ids.append(f.friend_id)
            else:
                friend_ids.append(f.user_id)

        if not friend_ids:
            return []

        db_users = self.db.query(UserDB).filter(UserDB.id.in_(friend_ids)).all()
        return [
            User(
                id=u.id,
                username=u.username,
                email=u.email,
                display_name=u.display_name,
                password_hash=u.password_hash,
                avatar_url=u.avatar_url,
                created_at=u.created_at,
            )
            for u in db_users
        ]

    def get_pending_requests(self, user_id: UUID) -> List[Dict[str, Any]]:
        # Incoming requests to user_id, meaning friend_id == user_id and status == 'pending'
        rows = (
            self.db.query(
                FriendshipDB.user_id,
                FriendshipDB.created_at,
                UserDB.username,
                UserDB.display_name,
                UserDB.avatar_url,
            )
            .join(UserDB, FriendshipDB.user_id == UserDB.id)
            .filter(FriendshipDB.friend_id == user_id, FriendshipDB.status == "pending")
            .order_by(FriendshipDB.created_at.desc())
            .all()
        )
        return [
            {
                "sender_id": r.user_id,
                "created_at": r.created_at,
                "sender": {
                    "id": r.user_id,
                    "username": r.username,
                    "display_name": r.display_name,
                    "avatar_url": r.avatar_url,
                },
            }
            for r in rows
        ]

    def get_friends_count(self, user_id: UUID) -> int:
        return (
            self.db.query(FriendshipDB)
            .filter(
                ((FriendshipDB.user_id == user_id) | (FriendshipDB.friend_id == user_id))
                & (FriendshipDB.status == "accepted")
            )
            .count()
        )


class SQLAlchemyMessageRepository(MessageRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_domain(self, db_msg: MessageDB) -> Message:
        return Message(
            id=db_msg.id,
            sender_id=db_msg.sender_id,
            receiver_id=db_msg.receiver_id,
            content=db_msg.content,
            is_read=db_msg.is_read,
            created_at=db_msg.created_at,
        )

    def add(self, message: Message) -> Message:
        db_msg = MessageDB(
            id=message.id,
            sender_id=message.sender_id,
            receiver_id=message.receiver_id,
            content=message.content,
            is_read=message.is_read,
            created_at=message.created_at,
        )
        self.db.add(db_msg)
        self.db.commit()
        self.db.refresh(db_msg)
        return self._to_domain(db_msg)

    def get_conversation(self, user1_id: UUID, user2_id: UUID) -> List[Message]:
        db_messages = (
            self.db.query(MessageDB)
            .filter(
                or_(
                    (MessageDB.sender_id == user1_id) & (MessageDB.receiver_id == user2_id),
                    (MessageDB.sender_id == user2_id) & (MessageDB.receiver_id == user1_id),
                )
            )
            .order_by(MessageDB.created_at.asc())
            .all()
        )
        return [self._to_domain(m) for m in db_messages]

    def mark_as_read(self, sender_id: UUID, receiver_id: UUID) -> None:
        self.db.query(MessageDB).filter(
            MessageDB.sender_id == sender_id,
            MessageDB.receiver_id == receiver_id,
            MessageDB.is_read == False,
        ).update({"is_read": True}, synchronize_session=False)
        self.db.commit()


class SQLAlchemyBrowserCookieRepository(BrowserCookieRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_domain(self, db_cookie: BrowserCookieDB) -> BrowserCookie:
        return BrowserCookie(
            username=db_cookie.username,
            cookies=db_cookie.cookies,
            local_storage=db_cookie.local_storage,
            updated_at=db_cookie.updated_at,
        )

    def save(self, cookie: BrowserCookie) -> BrowserCookie:
        db_cookie = (
            self.db.query(BrowserCookieDB)
            .filter(BrowserCookieDB.username == cookie.username)
            .first()
        )
        if db_cookie:
            db_cookie.cookies = cookie.cookies
            db_cookie.local_storage = cookie.local_storage
            db_cookie.updated_at = datetime.utcnow()
        else:
            db_cookie = BrowserCookieDB(
                username=cookie.username,
                cookies=cookie.cookies,
                local_storage=cookie.local_storage,
                updated_at=cookie.updated_at,
            )
            self.db.add(db_cookie)
        self.db.commit()
        self.db.refresh(db_cookie)
        return self._to_domain(db_cookie)

    def get_by_username(self, username: str) -> Optional[BrowserCookie]:
        db_cookie = (
            self.db.query(BrowserCookieDB)
            .filter(BrowserCookieDB.username == username)
            .first()
        )
        return self._to_domain(db_cookie) if db_cookie else None
