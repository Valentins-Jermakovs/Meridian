# ==============================
# Library Imports
# ==============================

from sqlmodel import Field

from pydantic import BaseModel


# ==============================
# Login Request Schema
# ==============================

class LoginRequest(BaseModel):
    """
    Represents a user login request.

    Attributes:
        login (str): Username or email address.
        password (str): User password.
    """

    # Username or email address
    login: str = Field(
        min_length=1,
        max_length=255,
    )

    # User password
    password: str = Field(
        min_length=1,
        max_length=255,
    )


# ==============================
# Token Response Schema
# ==============================

class TokenResponse(BaseModel):
    """
    Represents the authentication token response.

    Attributes:
        access_token (str): JWT access token.
        refresh_token (str): JWT refresh token.
        token_type (str): Type of authentication token.
    """

    # JWT access token
    access_token: str

    # JWT refresh token
    refresh_token: str

    # Authentication token type
    token_type: str = "bearer"