# ==============================
# Bibliotēku imports
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
# Autentifikācijas maršrutētājs
# ==============================

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ==============================
# Lietotāja reģistrācija
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
    facade = AuthFacade(session)

    return await facade.register(
        data
    )


# ==============================
# Lietotāja pieslēgšanās
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
    facade = AuthFacade(session)

    return await facade.login(
        data
    )


# ==============================
# Refresh tokena rotācija
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
    facade = AuthFacade(session)

    return await facade.refresh(
        data
    )


# ==============================
# Atteikšanās no pašreizējās sesijas
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
    facade = AuthFacade(session)

    await facade.logout(
        data
    )


# ==============================
# Atteikšanās no visām sesijām
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
    facade = AuthFacade(session)

    user_id = int(
        current_user["sub"]
    )

    await facade.logout_all(
        user_id
    )