class DomainException(Exception):
    """Base exception for all domain-related errors."""
    pass

class UserAlreadyExistsException(DomainException):
    def __init__(self, message: str = "A user with this username or email already exists."):
        self.message = message
        super().__init__(self.message)

class InvalidCredentialsException(DomainException):
    def __init__(self, message: str = "Invalid username/email or password."):
        self.message = message
        super().__init__(self.message)

class EntityNotFoundException(DomainException):
    def __init__(self, entity_name: str, identifier: str):
        self.message = f"{entity_name} with identifier '{identifier}' was not found."
        super().__init__(self.message)

class FriendshipException(DomainException):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class UnauthorizedException(DomainException):
    def __init__(self, message: str = "Access unauthorized."):
        self.message = message
        super().__init__(self.message)
