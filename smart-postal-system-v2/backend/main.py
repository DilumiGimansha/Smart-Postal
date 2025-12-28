"""
Smart Postal Service - FastAPI Backend
Production Ready Application
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd
import io
import requests
from time import sleep
import json

# Import ML models from the existing module
import sys
sys.path.append('.')
from postal_ml_webapp import (
    PriorityClassificationModel,
    DynamicRouteOptimizer,
    DynamicRerouter,
    RelocationTracker
)

# Database Configuration
DATABASE_URL = "mysql+pymysql://root:@localhost/postal_service"
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class DeliveryPoint(Base):
    __tablename__ = "delivery_points"
    
    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    city = Column(String(100))
    postal_code = Column(String(20))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    parcels = Column(Integer, default=1)
    urgent = Column(Integer, default=0)
    time_window = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class MailRecord(Base):
    __tablename__ = "mail_records"
    
    id = Column(Integer, primary_key=True, index=True)
    mail_type = Column(String(100), nullable=False)
    sender_type = Column(String(100), nullable=False)
    recipient_type = Column(String(100), nullable=False)
    time_received = Column(String(10), nullable=False)
    day_of_week = Column(String(20), nullable=False)
    priority = Column(String(20))
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.now)

class RouteOptimization(Base):
    __tablename__ = "route_optimizations"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_name = Column(String(255))
    method = Column(String(50))
    route_sequence = Column(Text)
    total_distance_km = Column(Float)
    total_time_hours = Column(Float)
    urgent_on_time = Column(Integer)
    traffic_level = Column(String(50))
    weather_condition = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)

class RelocationRecord(Base):
    __tablename__ = "relocations"
    
    id = Column(Integer, primary_key=True, index=True)
    relocation_id = Column(String(50), unique=True)
    location_id = Column(Integer, nullable=False)
    old_latitude = Column(Float)
    old_longitude = Column(Float)
    new_latitude = Column(Float)
    new_longitude = Column(Float)
    distance_change_km = Column(Float)
    reason = Column(String(255))
    status = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class DeliveryPointCreate(BaseModel):
    location_name: str
    address: str
    city: Optional[str] = None
    postal_code: Optional[str] = None
    parcels: int = 1
    urgent: int = 0
    time_window: Optional[float] = None

class DeliveryPointResponse(BaseModel):
    id: int
    location_name: str
    address: str
    city: Optional[str]
    postal_code: Optional[str]
    latitude: float
    longitude: float
    parcels: int
    urgent: int
    time_window: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True

class MailClassificationRequest(BaseModel):
    mail_type: str
    sender_type: str
    recipient_type: str
    time_received: str
    day_of_week: str

class RouteOptimizationRequest(BaseModel):
    point_ids: List[int]
    traffic_level: str = "moderate"
    weather_condition: str = "clear"
    methods: List[str] = ["nearest_neighbor", "urgent_priority", "2opt", "q_learning"]

class RelocationRequest(BaseModel):
    location_id: int
    new_address: str
    reason: str = "customer_request"

# Initialize FastAPI
app = FastAPI(title="Smart Postal Service API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize ML Models
priority_model = PriorityClassificationModel()
route_optimizer = DynamicRouteOptimizer()
rerouter = DynamicRerouter(route_optimizer)

# Geocoding Service
class GeocodingService:
    @staticmethod
    def geocode_address(address: str, city: str = None) -> Dict[str, float]:
        """
        Geocode address using Nominatim (OpenStreetMap)
        Returns latitude and longitude
        """
        try:
            full_address = f"{address}, {city}, Sri Lanka" if city else f"{address}, Sri Lanka"
            
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': full_address,
                'format': 'json',
                'limit': 1
            }
            headers = {
                'User-Agent': 'PostalServiceApp/1.0'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                return {
                    'latitude': float(data[0]['lat']),
                    'longitude': float(data[0]['lon'])
                }
            else:
                # Default to Colombo, Sri Lanka if address not found
                return {
                    'latitude': 6.9271,
                    'longitude': 79.8612
                }
        except Exception as e:
            print(f"Geocoding error: {str(e)}")
            # Return default Colombo coordinates
            return {
                'latitude': 6.9271,
                'longitude': 79.8612
            }

geocoding_service = GeocodingService()

# API Endpoints

@app.get("/")
def root():
    return {
        "message": "Smart Postal Service API",
        "version": "1.0.0",
        "status": "running"
    }

# Delivery Points Management

@app.post("/api/delivery-points/", response_model=DeliveryPointResponse)
def create_delivery_point(point: DeliveryPointCreate, db: Session = Depends(get_db)):
    """Create a single delivery point with automatic geocoding"""
    
    # Geocode the address
    coords = geocoding_service.geocode_address(point.address, point.city)
    
    db_point = DeliveryPoint(
        location_name=point.location_name,
        address=point.address,
        city=point.city,
        postal_code=point.postal_code,
        latitude=coords['latitude'],
        longitude=coords['longitude'],
        parcels=point.parcels,
        urgent=point.urgent,
        time_window=point.time_window
    )
    
    db.add(db_point)
    db.commit()
    db.refresh(db_point)
    
    return db_point

@app.post("/api/delivery-points/bulk-upload/")
async def bulk_upload_delivery_points(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Bulk upload delivery points from CSV
    Expected columns: location_name, address, city, postal_code, parcels, urgent, time_window
    """
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate required columns
        required_columns = ['location_name', 'address']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # Fill optional columns with defaults
        if 'city' not in df.columns:
            df['city'] = None
        if 'postal_code' not in df.columns:
            df['postal_code'] = None
        if 'parcels' not in df.columns:
            df['parcels'] = 1
        if 'urgent' not in df.columns:
            df['urgent'] = 0
        if 'time_window' not in df.columns:
            df['time_window'] = None
        
        created_points = []
        errors = []
        
        for idx, row in df.iterrows():
            try:
                # Geocode address
                coords = geocoding_service.geocode_address(
                    str(row['address']),
                    str(row['city']) if pd.notna(row['city']) else None
                )
                
                db_point = DeliveryPoint(
                    location_name=str(row['location_name']),
                    address=str(row['address']),
                    city=str(row['city']) if pd.notna(row['city']) else None,
                    postal_code=str(row['postal_code']) if pd.notna(row['postal_code']) else None,
                    latitude=coords['latitude'],
                    longitude=coords['longitude'],
                    parcels=int(row['parcels']),
                    urgent=int(row['urgent']),
                    time_window=float(row['time_window']) if pd.notna(row['time_window']) else None
                )
                
                db.add(db_point)
                created_points.append(row['location_name'])
                
                # Rate limiting for geocoding API
                sleep(1)
                
            except Exception as e:
                errors.append(f"Row {idx + 2}: {str(e)}")
        
        db.commit()
        
        return {
            "status": "success",
            "total_rows": len(df),
            "created": len(created_points),
            "errors": len(errors),
            "error_details": errors[:10] if errors else []
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")

@app.get("/api/delivery-points/", response_model=List[DeliveryPointResponse])
def get_delivery_points(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all delivery points with pagination"""
    points = db.query(DeliveryPoint).offset(skip).limit(limit).all()
    return points

@app.get("/api/delivery-points/{point_id}", response_model=DeliveryPointResponse)
def get_delivery_point(point_id: int, db: Session = Depends(get_db)):
    """Get a specific delivery point"""
    point = db.query(DeliveryPoint).filter(DeliveryPoint.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="Delivery point not found")
    return point

@app.delete("/api/delivery-points/{point_id}")
def delete_delivery_point(point_id: int, db: Session = Depends(get_db)):
    """Delete a delivery point"""
    point = db.query(DeliveryPoint).filter(DeliveryPoint.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="Delivery point not found")
    
    db.delete(point)
    db.commit()
    return {"status": "success", "message": "Delivery point deleted"}

# Priority Classification

@app.post("/api/classify-priority/")
def classify_mail_priority(request: MailClassificationRequest, db: Session = Depends(get_db)):
    """Classify mail priority using ML model"""
    
    try:
        # Check if model is trained, if not, train with default data
        if not priority_model.is_trained:
            # Train with minimal sample data
            sample_data = [
                {
                    'mail_type': 'Court Notice',
                    'sender_type': 'Court',
                    'recipient_type': 'Individual',
                    'time_received': '08:00',
                    'day_of_week': 'Monday'
                },
                {
                    'mail_type': 'Standard Letter',
                    'sender_type': 'Individual',
                    'recipient_type': 'Individual',
                    'time_received': '14:30',
                    'day_of_week': 'Wednesday'
                }
            ]
            sample_labels = ['urgent', 'regular']
            priority_model.train(sample_data, sample_labels)
        
        result = priority_model.predict(request.dict())
        
        # Save to database
        mail_record = MailRecord(
            mail_type=request.mail_type,
            sender_type=request.sender_type,
            recipient_type=request.recipient_type,
            time_received=request.time_received,
            day_of_week=request.day_of_week,
            priority=result['priority'],
            confidence=result['confidence']
        )
        db.add(mail_record)
        db.commit()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")

# Route Optimization

@app.post("/api/optimize-route/")
def optimize_route(request: RouteOptimizationRequest, db: Session = Depends(get_db)):
    """Optimize delivery route using multiple algorithms"""
    
    try:
        # Fetch delivery points
        points = db.query(DeliveryPoint).filter(DeliveryPoint.id.in_(request.point_ids)).all()
        
        if len(points) == 0:
            raise HTTPException(status_code=400, detail="No valid delivery points found")
        
        # Add depot as first point (default to Colombo Central Post Office)
        depot = {
            'id': 0,
            'location_name': 'Central Depot',
            'latitude': 6.9344,
            'longitude': 79.8428,
            'parcels': 0,
            'urgent': 0,
            'time_window': None
        }
        
        delivery_points = [depot] + [
            {
                'id': p.id,
                'location_name': p.location_name,
                'latitude': p.latitude,
                'longitude': p.longitude,
                'parcels': p.parcels,
                'urgent': p.urgent,
                'time_window': p.time_window
            }
            for p in points
        ]
        
        # Traffic and weather factors
        traffic_factors = {
            'light': 1.0,
            'moderate': 1.3,
            'heavy': 1.8
        }
        
        weather_factors = {
            'clear': 1.0,
            'rain': 1.4,
            'storm': 2.0
        }
        
        scenario = {
            'delivery_points': delivery_points,
            'traffic_factor': traffic_factors.get(request.traffic_level, 1.3),
            'weather_factor': weather_factors.get(request.weather_condition, 1.0),
            'traffic_level': request.traffic_level,
            'weather_condition': request.weather_condition
        }
        
        result = route_optimizer.optimize_route(scenario, request.methods)
        
        # Save best route to database
        best_result = result['best_result']
        route_record = RouteOptimization(
            scenario_name=f"Route_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            method=result['best_method'],
            route_sequence=json.dumps(best_result['route']),
            total_distance_km=best_result['total_distance_km'],
            total_time_hours=best_result['total_time_hours'],
            urgent_on_time=best_result['urgent_on_time'],
            traffic_level=request.traffic_level,
            weather_condition=request.weather_condition
        )
        db.add(route_record)
        db.commit()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")

# Dynamic Rerouting

@app.post("/api/relocate/")
def register_relocation(request: RelocationRequest, db: Session = Depends(get_db)):
    """Register address relocation and analyze impact"""
    
    try:
        # Get old location
        old_point = db.query(DeliveryPoint).filter(DeliveryPoint.id == request.location_id).first()
        if not old_point:
            raise HTTPException(status_code=404, detail="Location not found")
        
        # Geocode new address
        new_coords = geocoding_service.geocode_address(request.new_address, old_point.city)
        
        # Register relocation
        relocation = rerouter.relocation_tracker.register_relocation(
            location_id=request.location_id,
            old_coords=(old_point.latitude, old_point.longitude),
            new_coords=(new_coords['latitude'], new_coords['longitude']),
            reason=request.reason
        )
        
        # Save to database
        relocation_record = RelocationRecord(
            relocation_id=relocation['relocation_id'],
            location_id=request.location_id,
            old_latitude=relocation['old_latitude'],
            old_longitude=relocation['old_longitude'],
            new_latitude=relocation['new_latitude'],
            new_longitude=relocation['new_longitude'],
            distance_change_km=relocation['distance_change_km'],
            reason=request.reason,
            status='pending'
        )
        db.add(relocation_record)
        db.commit()
        
        return relocation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Relocation error: {str(e)}")

@app.get("/api/relocations/")
def get_relocations(db: Session = Depends(get_db)):
    """Get all pending relocations"""
    relocations = db.query(RelocationRecord).filter(RelocationRecord.status == 'pending').all()
    return [
        {
            'relocation_id': r.relocation_id,
            'location_id': r.location_id,
            'old_latitude': r.old_latitude,
            'old_longitude': r.old_longitude,
            'new_latitude': r.new_latitude,
            'new_longitude': r.new_longitude,
            'distance_change_km': r.distance_change_km,
            'reason': r.reason,
            'status': r.status
        }
        for r in relocations
    ]

# Statistics and Reports

@app.get("/api/statistics/")
def get_statistics(db: Session = Depends(get_db)):
    """Get system statistics"""
    
    total_points = db.query(DeliveryPoint).count()
    urgent_points = db.query(DeliveryPoint).filter(DeliveryPoint.urgent > 0).count()
    total_routes = db.query(RouteOptimization).count()
    pending_relocations = db.query(RelocationRecord).filter(RelocationRecord.status == 'pending').count()
    
    return {
        'total_delivery_points': total_points,
        'urgent_deliveries': urgent_points,
        'total_routes_optimized': total_routes,
        'pending_relocations': pending_relocations
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)