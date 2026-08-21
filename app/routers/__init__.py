# ==============================
# Library Imports
# ==============================

from fastapi import APIRouter


# ==============================
# Router Imports
# ==============================

from .auth import router as auth_router
from .users import router as users_router
from .metrics import router as metrics_router
from .audit_log import router as audit_log_router

# ==============================
# Main Router
# ==============================

main_router = APIRouter()


# ==============================
# Add Routes to Main Router
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