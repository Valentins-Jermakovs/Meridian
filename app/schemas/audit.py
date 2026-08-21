# ==============================
# Library Imports
# ==============================

from datetime import datetime

from pydantic import BaseModel

from models import AuditAction


# ==============================
# Audit Log List Item
# ==============================

class AuditLogListItem(BaseModel):
    """
    Represents a single entry in the audit log.

    Attributes:
        id (int): Unique identifier of the log entry.
        user_id (int | None): Identifier of the user who performed the action.
        action (AuditAction): Type of action performed.
        description (str): Brief description of the action.
        success (bool): Indicates whether the action was successful.
        created_at (datetime): Timestamp when the log entry was created.
    """

    id: int
    user_id: int | None
    action: AuditAction
    description: str
    success: bool
    created_at: datetime


# ==============================
# Audit Log List Response
# ==============================

class AuditLogListResponse(BaseModel):
    """
    Represents a paginated response containing audit log entries.

    Attributes:
        items (list[AuditLogListItem]): List of audit log entries on the current page.
        page (int): Current page number.
        page_size (int): Number of log entries per page.
        total (int): Total number of audit log entries.
        pages (int): Total number of available pages.
    """

    items: list[AuditLogListItem]
    page: int
    page_size: int
    total: int
    pages: int