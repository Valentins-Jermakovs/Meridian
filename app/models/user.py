# ==============================
# Library imports
# ==============================

from datetime import datetime

from typing import TYPE_CHECKING

from pydantic import EmailStr

from sqlmodel import (
    Field, 
    Relationship, 
    SQLModel
)

from .user_role import UserRole

if TYPE_CHECKING:
    from .refresh_token import RefreshToken
    from .role import Role


# ==============================
# User Model
# ==============================

class User(SQLModel, table=True):
    """
    A model representing a user in the system.
    
    Attributes:
        id (int | None): The unique ID of the user entry.
        
        username (str): The username chosen by the user.
        
        full_name (str): The full name of the user.
        
        email (EmailStr): The email address of the user.
        
        password_hash (str): The hashed value of the user's password.
        
        is_active (bool): Whether the user is active or not.
        
        created_at (datetime): The timestamp when the user was created.
        
        refresh_tokens (list[RefreshToken]): The list of refresh tokens associated with this user.
        
        roles (list[Role]): The list of roles assigned to this user.
    """

    __tablename__ = "users"


    id: int | None = Field(
        default=None,
        primary_key=True,
    )


    username: str = Field(
        unique=True,
        index=True,
        min_length=5,
        max_length=100,
    )


    full_name: str = Field(
        min_length=10,
        max_length=255,
    )


    email: EmailStr = Field(
        unique=True,
        index=True,
        max_length=255,
    )


    password_hash: str = Field(
        max_length=255,
    )


    is_active: bool = Field(
        default=True,
    )


    created_at: datetime = Field(
        default_factory=datetime.now,
    )


    refresh_tokens: list["RefreshToken"] = Relationship(
        back_populates="user",
    )


    roles: list["Role"] = Relationship(
        back_populates="users",
        link_model=UserRole,
    )