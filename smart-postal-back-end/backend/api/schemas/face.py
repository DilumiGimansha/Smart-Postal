from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

# Face Enrollment (ID Card Upload)
class FaceIDUploadRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class FaceIDUploadResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[int] = None
    face_id: Optional[int] = None
    quality_score: Optional[float] = None
    liveness_passed: Optional[bool] = None

# Face Verification
class FaceVerificationRequest(BaseModel):
    user_id: int
    order_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class FaceVerificationResponse(BaseModel):
    success: bool
    verified: bool
    confidence: float
    similarity_score: float
    threshold: float
    message: str
    quality_score: Optional[float] = None
    liveness_passed: Optional[bool] = None
    metrics: Optional[Dict[str, Any]] = None  # Allow strings and numbers

# Locker Face Verification
class LockerVerificationRequest(BaseModel):
    locker_id: str
    user_id: int
    parcel_id: Optional[str] = None

class LockerVerificationResponse(BaseModel):
    success: bool
    unlock: bool
    token: Optional[str] = None
    message: str
    confidence: float
    expires_in: Optional[int] = None  # Token expiry in seconds

# Locker Unlock
class LockerUnlockRequest(BaseModel):
    token: str
    locker_id: str

class LockerUnlockResponse(BaseModel):
    success: bool
    status: str
    message: str
    locker_id: str
    unlocked_at: Optional[datetime] = None

# Face Template Info
class FaceTemplateResponse(BaseModel):
    id: int
    user_id: int
    enrollment_type: Optional[str]
    quality_score: Optional[float]
    confidence_score: Optional[float]
    liveness_score: Optional[float]
    anti_spoof_passed: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
