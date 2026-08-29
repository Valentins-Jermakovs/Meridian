"""
The schemas define request and response structures for authentication,
tokens, users, system metrics, and audit logs.
"""


# ==============================
# Authentication schemas
# ==============================

from .auth import (
    LoginRequest,
    TokenResponse,
)


# ==============================
# Token schemas
# ==============================

from .refresh_token import RefreshTokenRequest
from .token import TokenCleanupResponse


# ==============================
# User schemas
# ==============================

from .user import (
    UserAdminUpdate,
    UserCreate,
    UserListItem,
    UserListResponse,
    UserRegistrationStatisticItem,
    UserRegistrationStatisticsResponse,
    UserResponse,
    UserSelfUpdate,
    UserStatisticsResponse,
)


# ==============================
# Metrics schemas
# ==============================

from .metrics import SystemMetricsResponse


# ==============================
# Audit schemas
# ==============================

from .audit import (
    AuditLogListItem,
    AuditLogListResponse,
)