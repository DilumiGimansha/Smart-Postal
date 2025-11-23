from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
import pickle
import numpy as np
from typing import Optional

from models.database import get_db
from models.user import User
from models.order import Order
from models.biometric import VoiceTemplate, VerificationLog
from api.schemas.biometric import (
    VoiceEnrollmentResponse, 
    VoiceVerificationResponse
)
from api.middleware.auth import get_current_user
from utils.voice_banking import voice_processor
from config.settings import get_settings
from loguru import logger

router = APIRouter(prefix="/api/voice", tags=["Voice Authentication"])
settings = get_settings()

@router.post("/enroll", response_model=VoiceEnrollmentResponse)
async def enroll_voice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Enroll a voice sample for the current user.
    Requires multiple samples to build a robust template.
    """
    # 1. Process the audio file with quality checks (liveness check disabled for enrollment flexibility)
    try:
        result = await voice_processor.process_audio(
            file,
            perform_quality_check=True,
            perform_liveness_check=False  # Less strict for enrollment
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Audio validation failed: {result['error']}"
            )
        
        new_embedding = result["embedding"]
        quality_metrics = result.get("quality_metrics", {})
        liveness_metrics = result.get("liveness_metrics", {})
        
        logger.info(f"Enrollment audio processed - Quality: {quality_metrics}, Liveness: {liveness_metrics}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing audio: {str(e)}"
        )

    # 2. Get or create voice template
    voice_template = db.query(VoiceTemplate).filter(
        VoiceTemplate.user_id == current_user.id
    ).first()

    if not voice_template:
        voice_template = VoiceTemplate(
            user_id=current_user.id,
            embedding_data=pickle.dumps(new_embedding),
            sample_count=1,
            is_active=True
        )
        db.add(voice_template)
    else:
        # Update existing template (averaging)
        try:
            current_embedding = pickle.loads(voice_template.embedding_data)
            n = voice_template.sample_count
            
            # Weighted average: (old * n + new) / (n + 1)
            updated_embedding = (current_embedding * n + new_embedding) / (n + 1)
            # Re-normalize
            updated_embedding = updated_embedding / (np.linalg.norm(updated_embedding) + 1e-8)
            
            voice_template.embedding_data = pickle.dumps(updated_embedding)
            voice_template.sample_count += 1
        except (pickle.UnpicklingError, Exception) as e:
            # If old data is corrupted, replace it with new data
            voice_template.embedding_data = pickle.dumps(new_embedding)
            voice_template.sample_count = 1

    db.commit()
    db.refresh(voice_template)

    # 3. Check if enrollment is complete
    is_complete = voice_template.sample_count >= settings.MIN_VOICE_SAMPLES
    
    return VoiceEnrollmentResponse(
        success=True,
        message="Voice sample processed successfully",
        samples_recorded=voice_template.sample_count,
        samples_required=settings.MIN_VOICE_SAMPLES,
        enrollment_complete=is_complete,
        quality_score=0.95 # Placeholder for quality score
    )

@router.post("/verify", response_model=VoiceVerificationResponse)
async def verify_voice(
    order_id: int = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verify voice against the enrolled template.
    If order_id is provided, verifies against the order's customer.
    Otherwise, verifies against the current user.
    """
    # 1. Determine which user to verify against
    if order_id:
        # Validate Order
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        customer_id = order.customer_id
    else:
        # For testing: verify against current user
        customer_id = current_user.id

    # 2. Get Customer's Voice Template
    voice_template = db.query(VoiceTemplate).filter(
        VoiceTemplate.user_id == customer_id
    ).first()

    if not voice_template or not voice_template.embedding_data:
        raise HTTPException(
            status_code=400, 
            detail="User has not enrolled for voice authentication"
        )

    # 3. Process incoming audio with security checks
    try:
        result = await voice_processor.process_audio(
            file,
            perform_quality_check=True,
            perform_liveness_check=True
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Audio validation failed: {result['error']}"
            )
        
        incoming_embedding = result["embedding"]
        quality_metrics = result.get("quality_metrics", {})
        liveness_metrics = result.get("liveness_metrics", {})
        
        logger.info(f"Verification audio processed - Quality: {quality_metrics}, Liveness: {liveness_metrics}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing audio: {str(e)}")

    # 4. Verify
    try:
        stored_embedding = pickle.loads(voice_template.embedding_data)
    except (pickle.UnpicklingError, Exception) as e:
        raise HTTPException(
            status_code=400,
            detail="Voice template data is corrupted. Please re-enroll."
        )
    
    # Use ensemble verification (banking-grade)
    is_verified, ensemble_score, verification_metrics = voice_processor.verify_voice_ensemble(
        incoming_embedding, 
        stored_embedding,
        use_strict_threshold=False  # Set True for high-security transactions
    )
    
    logger.info(f"Verification metrics: {verification_metrics}")
    
    # Liveness check already performed during audio processing
    # The liveness_metrics contains anti-spoofing results
    is_ai = not liveness_metrics.get("is_live", True) if liveness_metrics else False
    ai_score = 1.0 - liveness_metrics.get("confidence", 1.0) if liveness_metrics else 0.0
    
    if not liveness_metrics.get("is_live", True):
        is_verified = False
        message = f"Voice verification failed: Liveness check failed (possible replay attack or synthetic voice)"
    elif is_verified:
        message = f"✓ Voice verification successful (Ensemble: {ensemble_score:.3f}, Cosine: {verification_metrics['cosine_similarity']:.3f})"
        
        # --- Adaptive Learning: Update template with verified sample ---
        try:
            # We already have stored_embedding loaded
            n = voice_template.sample_count
            
            # Weighted average: (old * n + new) / (n + 1)
            updated_embedding = (stored_embedding * n + incoming_embedding) / (n + 1)
            # Re-normalize
            updated_embedding = updated_embedding / (np.linalg.norm(updated_embedding) + 1e-8)
            
            voice_template.embedding_data = pickle.dumps(updated_embedding)
            voice_template.sample_count += 1
            db.add(voice_template)
            logger.info(f"✓ Adaptive Learning: Template updated (samples: {n} -> {n+1})")
        except Exception as e:
            logger.error(f"Failed to update voice template: {e}")
            # Don't fail verification if update fails
            
    else:
        # Use specific failure reason if available
        fail_reason = verification_metrics.get('fail_reason')
        if fail_reason:
            message = f"✗ Voice verification failed: {fail_reason}"
        else:
            actual_threshold = verification_metrics.get('threshold_used', settings.VOICE_SIMILARITY_THRESHOLD)
            message = f"✗ Voice verification failed: Voice did not match (Ensemble: {ensemble_score:.3f}, Threshold: {actual_threshold:.3f})"

    # 5. Log the attempt with enhanced security metrics
    log = VerificationLog(
        user_id=customer_id,
        order_id=order_id,
        verification_type="voice",
        success=is_verified,
        confidence_score=ensemble_score,
        ai_detected=is_ai,
        ai_detection_score=ai_score,
        ip_address="0.0.0.0", # TODO: Get from request
        device_info="unknown" # TODO: Get from request
    )
    db.add(log)
    db.commit()

    return VoiceVerificationResponse(
        success=True,
        verified=is_verified,
        confidence_score=ensemble_score,
        ai_detected=is_ai,
        ai_detection_score=ai_score,
        message=message
    )
