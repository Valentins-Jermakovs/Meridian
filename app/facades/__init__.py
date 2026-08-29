"""
This module contains facade classes that provide simple interfaces
for authentication, user, and audit log-related functionality.
"""


# ==============================
# Facade imports
# ==============================

from .audit import AuditLogFacade
from .auth import AuthFacade
from .user import UserFacade