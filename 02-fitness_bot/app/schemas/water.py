from datetime import datetime
from pydantic import BaseModel


class WaterLog(BaseModel):
    user_id: int
    amount: float
    timestamp: datetime

    class Config:
        from_attributes = True
