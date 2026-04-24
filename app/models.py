from datetime import datetime
from typing import List, Literal
from pydantic import BaseModel, Field

class TelemetryRecord(BaseModel):
    vehicle_id: str
    timestamp: datetime
    fault_codes: List[str]
    speed_kmh: float
    engine_temp_celsius: float
    mileage_km: int

class SummaryResponse(BaseModel):
    vehicle_id: str
    summary: str
    severity: Literal['LOW', 'MEDIUM', 'HIGH']
