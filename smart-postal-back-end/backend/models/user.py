from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from .database import Base

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    COURIER = "courier"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.CUSTOMER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    orders = relationship("Order", back_populates="customer", foreign_keys="Order.customer_id")
    voice_templates = relationship("VoiceTemplate", back_populates="user", cascade="all, delete-orphan", lazy="select")
    fingerprint_templates = relationship("FingerprintTemplate", back_populates="user", cascade="all, delete-orphan", lazy="select")
    face_templates = relationship("FaceTemplate", back_populates="user", cascade="all, delete-orphan", lazy="select")
    verification_logs = relationship("VerificationLog", back_populates="user", lazy="select")