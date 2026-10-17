
# ==============================
# Standard library imports
# ==============================

from typing import Annotated

# ==============================
# Third-party imports
# ==============================

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# ==============================
# Application configuration
# ==============================

from config.config import settings
from config.database import get_session

# ==============================
# Application facades
# ==============================

from facades import (
    AuditLogFacade,
    AuthFacade,
    UserFacade,
)

# ==============================
# Authentication utilities
# ==============================

from utils import JWTAuth, JWTManager


# ==============================
# JWT authentication
# ==============================

# Create one shared JWT manager using application settings.
jwt_manager = JWTManager(
    secret_key=settings.JWT_SECRET_KEY,
    algorithm=settings.JWT_ALGORITHM,
    access_token_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
)

# Create shared authentication dependencies for API routes.
jwt_auth = JWTAuth(
    jwt_manager=jwt_manager,
)


# ==============================
# Authentication facade dependency
# ==============================

def get_auth_facade(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AuthFacade:
    """Provide the authentication facade."""
    return AuthFacade(
        session=session,
        jwt_manager=jwt_manager,
    )


# ==============================
# User facade dependency
# ==============================

def get_user_facade(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserFacade:
    """Provide the user facade."""
    return UserFacade(
        session=session,
    )


# ==============================
# Audit facade dependency
# ==============================

def get_audit_log_facade(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AuditLogFacade:
    """Provide the audit facade."""
    return AuditLogFacade(
        session=session,
    )
