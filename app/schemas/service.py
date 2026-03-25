from pydantic import BaseModel
from typing import Optional

class ServiceBase(BaseModel):
    name: str
    description: str
    icon: str

class ServiceItem(ServiceBase):
    id: int

    class Config:
        from_attributes = True

class AppointmentCreate(BaseModel):
    service_id: int
    date_time: str
    notes: Optional[str] = None
