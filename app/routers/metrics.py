
# ==============================
# Standard library imports
# ==============================

import asyncio
import logging

# ==============================
# Third-party imports
# ==============================

import jwt
import psutil

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect


# ==============================
# Application imports
# ==============================

from routers.dependencies import jwt_manager
from schemas import SystemMetricsResponse


# ==============================
# Logger configuration
# ==============================

logger = logging.getLogger(__name__)


# ==============================
# Metrics router
# ==============================

router = APIRouter(
    prefix="/metrics",
    tags=["Metrics services"],
)


# ==============================
# Server metrics WebSocket
# ==============================

@router.websocket("/ws/stats")
async def metrics_websocket(
    websocket: WebSocket,
    token: str | None = Query(default=None),
) -> None:
    """Stream process metrics to authenticated administrators."""

    # Require an access token.
    if not token:
        await websocket.close(code=1008)
        return

    # Validate the access token.
    try:
        payload = jwt_manager.validate_access_token(token)

    except jwt.InvalidTokenError:
        await websocket.close(code=1008)
        return

    # Allow administrators only.
    roles = payload.get("roles", [])

    if not isinstance(roles, list) or "admin" not in roles:
        await websocket.close(code=1008)
        return

    # Accept the connection after successful authorization.
    await websocket.accept()
    logger.info("Administrator connected to metrics WebSocket.")

    # Monitor the current API process.
    process = psutil.Process()
    process.cpu_percent()

    try:
        while True:
            # Collect metrics once per second.
            await asyncio.sleep(1)

            memory = process.memory_info()

            data: SystemMetricsResponse = {
                "cpu_percent": process.cpu_percent(),
                "memory_percent": round(
                    process.memory_percent(),
                    2,
                ),
                "memory_used_mb": round(
                    memory.rss / (1024 ** 2)
                ),
            }

            # Send the current metrics to the connected client.
            await websocket.send_json(data)

    except WebSocketDisconnect:
        logger.info("Administrator disconnected from metrics WebSocket.")
