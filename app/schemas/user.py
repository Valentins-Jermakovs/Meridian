# ==============================
# Bibliotēku imports
# ==============================

from datetime import datetime

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


# ==============================
# Lietotāja izveides shēma
# ==============================

class UserCreate(SQLModel):

    # Lietotājvārds
    username: str = Field(
        min_length=5,
        max_length=100,
    )

    # Pilnais vārds
    full_name: str = Field(
        min_length=10,
        max_length=255,
    )

    # E-pasta adrese
    email: EmailStr

    # Parole
    password: str = Field(
        min_length=8,
        max_length=255,
    )


# ==============================
# Lietotāja pašatjaunošanas shēma
# ==============================

class UserSelfUpdate(SQLModel):

    # Lietotājvārds
    username: str | None = Field(
        default=None,
        min_length=5,
        max_length=100,
    )

    # Pilnais vārds
    full_name: str | None = Field(
        default=None,
        min_length=10,
        max_length=255,
    )

    # E-pasta adrese
    email: EmailStr | None = None

    # Pašreizējā parole
    current_password: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    # Jaunā parole
    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=255,
    )


# ==============================
# Lietotāja administratora
# atjaunošanas shēma
# ==============================

class UserAdminUpdate(SQLModel):

    # Lietotājvārds
    username: str | None = Field(
        default=None,
        min_length=5,
        max_length=100,
    )

    # Pilnais vārds
    full_name: str | None = Field(
        default=None,
        min_length=10,
        max_length=255,
    )

    # E-pasta adrese
    email: EmailStr | None = None

    # Jaunā parole
    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=255,
    )

    # Konta aktivitātes statuss
    is_active: bool | None = None

    # Lietotāja lomas
    roles: list[str] | None = None


# ==============================
# Lietotāja pilnā atbildes shēma
# ==============================

# ==============================
# Lietotāja pilnā atbildes shēma
# ==============================

class UserResponse(SQLModel):

    # Lietotāja identifikators
    id: int

    # Lietotājvārds
    username: str

    # Lietotāja pilnais vārds
    full_name: str

    # Lietotāja e-pasta adrese
    email: EmailStr

    # Lietotāja lomas
    roles: list[str]

    # Lietotāja konta aktivitātes statuss
    is_active: bool

    # Lietotāja izveidošanas datums
    created_at: datetime


# ==============================
# Lietotāja saraksta elementa shēma
# ==============================

class UserListItem(SQLModel):

    # Lietotāja identifikators
    id: int

    # Lietotājvārds
    username: str

    # Pilnais vārds
    full_name: str

    # E-pasta adrese
    email: EmailStr

    # Konta aktivitātes statuss
    is_active: bool


# ==============================
# Lietotāju saraksta atbildes shēma
# ==============================

class UserListResponse(SQLModel):

    # Lietotāju saraksts
    items: list[UserListItem]

    # Pašreizējā lapa
    page: int

    # Lietotāju skaits vienā lapā
    page_size: int

    # Kopējais lietotāju skaits
    total: int

    # Kopējais lapu skaits
    pages: int