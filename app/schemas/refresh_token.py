# ==============================
# Bibliotēku imports
# ==============================

from sqlmodel import SQLModel


# ==============================
# Refresh tokena atjaunošanas shēma
# ==============================

class RefreshTokenRequest(SQLModel):

    # Refresh tokens
    refresh_token: str