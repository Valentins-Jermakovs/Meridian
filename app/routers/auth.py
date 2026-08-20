# ==============================
# Bibliotēku imports
# ==============================

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_session

from facades import AuthFacade

from schemas import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
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