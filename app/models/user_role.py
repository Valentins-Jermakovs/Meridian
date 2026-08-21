# ==============================
# Library imports
# ==============================

from sqlmodel import (
    Field, 
    SQLModel
)


# ==============================
# User Role Association Model
# ==============================

class UserRole(SQLModel, table=True):
    """
    A model representing the many-to-many relationship between users and roles.
    
    Attributes:
        user_id (int): The ID of the user.
        
        role_id (int): The ID of the role.
    """

    __tablename__ = "user_roles"


    user_id: int = Field(
        foreign_key="users.id",
        primary_key=True,
    )


    role_id: int = Field(
        foreign_key="roles.id",
        primary_key=True,
    )