# ==============================
# Library Imports
# ==============================

import asyncio

from argon2 import PasswordHasher


# ==============================
# Password Management
# ==============================

class PasswordManager:
    """
    Provides password hashing and verification using Argon2.

    Password verification is executed in a separate thread to prevent
    the CPU-intensive hashing operation from blocking the asynchronous
    application event loop.
    """

    def __init__(
        self,
    ):
        """
        Initializes the password manager.

        Creates an Argon2 password hashing instance used for hashing
        and verifying passwords.
        """

        # Argon2 password hashing instance
        self.hasher = PasswordHasher()

    # ==============================
    # Hash Password
    # ==============================

    def hash_password(
        self,
        password: str,
    ) -> str:
        """
        Hashes a plain-text password using Argon2.

        Args:
            password (str):
                Plain-text password to hash.

        Returns:
            str: Argon2 password hash.
        """

        return self.hasher.hash(
            password
        )

    # ==============================
    # Synchronous Password Verification
    # ==============================

    def _verify_password(
        self,
        password: str,
        password_hash: str,
    ) -> bool:
        """
        Verifies a plain-text password against an Argon2 hash.

        This method performs the verification synchronously and is
        intended to be executed outside the main asynchronous event loop.

        Args:
            password (str):
                Plain-text password to verify.
            password_hash (str):
                Previously generated Argon2 password hash.

        Returns:
            bool: True if the password matches the hash, otherwise False.
        """

        try:
            return self.hasher.verify(
                password_hash,
                password,
            )

        except Exception:
            return False

    # ==============================
    # Asynchronous Password Verification
    # ==============================

    async def verify_password(
        self,
        password: str,
        password_hash: str,
    ) -> bool:
        """
        Asynchronously verifies a password against an Argon2 hash.

        The CPU-intensive verification operation is executed in a
        background thread so that the main event loop remains responsive.

        Args:
            password (str):
                Plain-text password to verify.
            password_hash (str):
                Previously generated Argon2 password hash.

        Returns:
            bool: True if the password matches the hash, otherwise False.
        """

        return await asyncio.to_thread(
            self._verify_password,
            password,
            password_hash,
        )