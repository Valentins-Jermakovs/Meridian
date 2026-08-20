# ==============================
# Bibliotēku imports
# ==============================

from fastapi import APIRouter


# ==============================
# Maršrutētāju imports
# ==============================

from .auth import router as auth_router
from .users import router as users_router
from .metrics import router as metrics_router
from .audit_log import router as audit_log_router

# ==============================
# Galvenais maršrutētājs
# ==============================

main_router = APIRouter()


# ==============================
# Maršrutu pievienošana
# ==============================

main_router.include_router(
    auth_router
)

main_router.include_router(
    users_router
)

main_router.include_router(
    metrics_router
)

main_router.include_router(
    audit_log_router
)