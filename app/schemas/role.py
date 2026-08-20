# ==============================
# Bibliotēku imports
# ==============================

from sqlmodel import SQLModel


# ==============================
# Lomas atbildes shēma
# ==============================

class RoleResponse(SQLModel):

    # Lomas identifikators
    id: int

    # Lomas nosaukums
    name: str

    # Lomas apraksts
    description: str | None = None