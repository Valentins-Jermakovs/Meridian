# ==============================
# Bibliotēku imports
# ==============================

from datetime import datetime

from sqlmodel import SQLModel

from models import AuditAction


# ==============================
# Audit žurnāla saraksta elements
# ==============================

class AuditLogListItem(SQLModel):

    # Ieraksta identifikators
    id: int

    # Lietotāja identifikators
    user_id: int | None

    # Veiktā darbība
    action: AuditAction

    # Darbības apraksts
    description: str

    # Darbības rezultāts
    success: bool

    # Ieraksta izveidošanas laiks
    created_at: datetime


# ==============================
# Audit žurnāla saraksta atbilde
# ==============================

class AuditLogListResponse(SQLModel):

    # Audit ieraksti
    items: list[AuditLogListItem]

    # Pašreizējā lapa
    page: int

    # Ierakstu skaits vienā lapā
    page_size: int

    # Kopējais ierakstu skaits
    total: int

    # Kopējais lapu skaits
    pages: int