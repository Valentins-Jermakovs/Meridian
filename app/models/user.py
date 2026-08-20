# ==============================
# Bibliotēku imports
# ==============================

from datetime import datetime
from typing import TYPE_CHECKING
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel
from .user_role import UserRole

if TYPE_CHECKING:
    from .refresh_token import RefreshToken
    from .role import Role


# ==============================
# Lietotāja modelis
# ==============================

class User(SQLModel, table=True):
    __tablename__ = "users"

    # Lietotāja identifikators
    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    # Lietotājvārds
    username: str = Field(
        unique=True,
        index=True,
        min_length=5,
        max_length=100,
    )

    # Lietotāja pilnais vārds
    full_name: str = Field(
        min_length=10,
        max_length=255,
    )

    # Lietotāja e-pasta adrese
    email: EmailStr = Field(
        unique=True,
        index=True,
        max_length=255,
    )

    # Lietotāja paroles hešs
    password_hash: str = Field(
        max_length=255,
    )

    # Lietotāja konta aktivitātes statuss
    is_active: bool = Field(
        default=True,
    )

    # Lietotāja izveidošanas datums
    created_at: datetime = Field(
        default_factory=datetime.now,
    )

    # Lietotāja atjaunošanas tokeni
    refresh_tokens: list["RefreshToken"] = Relationship(
        back_populates="user",
    )

    # Lietotāja lomas
    roles: list["Role"] = Relationship(
        back_populates="users",
        link_model=UserRole,
    )