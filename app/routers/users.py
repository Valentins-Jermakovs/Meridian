# ==============================
# Library Imports
# ==============================
from fastapi import (
    APIRouter, 
    Depends
)
from sqlalchemy.ext.asyncio import AsyncSession

from config.config import settings
from config.database import get_session
from config.redis import redis_client

from facades.user import UserFacade

from schemas import (
    UserAdminUpdate,
    UserListResponse,
    UserResponse,
    UserSelfUpdate,
)

from utils import (
    RedisCache, 
    JWTManager, 
    JWTAuth
)


# ==============================
# Redis cache configuration
# ==============================

redis_cache = RedisCache(
    client=redis_client,
    ttl=settings.REDIS_CACHE_TTL,
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
# User Router
# ==============================

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ==============================
# Search Users
# ==============================

@router.get(
    "/",
    response_model=UserListResponse,
)
async def search_users(
    query: str | None = None,
    page: int = 1,
    page_size: int = 20,
    current_user: dict = Depends(
        jwt_auth.require_roles(
            ["admin"]
        )
    ),
    session: AsyncSession = Depends(
        get_session
    ),
):
    """
    Searches for users.
    
    Args:
        query (str | None): The search query. Defaults to None.
        page (int): The page number. Defaults to 1.
        page_size (int): The page size. Defaults to 20.
        current_user (dict): The current user. Depends on JWTAuth.
        session (AsyncSession): The asynchronous database session. Depends on get_session.
    
    Returns:
        UserListResponse: The list of users.
    """
    facade = UserFacade(
        session=session,
        redis_cache=redis_cache,
    )

    return await facade.search(
        query=query,
        page=page,
        page_size=page_size,
    )


# ==============================
# Current User Information
# ==============================

@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_current_user(
    current_user: dict = Depends(
        jwt_auth.get_current_user
    ),
    session: AsyncSession = Depends(
        get_session
    ),
):
    """
    Gets the current user information.
    
    Args:
        current_user (dict): The current user. Defaults to None.
        session (AsyncSession): The asynchronous database session. Defaults to None.
    
    Returns:
        UserResponse: The current user information.
    """
    facade = UserFacade(
        session=session,
        redis_cache=redis_cache,
    )

    user_id = int(
        current_user["sub"]
    )

    return await facade.get_by_id(
        user_id
    )


# ==============================
# Update Current User Information
# ==============================

@router.patch(
    "/me",
    response_model=UserResponse,
)
async def update_current_user(
    data: UserSelfUpdate,
    current_user: dict = Depends(
        jwt_auth.get_current_user
    ),
    session: AsyncSession = Depends(
        get_session
    ),
):
    """
    Updates the current user information.
    
    Args:
        data (UserSelfUpdate): The new user information.
        current_user (dict): The current user. Defaults to None.
        session (AsyncSession): The asynchronous database session. Defaults to None.
    
    Returns:
        UserResponse: The updated user information.
    """
    facade = UserFacade(
        session=session,
        redis_cache=redis_cache,
    )

    user_id = int(
        current_user["sub"]
    )

    return await facade.update_self(
        user_id=user_id,
        data=data,
    )


# ==============================
# Get User Information by ID
# Administrator Role
# ==============================

@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user_by_id(
    user_id: int,
    current_user: dict = Depends(
        jwt_auth.require_roles(
            ["admin"]
        )
    ),
    session: AsyncSession = Depends(
        get_session
    ),
):
    """
    Gets the user information by ID.
    
    Args:
        user_id (int): The user ID.
        current_user (dict): The current user. Defaults to None.
        session (AsyncSession): The asynchronous database session. Defaults to None.
    
    Returns:
        UserResponse: The user information.
    """
    facade = UserFacade(
        session=session,
        redis_cache=redis_cache,
    )

    return await facade.get_by_id(
        user_id
    )


# ==============================
# Update User Information by Admin
# ==============================

@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
async def update_user_by_admin(
    user_id: int,
    data: UserAdminUpdate,
    current_user: dict = Depends(
        jwt_auth.require_roles(
            ["admin"]
        )
    ),
    session: AsyncSession = Depends(
        get_session
    ),
):
    """
    Updates the user information by admin.
    
    Args:
        user_id (int): The user ID.
        data (UserAdminUpdate): The new user information.
        current_user (dict): The current user. Defaults to None.
        session (AsyncSession): The asynchronous database session. Defaults to None.
    
    Returns:
        UserResponse: The updated user information.
    """
    facade = UserFacade(
        session=session,
        redis_cache=redis_cache,
    )

    admin_id = int(
        current_user["sub"]
    )

    return await facade.update_by_admin(
        admin_id=admin_id,
        user_id=user_id,
        data=data,
    )