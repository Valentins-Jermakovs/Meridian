# ==============================
# Library imports
# ==============================

from typing import TYPE_CHECKING

from sqlmodel import (
    Field, 
    Relationship, 
    SQLModel
)

from .user_role import UserRole

if TYPE_CHECKING:
    from .user import User


# ==============================
# Role Model
# ==============================

class Role(SQLModel, table=True):
    """
    A model representing a role that users can have.
    
    Attributes:
        id (int | None): The unique ID of the role entry.
        
        name (str): The name of the role.
        
        description (str | None): A brief description of the role.
        
        users (list[User]): The list of users who have this role.
    """

    __tablename__ = "roles"


    id: int | None = Field(
        default=None,
        primary_key=True,
    )


    name: str = Field(
        unique=True,
        index=True,
        max_length=50,
    )


    description: str | None = Field(
        default=None,
        max_length=255,
    )


    users: list["User"] = Relationship(
        back_populates="roles",
        link_model=UserRole,
    )