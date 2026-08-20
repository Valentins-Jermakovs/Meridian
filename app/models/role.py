# ==============================
# Bibliotēku imports
# ==============================

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from .user_role import UserRole

if TYPE_CHECKING:
    from .user import User


# ==============================
# Lomas modelis
# ==============================

class Role(SQLModel, table=True):
    __tablename__ = "roles"

    # Lomas identifikators
    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    # Lomas nosaukums
    name: str = Field(
        unique=True,
        index=True,
        max_length=50,
    )

    # Lomas apraksts
    description: str | None = Field(
        default=None,
        max_length=255,
    )

    # Lietotāji, kuriem piešķirta šī loma
    users: list["User"] = Relationship(
        back_populates="roles",
        link_model=UserRole,
    )