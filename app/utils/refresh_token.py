# ==============================
# Library Imports
# ==============================

import hashlib
import secrets


# ==============================
# Refresh Token Management
# ==============================

class RefreshTokenManager:
    """
    Provides functionality for generating, hashing, and verifying
    refresh tokens.

    Raw refresh tokens are generated using a cryptographically secure
    random generator and are hashed before being stored.
    """


    # ==============================
    # Generate Refresh Token
    # ==============================

    def generate_token(self) -> str:
        """
        Generates a cryptographically secure random refresh token.

        Returns:
            str: URL-safe random refresh token.
        """

        return secrets.token_urlsafe(64)


    # ==============================
    # Hash Refresh Token
    # ==============================

    def hash_token(
        self,
        token: str,
    ) -> str:
        """
        Creates a SHA-256 hash of a refresh token.

        The raw token is not required to be stored in the database.
        Only its hash can be stored and later used for verification.

        Args:
            token (str):
                Raw refresh token.

        Returns:
            str: Hexadecimal SHA-256 hash of the token.
        """

        return hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()


    # ==============================
    # Verify Refresh Token
    # ==============================

    def verify_token(
        self,
        token: str,
        token_hash: str,
    ) -> bool:
        """
        Verifies a refresh token against its stored hash.

        Constant-time comparison is used to reduce the risk of
        timing-based attacks during hash comparison.

        Args:
            token (str):
                Raw refresh token provided by the client.
            token_hash (str):
                Previously stored SHA-256 hash.

        Returns:
            bool:
                True if the token matches the stored hash,
                otherwise False.
        """

        # Calculate the hash of the provided token
        token_hash_from_token = self.hash_token(
            token
        )

        # Compare hashes using constant-time comparison
        return secrets.compare_digest(
            token_hash_from_token,
            token_hash,
        )