from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

# Voice Enrollment
class VoiceEnrollmentRequest(BaseModel):
    order_id: Optional[int] = None
    # Audio will be sent as file upload, not in JSON
    metadata: Optional[Dict[str, Any]] = None  # Device/network metadata

class VoiceEnrollmentResponse(BaseModel):
    success: bool
    message: str
    samples_recorded: int
    samples_required: int
    enrollment_complete: bool
    quality_score: Optional[float] = None
    decision: Optional[str] = None  # accept, challenge, deny, require_2fa
    risk_level: Optional[str] = None  # low, medium, high, critical
    risk_score: Optional[float] = None
    challenge_id: Optional[str] = None  # If challenge required

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
    metadata: Optional[Dict[str, Any]] = None  # Device/network metadata
    challenge_id: Optional[str] = None  # If responding to challenge

class VoiceVerificationResponse(BaseModel):
    success: bool
    verified: bool
    confidence_score: float
    ai_detected: bool
    ai_detection_score: Optional[float]
    ai_probability: Optional[float] = None
    is_rerecorded: Optional[bool] = None
    message: str
    decision: Optional[str] = None  # accept, challenge, deny, require_2fa
    risk_level: Optional[str] = None  # low, medium, high, critical
    risk_score: Optional[float] = None
    challenge_id: Optional[str] = None  # If challenge required
    challenge_phrase: Optional[str] = None  # If challenge required
    should_flag: Optional[bool] = None  # Flag for review

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

# Challenge Request/Response (Active Liveness)
class ChallengeCreateRequest(BaseModel):
    user_id: Optional[int] = None  # Optional, can use current user

class ChallengeCreateResponse(BaseModel):
    success: bool
    challenge_id: str
    phrase: str
    expires_in_seconds: int
    message: str

class ChallengeVerifyRequest(BaseModel):
    challenge_id: str
    # Audio will be sent as file upload
    order_id: Optional[int] = None

class ChallengeVerifyResponse(BaseModel):
    success: bool
    verified: bool
    challenge_passed: bool
    confidence_score: float
    ai_detected: bool
    message: str
    decision: str  # Final decision after challenge
    risk_level: str

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
