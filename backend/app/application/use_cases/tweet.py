from uuid import UUID
from typing import List, Dict, Any
from app.domain.models import Tweet, Comment
from app.domain.repositories import TweetRepository, CommentRepository
from app.domain.exceptions import EntityNotFoundException
from app.application.dtos import TweetCreateRequest, CommentCreateRequest

class CreateTweetUseCase:
    def __init__(self, tweet_repo: TweetRepository):
        self.tweet_repo = tweet_repo

    def execute(self, user_id: UUID, request: TweetCreateRequest) -> Tweet:
        tweet = Tweet(user_id=user_id, content=request.content)
        return self.tweet_repo.add(tweet)

class GetFeedUseCase:
    def __init__(self, tweet_repo: TweetRepository):
        self.tweet_repo = tweet_repo

    def execute(self, current_user_id: UUID) -> List[Dict[str, Any]]:
        return self.tweet_repo.get_feed(current_user_id)

class GetUserTweetsUseCase:
    def __init__(self, tweet_repo: TweetRepository):
        self.tweet_repo = tweet_repo

    def execute(self, user_id: UUID, current_user_id: UUID) -> List[Dict[str, Any]]:
        return self.tweet_repo.get_by_user_id(user_id, current_user_id)

class GetLikedTweetsUseCase:
    def __init__(self, tweet_repo: TweetRepository):
        self.tweet_repo = tweet_repo

    def execute(self, user_id: UUID, current_user_id: UUID) -> List[Dict[str, Any]]:
        return self.tweet_repo.get_liked_by_user_id(user_id, current_user_id)

class ToggleLikeUseCase:
    def __init__(self, tweet_repo: TweetRepository):
        self.tweet_repo = tweet_repo

    def execute(self, user_id: UUID, tweet_id: UUID) -> bool:
        tweet = self.tweet_repo.get_by_id(tweet_id)
        if not tweet:
            raise EntityNotFoundException("Tweet", str(tweet_id))
        
        # Check if user already liked
        if self.tweet_repo.is_liked(user_id, tweet_id):
            self.tweet_repo.remove_like(user_id, tweet_id)
            return False  # Unliked
        else:
            self.tweet_repo.add_like(user_id, tweet_id)
            return True  # Liked

class AddCommentUseCase:
    def __init__(self, comment_repo: CommentRepository, tweet_repo: TweetRepository):
        self.comment_repo = comment_repo
        self.tweet_repo = tweet_repo

    def execute(self, user_id: UUID, tweet_id: UUID, request: CommentCreateRequest) -> Comment:
        tweet = self.tweet_repo.get_by_id(tweet_id)
        if not tweet:
            raise EntityNotFoundException("Tweet", str(tweet_id))

        comment = Comment(tweet_id=tweet_id, user_id=user_id, content=request.content)
        return self.comment_repo.add(comment)

class GetCommentsUseCase:
    def __init__(self, comment_repo: CommentRepository):
        self.comment_repo = comment_repo

    def execute(self, tweet_id: UUID) -> List[Dict[str, Any]]:
        return self.comment_repo.get_by_tweet_id(tweet_id)
