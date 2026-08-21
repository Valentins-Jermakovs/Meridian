# ==============================
# Library Imports
# ==============================

from fastapi import (
    APIRouter,
    Depends,
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
    UserStatisticsResponse,
)

from utils import (
    RedisCache,
    JWTManager,
    JWTAuth,
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
        query (str | None):
            The search query.
        page (int):
            The page number.
        page_size (int):
            The page size.
        current_user (dict):
            Authenticated administrator.
        session (AsyncSession):
            Asynchronous database session.

    Returns:
        UserListResponse:
            Paginated list of users.
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
# User Statistics
# ==============================

@router.get(
    "/stats",
    response_model=UserStatisticsResponse,
)
async def get_user_statistics(
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
    Returns aggregated user statistics.

    The statistics are cached in Redis by the user service.

    Args:
        current_user (dict):
            Authenticated administrator.
        session (AsyncSession):
            Asynchronous database session.

    Returns:
        UserStatisticsResponse:
            Total, active, and blocked user counts.
    """

    facade = UserFacade(
        session=session,
        redis_cache=redis_cache,
    )

    return await facade.get_statistics()


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
        current_user (dict):
            Authenticated user.
        session (AsyncSession):
            Asynchronous database session.

    Returns:
        UserResponse:
            Current user information.
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
        data (UserSelfUpdate):
            New user information.
        current_user (dict):
            Authenticated user.
        session (AsyncSession):
            Asynchronous database session.

    Returns:
        UserResponse:
            Updated user information.
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
    Gets user information by ID.

    Args:
        user_id (int):
            User ID.
        current_user (dict):
            Authenticated administrator.
        session (AsyncSession):
            Asynchronous database session.

    Returns:
        UserResponse:
            User information.
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
    Updates user information by administrator.

    Args:
        user_id (int):
            User ID.
        data (UserAdminUpdate):
            New user information.
        current_user (dict):
            Authenticated administrator.
        session (AsyncSession):
            Asynchronous database session.

    Returns:
        UserResponse:
            Updated user information.
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