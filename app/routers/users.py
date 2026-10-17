
# ==============================
# Standard library imports
# ==============================

from typing import Annotated

# ==============================
# Third-party imports
# ==============================

from fastapi import APIRouter, Depends, Query

# ==============================
# Application facades
# ==============================

from facades.user import UserFacade

# ==============================
# Application schemas
# ==============================

from schemas import (
    UserAdminUpdate,
    UserListResponse,
    UserRegistrationStatisticsResponse,
    UserResponse,
    UserSelfUpdate,
    UserStatisticsResponse,
)

# ==============================
# Router dependencies
# ==============================

from routers.dependencies import (
    get_user_facade,
    jwt_auth,
)


# ==============================
# Users router
# ==============================

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ==============================
# Search users
# Administrator only
# ==============================

@router.get(
    "/",
    response_model=UserListResponse,
)
async def search_users(
    current_user: Annotated[
        dict,
        Depends(jwt_auth.require_roles(["admin"])),
    ],
    facade: Annotated[
        UserFacade,
        Depends(get_user_facade),
    ],
    query: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> UserListResponse:
    """Search users with pagination."""
    return await facade.search(
        query=query,
        page=page,
        page_size=page_size,
    )


# ==============================
# User statistics
# Administrator only
# ==============================

@router.get(
    "/stats",
    response_model=UserStatisticsResponse,
)
async def get_user_statistics(
    current_user: Annotated[
        dict,
        Depends(jwt_auth.require_roles(["admin"])),
    ],
    facade: Annotated[
        UserFacade,
        Depends(get_user_facade),
    ],
) -> UserStatisticsResponse:
    """Return aggregated user statistics."""
    return await facade.get_statistics()


# ==============================
# User registration statistics
# Administrator only
# ==============================

@router.get(
    "/stats/registrations",
    response_model=UserRegistrationStatisticsResponse,
)
async def get_user_registration_statistics(
    current_user: Annotated[
        dict,
        Depends(jwt_auth.require_roles(["admin"])),
    ],
    facade: Annotated[
        UserFacade,
        Depends(get_user_facade),
    ],
    year: int | None = Query(default=None, ge=2000, le=2100),
) -> UserRegistrationStatisticsResponse:
    """Return monthly registration statistics for a year."""
    return await facade.get_registration_statistics(
        year=year,
    )


# ==============================
# Current user profile
# Authenticated users
# ==============================

@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_current_user(
    current_user: Annotated[
        dict,
        Depends(jwt_auth.get_current_user),
    ],
    facade: Annotated[
        UserFacade,
        Depends(get_user_facade),
    ],
) -> UserResponse:
    """Return the profile of the authenticated user."""
    return await facade.get_by_id(
        user_id=int(current_user["sub"]),
    )


# ==============================
# Update current user profile
# Authenticated users
# ==============================

@router.patch(
    "/me",
    response_model=UserResponse,
)
async def update_current_user(
    data: UserSelfUpdate,
    current_user: Annotated[
        dict,
        Depends(jwt_auth.get_current_user),
    ],
    facade: Annotated[
        UserFacade,
        Depends(get_user_facade),
    ],
) -> UserResponse:
    """Update the authenticated user's profile."""
    return await facade.update_self(
        user_id=int(current_user["sub"]),
        data=data,
    )


# ==============================
# Get user by ID
# Administrator only
# ==============================

@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user_by_id(
    user_id: int,
    current_user: Annotated[
        dict,
        Depends(jwt_auth.require_roles(["admin"])),
    ],
    facade: Annotated[
        UserFacade,
        Depends(get_user_facade),
    ],
) -> UserResponse:
    """Return a user's profile by ID."""
    return await facade.get_by_id(
        user_id=user_id,
    )


# ==============================
# Update user by administrator
# Administrator only
# ==============================

@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
async def update_user_by_admin(
    user_id: int,
    data: UserAdminUpdate,
    current_user: Annotated[
        dict,
        Depends(jwt_auth.require_roles(["admin"])),
    ],
    facade: Annotated[
        UserFacade,
        Depends(get_user_facade),
    ],
) -> UserResponse:
    """Update a user's profile with administrator privileges."""
    return await facade.update_by_admin(
        admin_id=int(current_user["sub"]),
        user_id=user_id,
        data=data,
    )
