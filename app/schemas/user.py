# ==============================
# Library Imports
# ==============================

from datetime import datetime

from pydantic import (
    EmailStr,
    BaseModel,
)

from sqlmodel import Field


# ==============================
# User Registration Statistics
# ==============================
class UserRegistrationStatisticItem(
    BaseModel
):

    month: int
    registrations: int


class UserRegistrationStatisticsResponse(
    BaseModel
):

    year: int
    items: list[
        UserRegistrationStatisticItem
    ]

# ==============================
# User Statistics Response
# ==============================

class UserStatisticsResponse(BaseModel):

    total: int
    active: int
    blocked: int


# ==============================
# User Create Schema
# ==============================

class UserCreate(BaseModel):

    # Username
    username: str = Field(
        min_length=5,
        max_length=100,
    )

    # Full name
    full_name: str = Field(
        min_length=10,
        max_length=255,
    )

    # Email address
    email: EmailStr

    # Password
    password: str = Field(
        min_length=8,
        max_length=255,
    )


# ==============================
# User Self-Update Schema
# ==============================

class UserSelfUpdate(BaseModel):

    # Username
    username: str | None = Field(
        default=None,
        min_length=5,
        max_length=100,
    )

    # Full name
    full_name: str | None = Field(
        default=None,
        min_length=10,
        max_length=255,
    )

    # Email address
    email: EmailStr | None = None

    # Current password
    current_password: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    # New password
    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=255,
    )


# ==============================
# User Admin Update Schema
# ==============================

class UserAdminUpdate(BaseModel):

    # Username
    username: str | None = Field(
        default=None,
        min_length=5,
        max_length=100,
    )

    # Full name
    full_name: str | None = Field(
        default=None,
        min_length=10,
        max_length=255,
    )

    # Email address
    email: EmailStr | None = None

    # New password
    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=255,
    )

    # Account activity status
    is_active: bool | None = None

    # User roles
    roles: list[str] | None = None


# ==============================
# Full User Response Schema
# ==============================

class UserResponse(BaseModel):

    # User identifier
    id: int

    # Username
    username: str

    # Full name
    full_name: str

    # User email address
    email: EmailStr

    # User roles
    roles: list[str]

    # User account activity status
    is_active: bool

    # User creation timestamp
    created_at: datetime


# ==============================
# User List Item Schema
# ==============================

class UserListItem(BaseModel):

    # User identifier
    id: int

    # Username
    username: str

    # Full name
    full_name: str

    # Email address
    email: EmailStr

    # Account activity status
    is_active: bool


# ==============================
# User List Response Schema
# ==============================

class UserListResponse(BaseModel):

    # List of users
    items: list[UserListItem]

    # Current page number
    page: int

    # Number of users per page
    page_size: int

    # Total number of users
    total: int

    # Total number of pages
    pages: int