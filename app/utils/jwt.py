# ==============================
# Bibliotēku imports
# ==============================

from datetime import datetime, timedelta, timezone

import jwt


# ==============================
# JWT tokenu pārvaldības klase
# ==============================

class JWTManager:

    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        access_token_expire_minutes: int,
    ):
        # JWT slepenā atslēga
        self.secret_key = secret_key

        # JWT algoritms
        self.algorithm = algorithm

        # Access tokena derīguma termiņš
        self.access_token_expire_minutes = (
            access_token_expire_minutes
        )

    # Access tokena izveide
    def create_access_token(
        self,
        user_id: int,
        roles: list[str],
    ) -> str:

        now = datetime.now(timezone.utc)

        payload = {
            "sub": str(user_id),
            "roles": roles,
            "type": "access",
            "iat": now,
            "exp": now + timedelta(
                minutes=self.access_token_expire_minutes
            ),
        }

        return jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm,
        )

    # JWT tokena dekodēšana
    def decode_access_token(
        self,
        token: str,
    ) -> dict:

        return jwt.decode(
            token,
            self.secret_key,
            algorithms=[self.algorithm],
        )

    # JWT tokena validācija
    def validate_access_token(
        self,
        token: str,
    ) -> bool:

        try:
            payload = self.decode_access_token(token)

            # Pārbauda tokena tipu
            if payload.get("type") != "access":
                return False

            # Pārbauda lietotāja identifikatoru
            if not payload.get("sub"):
                return False

            return True

        except jwt.ExpiredSignatureError:
            return False

        except jwt.InvalidTokenError:
            return False

    # Pārbauda, vai tokenam ir konkrēta loma
    def has_role(
        self,
        token: str,
        role: str,
    ) -> bool:

        try:
            payload = self.decode_access_token(token)

            if payload.get("type") != "access":
                return False

            roles = payload.get("roles", [])

            return role in roles

        except jwt.InvalidTokenError:
            return False

    # Atgriež lietotāja identifikatoru no tokena
    def get_user_id(
        self,
        token: str,
    ) -> int:

        payload = self.decode_access_token(token)

        return int(payload["sub"])

    # Atgriež lietotāja lomas no tokena
    def get_roles(
        self,
        token: str,
    ) -> list[str]:

        payload = self.decode_access_token(token)

        return payload.get("roles", [])