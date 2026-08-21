# ==============================
# Library imports
# ==============================

from datetime import datetime

from enum import Enum

from sqlmodel import (
    Field, 
    SQLModel
)


# ==============================
# Audit Actions
# ==============================

class AuditAction(str, Enum):
    """
    Enum for audit log actions.
    
    Values:
        REGISTER: User registration.
        LOGIN: Successful login attempt.
        FAILED_LOGIN: Unsuccessful login attempt.
        
        REFRESH: Refresh token rotation.
        
        LOGOUT: Logout of current session.
        LOGOUT_ALL: Logout of all sessions.
        
        UPDATE_SELF: Update own user data.
        ADMIN_UPDATE_USER: Update user data as administrator.
        
        CHANGE_PASSWORD: Change own password.
        CHANGE_ROLE: Change own role.
        
        ACCOUNT_ACTIVATED: Activate account.
        ACCOUNT_DEACTIVATED: Deactivate account.
        
        TOKEN_REUSE: Reuse of token.
    """

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
# Audit Log Model
# ==============================

class AuditLog(SQLModel, table=True):
    """
    A model for logging important events in the system.
    
    Attributes:
        id (int | None): The unique ID of the audit log entry.
        
        user_id (int | None): The ID of the user who performed the action.
        
        action (AuditAction): The type of action performed.
        
        description (str): A human-readable description of the action.
        
        success (bool): Whether the action was successful.
        
        created_at (datetime): The timestamp when the log entry was created.
    """

    __tablename__ = "audit_logs"


    id: int | None = Field(
        default=None,
        primary_key=True,
    )


    user_id: int | None = Field(
        default=None,
        foreign_key="users.id",
        index=True,
    )


    action: AuditAction = Field(
        index=True,
    )


    description: str = Field(
        max_length=500,
    )


    success: bool = Field(
        default=True,
        index=True,
    )


    created_at: datetime = Field(
        default_factory=datetime.now,
        index=True,
    )