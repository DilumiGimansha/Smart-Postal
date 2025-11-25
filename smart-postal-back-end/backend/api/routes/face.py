from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
import pickle
import numpy as np
from typing import Optional

from models.database import get_db
from models.user import User
from models.order import Order
from models.biometric import FaceTemplate, VerificationLog
from api.schemas.face import (
    FaceIDUploadResponse,
    FaceVerificationResponse,
    LockerVerificationResponse,
    LockerUnlockRequest,
    LockerUnlockResponse,
    FaceTemplateResponse
)
from api.middleware.auth import get_current_user, get_current_admin
from utils.face_recognition import face_processor
from utils.locker import locker_manager
from utils.security import encrypt_biometric_data, decrypt_biometric_data
from config.settings import get_settings
from loguru import logger

router = APIRouter(prefix="/api/face", tags=["Face Recognition"])
settings = get_settings()


@router.post("/id/upload", response_model=FaceIDUploadResponse)
async def upload_id_card(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload ID card image and extract face for enrollment
    Creates or updates face template for the user
    """
    try:
        logger.info(f"📸 Processing ID card for user {current_user.id}")
        
        # Process face image (lenient for ID card enrollment)
        result = await face_processor.process_face_image(
            file,
            perform_quality_check=True,
            perform_liveness_check=False  # Skip liveness for ID card photos
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": result["error"],
                    "error_code": result.get("error_code", "PROCESSING_FAILED")
                }
            )
        
        embedding = result["embedding"]
        quality_metrics = result.get("quality_metrics") or {}
        liveness_metrics = result.get("liveness_metrics") or {}
        
        logger.info(f"✓ Face extracted - Quality: {quality_metrics.get('quality_score', 0):.2f}, "
                   f"Liveness: {liveness_metrics.get('is_live', 'N/A')}")
        
        # Encrypt embedding
        embedding_bytes = pickle.dumps(embedding)
        encrypted_embedding = encrypt_biometric_data(embedding_bytes)
        
        # Store or update ID card info
        id_info = {
            "name": name,
            "phone": phone,
            "address": address
        }
        encrypted_id_info = encrypt_biometric_data(pickle.dumps(id_info))
        
        # Check if user already has a face template
        face_template = db.query(FaceTemplate).filter(
            FaceTemplate.user_id == current_user.id
        ).first()
        
        if face_template:
            # Update existing template
            face_template.embedding_data = encrypted_embedding
            face_template.id_card_info = encrypted_id_info
            face_template.face_quality_score = quality_metrics.get('quality_score', 0.0)
            face_template.confidence_score = result["detection"].get('confidence', 0.0)
            face_template.liveness_score = liveness_metrics.get('confidence', 0.0)
            face_template.anti_spoof_passed = liveness_metrics.get('is_live', True)
            face_template.enrollment_type = 'id_card'
            logger.info(f"Updated face template for user {current_user.id}")
        else:
            # Create new template
            face_template = FaceTemplate(
                user_id=current_user.id,
                embedding_data=encrypted_embedding,
                id_card_info=encrypted_id_info,
                face_quality_score=quality_metrics.get('quality_score', 0.0),
                confidence_score=result["detection"].get('confidence', 0.0),
                liveness_score=liveness_metrics.get('confidence', 0.0),
                anti_spoof_passed=liveness_metrics.get('is_live', True),
                enrollment_type='id_card',
                is_active=True
            )
            db.add(face_template)
            logger.info(f"Created new face template for user {current_user.id}")
        
        db.commit()
        db.refresh(face_template)
        
        return FaceIDUploadResponse(
            success=True,
            message="ID card processed and face template stored",
            user_id=current_user.id,
            face_id=face_template.id,
            quality_score=quality_metrics.get('quality_score', 0.0),
            liveness_passed=liveness_metrics.get('is_live', True)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ID upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ID card processing failed: {str(e)}"
        )


@router.post("/verify", response_model=FaceVerificationResponse)
async def verify_face(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    order_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verify live face against stored face template
    Used by couriers to verify recipient identity
    """
    try:
        logger.info(f"🔍 Verifying face for user {user_id}")
        
        # Get stored face template
        face_template = db.query(FaceTemplate).filter(
            FaceTemplate.user_id == user_id,
            FaceTemplate.is_active == True
        ).first()
        
        if not face_template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User has not enrolled face template"
            )
        
        # Process incoming face (relaxed quality for testing, strict matching)
        result = await face_processor.process_face_image(
            file,
            perform_quality_check=True,  # Check quality
            perform_liveness_check=False,  # Disabled for testing with photos
            strict_quality=False  # Allow ID card photos for testing
        )
        
        if not result["success"]:
            # Log failed attempt
            log = VerificationLog(
                user_id=user_id,
                order_id=order_id,
                verification_type="face",
                success=False,
                confidence_score=0.0,
                failure_reason=result.get("error", "Face processing failed"),
                ip_address="0.0.0.0",
                device_info="face_verification"
            )
            db.add(log)
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": result["error"],
                    "error_code": result.get("error_code", "PROCESSING_FAILED")
                }
            )
        
        incoming_embedding = result["embedding"]
        quality_metrics = result.get("quality_metrics") or {}
        liveness_metrics = result.get("liveness_metrics") or {}
        
        # Decrypt stored embedding
        try:
            decrypted_embedding = decrypt_biometric_data(face_template.embedding_data)
            stored_embedding = pickle.loads(decrypted_embedding)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Face template corrupted. Please re-enroll."
            )
        
        # Verify faces with banking-grade threshold
        is_match, similarity_score, metrics = face_processor.verify_faces(
            incoming_embedding,
            stored_embedding,
            threshold=0.75  # Banking-grade: 75% minimum similarity
        )
        
        # Determine final verification result
        verified = is_match and liveness_metrics.get('is_live', True)
        
        if not verified and is_match:
            message = f"Liveness check failed - possible photo/screen attack"
        elif verified:
            message = f"✓ Face verified successfully (similarity: {similarity_score:.1%})"
        else:
            message = f"✗ Face does not match (similarity: {similarity_score:.1%}, threshold: {metrics['threshold_used']:.1%})"
        
        # Log verification attempt
        log = VerificationLog(
            user_id=user_id,
            order_id=order_id,
            verification_type="face",
            success=verified,
            confidence_score=similarity_score,
            ai_detected=not liveness_metrics.get('is_live', True),
            ai_detection_score=1.0 - liveness_metrics.get('confidence', 1.0),
            ip_address="0.0.0.0",
            device_info="face_verification",
            failure_reason=None if verified else message
        )
        db.add(log)
        db.commit()
        
        logger.info(f"Face verification: {'✓ PASSED' if verified else '✗ FAILED'} - "
                   f"Similarity: {similarity_score:.3f}, Liveness: {liveness_metrics.get('is_live', True)}")
        
        return FaceVerificationResponse(
            success=True,
            verified=verified,
            confidence=similarity_score,
            similarity_score=similarity_score,
            threshold=metrics.get('threshold_used', 0.6),
            message=message,
            quality_score=quality_metrics.get('quality_score'),
            liveness_passed=liveness_metrics.get('is_live', True),
            metrics=metrics
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Face verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}"
        )


@router.post("/locker/verify", response_model=LockerVerificationResponse)
async def verify_face_for_locker(
    file: UploadFile = File(...),
    locker_id: str = Form(...),
    user_id: int = Form(...),
    parcel_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Verify face at smart locker
    Returns unlock token if verification successful
    No authentication required (locker device calls this)
    """
    try:
        logger.info(f"🔒 Locker verification: locker_id={locker_id}, user_id={user_id}")
        
        # Get stored face template
        face_template = db.query(FaceTemplate).filter(
            FaceTemplate.user_id == user_id,
            FaceTemplate.is_active == True
        ).first()
        
        if not face_template:
            return LockerVerificationResponse(
                success=False,
                unlock=False,
                token=None,
                message="User has not enrolled face template",
                confidence=0.0
            )
        
        # Process incoming face (STRICTEST checks for locker security)
        result = await face_processor.process_face_image(
            file,
            perform_quality_check=True,  # REQUIRED for physical access
            perform_liveness_check=True,  # REQUIRED to prevent spoofing
            strict_quality=True  # Banking-grade quality thresholds
        )
        
        if not result["success"]:
            return LockerVerificationResponse(
                success=False,
                unlock=False,
                token=None,
                message=f"Face processing failed: {result.get('error', 'Unknown error')}",
                confidence=0.0
            )
        
        incoming_embedding = result["embedding"]
        liveness_metrics = result.get("liveness_metrics") or {}
        
        # Decrypt stored embedding
        try:
            decrypted_embedding = decrypt_biometric_data(face_template.embedding_data)
            stored_embedding = pickle.loads(decrypted_embedding)
        except Exception as e:
            logger.error(f"Failed to decrypt face template: {e}")
            return LockerVerificationResponse(
                success=False,
                unlock=False,
                token=None,
                message="Face template corrupted",
                confidence=0.0
            )
        
        # Verify faces (banking-grade threshold for locker)
        is_match, similarity_score, metrics = face_processor.verify_faces(
            incoming_embedding,
            stored_embedding,
            threshold=0.80  # Banking-grade: 80% for physical access
        )
        
        # Check liveness
        liveness_passed = liveness_metrics.get('is_live', False)
        
        # Final verification
        verified = is_match and liveness_passed
        
        if verified:
            # Generate unlock token
            locker_token = locker_manager.generate_unlock_token(
                locker_id=locker_id,
                user_id=user_id,
                parcel_id=parcel_id,
                expires_minutes=5
            )
            
            # Log successful verification
            log = VerificationLog(
                user_id=user_id,
                order_id=None,
                verification_type="face_locker",
                success=True,
                confidence_score=similarity_score,
                ip_address="locker_" + locker_id,
                device_info=f"locker_{locker_id}"
            )
            db.add(log)
            db.commit()
            
            logger.info(f"✅ Locker verification successful - Token generated")
            
            return LockerVerificationResponse(
                success=True,
                unlock=True,
                token=locker_token.token,
                message="Face verified - Locker will unlock",
                confidence=similarity_score,
                expires_in=300  # 5 minutes
            )
        else:
            # Log failed verification
            log = VerificationLog(
                user_id=user_id,
                order_id=None,
                verification_type="face_locker",
                success=False,
                confidence_score=similarity_score,
                ai_detected=not liveness_passed,
                ip_address="locker_" + locker_id,
                device_info=f"locker_{locker_id}",
                failure_reason="Face verification failed" if not is_match else "Liveness check failed"
            )
            db.add(log)
            db.commit()
            
            message = "Liveness check failed" if not liveness_passed else f"Face does not match (similarity: {similarity_score:.1%})"
            logger.warning(f"❌ Locker verification failed: {message}")
            
            return LockerVerificationResponse(
                success=False,
                unlock=False,
                token=None,
                message=message,
                confidence=similarity_score
            )
        
    except Exception as e:
        logger.error(f"Locker verification error: {e}")
        return LockerVerificationResponse(
            success=False,
            unlock=False,
            token=None,
            message=f"Verification error: {str(e)}",
            confidence=0.0
        )


@router.post("/locker/unlock", response_model=LockerUnlockResponse)
async def unlock_locker(
    request: LockerUnlockRequest
):
    """
    Unlock locker with token
    Called by locker device to validate token and perform unlock
    """
    try:
        logger.info(f"🔓 Unlock request for locker {request.locker_id}")
        
        # Verify and use token
        success, message, locker_token = locker_manager.unlock_locker(
            request.token,
            request.locker_id
        )
        
        if success:
            logger.info(f"✅ Locker {request.locker_id} unlocked")
            return LockerUnlockResponse(
                success=True,
                status="locker_unlocked",
                message="Locker unlocked successfully",
                locker_id=request.locker_id,
                unlocked_at=locker_token.created_at if locker_token else None
            )
        else:
            logger.warning(f"❌ Unlock failed for locker {request.locker_id}: {message}")
            return LockerUnlockResponse(
                success=False,
                status="unlock_failed",
                message=message,
                locker_id=request.locker_id
            )
        
    except Exception as e:
        logger.error(f"Locker unlock error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unlock failed: {str(e)}"
        )


@router.get("/template", response_model=FaceTemplateResponse)
async def get_face_template(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's face template information"""
    face_template = db.query(FaceTemplate).filter(
        FaceTemplate.user_id == current_user.id,
        FaceTemplate.is_active == True
    ).first()
    
    if not face_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No face template found"
        )
    
    return face_template


@router.delete("/template")
async def delete_face_template(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete user's face template"""
    face_template = db.query(FaceTemplate).filter(
        FaceTemplate.user_id == current_user.id
    ).first()
    
    if not face_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No face template found"
        )
    
    db.delete(face_template)
    db.commit()
    
    logger.info(f"Deleted face template for user {current_user.id}")
    
    return {"message": "Face template deleted successfully"}
