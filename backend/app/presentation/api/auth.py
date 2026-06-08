from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.infrastructure.database.connection import get_db
from app.infrastructure.database.repositories import SQLAlchemyUserRepository
from app.application.dtos import UserRegisterRequest, UserLoginRequest, TokenResponse, UserBriefResponse
from app.application.use_cases.auth import RegisterUserUseCase, LoginUserUseCase
from app.domain.exceptions import UserAlreadyExistsException, InvalidCredentialsException
from app.domain.models import User
from app.presentation.api.dependencies import get_current_user, get_user_repository

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserBriefResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: UserRegisterRequest,
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository)
):
    use_case = RegisterUserUseCase(user_repo)
    return use_case.execute(request)

@router.post("/login", response_model=TokenResponse)
def login(
    request: UserLoginRequest,
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository)
):
    use_case = LoginUserUseCase(user_repo)
    return use_case.execute(request)

@router.get("/me", response_model=UserBriefResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/user/{user_id}", response_model=UserBriefResponse)
def get_user_profile(
    user_id: UUID,
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository)
):
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
