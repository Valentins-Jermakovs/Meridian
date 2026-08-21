# ==============================
# Library Imports
# ==============================

import asyncio

import psutil

from fastapi import (
    APIRouter,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)

from config.config import settings

from schemas import SystemMetricsResponse

from utils import (
    JWTManager,
    JWTAuth,
)


# ==============================
# JWT Configuration
# ==============================

jwt_manager = JWTManager(
    secret_key=settings.JWT_SECRET_KEY,
    algorithm=settings.JWT_ALGORITHM,
    access_token_expire_minutes=(
        settings.ACCESS_TOKEN_EXPIRE_MINUTES
    ),
)

jwt_auth = JWTAuth(
    jwt_manager=jwt_manager,
)


# ==============================
# Metrics Router
# ==============================

router = APIRouter(
    prefix="/metrics",
    tags=["Metrics services"],
)


# ==============================
# Server Metrics WebSocket
# ==============================

@router.websocket("/ws/stats")
async def metrics_websocket(
    websocket: WebSocket,
    token: str | None = Query(default=None),
):
    """
    Sends server metrics over a WebSocket connection.

    Args:
        websocket (WebSocket): The WebSocket connection.
        token (str | None): The access token. Defaults to None.

    Returns:
        None
    """

    # Check whether an access token was provided
    if token is None:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION
        )
        return

    # Validate the access token
    try:
        payload = jwt_manager.validate_access_token(
            token
        )

        # Check whether the user has the administrator role
        roles = payload.get(
            "roles",
            []
        )

        if "admin" not in roles:
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION
            )
            return

    except Exception:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION
        )
        return

    # Accept the WebSocket connection
    await websocket.accept()

    # Get the current FastAPI/Uvicorn process
    process = psutil.Process()

    try:
        while True:
            # Get CPU usage of the current process
            cpu_percent = process.cpu_percent()

            # Get memory information of the current process
            memory = process.memory_info()

            data: SystemMetricsResponse = {
                "cpu_percent": cpu_percent,

                "memory_percent": round(
                    process.memory_percent(),
                    2,
                ),

                "memory_used_mb": round(
                    memory.rss / (1024 ** 2)
                ),
            }

            # Send metrics to the connected client
            await websocket.send_json(
                data
            )

            # Update metrics every second
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        pass