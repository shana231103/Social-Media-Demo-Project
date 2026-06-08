from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Dict, Any

from app.infrastructure.database.connection import get_db
from app.infrastructure.database.repositories import SQLAlchemyTweetRepository, SQLAlchemyCommentRepository
from app.application.dtos import (
    TweetCreateRequest,
    TweetResponse,
    CommentCreateRequest,
    CommentResponse,
)
from app.application.use_cases.tweet import (
    CreateTweetUseCase,
    GetFeedUseCase,
    GetUserTweetsUseCase,
    GetLikedTweetsUseCase,
    ToggleLikeUseCase,
    AddCommentUseCase,
    GetCommentsUseCase,
)
from app.domain.exceptions import EntityNotFoundException
from app.domain.models import User
from app.presentation.api.dependencies import get_current_user

router = APIRouter(prefix="/tweets", tags=["tweets"])

def get_tweet_repo(db: Session = Depends(get_db)) -> SQLAlchemyTweetRepository:
    return SQLAlchemyTweetRepository(db)

def get_comment_repo(db: Session = Depends(get_db)) -> SQLAlchemyCommentRepository:
    return SQLAlchemyCommentRepository(db)

@router.post("", response_model=TweetResponse, status_code=status.HTTP_201_CREATED)
def create_tweet(
    request: TweetCreateRequest,
    current_user: User = Depends(get_current_user),
    tweet_repo: SQLAlchemyTweetRepository = Depends(get_tweet_repo),
):
    use_case = CreateTweetUseCase(tweet_repo)
    tweet = use_case.execute(current_user.id, request)
    
    # Reload full details to fit TweetResponse DTO
    feed_use_case = GetFeedUseCase(tweet_repo)
    feed = feed_use_case.execute(current_user.id)
    for t in feed:
        if t["id"] == tweet.id:
            return t
            
    # Fallback
    return {
        "id": tweet.id,
        "content": tweet.content,
        "created_at": tweet.created_at,
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "display_name": current_user.display_name,
            "avatar_url": current_user.avatar_url,
        },
        "likes_count": 0,
        "comments_count": 0,
        "is_liked": False
    }

@router.get("", response_model=List[TweetResponse])
def get_feed(
    current_user: User = Depends(get_current_user),
    tweet_repo: SQLAlchemyTweetRepository = Depends(get_tweet_repo),
):
    use_case = GetFeedUseCase(tweet_repo)
    return use_case.execute(current_user.id)

@router.get("/user/{user_id}", response_model=List[TweetResponse])
def get_user_tweets(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    tweet_repo: SQLAlchemyTweetRepository = Depends(get_tweet_repo),
):
    use_case = GetUserTweetsUseCase(tweet_repo)
    return use_case.execute(user_id, current_user.id)

@router.get("/liked/{user_id}", response_model=List[TweetResponse])
def get_liked_tweets(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    tweet_repo: SQLAlchemyTweetRepository = Depends(get_tweet_repo),
):
    use_case = GetLikedTweetsUseCase(tweet_repo)
    return use_case.execute(user_id, current_user.id)

@router.post("/{tweet_id}/like")
def toggle_like(
    tweet_id: UUID,
    current_user: User = Depends(get_current_user),
    tweet_repo: SQLAlchemyTweetRepository = Depends(get_tweet_repo),
):
    use_case = ToggleLikeUseCase(tweet_repo)
    is_liked = use_case.execute(current_user.id, tweet_id)
    return {"liked": is_liked}

@router.post("/{tweet_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment(
    tweet_id: UUID,
    request: CommentCreateRequest,
    current_user: User = Depends(get_current_user),
    comment_repo: SQLAlchemyCommentRepository = Depends(get_comment_repo),
    tweet_repo: SQLAlchemyTweetRepository = Depends(get_tweet_repo),
):
    use_case = AddCommentUseCase(comment_repo, tweet_repo)
    comment = use_case.execute(current_user.id, tweet_id, request)
    return {
        "id": comment.id,
        "content": comment.content,
        "created_at": comment.created_at,
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "display_name": current_user.display_name,
            "avatar_url": current_user.avatar_url,
        }
    }

@router.get("/{tweet_id}/comments", response_model=List[CommentResponse])
def get_comments(
    tweet_id: UUID,
    comment_repo: SQLAlchemyCommentRepository = Depends(get_comment_repo),
):
    use_case = GetCommentsUseCase(comment_repo)
    return use_case.execute(tweet_id)
