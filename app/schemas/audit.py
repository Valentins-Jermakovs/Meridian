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

    items: list[AuditLogListItem]
    page: int
    page_size: int
    total: int
    pages: int