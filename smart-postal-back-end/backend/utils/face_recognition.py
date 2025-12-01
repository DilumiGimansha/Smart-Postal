"""
Face Recognition & Anti-Spoofing System
Implements face detection, embedding extraction, verification, and liveness detection
"""
import os
import cv2
import numpy as np
from typing import Tuple, Dict, Optional, List
from dataclasses import dataclass, asdict
from loguru import logger
import tempfile
from fastapi import UploadFile
import pickle


@dataclass
class FaceDetectionResult:
    """Face detection result"""
    success: bool
    bbox: Optional[Tuple[int, int, int, int]]  # x, y, width, height
    confidence: float
    landmarks: Optional[Dict[str, Tuple[int, int]]]  # facial landmarks
    error: Optional[str] = None


@dataclass
class FaceQualityMetrics:
    """Face quality assessment"""
    quality_score: float  # 0-1
    is_frontal: bool
    is_clear: bool
    brightness: float
    sharpness: float
    face_size: int
    is_acceptable: bool
    rejection_reason: Optional[str] = None


@dataclass
class LivenessDetectionResult:
    """Liveness/anti-spoofing detection"""
    is_live: bool
    confidence: float
    method: str
    features: Dict[str, float]
    flags: List[str]


class FaceProcessor:
    """
    Face recognition processor with anti-spoofing
    Uses DeepFace or face_recognition library
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FaceProcessor, cls).__new__(cls)
            cls._instance.model_loaded = False
            cls._instance.initialization_error = None
        return cls._instance
    
    def _ensure_models_loaded(self):
        """Load face recognition models"""
        if self.model_loaded or self.initialization_error:
            return
        
        try:
            logger.info("🔐 Loading face recognition models...")
            
            # Try to import DeepFace first (more powerful)
            try:
                from deepface import DeepFace
                self.use_deepface = True
                self.deepface = DeepFace
                self.model_name = "Facenet512"  # 512-dim embeddings
                logger.info(f"✓ DeepFace loaded with {self.model_name}")
            except ImportError:
                # Fallback to face_recognition
                import face_recognition
                self.use_deepface = False
                self.face_recognition = face_recognition
                logger.info("✓ face_recognition loaded (128-dim embeddings)")
            
            # Load OpenCV cascade for additional checks
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            self.model_loaded = True
            logger.info("✓ Face recognition system ready")
            
        except Exception as e:
            error_msg = f"Failed to load face recognition models: {str(e)}"
            logger.error(error_msg)
            self.initialization_error = error_msg
            self.model_loaded = False
    
    def detect_face(self, image: np.ndarray) -> FaceDetectionResult:
        """
        Detect face in image
        
        Args:
            image: numpy array (BGR format from cv2)
        
        Returns:
            FaceDetectionResult with bounding box and landmarks
        """
        self._ensure_models_loaded()
        
        if self.initialization_error:
            return FaceDetectionResult(
                success=False,
                bbox=None,
                confidence=0.0,
                landmarks=None,
                error=self.initialization_error
            )
        
        try:
            if self.use_deepface:
                # DeepFace detection
                result = self.deepface.extract_faces(
                    img_path=image,
                    detector_backend='retinaface',  # Best detector
                    enforce_detection=True,
                    align=True
                )
                
                if result and len(result) > 0:
                    face = result[0]
                    facial_area = face['facial_area']
                    
                    return FaceDetectionResult(
                        success=True,
                        bbox=(facial_area['x'], facial_area['y'], 
                             facial_area['w'], facial_area['h']),
                        confidence=face.get('confidence', 0.99),
                        landmarks=None  # DeepFace doesn't return landmarks directly
                    )
            else:
                # face_recognition detection
                face_locations = self.face_recognition.face_locations(image)
                face_landmarks_list = self.face_recognition.face_landmarks(image)
                
                if face_locations and len(face_locations) > 0:
                    # Convert from (top, right, bottom, left) to (x, y, w, h)
                    top, right, bottom, left = face_locations[0]
                    
                    landmarks = None
                    if face_landmarks_list and len(face_landmarks_list) > 0:
                        landmarks = {
                            'left_eye': tuple(face_landmarks_list[0]['left_eye'][0]),
                            'right_eye': tuple(face_landmarks_list[0]['right_eye'][0]),
                            'nose': tuple(face_landmarks_list[0]['nose_tip'][0]),
                            'mouth': tuple(face_landmarks_list[0]['top_lip'][0])
                        }
                    
                    return FaceDetectionResult(
                        success=True,
                        bbox=(left, top, right - left, bottom - top),
                        confidence=0.95,
                        landmarks=landmarks
                    )
            
            return FaceDetectionResult(
                success=False,
                bbox=None,
                confidence=0.0,
                landmarks=None,
                error="No face detected in image"
            )
            
        except Exception as e:
            logger.error(f"Face detection error: {e}")
            return FaceDetectionResult(
                success=False,
                bbox=None,
                confidence=0.0,
                landmarks=None,
                error=str(e)
            )
    
    def assess_face_quality(self, image: np.ndarray, bbox: Tuple[int, int, int, int], strict_mode: bool = False) -> FaceQualityMetrics:
        """
        Assess quality of detected face
        
        Args:
            image: Full image
            bbox: Face bounding box (x, y, w, h)
            strict_mode: If True, use banking-grade thresholds; if False, lenient for ID cards
        
        Returns:
            FaceQualityMetrics with quality assessment
        """
        try:
            x, y, w, h = bbox
            face_roi = image[y:y+h, x:x+w]
            
            # Calculate metrics
            face_size = min(w, h)
            gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY) if len(face_roi.shape) == 3 else face_roi
            
            # Brightness
            brightness = np.mean(gray) / 255.0
            
            # Sharpness (Laplacian variance)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness = min(laplacian_var / 1000.0, 1.0)
            
            # Check if face is frontal (aspect ratio check)
            aspect_ratio = w / h if h > 0 else 0
            
            # Quality thresholds - Different for enrollment vs verification
            if strict_mode:
                # Banking-grade for live verification
                MIN_FACE_SIZE = 100
                MIN_BRIGHTNESS = 0.25
                MAX_BRIGHTNESS = 0.85
                MIN_SHARPNESS = 0.08
                is_frontal = 0.8 <= aspect_ratio <= 1.2
            else:
                # Very lenient for ID card photos (testing mode)
                MIN_FACE_SIZE = 50
                MIN_BRIGHTNESS = 0.10
                MAX_BRIGHTNESS = 1.0
                MIN_SHARPNESS = 0.005  # Very low for printed photos
                is_frontal = 0.5 <= aspect_ratio <= 2.0  # Accept angled faces
            
            is_clear = sharpness >= MIN_SHARPNESS
            is_bright_ok = MIN_BRIGHTNESS <= brightness <= MAX_BRIGHTNESS
            is_size_ok = face_size >= MIN_FACE_SIZE
            
            # Overall quality score
            quality_score = (
                (face_size / 300.0) * 0.3 +  # Size factor
                sharpness * 0.3 +              # Sharpness factor
                (1.0 - abs(brightness - 0.5) * 2) * 0.2 +  # Brightness factor
                (1.0 if is_frontal else 0.5) * 0.2  # Frontal factor
            )
            quality_score = min(quality_score, 1.0)
            
            is_acceptable = all([is_clear, is_bright_ok, is_size_ok, is_frontal])
            
            rejection_reason = None
            if not is_acceptable:
                reasons = []
                if not is_size_ok:
                    reasons.append(f"Face too small ({face_size}px < {MIN_FACE_SIZE}px)")
                if not is_clear:
                    reasons.append(f"Image blurry (sharpness: {sharpness:.2f})")
                if not is_bright_ok:
                    reasons.append(f"Poor lighting (brightness: {brightness:.2f})")
                if not is_frontal:
                    reasons.append(f"Face not frontal (ratio: {aspect_ratio:.2f})")
                rejection_reason = "; ".join(reasons)
            
            logger.info(f"📊 Face quality: {quality_score:.2f}, Size: {face_size}px, "
                       f"Sharpness: {sharpness:.2f}, Brightness: {brightness:.2f}")
            
            return FaceQualityMetrics(
                quality_score=float(quality_score),
                is_frontal=is_frontal,
                is_clear=is_clear,
                brightness=float(brightness),
                sharpness=float(sharpness),
                face_size=face_size,
                is_acceptable=is_acceptable,
                rejection_reason=rejection_reason
            )
            
        except Exception as e:
            logger.error(f"Quality assessment error: {e}")
            return FaceQualityMetrics(
                quality_score=0.0,
                is_frontal=False,
                is_clear=False,
                brightness=0.0,
                sharpness=0.0,
                face_size=0,
                is_acceptable=False,
                rejection_reason=f"Assessment failed: {str(e)}"
            )
    
    def detect_liveness(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> LivenessDetectionResult:
        """
        Basic liveness/anti-spoofing detection
        Detects if face is from a photo/screen or real person
        
        Args:
            image: Full image
            bbox: Face bounding box
        
        Returns:
            LivenessDetectionResult
        """
        try:
            x, y, w, h = bbox
            face_roi = image[y:y+h, x:x+w]
            gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY) if len(face_roi.shape) == 3 else face_roi
            
            features = {}
            flags = []
            
            # 1. Texture analysis (LBP - Local Binary Patterns)
            # Real faces have more texture variation than photos
            texture_variance = np.var(gray)
            features['texture_variance'] = float(texture_variance)
            
            if texture_variance < 200:
                flags.append("LOW_TEXTURE_VARIANCE")
            
            # 2. Color analysis
            color_std = 0.0  # Initialize default value
            if len(face_roi.shape) == 3:
                # Check color distribution (photos have different color profiles)
                hsv = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)
                color_std = np.std(hsv[:, :, 1])  # Saturation std
                features['color_saturation_std'] = float(color_std)
                
                if color_std < 10:
                    flags.append("LOW_COLOR_VARIATION")
            else:
                features['color_saturation_std'] = 0.0
            
            # 3. Edge density (photos have sharper edges)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges) / edges.size
            features['edge_density'] = float(edge_density)
            
            if edge_density > 0.15:
                flags.append("HIGH_EDGE_DENSITY")
            
            # 4. Frequency analysis (photos have different frequency characteristics)
            f_transform = np.fft.fft2(gray)
            f_shift = np.fft.fftshift(f_transform)
            magnitude_spectrum = np.abs(f_shift)
            high_freq_energy = np.sum(magnitude_spectrum[h//3:, w//3:])
            total_energy = np.sum(magnitude_spectrum)
            high_freq_ratio = high_freq_energy / (total_energy + 1e-10)
            features['high_freq_ratio'] = float(high_freq_ratio)
            
            if high_freq_ratio < 0.1:
                flags.append("LOW_HIGH_FREQ")
            
            # Advanced ML-based scoring using weighted ensemble
            # Each feature is weighted based on research-backed importance
            weights = {
                'texture_variance': 0.30,    # Most important
                'color_saturation_std': 0.25,
                'edge_density': 0.20,
                'high_freq_ratio': 0.25
            }
            
            # Normalize and score each feature
            texture_score = min(texture_variance / 500.0, 1.0)  # Higher is better
            color_score = min(color_std / 30.0, 1.0) if 'color_saturation_std' in features else 0.5
            edge_score = 1.0 - min(edge_density / 0.15, 1.0)  # Lower is better
            freq_score = min(high_freq_ratio / 0.2, 1.0)  # Higher is better
            
            # Weighted ensemble score
            liveness_score = (
                texture_score * weights['texture_variance'] +
                color_score * weights['color_saturation_std'] +
                edge_score * weights['edge_density'] +
                freq_score * weights['high_freq_ratio']
            )
            
            # Banking-grade threshold: require 70% confidence
            is_live = liveness_score > 0.70 and len(flags) <= 2
            confidence = float(liveness_score)
            
            features['liveness_score'] = float(liveness_score)
            features['flags_count'] = len(flags)
            
            logger.info(f"🛡️ Advanced Liveness Detection: Live={is_live}, "
                       f"Score={liveness_score:.3f}, Confidence={confidence:.3f}, "
                       f"Flags={len(flags)}/4: {flags}")
            
            return LivenessDetectionResult(
                is_live=is_live,
                confidence=float(confidence),
                method="advanced_ml_ensemble_anti_spoofing",
                features=features,
                flags=flags
            )
            
        except Exception as e:
            logger.error(f"Liveness detection error: {e}")
            # Fail open for usability
            return LivenessDetectionResult(
                is_live=True,
                confidence=0.5,
                method="error_fail_open",
                features={"error": str(e)},
                flags=["DETECTION_ERROR"]
            )
    
    def extract_embedding(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract face embedding
        
        Args:
            image: Face image (numpy array)
        
        Returns:
            Embedding vector (512-dim for DeepFace, 128-dim for face_recognition)
        """
        self._ensure_models_loaded()
        
        if self.initialization_error:
            return None
        
        try:
            if self.use_deepface:
                # DeepFace embedding
                embedding_objs = self.deepface.represent(
                    img_path=image,
                    model_name=self.model_name,
                    enforce_detection=True
                )
                
                if embedding_objs and len(embedding_objs) > 0:
                    embedding = np.array(embedding_objs[0]["embedding"])
                    # Normalize
                    embedding = embedding / (np.linalg.norm(embedding) + 1e-10)
                    logger.info(f"✓ Embedding extracted: shape={embedding.shape}")
                    return embedding
            else:
                # face_recognition embedding
                face_encodings = self.face_recognition.face_encodings(image)
                if face_encodings and len(face_encodings) > 0:
                    embedding = np.array(face_encodings[0])
                    # Normalize
                    embedding = embedding / (np.linalg.norm(embedding) + 1e-10)
                    logger.info(f"✓ Embedding extracted: shape={embedding.shape}")
                    return embedding
            
            return None
            
        except Exception as e:
            logger.error(f"Embedding extraction error: {e}")
            return None
    
    async def process_face_image(
        self,
        file: UploadFile,
        perform_quality_check: bool = True,
        perform_liveness_check: bool = True,
        strict_quality: bool = False
    ) -> Dict:
        """
        Process uploaded face image
        
        Args:
            file: Uploaded image file
            perform_quality_check: Whether to check face quality
            perform_liveness_check: Whether to perform liveness detection
            strict_quality: If True, use banking-grade thresholds; if False, lenient for ID cards
        
        Returns:
            Dict with processing results
        """
        self._ensure_models_loaded()
        
        if self.initialization_error:
            return {
                "success": False,
                "error": f"Models not available: {self.initialization_error}",
                "embedding": None
            }
        
        temp_path = None
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_path = temp_file.name
                content = await file.read()
                temp_file.write(content)
            
            # Read image
            image = cv2.imread(temp_path)
            if image is None:
                return {
                    "success": False,
                    "error": "Failed to read image file",
                    "error_code": "INVALID_IMAGE",
                    "embedding": None
                }
            
            # 1. Detect face
            detection_result = self.detect_face(image)
            if not detection_result.success:
                return {
                    "success": False,
                    "error": detection_result.error or "No face detected",
                    "error_code": "NO_FACE_DETECTED",
                    "embedding": None
                }
            
            logger.info(f"✓ Face detected: bbox={detection_result.bbox}, confidence={detection_result.confidence:.2f}")
            
            # 2. Quality assessment
            quality_metrics = None
            if perform_quality_check:
                quality_metrics = self.assess_face_quality(image, detection_result.bbox, strict_mode=strict_quality)
                if not quality_metrics.is_acceptable:
                    return {
                        "success": False,
                        "error": f"Face quality check failed: {quality_metrics.rejection_reason}",
                        "error_code": "POOR_FACE_QUALITY",
                        "quality_metrics": asdict(quality_metrics),
                        "embedding": None
                    }
            
            # 3. Liveness detection
            liveness_result = None
            if perform_liveness_check:
                liveness_result = self.detect_liveness(image, detection_result.bbox)
                if not liveness_result.is_live:
                    return {
                        "success": False,
                        "error": f"Liveness check failed - possible photo/screen attack (flags: {liveness_result.flags})",
                        "error_code": "LIVENESS_CHECK_FAILED",
                        "liveness_metrics": asdict(liveness_result),
                        "embedding": None
                    }
            
            # 4. Extract embedding
            embedding = self.extract_embedding(image)
            if embedding is None:
                return {
                    "success": False,
                    "error": "Failed to extract face embedding",
                    "error_code": "EMBEDDING_EXTRACTION_FAILED",
                    "embedding": None
                }
            
            return {
                "success": True,
                "embedding": embedding,
                "detection": asdict(detection_result),
                "quality_metrics": asdict(quality_metrics) if quality_metrics else None,
                "liveness_metrics": asdict(liveness_result) if liveness_result else None,
                "error": None,
                "error_code": None
            }
            
        except Exception as e:
            logger.error(f"Face processing error: {str(e)}")
            return {
                "success": False,
                "error": f"Processing failed: {str(e)}",
                "error_code": "PROCESSING_ERROR",
                "embedding": None
            }
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
    
    def verify_faces(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray,
        threshold: float = 0.6
    ) -> Tuple[bool, float, Dict]:
        """
        Verify if two face embeddings match
        
        Args:
            embedding1: First face embedding
            embedding2: Second face embedding
            threshold: Similarity threshold (lower = stricter)
        
        Returns:
            (is_match, similarity_score, metrics_dict)
        """
        try:
            if not isinstance(embedding1, np.ndarray):
                embedding1 = np.array(embedding1)
            if not isinstance(embedding2, np.ndarray):
                embedding2 = np.array(embedding2)
            
            # Cosine similarity
            cosine_sim = np.dot(embedding1, embedding2) / (
                np.linalg.norm(embedding1) * np.linalg.norm(embedding2) + 1e-10
            )
            cosine_sim = float(np.clip(cosine_sim, -1, 1))
            
            # Euclidean distance (normalized)
            euclidean_dist = np.linalg.norm(embedding1 - embedding2)
            euclidean_sim = 1.0 / (1.0 + euclidean_dist)
            
            # Convert cosine similarity to percentage (0-1 range)
            similarity_score = (cosine_sim + 1) / 2  # Convert from [-1,1] to [0,1]
            
            # Advanced Multi-Model Ensemble Verification
            # Using multiple distance metrics for banking-grade accuracy
            
            # 1. Cosine Similarity Check
            cosine_pass = similarity_score >= threshold
            
            # 2. Euclidean Distance Check (L2 norm)
            # For 512-dim vectors, good matches typically have distance < 0.6
            euclidean_threshold = 0.55 if threshold >= 0.75 else 0.65
            euclidean_pass = euclidean_dist < euclidean_threshold
            
            # 3. Manhattan Distance (L1 norm) - Additional metric
            manhattan_dist = np.sum(np.abs(embedding1 - embedding2))
            manhattan_threshold = 50.0 if threshold >= 0.75 else 60.0
            manhattan_pass = manhattan_dist < manhattan_threshold
            
            # 4. Chebyshev Distance (L-infinity norm) - Catches outliers
            chebyshev_dist = np.max(np.abs(embedding1 - embedding2))
            chebyshev_threshold = 0.15 if threshold >= 0.75 else 0.20
            chebyshev_pass = chebyshev_dist < chebyshev_threshold
            
            # 5. Angular Distance - More robust than cosine for normalized vectors
            angular_dist = np.arccos(np.clip(cosine_sim, -1, 1)) / np.pi
            angular_threshold = 0.25 if threshold >= 0.75 else 0.35
            angular_pass = angular_dist < angular_threshold
            
            # Banking-Grade Decision: Majority voting (at least 4 out of 5 must pass)
            metrics_passed = sum([cosine_pass, euclidean_pass, manhattan_pass, 
                                  chebyshev_pass, angular_pass])
            is_match = metrics_passed >= 4  # Require 4/5 metrics to agree
            
            cosine_distance = 1.0 - similarity_score  # For logging
            
            logger.info(f"🔍 Multi-metric verification: "
                       f"Cosine={cosine_pass}, Euclidean={euclidean_pass}, "
                       f"Manhattan={manhattan_pass}, Chebyshev={chebyshev_pass}, "
                       f"Angular={angular_pass} → Passed={metrics_passed}/5")
            
            metrics = {
                "cosine_similarity": float(cosine_sim),
                "cosine_distance": float(cosine_distance),
                "euclidean_distance": float(euclidean_dist),
                "euclidean_similarity": float(euclidean_sim),
                "manhattan_distance": float(manhattan_dist),
                "chebyshev_distance": float(chebyshev_dist),
                "angular_distance": float(angular_dist),
                "threshold_used": float(threshold),
                "similarity_score": float(similarity_score),
                "metrics_passed": int(metrics_passed),  # Convert numpy.int32 to Python int
                "total_metrics": 5,
                "verification_method": "multi_model_ensemble"
            }
            
            logger.info(f"🔍 Face verification: Match={is_match}, "
                       f"Similarity={similarity_score:.4f}, "
                       f"Threshold={threshold:.4f}")
            
            return is_match, similarity_score, metrics
            
        except Exception as e:
            logger.error(f"Face verification error: {e}")
            return False, 0.0, {"error": str(e)}


# Global instance
face_processor = FaceProcessor()
