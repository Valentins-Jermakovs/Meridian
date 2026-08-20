# ==============================
# Bibliotēku imports
# ==============================

from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel


# ==============================
# Audit darbības
# ==============================

class AuditAction(str, Enum):

    REGISTER = "register"
    LOGIN = "login"
    FAILED_LOGIN = "failed_login"

    REFRESH = "refresh"

    LOGOUT = "logout"
    LOGOUT_ALL = "logout_all"

    UPDATE_SELF = "update_self"
    ADMIN_UPDATE_USER = "admin_update_user"

    CHANGE_PASSWORD = "change_password"
    CHANGE_ROLE = "change_role"

    ACCOUNT_ACTIVATED = "account_activated"
    ACCOUNT_DEACTIVATED = "account_deactivated"

    TOKEN_REUSE = "token_reuse"


# ==============================
# Audit žurnāla modelis
# ==============================

class AuditLog(SQLModel, table=True):

    __tablename__ = "audit_logs"

    # Žurnāla ieraksta identifikators
    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    # Lietotājs, kurš veica darbību
    user_id: int | None = Field(
        default=None,
        foreign_key="users.id",
        index=True,
    )

    # Veiktā darbība
    action: AuditAction = Field(
        index=True,
    )

    # Cilvēkam saprotams darbības apraksts
    description: str = Field(
        max_length=500,
    )

    # Darbības rezultāts
    success: bool = Field(
        default=True,
        index=True,
    )

    # Ieraksta izveidošanas laiks
    created_at: datetime = Field(
        default_factory=datetime.now,
        index=True,
    )