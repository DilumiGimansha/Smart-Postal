from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    BIOMETRIC_ENROLLED = "biometric_enrolled"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    FAILED = "failed"

# Order Creation
class OrderCreate(BaseModel):
    delivery_address: str = Field(..., min_length=10, max_length=500)
    delivery_city: str = Field(..., min_length=2, max_length=100)
    delivery_postal_code: str = Field(..., min_length=4, max_length=10)
    delivery_instructions: Optional[str] = Field(None, max_length=500)
    total_amount: float = Field(..., gt=0)
    verification_required: bool = True
    
    @validator('total_amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Total amount must be greater than 0')
        return round(v, 2)

# Order Response
class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_id: int
    courier_id: Optional[int]
    delivery_address: str
    delivery_city: str
    delivery_postal_code: str
    delivery_instructions: Optional[str]
    status: OrderStatus
    total_amount: float
    voice_enrolled: bool
    fingerprint_enrolled: bool
    verification_required: bool
    created_at: datetime
    updated_at: Optional[datetime]
    delivered_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Order Update
class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    courier_id: Optional[int] = None
    delivery_instructions: Optional[str] = None

# Order List Filter
class OrderFilter(BaseModel):
    status: Optional[OrderStatus] = None
    customer_id: Optional[int] = None
    courier_id: Optional[int] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None

# Courier Assignment
class CourierAssignment(BaseModel):
    order_id: int
    courier_id: int