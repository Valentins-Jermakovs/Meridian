# ==============================
# Bibliotēku imports
# ==============================

from sqlmodel import Field, SQLModel


# ==============================
# Lietotāja un lomas saistības modelis
# ==============================

class UserRole(SQLModel, table=True):
    __tablename__ = "user_roles"

    # Lietotāja identifikators
    user_id: int = Field(
        foreign_key="users.id",
        primary_key=True,
    )

    # Lomas identifikators
    role_id: int = Field(
        foreign_key="roles.id",
        primary_key=True,
    )