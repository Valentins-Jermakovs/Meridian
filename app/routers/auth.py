# ==============================
# Library Imports
# ==============================

from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from config.config import settings
from config.database import get_session

from facades import AuthFacade

from schemas import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)

from utils import (
    JWTManager, 
    JWTAuth
)



# ==============================
# JWT Configuration
# ==============================

jwt_manager = JWTManager(
    secret_key=settings.JWT_SECRET_KEY,
    algorithm=settings.JWT_ALGORITHM,
    access_token_expire_minutes=(
        settings.ACCESS_TOKEN_EXPIRE_MINUTES
    ),
)

jwt_auth = JWTAuth(
    jwt_manager=jwt_manager,
)


# ==============================
# Authentication Router
# ==============================

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ==============================
# User Registration
# ==============================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
async def register(
    data: UserCreate,
    session: AsyncSession = Depends(
        get_session
    ),
):
    """
    Registers a new user.
    
    Args:
        data (UserCreate): The user data.
        session (AsyncSession): The asynchronous database session. Depends on get_session.
    
    Returns:
        UserResponse: The registered user.
    """
    facade = AuthFacade(session)

    return await facade.register(
        data
    )


# ==============================
# User Login
# ==============================

@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    data: LoginRequest,
    session: AsyncSession = Depends(
        get_session
    ),
):
    """
    Logs in a user.
    
    Args:
        data (LoginRequest): The login request.
        session (AsyncSession): The asynchronous database session. Depends on get_session.
    
    Returns:
        TokenResponse: The token response.
    """
    facade = AuthFacade(session)

    return await facade.login(
        data
    )


# ==============================
# Refresh Token Rotation
# ==============================

@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh(
    data: RefreshTokenRequest,
    session: AsyncSession = Depends(
        get_session
    ),
):
    """
    Rotates the refresh token.
    
    Args:
        data (RefreshTokenRequest): The refresh token request.
        session (AsyncSession): The asynchronous database session. Depends on get_session.
    
    Returns:
        TokenResponse: The rotated token response.
    """
    facade = AuthFacade(session)

    return await facade.refresh(
        data
    )


# ==============================
# Log out Current Session
# ==============================

@router.post(
    "/logout",
    status_code=204,
)
async def logout(
    data: RefreshTokenRequest,
    session: AsyncSession = Depends(
        get_session
    ),
):
    """
    Logs out the current session.
    
    Args:
        data (RefreshTokenRequest): The refresh token request.
        session (AsyncSession): The asynchronous database session. Depends on get_session.
    """
    facade = AuthFacade(session)

    await facade.logout(
        data
    )


# ==============================
# Log out All Sessions
# ==============================

@router.post(
    "/logout-all",
    status_code=204,
)
async def logout_all(
    current_user: dict = Depends(
        jwt_auth.get_current_user
    ),
    session: AsyncSession = Depends(
        get_session
    ),
):
    """
    Logs out all sessions.
    
    Args:
        current_user (dict): The current user. Depends on JWTAuth.
        session (AsyncSession): The asynchronous database session. Depends on get_session.
    """
    facade = AuthFacade(session)

    user_id = int(
        current_user["sub"]
    )

    await facade.logout_all(
        user_id
    )