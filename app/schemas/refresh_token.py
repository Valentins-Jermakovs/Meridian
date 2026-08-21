# ==============================
# Library Imports
# ==============================

from pydantic import BaseModel


# ==============================
# Refresh Token Request Schema
# ==============================

class RefreshTokenRequest(BaseModel):
    """
    Represents a request to refresh an access token.

    Attributes:
        refresh_token (str): Refresh token used to obtain a new access token.
    """

    # Refresh token used to obtain a new access token
    refresh_token: str