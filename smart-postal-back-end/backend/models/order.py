from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    BIOMETRIC_ENROLLED = "biometric_enrolled"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    FAILED = "failed"

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    courier_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Delivery Information
    delivery_address = Column(Text, nullable=False)
    delivery_city = Column(String(100), nullable=False)
    delivery_postal_code = Column(String(20), nullable=False)
    delivery_instructions = Column(Text, nullable=True)
    
    # Order Details
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    total_amount = Column(Float, nullable=False)
    
    # Biometric Verification Status
    voice_enrolled = Column(Boolean, default=False)
    fingerprint_enrolled = Column(Boolean, default=False)
    verification_required = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    customer = relationship("User", foreign_keys=[customer_id], back_populates="orders")
    courier = relationship("User", foreign_keys=[courier_id])
    deliveries = relationship("Delivery", back_populates="order", cascade="all, delete-orphan")