# ==============================
# Library Imports
# ==============================

from pydantic import BaseModel


# ==============================
# System Metrics Schema
# ==============================

class SystemMetricsResponse(BaseModel):

    # Current CPU usage percentage
    cpu_percent: float

    # Current memory usage percentage
    memory_percent: float

    # Memory currently used by the process in megabytes
    memory_used_mb: int