# ==============================
# Library imports
# ==============================

from datetime import datetime

from typing import TYPE_CHECKING

from sqlmodel import (
    Field, 
    Relationship, 
    SQLModel
)

if TYPE_CHECKING:
    from .user import User


# ==============================
# Refresh Token Model
# ==============================

class RefreshToken(SQLModel, table=True):
    """
    A model representing a refresh token for authentication purposes.
    
    Attributes:
        id (int | None): The unique ID of the refresh token entry.
        
        user_id (int): The ID of the user who owns this refresh token.
        
        token_hash (str): The hashed value of the refresh token.
        
        expires_at (datetime): The timestamp when the token expires.
        
        created_at (datetime): The timestamp when the token was created.
        
        revoked (bool): Whether the token has been revoked.
        
        user (User): The user who owns this refresh token.
    """

    __tablename__ = "refresh_tokens"


    id: int | None = Field(
        default=None,
        primary_key=True,
    )


    user_id: int = Field(
        foreign_key="users.id",
        index=True,
    )


    token_hash: str = Field(
        unique=True,
        index=True,
        max_length=255,
    )


    expires_at: datetime


    created_at: datetime = Field(
        default_factory=datetime.now,
    )


    revoked: bool = Field(
        default=False,
    )


    user: "User" = Relationship(
        back_populates="refresh_tokens",
    )