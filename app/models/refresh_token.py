from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .user import User


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    id: int | None = Field(default=None, primary_key=True)

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

    revoked: bool = Field(default=False)

    user: "User" = Relationship(
        back_populates="refresh_tokens",
    )