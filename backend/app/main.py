from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.database.connection import init_db
from app.domain.exceptions import DomainException, EntityNotFoundException, InvalidCredentialsException, UserAlreadyExistsException, FriendshipException, UnauthorizedException
from app.presentation.api.auth import router as auth_router
from app.presentation.api.tweets import router as tweets_router
from app.presentation.api.friendships import router as friendships_router
from app.presentation.api.messages import router as messages_router

# Initialize database tables
init_db()

app = FastAPI(
    title="X Clone API",
    description="Backend API for X Clone using DDD - Clean Architecture & MVC mapping",
    version="1.0.0",
)

# CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers for Domain Exceptions
@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    status_code = 400
    if isinstance(exc, InvalidCredentialsException):
        status_code = 401
    elif isinstance(exc, EntityNotFoundException):
        status_code = 404
    elif isinstance(exc, UnauthorizedException):
        status_code = 403
        
    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.message},
    )

# Include controllers / routers
app.include_router(auth_router, prefix="/api")
app.include_router(tweets_router, prefix="/api")
app.include_router(friendships_router, prefix="/api")
app.include_router(messages_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to X Clone API", "status": "running"}
