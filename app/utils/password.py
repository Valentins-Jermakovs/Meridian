# ==============================
# Bibliotēku imports
# ==============================

from argon2 import PasswordHasher


# ==============================
# Paroļu pārvaldības klase
# ==============================

class PasswordManager:

    def __init__(self):
        # Argon2 paroļu hešēšanas objekts
        self.hasher = PasswordHasher()

    # Paroles hešošana
    def hash_password(
        self,
        password: str,
    ) -> str:

        return self.hasher.hash(password)

    # Paroles pārbaude pret hešu
    def verify_password(
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