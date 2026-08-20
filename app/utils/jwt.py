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

    # Access tokena dekodēšana
    def decode_access_token(
        self,
        token: str,
    ) -> dict:

        return jwt.decode(
            token,
            self.secret_key,
            algorithms=[self.algorithm],
        )

    # Access tokena validācija
    def validate_access_token(
        self,
        token: str,
    ) -> dict:

        payload = self.decode_access_token(token)

        # Pārbauda tokena tipu
        if payload.get("type") != "access":
            raise jwt.InvalidTokenError(
                "Invalid token type"
            )

        # Pārbauda lietotāja identifikatoru
        if not payload.get("sub"):
            raise jwt.InvalidTokenError(
                "Missing subject"
            )

        return payload

    # Pārbauda, vai tokenam ir konkrēta loma
    def has_role(
        self,
        token: str,
        role: str,
    ) -> bool:

        payload = self.validate_access_token(
            token
        )

        roles = payload.get("roles", [])

        return role in roles

    # Atgriež lietotāja identifikatoru no tokena
    def get_user_id(
        self,
        token: str,
    ) -> int:

        payload = self.validate_access_token(
            token
        )

        return int(payload["sub"])

    # Atgriež lietotāja lomas no tokena
    def get_roles(
        self,
        token: str,
    ) -> list[str]:

        payload = self.validate_access_token(
            token
        )

        return payload.get("roles", [])