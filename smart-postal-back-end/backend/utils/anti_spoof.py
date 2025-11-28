"""
Enhanced Anti-Spoofing Utilities
Implements challenge-response, LFCC features, and risk-based decision engine
"""
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import numpy as np
from dataclasses import dataclass
from enum import Enum
import librosa
from scipy.fftpack import dct
from loguru import logger


class DecisionType(str, Enum):
    """Decision types for verification attempts"""
    ACCEPT = "accept"
    CHALLENGE = "challenge"
    DENY = "deny"
    REQUIRE_2FA = "require_2fa"
    FLAG_FOR_REVIEW = "flag_for_review"


class RiskLevel(str, Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Challenge:
    """Challenge for active liveness verification"""
    challenge_id: str
    user_id: int
    phrase: str
    expected_digits: str  # The digits that should be spoken
    created_at: datetime
    expires_at: datetime
    is_used: bool = False


@dataclass
class DecisionResult:
    """Enhanced decision result with risk assessment"""
    decision: DecisionType
    risk_level: RiskLevel
    risk_score: float
    reason: str
    challenge: Optional[Challenge] = None
    require_2fa: bool = False
    should_flag: bool = False


class ChallengeManager:
    """Manages challenge-response for active liveness"""
    
    def __init__(self):
        self.active_challenges: Dict[str, Challenge] = {}
        self.phrases = [
            "Please say the numbers: {digits}",
            "Repeat after me: {digits}",
            "Verify with digits: {digits}",
            "Say these numbers: {digits}",
            "Confirm by saying: {digits}"
        ]
    
    def generate_challenge(self, user_id: int) -> Challenge:
        """Generate a random challenge phrase"""
        # Generate random 4-digit code
        digits = ''.join(random.choices(string.digits, k=4))
        
        # Select random phrase template
        phrase_template = random.choice(self.phrases)
        phrase = phrase_template.format(digits=digits)
        
        # Create challenge with 5-minute expiry
        challenge_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        challenge = Challenge(
            challenge_id=challenge_id,
            user_id=user_id,
            phrase=phrase,
            expected_digits=digits,  # Store the digits for verification
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(minutes=5),
            is_used=False
        )
        
        # Store challenge
        self.active_challenges[challenge_id] = challenge
        logger.info(f"Generated challenge {challenge_id} for user {user_id} with digits {digits}")
        
        return challenge
    
    def get_challenge(self, challenge_id: str) -> Optional[Challenge]:
        """Retrieve a challenge by ID"""
        challenge = self.active_challenges.get(challenge_id)
        
        if challenge is None:
            return None
        
        # Check expiry
        if datetime.now() > challenge.expires_at:
            logger.warning(f"Challenge {challenge_id} expired")
            del self.active_challenges[challenge_id]
            return None
        
        # Check if already used
        if challenge.is_used:
            logger.warning(f"Challenge {challenge_id} already used")
            return None
        
        return challenge
    
    def mark_used(self, challenge_id: str):
        """Mark challenge as used"""
        if challenge_id in self.active_challenges:
            self.active_challenges[challenge_id].is_used = True
            logger.info(f"Challenge {challenge_id} marked as used")
    
    def cleanup_expired(self):
        """Remove expired challenges"""
        now = datetime.now()
        expired = [cid for cid, c in self.active_challenges.items() if now > c.expires_at]
        for cid in expired:
            del self.active_challenges[cid]
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired challenges")


class LFCCExtractor:
    """
    Log Filterbank Cepstral Coefficients (LFCC) Extractor
    More effective than MFCC for anti-spoofing detection
    """
    
    def __init__(self, n_filters=40, n_lfcc=20, sr=16000):
        self.n_filters = n_filters
        self.n_lfcc = n_lfcc
        self.sr = sr
    
    def extract(self, audio: np.ndarray) -> np.ndarray:
        """
        Extract LFCC features from audio
        
        Args:
            audio: Audio signal (1D numpy array)
        
        Returns:
            LFCC features (n_lfcc x time_frames)
        """
        try:
            # Compute STFT
            stft = librosa.stft(audio, n_fft=512, hop_length=160, win_length=400)
            magnitude = np.abs(stft)
            
            # Create linear filterbank
            linear_filterbank = self._create_linear_filterbank()
            
            # Apply filterbank
            filterbank_energies = np.dot(linear_filterbank, magnitude)
            
            # Log compression
            log_filterbank = np.log(filterbank_energies + 1e-10)
            
            # Apply DCT to get cepstral coefficients
            lfcc = dct(log_filterbank, axis=0, norm='ortho')[:self.n_lfcc, :]
            
            return lfcc
            
        except Exception as e:
            logger.error(f"LFCC extraction error: {e}")
            # Return zeros if extraction fails
            return np.zeros((self.n_lfcc, 100))
    
    def _create_linear_filterbank(self) -> np.ndarray:
        """Create linear filterbank (not mel-scale)"""
        n_fft = 512
        fft_freqs = librosa.fft_frequencies(sr=self.sr, n_fft=n_fft)
        
        # Linear spacing from 0 to sr/2
        filter_freqs = np.linspace(0, self.sr / 2, self.n_filters + 2)
        
        # Create triangular filters
        filterbank = np.zeros((self.n_filters, n_fft // 2 + 1))
        
        for i in range(self.n_filters):
            left = filter_freqs[i]
            center = filter_freqs[i + 1]
            right = filter_freqs[i + 2]
            
            for j, freq in enumerate(fft_freqs):
                if left <= freq <= center:
                    filterbank[i, j] = (freq - left) / (center - left)
                elif center <= freq <= right:
                    filterbank[i, j] = (right - freq) / (right - center)
        
        return filterbank
    
    def compute_statistics(self, lfcc: np.ndarray) -> Dict[str, float]:
        """Compute statistics from LFCC for spoofing detection"""
        try:
            stats = {
                'lfcc_mean': float(np.mean(lfcc)),
                'lfcc_std': float(np.std(lfcc)),
                'lfcc_max': float(np.max(lfcc)),
                'lfcc_min': float(np.min(lfcc)),
                'lfcc_range': float(np.max(lfcc) - np.min(lfcc)),
                'lfcc_kurtosis': float(np.mean([self._kurtosis(lfcc[i, :]) for i in range(lfcc.shape[0])])),
                'lfcc_skewness': float(np.mean([self._skewness(lfcc[i, :]) for i in range(lfcc.shape[0])]))
            }
            
            # Delta features (temporal changes)
            delta_lfcc = np.diff(lfcc, axis=1)
            stats['lfcc_delta_mean'] = float(np.mean(np.abs(delta_lfcc)))
            stats['lfcc_delta_std'] = float(np.std(delta_lfcc))
            
            return stats
        except Exception as e:
            logger.error(f"LFCC statistics error: {e}")
            return {}
    
    @staticmethod
    def _kurtosis(data: np.ndarray) -> float:
        """Compute kurtosis"""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0
        return np.mean(((data - mean) / std) ** 4) - 3.0
    
    @staticmethod
    def _skewness(data: np.ndarray) -> float:
        """Compute skewness"""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0
        return np.mean(((data - mean) / std) ** 3)


class EnhancedDecisionEngine:
    """
    Risk-based decision engine with multi-tier thresholds
    Implements the blueprint's decision logic
    """
    
    def __init__(self, challenge_manager: ChallengeManager):
        self.challenge_manager = challenge_manager
        
        # Risk thresholds (configurable)
        self.thresholds = {
            'ai_critical': 0.85,      # Critical AI probability - instant deny
            'ai_high': 0.60,          # High AI probability - challenge
            'ai_medium': 0.35,        # Medium AI probability - scrutinize
            'asv_min': 0.70,          # Minimum ASV/ensemble score
            'combined_risk_high': 0.70,  # Combined risk - deny
            'combined_risk_medium': 0.45  # Combined risk - challenge
        }
    
    def evaluate(
        self,
        user_id: int,
        asv_score: float,
        ai_probability: float,
        ai_flags: list,
        metadata: Optional[Dict] = None,
        is_enrollment: bool = False
    ) -> DecisionResult:
        """
        Evaluate verification attempt and make decision
        
        Args:
            user_id: User ID
            asv_score: Speaker verification score (ensemble)
            ai_probability: AI/synthetic probability (0-1)
            ai_flags: List of AI detection flags
            metadata: Device/network metadata
            is_enrollment: Whether this is enrollment or verification
        
        Returns:
            DecisionResult with decision type and details
        """
        
        # Calculate risk components
        ai_risk = self._calculate_ai_risk(ai_probability, ai_flags)
        asv_risk = self._calculate_asv_risk(asv_score)
        metadata_risk = self._calculate_metadata_risk(metadata) if metadata else 0.0
        
        # Combined risk score
        risk_score = (
            ai_risk * 0.60 +        # AI detection most important
            asv_risk * 0.30 +       # Voice matching secondary
            metadata_risk * 0.10    # Metadata least weighted
        )
        
        # Determine risk level
        risk_level = self._classify_risk_level(risk_score)
        
        logger.info(f"Risk assessment - AI: {ai_risk:.3f}, ASV: {asv_risk:.3f}, "
                   f"Metadata: {metadata_risk:.3f}, Combined: {risk_score:.3f}, Level: {risk_level}")
        
        # Decision logic based on blueprint
        decision = self._make_decision(
            user_id=user_id,
            risk_score=risk_score,
            risk_level=risk_level,
            ai_probability=ai_probability,
            asv_score=asv_score,
            ai_flags=ai_flags,
            is_enrollment=is_enrollment
        )
        
        return decision
    
    def _calculate_ai_risk(self, ai_probability: float, ai_flags: list) -> float:
        """Calculate risk from AI detection"""
        # Base risk from probability
        risk = ai_probability
        
        # Increase risk if multiple flags
        flag_bonus = min(len(ai_flags) * 0.05, 0.20)  # Max +0.20
        risk = min(risk + flag_bonus, 1.0)
        
        # Specific high-risk flags
        high_risk_flags = ['ECHO_DETECTED', 'BANDLIMITED_SIGNAL', 'LOW_HIGH_FREQ_CONTENT']
        if any(flag in ai_flags for flag in high_risk_flags):
            risk = min(risk + 0.10, 1.0)
        
        return risk
    
    def _calculate_asv_risk(self, asv_score: float) -> float:
        """Calculate risk from speaker verification score"""
        # Inverse of ASV score (lower score = higher risk)
        if asv_score >= 0.80:
            return 0.0  # No risk
        elif asv_score >= 0.70:
            return 0.2  # Low risk
        elif asv_score >= 0.60:
            return 0.5  # Medium risk
        else:
            return 0.9  # High risk
    
    def _calculate_metadata_risk(self, metadata: Dict) -> float:
        """Calculate risk from device/network metadata"""
        risk = 0.0
        
        # Missing metadata is slightly suspicious
        if not metadata:
            return 0.1
        
        # Check for suspicious patterns
        if metadata.get('device_rooted', False):
            risk += 0.3
        
        if metadata.get('emulator_detected', False):
            risk += 0.4
        
        if metadata.get('vpn_detected', False):
            risk += 0.1
        
        # Unusual network changes
        if metadata.get('network_changed', False):
            risk += 0.05
        
        # Fast retry attempts
        retry_count = metadata.get('retry_count', 0)
        if retry_count > 2:
            risk += min(retry_count * 0.1, 0.3)
        
        return min(risk, 1.0)
    
    def _classify_risk_level(self, risk_score: float) -> RiskLevel:
        """Classify risk level"""
        if risk_score >= 0.80:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.60:
            return RiskLevel.HIGH
        elif risk_score >= 0.35:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _make_decision(
        self,
        user_id: int,
        risk_score: float,
        risk_level: RiskLevel,
        ai_probability: float,
        asv_score: float,
        ai_flags: list,
        is_enrollment: bool
    ) -> DecisionResult:
        """Make final decision based on risk assessment"""
        
        # CRITICAL RISK - Instant deny + 2FA
        if risk_level == RiskLevel.CRITICAL or ai_probability >= self.thresholds['ai_critical']:
            return DecisionResult(
                decision=DecisionType.REQUIRE_2FA,
                risk_level=risk_level,
                risk_score=risk_score,
                reason=f"Critical security risk detected (AI: {ai_probability:.1%}, Flags: {len(ai_flags)})",
                require_2fa=True,
                should_flag=True
            )
        
        # HIGH RISK - Challenge required
        if risk_level == RiskLevel.HIGH or (
            ai_probability >= self.thresholds['ai_high'] or
            asv_score < self.thresholds['asv_min']
        ):
            challenge = self.challenge_manager.generate_challenge(user_id)
            return DecisionResult(
                decision=DecisionType.CHALLENGE,
                risk_level=risk_level,
                risk_score=risk_score,
                reason=f"High risk - Active liveness required (AI: {ai_probability:.1%}, ASV: {asv_score:.2f})",
                challenge=challenge
            )
        
        # MEDIUM RISK - Flag for review but may accept
        if risk_level == RiskLevel.MEDIUM:
            # For enrollment, be more strict
            if is_enrollment and ai_probability >= self.thresholds['ai_medium']:
                challenge = self.challenge_manager.generate_challenge(user_id)
                return DecisionResult(
                    decision=DecisionType.CHALLENGE,
                    risk_level=risk_level,
                    risk_score=risk_score,
                    reason=f"Medium risk during enrollment - Challenge required",
                    challenge=challenge
                )
            
            # For verification, accept but flag
            return DecisionResult(
                decision=DecisionType.ACCEPT,
                risk_level=risk_level,
                risk_score=risk_score,
                reason=f"Medium risk - Accepted with monitoring",
                should_flag=True
            )
        
        # LOW RISK - Accept
        return DecisionResult(
            decision=DecisionType.ACCEPT,
            risk_level=risk_level,
            risk_score=risk_score,
            reason=f"Low risk - Verification successful"
        )


# Global instances
challenge_manager = ChallengeManager()
lfcc_extractor = LFCCExtractor()
decision_engine = EnhancedDecisionEngine(challenge_manager)
