# ==============================
# Bibliotēku imports
# ==============================

import hashlib
import secrets


# ==============================
# Refresh tokenu pārvaldības klase
# ==============================

class RefreshTokenManager:

    # Refresh tokena ģenerēšana
    def generate_token(self) -> str:

        return secrets.token_urlsafe(64)

    # Refresh tokena hešošana
    def hash_token(
        self,
        token: str,
    ) -> str:

        return hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

    # Refresh tokena pārbaude pret hešu
    def verify_token(
        self,
        token: str,
        token_hash: str,
    ) -> bool:

        token_hash_from_token = self.hash_token(
            token
        )

        return secrets.compare_digest(
            token_hash_from_token,
            token_hash,
        )