from fastapi import HTTPException


class PermissionDeniedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=403,
            detail="You do not have permission to perform this action."
        )


class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=404,
            detail="User does not exist"
        )


class UsernameAlreadyExistsException(HTTPException):
    def __init__(self, username: str):
        super().__init__(
            status_code=400,
            detail=f"Username '{username}' is already registered."
        )


class EmailAlreadyExistsException(HTTPException):
    def __init__(self, email: str):
        detail = f"Email '{email}' is already registered."
        super().__init__(
            status_code=400,
            detail=f"Email '{email}' is already registered."
        )