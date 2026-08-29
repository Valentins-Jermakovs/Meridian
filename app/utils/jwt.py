# ==============================
# Library Imports
# ==============================

from datetime import (
    datetime,
    timedelta,
    timezone,
)

import jwt


# ==============================
# JWT Token Management
# ==============================

class JWTManager:
    """
    Provides functionality for creating, decoding, and validating
    JWT access tokens.

    The manager stores user identification and role information
    inside the token and validates the token type and subject
    before allowing it to be used for authentication.
    """


    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        access_token_expire_minutes: int,
    ):
        """
        Initializes the JWT manager.

        Args:
            secret_key (str):
                Secret key used to sign and validate JWT tokens.
            algorithm (str):
                JWT signing algorithm.
            access_token_expire_minutes (int):
                Lifetime of an access token in minutes.
        """

        # JWT secret key
        self.secret_key = secret_key

        # JWT signing algorithm
        self.algorithm = algorithm

        # Access token expiration period
        self.access_token_expire_minutes = (
            access_token_expire_minutes
        )


    # ==============================
    # Create Access Token
    # ==============================

    def create_access_token(
        self,
        user_id: int,
        roles: list[str],
    ) -> str:
        """
        Creates a signed JWT access token for a user.

        The token contains the user's identifier, assigned roles,
        token type, creation time, and expiration time.

        Args:
            user_id (int):
                Unique identifier of the user.
            roles (list[str]):
                Roles assigned to the user.

        Returns:
            str: Encoded JWT access token.
        """

        # Get the current UTC time
        now = datetime.now(timezone.utc)

        # Build JWT payload
        payload = {
            "sub": str(user_id),
            "roles": roles,
            "type": "access",
            "iat": now,
            "exp": now + timedelta(
                minutes=self.access_token_expire_minutes
            ),
        }

        # Encode and sign the JWT
        return jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm,
        )


    # ==============================
    # Decode Access Token
    # ==============================

    def decode_access_token(
        self,
        token: str,
    ) -> dict:
        """
        Decodes and verifies a JWT access token.

        Args:
            token (str):
                Encoded JWT access token.

        Returns:
            dict: Decoded JWT payload.

        Raises:
            jwt.InvalidTokenError:
                If the token is invalid or cannot be verified.
            jwt.ExpiredSignatureError:
                If the token has expired.
        """

        return jwt.decode(
            token,
            self.secret_key,
            algorithms=[self.algorithm],
        )


    # ==============================
    # Validate Access Token
    # ==============================

    def validate_access_token(
        self,
        token: str,
    ) -> dict:
        """
        Validates the structure and contents of an access token.

        In addition to cryptographic validation, the method verifies
        that the token has the expected access-token type and contains
        a user identifier.

        Args:
            token (str):
                Encoded JWT access token.

        Returns:
            dict: Validated JWT payload.

        Raises:
            jwt.InvalidTokenError:
                If the token type or subject is invalid or missing.
        """

        # Decode and cryptographically validate the token
        payload = self.decode_access_token(token)

        # Check token type
        if payload.get("type") != "access":
            raise jwt.InvalidTokenError(
                "Invalid token type"
            )

        # Check user identifier
        if not payload.get("sub"):
            raise jwt.InvalidTokenError(
                "Missing subject"
            )

        return payload


    # ==============================
    # Check User Role
    # ==============================

    def has_role(
        self,
        token: str,
        role: str,
    ) -> bool:
        """
        Checks whether an access token contains a specific role.

        Args:
            token (str):
                Encoded JWT access token.
            role (str):
                Role to check.

        Returns:
            bool: True if the specified role is assigned to the user,
                otherwise False.
        """

        # Validate and decode the access token
        payload = self.validate_access_token(
            token
        )

        # Get roles from the token
        roles = payload.get("roles", [])

        return role in roles


    # ==============================
    # Get User ID
    # ==============================

    def get_user_id(
        self,
        token: str,
    ) -> int:
        """
        Extracts the user identifier from an access token.

        Args:
            token (str):
                Encoded JWT access token.

        Returns:
            int: User identifier stored in the token.
        """

        # Validate and decode the access token
        payload = self.validate_access_token(
            token
        )

        return int(payload["sub"])


    # ==============================
    # Get User Roles
    # ==============================

    def get_roles(
        self,
        token: str,
    ) -> list[str]:
        """
        Extracts the user's roles from an access token.

        Args:
            token (str):
                Encoded JWT access token.

        Returns:
            list[str]: List of roles stored in the token.
        """

        # Validate and decode the access token
        payload = self.validate_access_token(
            token
        )

        return payload.get("roles", [])