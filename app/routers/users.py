# ==============================
# Bibliotēku imports
# ==============================

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.config import settings
from config.database import get_session

from facades.user import UserFacade

from schemas import (
    UserAdminUpdate,
    UserListResponse,
    UserResponse,
    UserSelfUpdate,
)

from utils.jwt import JWTManager
from utils.jwt_auth import JWTAuth


# ==============================
# JWT konfigurācija
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
# Lietotāja maršrutētājs
# ==============================

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ==============================
# Lietotāju meklēšana
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
    facade = UserFacade(session)

    return await facade.search(
        query=query,
        page=page,
        page_size=page_size,
    )



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
    facade = UserFacade(session)

    user_id = int(
        current_user["sub"]
    )

    return await facade.get_by_id(
        user_id
    )


# ==============================
# Paša lietotāja atjaunošana
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
    facade = UserFacade(session)

    user_id = int(
        current_user["sub"]
    )

    return await facade.update_self(
        user_id=user_id,
        data=data,
    )


# ==============================
# Lietotāja atjaunošana
# administratora režīmā
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
    facade = UserFacade(session)

    admin_id = int(
        current_user["sub"]
    )

    return await facade.update_by_admin(
        admin_id=admin_id,
        user_id=user_id,
        data=data,
    )