from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    CUSTOMER = "customer"
    COURIER = "courier"
    ADMIN = "admin"

# User Registration
class UserCreate(BaseModel):
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8, max_length=100)
    role: UserRole = UserRole.CUSTOMER
    
    @validator('phone')
    def validate_phone(cls, v):
        # Remove spaces and dashes
        phone = v.replace(" ", "").replace("-", "")
        if not phone.isdigit():
            raise ValueError('Phone must contain only digits')
        return phone
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

# User Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# User Response
class UserResponse(BaseModel):
    id: int
    email: str
    phone: str
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Token Response
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None

# User Update
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v:
            phone = v.replace(" ", "").replace("-", "")
            if not phone.isdigit():
                raise ValueError('Phone must contain only digits')
            return phone
        return v

# Password Change
class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v