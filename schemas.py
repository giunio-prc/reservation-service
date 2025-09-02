from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List

class AvailabilityBase(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    hour: int = Field(..., ge=0, le=23, description="Hour in 24h format")
    is_available: bool = True

class AvailabilityCreate(AvailabilityBase):
    pass

class AvailabilityResponse(AvailabilityBase):
    id: int

    class Config:
        from_attributes = True

class ReservationBase(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    hour: int = Field(..., ge=0, le=23, description="Hour in 24h format")
    client_name: str = Field(..., min_length=1, max_length=100)
    client_email: EmailStr
    reservation_date: datetime

class ReservationCreate(ReservationBase):
    pass

class ReservationResponse(ReservationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AvailabilityBulkUpdate(BaseModel):
    availabilities: List[AvailabilityBase]

class ErrorResponse(BaseModel):
    detail: str