from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from .user_role import UserRole

if TYPE_CHECKING:
    from .refresh_token import RefreshToken
    from .role import Role


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)

    username: str = Field(
        unique=True,
        min_length=5,
        max_length=100,
    )

    full_name: str = Field(
        min_length=10,
        max_length=255,
    )

    email: str = Field(
        unique=True,
        index=True,
        max_length=255,
    )

    password_hash: str = Field(
        max_length=255,
    )

    is_active: bool = Field(default=True)

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