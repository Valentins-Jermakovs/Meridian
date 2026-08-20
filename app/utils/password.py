# ==============================
# Bibliotēku imports
# ==============================

import asyncio

from argon2 import PasswordHasher


# ==============================
# Paroļu pārvaldības klase
# ==============================

class PasswordManager:

    def __init__(
        self,
    ):
        # Argon2 paroļu hešēšanas objekts
        self.hasher = PasswordHasher()

    # ==============================
    # Paroles hešošana
    # ==============================

    def hash_password(
        self,
        password: str,
    ) -> str:

        return self.hasher.hash(
            password
        )

    # ==============================
    # Sinhronā paroles pārbaude
    # ==============================

    def _verify_password(
        self,
        password: str,
        password_hash: str,
    ) -> bool:

        try:
            return self.hasher.verify(
                password_hash,
                password,
            )

        except Exception:
            return False

    # ==============================
    # Asinhronā paroles pārbaude
    # ==============================

    async def verify_password(
        self,
        password: str,
        password_hash: str,
    ) -> bool:

        return await asyncio.to_thread(
            self._verify_password,
            password,
            password_hash,
        )