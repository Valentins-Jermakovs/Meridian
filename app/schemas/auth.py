# ==============================
# Bibliotēku imports
# ==============================

from sqlmodel import Field, SQLModel


# ==============================
# Pieslēgšanās shēma
# ==============================

class LoginRequest(SQLModel):

    # Lietotājvārds vai e-pasts
    login: str = Field(
        min_length=1,
        max_length=255,
    )

    # Parole
    password: str = Field(
        min_length=1,
        max_length=255,
    )


# ==============================
# Tokenu atbildes shēma
# ==============================

class TokenResponse(SQLModel):

    # Access tokens
    access_token: str

    # Refresh tokens
    refresh_token: str

    # Tokena tips
    token_type: str = "bearer"