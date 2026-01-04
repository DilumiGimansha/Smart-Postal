from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import secrets
from models.database import get_db
from models.user import User, UserRole
from models.order import Order, OrderStatus
from api.schemas import (
    OrderCreate, OrderResponse, OrderUpdate,
    CourierAssignment, OrderFilter
)
from api.middleware.auth import (
    get_current_user, get_current_customer,
    get_current_courier, get_current_admin
)

router = APIRouter(prefix="/api/orders", tags=["Orders"])

def generate_order_number() -> str:
    """Generate unique order number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_part = secrets.token_hex(4).upper()
    return f"ORD-{timestamp}-{random_part}"

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_customer)
):
    """Create a new order (Customer only)"""
    
    # Generate unique order number
    order_number = generate_order_number()
    
    # Create order
    new_order = Order(
        order_number=order_number,
        customer_id=current_user.id,
        delivery_address=order_data.delivery_address,
        delivery_city=order_data.delivery_city,
        delivery_postal_code=order_data.delivery_postal_code,
        delivery_instructions=order_data.delivery_instructions,
        total_amount=order_data.total_amount,
        verification_required=order_data.verification_required,
        status=OrderStatus.PENDING
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    return new_order

@router.get("/", response_model=List[OrderResponse])
async def list_orders(
    skip: int = 0,
    limit: int = 100,
    status: OrderStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List orders based on user role"""
    
    query = db.query(Order)
    
    # Filter based on user role
    if current_user.role == UserRole.CUSTOMER:
        query = query.filter(Order.customer_id == current_user.id)
    elif current_user.role == UserRole.COURIER:
        query = query.filter(Order.courier_id == current_user.id)
    # Admin can see all orders
    
    # Apply status filter
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get order by ID"""
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check authorization
    if current_user.role == UserRole.CUSTOMER and order.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order"
        )
    elif current_user.role == UserRole.COURIER and order.courier_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order"
        )
    
    return order

@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update order"""
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Authorization checks
    if current_user.role == UserRole.CUSTOMER:
        # Customers can only update their own orders and only certain fields
        if order.customer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this order"
            )
        # Customers can only update delivery instructions
        if order_update.delivery_instructions:
            order.delivery_instructions = order_update.delivery_instructions
    
    elif current_user.role == UserRole.COURIER:
        # Couriers can update status of assigned orders
        if order.courier_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this order"
            )
        if order_update.status:
            order.status = order_update.status
            if order_update.status == OrderStatus.DELIVERED:
                order.delivered_at = datetime.now()
    
    elif current_user.role == UserRole.ADMIN:
        # Admin can update everything
        if order_update.status:
            order.status = order_update.status
        if order_update.courier_id:
            order.courier_id = order_update.courier_id
        if order_update.delivery_instructions:
            order.delivery_instructions = order_update.delivery_instructions
    
    db.commit()
    db.refresh(order)
    return order

@router.post("/assign-courier", response_model=OrderResponse)
async def assign_courier(
    assignment: CourierAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Assign courier to order (Admin only)"""
    
    order = db.query(Order).filter(Order.id == assignment.order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify courier exists and has correct role
    courier = db.query(User).filter(
        User.id == assignment.courier_id,
        User.role == UserRole.COURIER
    ).first()
    if not courier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found"
        )
    
    order.courier_id = assignment.courier_id
    order.status = OrderStatus.IN_TRANSIT
    
    db.commit()
    db.refresh(order)
    return order

@router.get("/{order_id}/biometric-status")
async def get_biometric_status(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get biometric enrollment status for an order"""
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Authorization check
    if current_user.role == UserRole.CUSTOMER and order.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order"
        )
    
    return {
        "order_id": order.id,
        "order_number": order.order_number,
        "voice_enrolled": order.voice_enrolled,
        "fingerprint_enrolled": order.fingerprint_enrolled,
        "verification_required": order.verification_required,
        "biometric_enrollment_complete": order.voice_enrolled or order.fingerprint_enrolled
    }

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel an order"""
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Only customer or admin can cancel
    if current_user.role == UserRole.CUSTOMER and order.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this order"
        )
    
    # Can't cancel if already delivered or in delivery
    if order.status in [OrderStatus.DELIVERED, OrderStatus.OUT_FOR_DELIVERY]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel order in current status"
        )
    
    order.status = OrderStatus.CANCELLED
    db.commit()
    
    return None