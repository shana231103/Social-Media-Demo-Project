from app.domain.models import User
from app.domain.repositories import UserRepository
from app.domain.exceptions import UserAlreadyExistsException, InvalidCredentialsException
from app.application.dtos import UserRegisterRequest, UserLoginRequest, TokenResponse
from app.infrastructure.security.auth_handler import hash_password, verify_password, create_access_token

class RegisterUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(self, request: UserRegisterRequest) -> User:
        # Check if username already exists
        if self.user_repo.get_by_username(request.username):
            raise UserAlreadyExistsException(f"Username '{request.username}' is already taken.")
        
        # Check if email already exists
        if self.user_repo.get_by_email(request.email):
            raise UserAlreadyExistsException(f"Email '{request.email}' is already registered.")

        # Hash password and save user
        hashed_pwd = hash_password(request.password)
        avatar = request.avatar_url or f"https://api.dicebear.com/7.x/adventurer/svg?seed={request.username}"
        
        user = User(
            username=request.username,
            email=request.email,
            display_name=request.display_name,
            password_hash=hashed_pwd,
            avatar_url=avatar,
        )
        return self.user_repo.add(user)

class LoginUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(self, request: UserLoginRequest) -> TokenResponse:
        # Check if user exists by username or email
        user = self.user_repo.get_by_username(request.username_or_email)
        if not user:
            user = self.user_repo.get_by_email(request.username_or_email)

        if not user or not verify_password(request.password, user.password_hash):
            raise InvalidCredentialsException()

        # Create token
        token_data = {"sub": str(user.id)}
        token = create_access_token(data=token_data)

        return TokenResponse(
            access_token=token,
            user_id=user.id,
            username=user.username,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
        )
