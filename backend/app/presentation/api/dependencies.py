from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID

from app.infrastructure.database.connection import get_db
from app.infrastructure.database.repositories import SQLAlchemyUserRepository, SQLAlchemyBrowserCookieRepository
from app.infrastructure.security.auth_handler import verify_token
from app.domain.models import User

security = HTTPBearer()

def get_user_repository(db: Session = Depends(get_db)) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(db)

def get_cookie_repository(db: Session = Depends(get_db)) -> SQLAlchemyBrowserCookieRepository:
    return SQLAlchemyBrowserCookieRepository(db)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identity",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identity format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repo = SQLAlchemyUserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
