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
    """
    Contains registration statistics for one month.
    """

    month: int
    registrations: int


class UserRegistrationStatisticsResponse(
    BaseModel
):
    """
    Contains monthly user registration statistics.
    """

    year: int
    items: list[
        UserRegistrationStatisticItem
    ]

# ==============================
# User Statistics Response
# ==============================

class UserStatisticsResponse(BaseModel):
    """
    Contains aggregated user statistics.
    """

    total: int
    active: int
    blocked: int


# ==============================
# User Create Schema
# ==============================

class UserCreate(BaseModel):
    """
    Represents the data required to create a new user account.

    Attributes:
        username (str): Unique username of the user.
        full_name (str): Full name of the user.
        email (EmailStr): Valid email address of the user.
        password (str): Password for the user account.
    """

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
    """
    Represents the data a user can update for their own account.

    Attributes:
        username (str | None): New username.
        full_name (str | None): New full name.
        email (EmailStr | None): New email address.
        current_password (str | None): Current password used for verification.
        password (str | None): New password.
    """

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
    """
    Represents the data an administrator can update for a user account.

    Attributes:
        username (str | None): New username.
        full_name (str | None): New full name.
        email (EmailStr | None): New email address.
        password (str | None): New password.
        is_active (bool | None): Account activity status.
        roles (list[str] | None): List of roles assigned to the user.
    """

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
    """
    Represents the complete user information returned by the API.

    Attributes:
        id (int): Unique identifier of the user.
        username (str): Username of the user.
        full_name (str): Full name of the user.
        email (EmailStr): Email address of the user.
        roles (list[str]): Roles assigned to the user.
        is_active (bool): Indicates whether the user account is active.
        created_at (datetime): Timestamp when the user account was created.
    """

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
    """
    Represents a single user in a paginated user list.

    Attributes:
        id (int): Unique identifier of the user.
        username (str): Username of the user.
        full_name (str): Full name of the user.
        email (EmailStr): Email address of the user.
        is_active (bool): Indicates whether the user account is active.
    """

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
    """
    Represents a paginated response containing a list of users.

    Attributes:
        items (list[UserListItem]): Users included on the current page.
        page (int): Current page number.
        page_size (int): Number of users per page.
        total (int): Total number of users.
        pages (int): Total number of available pages.
    """

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