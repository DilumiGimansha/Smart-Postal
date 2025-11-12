from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Voice Enrollment
class VoiceEnrollmentRequest(BaseModel):
    order_id: Optional[int] = None
    # Audio will be sent as file upload, not in JSON

class VoiceEnrollmentResponse(BaseModel):
    success: bool
    message: str
    samples_recorded: int
    samples_required: int
    enrollment_complete: bool
    quality_score: Optional[float] = None

# Fingerprint Enrollment
class FingerprintEnrollmentRequest(BaseModel):
    order_id: Optional[int] = None
    device_id: str
    template_data: str  # Base64 encoded fingerprint template

class FingerprintEnrollmentResponse(BaseModel):
    success: bool
    message: str
    enrollment_complete: bool

# Voice Verification
class VoiceVerificationRequest(BaseModel):
    order_id: int
    # Audio will be sent as file upload

class VoiceVerificationResponse(BaseModel):
    success: bool
    verified: bool
    confidence_score: float
    ai_detected: bool
    ai_detection_score: Optional[float]
    message: str

# Fingerprint Verification
class FingerprintVerificationRequest(BaseModel):
    order_id: int
    device_id: str
    template_data: str  # Base64 encoded fingerprint template

class FingerprintVerificationResponse(BaseModel):
    success: bool
    verified: bool
    confidence_score: float
    message: str

# Verification Log Response
class VerificationLogResponse(BaseModel):
    id: int
    user_id: int
    order_id: Optional[int]
    verification_type: str
    success: bool
    confidence_score: Optional[float]
    ai_detection_score: Optional[float]
    ai_detected: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
