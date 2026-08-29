# ==============================
# Library Imports
# ==============================

from collections.abc import Callable

import jwt

from fastapi import (
    Depends,
    HTTPException,
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from .jwt import JWTManager


# ==============================
# JWT Route Protection
# ==============================

class JWTAuth:
    """
    Provides JWT-based authentication and role-based authorization
    for protected FastAPI routes.

    The class validates access tokens from the Authorization header
    and provides dependencies for checking the roles assigned to
    the authenticated user.
    """


    def __init__(
        self,
        jwt_manager: JWTManager,
    ):
        """
        Initializes the JWT authentication handler.

        Args:
            jwt_manager (JWTManager):
                Manager responsible for creating and validating JWTs.
        """

        # JWT manager
        self.jwt_manager = jwt_manager

        # Bearer authentication scheme
        self.bearer = HTTPBearer()


    # ==============================
    # Get Current User from Token
    # ==============================

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(
            HTTPBearer()
        ),
    ) -> dict:
        """
        Validates the access token from the Authorization header.

        Args:
            credentials (HTTPAuthorizationCredentials):
                Bearer authentication credentials provided by FastAPI.

        Returns:
            dict: JWT payload containing the authenticated user's data.

        Raises:
            HTTPException: If the token has expired or is invalid.
        """

        # Get token from the Authorization header
        token = credentials.credentials

        try:
            # Validate access token
            return self.jwt_manager.validate_access_token(
                token
            )

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token has expired",
            )

        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )


    # ==============================
    # Require Specific Roles
    # ==============================

    def require_roles(
        self,
        roles: list[str],
    ) -> Callable:
        """
        Creates a FastAPI dependency that requires at least one
        of the specified user roles.

        Args:
            roles (list[str]):
                Roles allowed to access the protected route.

        Returns:
            Callable:
                FastAPI dependency that validates the user's roles.

        Raises:
            HTTPException: If the authenticated user does not have
                any of the required roles.
        """

        async def dependency(
            payload: dict = Depends(
                self.get_current_user
            ),
        ) -> dict:
            """
            Validates whether the authenticated user has
            at least one required role.

            Args:
                payload (dict):
                    Validated JWT payload of the current user.

            Returns:
                dict: JWT payload of the authorized user.

            Raises:
                HTTPException: If the user does not have any
                    of the required roles.
            """

            # Get roles assigned to the authenticated user
            user_roles = payload.get(
                "roles",
                [],
            )

            # Check whether the user has at least one
            # of the required roles
            if not any(
                role in user_roles
                for role in roles
            ):
                raise HTTPException(
                    status_code=403,
                    detail="Forbidden",
                )

            return payload

        return dependency