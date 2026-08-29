# ==============================
# Library Imports
# ==============================

from pydantic import BaseModel

# ==============================
# Refresh Token Cleanup Response Schema
# ==============================

class TokenCleanupResponse(BaseModel):

   expired_deleted: int
   revoked_deleted: int