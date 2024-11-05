from fastapi import HTTPException, status
from config.logger import logger


class PermissionDeniedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="FORBIDDEN: No permission to perform this action"
        )


class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found: User does not exist"
        )


class OrderNotFoundException(HTTPException):
    def __init__(self, order_id):
        logger.error("Not found: Order ID=%s not exist", order_id)
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found: Order does not exist"
        )


class UsernameAlreadyExistsException(HTTPException):
    def __init__(self, username: str):
        logger.warning("Bad request: Username '%s' is already registered.", username)
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bad request: Username '{username}' is already registered."
        )


class EmailAlreadyExistsException(HTTPException):
    def __init__(self, email: str):
        logger.warning("Bad request: Email '%s' is already registered.", email)
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bad request: Email '{email}' is already registered."
        )


class CredentialException(HTTPException):
    def __init__(self):
        logger.error("Authentication failed: Could not validate credentials")
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'}
        )
