# ==============================
# Library Imports
# ==============================

from pydantic import BaseModel


# ==============================
# System Metrics Schema
# ==============================

class SystemMetricsResponse(BaseModel):
    """
    Represents system metrics for the current server process.

    Attributes:
        cpu_percent (float): Current CPU usage percentage.
        memory_percent (float): Current memory usage percentage.
        memory_used_mb (int): Amount of memory currently used in megabytes.
    """

    # Current CPU usage percentage
    cpu_percent: float

    # Current memory usage percentage
    memory_percent: float

    # Memory currently used by the process in megabytes
    memory_used_mb: int