"""
Smart Locker Integration System
Handles locker verification, token generation, and unlock management
"""
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional
from dataclasses import dataclass
from jose import jwt, JWTError
from config.settings import get_settings
from loguru import logger

settings = get_settings()


@dataclass
class LockerToken:
    """Locker unlock token"""
    locker_id: str
    user_id: int
    parcel_id: Optional[str]
    created_at: datetime
    expires_at: datetime
    token: str


class LockerManager:
    """Manages smart locker verification and unlocking"""
    
    def __init__(self):
        self.active_tokens: Dict[str, LockerToken] = {}
        self.unlock_history: list = []
    
    def generate_unlock_token(
        self,
        locker_id: str,
        user_id: int,
        parcel_id: Optional[str] = None,
        expires_minutes: int = 5
    ) -> LockerToken:
        """
        Generate a time-limited unlock token for a locker
        
        Args:
            locker_id: Unique locker identifier
            user_id: User who verified successfully
            parcel_id: Optional parcel identifier
            expires_minutes: Token validity in minutes (default: 5)
        
        Returns:
            LockerToken with JWT
        """
        now = datetime.utcnow()
        expires_at = now + timedelta(minutes=expires_minutes)
        
        # Create JWT payload
        payload = {
            "locker_id": locker_id,
            "user_id": user_id,
            "parcel_id": parcel_id,
            "iat": now,
            "exp": expires_at,
            "type": "locker_unlock",
            "jti": secrets.token_urlsafe(16)  # Unique token ID
        }
        
        # Sign token
        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        locker_token = LockerToken(
            locker_id=locker_id,
            user_id=user_id,
            parcel_id=parcel_id,
            created_at=now,
            expires_at=expires_at,
            token=token
        )
        
        # Store active token
        self.active_tokens[token] = locker_token
        
        logger.info(f"🔑 Generated unlock token for locker {locker_id}, user {user_id}, expires in {expires_minutes}min")
        
        return locker_token
    
    def verify_unlock_token(self, token: str, locker_id: str) -> tuple[bool, str]:
        """
        Verify unlock token
        
        Args:
            token: JWT token
            locker_id: Locker ID to unlock
        
        Returns:
            (is_valid, message)
        """
        try:
            # Decode token
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            # Verify token type
            if payload.get("type") != "locker_unlock":
                return False, "Invalid token type"
            
            # Verify locker ID
            if payload.get("locker_id") != locker_id:
                return False, f"Token not valid for locker {locker_id}"
            
            # Check if token is in active tokens
            if token not in self.active_tokens:
                return False, "Token already used or invalid"
            
            # Token is valid
            locker_token = self.active_tokens[token]
            logger.info(f"✅ Valid unlock token for locker {locker_id}, user {locker_token.user_id}")
            
            return True, "Token valid"
            
        except JWTError as e:
            logger.error(f"Token verification error: {e}")
            return False, f"Token verification failed: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False, f"Verification error: {str(e)}"
    
    def unlock_locker(self, token: str, locker_id: str) -> tuple[bool, str, Optional[LockerToken]]:
        """
        Unlock locker with token (marks token as used)
        
        Args:
            token: JWT token
            locker_id: Locker ID to unlock
        
        Returns:
            (success, message, locker_token)
        """
        # Verify token first
        is_valid, message = self.verify_unlock_token(token, locker_id)
        
        if not is_valid:
            return False, message, None
        
        # Get locker token
        locker_token = self.active_tokens.get(token)
        if not locker_token:
            return False, "Token not found", None
        
        # Mark as used (remove from active tokens)
        del self.active_tokens[token]
        
        # Add to history
        self.unlock_history.append({
            "locker_id": locker_id,
            "user_id": locker_token.user_id,
            "parcel_id": locker_token.parcel_id,
            "unlocked_at": datetime.utcnow(),
            "token_created_at": locker_token.created_at
        })
        
        logger.info(f"🔓 Locker {locker_id} unlocked by user {locker_token.user_id}")
        
        return True, "Locker unlocked successfully", locker_token
    
    def cleanup_expired_tokens(self):
        """Remove expired tokens from active tokens"""
        now = datetime.utcnow()
        expired = [token for token, lt in self.active_tokens.items() if now > lt.expires_at]
        
        for token in expired:
            del self.active_tokens[token]
        
        if expired:
            logger.info(f"🧹 Cleaned up {len(expired)} expired locker tokens")
    
    def get_unlock_history(self, locker_id: Optional[str] = None, user_id: Optional[int] = None) -> list:
        """Get unlock history filtered by locker_id or user_id"""
        history = self.unlock_history
        
        if locker_id:
            history = [h for h in history if h["locker_id"] == locker_id]
        
        if user_id:
            history = [h for h in history if h["user_id"] == user_id]
        
        return history


# Global instance
locker_manager = LockerManager()
