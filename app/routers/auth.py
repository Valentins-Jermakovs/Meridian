
# ==============================
# Standard library imports
# ==============================

from typing import Annotated

# ==============================
# Third-party imports
# ==============================

from fastapi import APIRouter, Depends

# ==============================
# Application facades
# ==============================

from facades import AuthFacade

# ==============================
# Application schemas
# ==============================

from schemas import (
    LoginRequest,
    RefreshTokenRequest,
    TokenCleanupResponse,
    TokenResponse,
    UserCreate,
    UserResponse,
)

# ==============================
# Router dependencies
# ==============================

from routers.dependencies import (
    get_auth_facade,
    jwt_auth,
)


# ==============================
# Authentication router
# ==============================

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ==============================
# User registration
# ==============================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
async def register(
    data: UserCreate,
    facade: Annotated[AuthFacade, Depends(get_auth_facade)],
) -> UserResponse:
    """Register a new user."""
    return await facade.register(data)


# ==============================
# User login
# ==============================

@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    data: LoginRequest,
    facade: Annotated[AuthFacade, Depends(get_auth_facade)],
) -> TokenResponse:
    """Authenticate a user and issue tokens."""
    return await facade.login(data)


# ==============================
# Refresh token rotation
# ==============================

@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh(
    data: RefreshTokenRequest,
    facade: Annotated[AuthFacade, Depends(get_auth_facade)],
) -> TokenResponse:
    """Rotate a refresh token."""
    return await facade.refresh(data)


# ==============================
# Logout current session
# ==============================

@router.post(
    "/logout",
    status_code=204,
)
async def logout(
    data: RefreshTokenRequest,
    facade: Annotated[AuthFacade, Depends(get_auth_facade)],
) -> None:
    """Log out the current refresh-token session."""
    await facade.logout(data)


# ==============================
# Logout all user sessions
# ==============================

@router.post(
    "/logout-all",
    status_code=204,
)
async def logout_all(
    current_user: Annotated[
        dict,
        Depends(jwt_auth.get_current_user),
    ],
    facade: Annotated[AuthFacade, Depends(get_auth_facade)],
) -> None:
    """Log out all sessions belonging to the authenticated user."""
    await facade.logout_all(
        user_id=int(current_user["sub"]),
    )


# ==============================
# Refresh token cleanup
# Administrator only
# ==============================

@router.post(
    "/tokens/cleanup",
    response_model=TokenCleanupResponse,
)
async def cleanup_tokens(
    admin: Annotated[
        dict,
        Depends(jwt_auth.require_roles(["admin"])),
    ],
    facade: Annotated[AuthFacade, Depends(get_auth_facade)],
) -> TokenCleanupResponse:
    """Delete expired and old revoked refresh tokens."""
    return await facade.cleanup_tokens()
