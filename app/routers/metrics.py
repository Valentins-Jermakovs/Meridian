# Libraries:
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

# Schemas
from schemas import SystemMetricsResponse

# Utils
from utils.jwt import JWTManager
from utils.jwt_auth import JWTAuth


# ==============================
# JWT konfigurācija
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
# Metriku maršrutētājs
# ==============================

router = APIRouter(
    prefix="/metrics",
    tags=["Metrics services"],
)



# ==============================
# Servera metrikas WebSocket
# ==============================

@router.websocket("/ws/stats")
async def metrics_websocket(
    websocket: WebSocket,
    token: str | None = Query(default=None),
):
    # Pārbauda, vai tokens ir saņemts
    if token is None:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION
        )
        return

    # Tokena validācija
    try:
        payload = jwt_manager.validate_access_token(
            token
        )

        # Pārbauda administratora lomu
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

    # Savienojuma pieņemšana
    await websocket.accept()

    try:
        while True:
            # CPU
            cpu_percent = psutil.cpu_percent()

            # Atmiņa
            memory = psutil.virtual_memory()

            data: SystemMetricsResponse = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_mb": round(
                    memory.used
                    / 1024
                    / 1024
                ),
            }

            # Metriku nosūtīšana klientam
            await websocket.send_json(data)

            # Metriku atjaunošana katru sekundi
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        # Klients aizvēra savienojumu
        pass
