# ==============================
# Library Imports
# ==============================

from pydantic import BaseModel


# ==============================
# Refresh Token Request Schema
# ==============================

class RefreshTokenRequest(BaseModel):

    # Refresh token used to obtain a new access token
    refresh_token: str