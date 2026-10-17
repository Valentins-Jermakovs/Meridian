# ==============================
# Third-party imports
# ==============================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text


# ==============================
# Application imports
# ==============================

from config.database import engine
from config.redis import get_redis
from routers.dependencies import jwt_auth


# ==============================
# Health router
# ==============================

router = APIRouter(
    tags=["Health"],
)


# ==============================
# API health check
# ==============================

@router.get("/health")
async def health_check(
    admin: dict = Depends(jwt_auth.require_roles(["admin"])),
) -> dict[str, str]:
    """Return the API health status."""
    return {"status": "ok"}


# ==============================
# Application readiness check
# ==============================

@router.get("/health/ready")
async def readiness_check(
    admin: dict = Depends(jwt_auth.require_roles(["admin"])),
) -> dict[str, str]:
    """Check whether PostgreSQL and Redis are available."""

    # Check PostgreSQL.
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database is unavailable.",
        ) from None

    # Check Redis.
    try:
        await get_redis().ping()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Redis is unavailable.",
        ) from None

    return {
        "status": "ready",
        "database": "ok",
        "redis": "ok",
    }