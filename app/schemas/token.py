# ==============================
# Library Imports
# ==============================

from pydantic import BaseModel

# ==============================
# Refresh Token Cleanup Response Schema
# ==============================

class TokenCleanupResponse(BaseModel):

    '''
    Represents a response to the token cleanup request.

    Attributes:
       expired_deleted (int): Number of expired tokens deleted.
       revoked_deleted (int): Number of revoked tokens deleted.
    '''

    expired_deleted: int
    revoked_deleted: int