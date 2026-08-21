# ==============================
# Schemas Imports
# ==============================


"""
This file contains the imports of all schemas used in the application.
"""

from .auth import (
    LoginRequest,
    TokenResponse
)
"""
Schemas for authentication-related data.

    - LoginRequest: The request body for the login endpoint.
    - TokenResponse: The response containing the access token and refresh token.
"""


from .refresh_token import RefreshTokenRequest
"""
Schema for refresh token requests.
    
    - RefreshTokenRequest: The request body for refreshing a token.
"""


from .user import (
    UserCreate,
    UserSelfUpdate,
    UserAdminUpdate,
    UserResponse,
    UserListItem,
    UserListResponse
)
"""
Schemas for user-related data.

    - UserCreate: The request body for creating a new user.
    - UserSelfUpdate: The request body for updating the current user's information.
    - UserAdminUpdate: The request body for updating another user's information by an admin.
    - UserResponse: The response containing the user's information.
    - UserListItem: The list item containing the user's information in a list of users.
    - UserListResponse: The response containing the list of users.
"""


from .metrics import SystemMetricsResponse
"""
Schema for system metrics-related data.

    - SystemMetricsResponse: The response containing the system metrics.
"""


from .audit import (
    AuditLogListItem,
    AuditLogListResponse
)
"""
Schemas for audit log-related data.

    - AuditLogListItem: The list item containing an audit log entry in a list of audit logs.
    - AuditLogListResponse: The response containing the list of audit logs.
"""
