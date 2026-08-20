# ==============================
# Bibliotēku imports
# ==============================

from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .user import User


# ==============================
# Atjaunošanas tokena modelis
# ==============================

class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    # Atjaunošanas tokena identifikators
    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    # Lietotāja identifikators
    user_id: int = Field(
        foreign_key="users.id",
        index=True,
    )

    # Atjaunošanas tokena hešs
    token_hash: str = Field(
        unique=True,
        index=True,
        max_length=255,
    )

    # Tokena derīguma termiņš
    expires_at: datetime

    # Tokena izveidošanas datums
    created_at: datetime = Field(
        default_factory=datetime.now,
    )

    # Tokena atsaukšanas statuss
    revoked: bool = Field(
        default=False,
    )

    # Lietotājs, kuram pieder tokens
    user: "User" = Relationship(
        back_populates="refresh_tokens",
    )