# Bibliotēkas:
from pydantic import BaseModel

# Metriku shēma
class SystemMetricsResponse(BaseModel):

    cpu_percent: float
    memory_percent: float
    memory_used_mb: int