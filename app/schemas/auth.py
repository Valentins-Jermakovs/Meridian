# ==============================
# Library Imports
# ==============================

from sqlmodel import Field

from pydantic import BaseModel


# ==============================
# Login Request Schema
# ==============================

class LoginRequest(BaseModel):

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

    # JWT access token
    access_token: str

    # JWT refresh token
    refresh_token: str

    # Authentication token type
    token_type: str = "bearer"