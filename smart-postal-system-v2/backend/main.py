from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import mysql.connector
from datetime import datetime, timedelta
import json
import os

# Import ML models
from postal_ml_webapp import (
    PriorityClassificationModel,
    DynamicRouteOptimizer,
    DynamicRerouter,
    RelocationTracker
)

app = FastAPI(title="Postal Route Optimization API with ML")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML models
priority_classifier = PriorityClassificationModel()
route_optimizer = DynamicRouteOptimizer()
dynamic_rerouter = DynamicRerouter(route_optimizer)
relocation_tracker = RelocationTracker()

# Try to load pre-trained model
MODEL_PATH = "priority_classifier_model.pkl"
if os.path.exists(MODEL_PATH):
    try:
        priority_classifier.load_model(MODEL_PATH)
        print("✓ Loaded pre-trained priority classification model")
    except Exception as e:
        print(f"⚠ Could not load model: {e}")

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="postal_optimization"
    )

# Pydantic Models
class DeliveryInput(BaseModel):
    address: str
    latitude: float
    longitude: float
    mail_type: str
    priority: Optional[str] = None
    parcels: Optional[int] = 1
    urgent: Optional[int] = 0
    time_window: Optional[float] = None

class RouteOptimizationRequest(BaseModel):
    zone_id: int
    deliveries: List[DeliveryInput]
    methods: Optional[List[str]] = None
    traffic_level: Optional[str] = "moderate"
    weather_condition: Optional[str] = "clear"

class PriorityClassificationInput(BaseModel):
    mail_type: str
    sender_type: str
    recipient_type: str
    time_received: str
    day_of_week: str

class TrainingDataInput(BaseModel):
    training_data: List[Dict]
    labels: List[str]

class RelocationInput(BaseModel):
    location_id: int
    old_latitude: float
    old_longitude: float
    new_latitude: float
    new_longitude: float
    reason: Optional[str] = "customer_request"

class ReroutingRequest(BaseModel):
    scenario: Dict
    relocations: List[Dict]
    method: Optional[str] = "q_learning"

# Helper Functions
def get_traffic_factor(level: str) -> float:
    """Convert traffic level to factor"""
    factors = {
        'low': 0.9,
        'moderate': 1.0,
        'high': 1.3,
        'severe': 1.6
    }
    return factors.get(level, 1.0)

def get_weather_factor(condition: str) -> float:
    """Convert weather condition to factor"""
    factors = {
        'clear': 1.0,
        'light_rain': 1.1,
        'heavy_rain': 1.3,
        'flooding': 1.8
    }
    return factors.get(condition, 1.0)

def format_route_for_map(route_sequence, deliveries):
    """Format route for frontend map display"""
    return [deliveries[i] for i in route_sequence if i < len(deliveries)]

# API Endpoints
@app.get("/")
def read_root():
    return {
        "message": "Postal Route Optimization API with ML",
        "status": "running",
        "ml_models": {
            "priority_classifier": priority_classifier.is_trained,
            "route_optimizer": "loaded",
            "dynamic_rerouter": "loaded"
        }
    }

@app.get("/api/postal-zones")
def get_postal_zones():
    """Get all postal zones"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM postal_zones")
        zones = cursor.fetchall()
        
        for zone in zones:
            zone['boundary_coordinates'] = json.loads(zone['boundary_coordinates'])
        
        cursor.close()
        conn.close()
        
        return {"zones": zones}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/deliveries/{zone_id}")
def get_deliveries(zone_id: int):
    """Get all deliveries for a specific zone"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT delivery_id, address, latitude, longitude, 
                   mail_type, priority, deadline, zone_id
            FROM deliveries
            WHERE zone_id = %s
        """, (zone_id,))
        
        deliveries = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {"deliveries": deliveries, "count": len(deliveries)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ml/classify-priority")
def classify_priority_ml(mail_data: PriorityClassificationInput):
    """Classify mail priority using XGBoost ML model"""
    try:
        if not priority_classifier.is_trained:
            # Fallback to rule-based
            urgent_types = ['Court Notice', 'Legal Document', 'Registered Letter', 
                          'Speed Post', 'Express Mail', 'Tax Document']
            priority = 'urgent' if mail_data.mail_type in urgent_types else 'regular'
            return {
                'priority': priority,
                'confidence': 0.85,
                'probability_regular': 0.15 if priority == 'urgent' else 0.85,
                'probability_urgent': 0.85 if priority == 'urgent' else 0.15,
                'method': 'rule_based'
            }
        
        result = priority_classifier.predict(mail_data.dict())
        result['method'] = 'ml_xgboost'
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ml/train-classifier")
def train_priority_classifier(data: TrainingDataInput):
    """Train the priority classification model"""
    try:
        result = priority_classifier.train(data.training_data, data.labels)
        
        # Save trained model
        priority_classifier.save_model(MODEL_PATH)
        
        return {
            "status": "success",
            "message": "Model trained and saved successfully",
            "model_path": MODEL_PATH
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ml/optimize-route")
def optimize_route_ml(request: RouteOptimizationRequest):
    """Optimize route using ML algorithms (Q-Learning, 2-Opt, etc.)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Prepare delivery points for ML model
        delivery_points = [
            {
                'id': 0,
                'address': 'Postal Depot',
                'latitude': 6.9271,
                'longitude': 79.8612,
                'parcels': 0,
                'urgent': 0
            }
        ]
        
        for idx, delivery in enumerate(request.deliveries, start=1):
            point = {
                'id': idx,
                'address': delivery.address,
                'latitude': delivery.latitude,
                'longitude': delivery.longitude,
                'parcels': delivery.parcels or 1,
                'urgent': delivery.urgent or (1 if delivery.priority == 'urgent' else 0),
                'time_window': delivery.time_window or (4.0 if delivery.priority == 'urgent' else 8.0)
            }
            delivery_points.append(point)
        
        # Create scenario
        scenario = {
            'delivery_points': delivery_points,
            'traffic_factor': get_traffic_factor(request.traffic_level),
            'weather_factor': get_weather_factor(request.weather_condition),
            'traffic_level': request.traffic_level,
            'weather_condition': request.weather_condition
        }
        
        # Optimize using multiple methods
        methods = request.methods or ['nearest_neighbor', 'urgent_priority', '2opt', 'q_learning']
        optimization_result = route_optimizer.optimize_route(scenario, methods)
        
        # Format results for frontend
        formatted_results = {}
        for method, result in optimization_result['results'].items():
            formatted_results[method] = {
                'route_sequence': result['route'],
                'deliveries': format_route_for_map(result['route'], delivery_points),
                'total_distance_km': result['total_distance_km'],
                'total_time_hours': result['total_time_hours'],
                'urgent_on_time': result['urgent_on_time'],
                'improvement_pct': result.get('improvement_pct', 0),
                'method': result['method']
            }
        
        # Save best route to database
        best_result = optimization_result['best_result']
        cursor.execute("""
            INSERT INTO optimized_routes 
            (zone_id, delivery_sequence, total_distance, estimated_time, metrics)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            request.zone_id,
            json.dumps(best_result['route']),
            best_result['total_distance_km'],
            int(best_result['total_time_hours'] * 60),
            json.dumps({
                'urgent_on_time': best_result['urgent_on_time'],
                'method': optimization_result['best_method'],
                'improvement_pct': best_result.get('improvement_pct', 0)
            })
        ))
        
        conn.commit()
        route_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return {
            'route_id': route_id,
            'best_method': optimization_result['best_method'],
            'results': formatted_results,
            'best_result': formatted_results[optimization_result['best_method']],
            'scenario': {
                'traffic_level': request.traffic_level,
                'weather_condition': request.weather_condition,
                'traffic_factor': scenario['traffic_factor'],
                'weather_factor': scenario['weather_factor']
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ml/register-relocation")
def register_relocation(relocation: RelocationInput):
    """Register a customer address relocation"""
    try:
        result = relocation_tracker.register_relocation(
            location_id=relocation.location_id,
            old_coords=(relocation.old_latitude, relocation.old_longitude),
            new_coords=(relocation.new_latitude, relocation.new_longitude),
            reason=relocation.reason
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ml/active-relocations")
def get_active_relocations():
    """Get all pending relocations"""
    try:
        relocations = relocation_tracker.get_active_relocations()
        return {"relocations": relocations, "count": len(relocations)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ml/analyze-relocation-impact")
def analyze_relocation_impact(scenario: Dict, relocation: Dict):
    """Analyze impact of address change on route"""
    try:
        impact = dynamic_rerouter.analyze_relocation_impact(scenario, relocation)
        return impact
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ml/execute-rerouting")
def execute_rerouting(request: ReroutingRequest):
    """Execute dynamic rerouting with ML"""
    try:
        result = dynamic_rerouter.execute_rerouting(
            scenario=request.scenario,
            relocations=request.relocations,
            method=request.method
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ml/compare-algorithms")
def compare_algorithms(request: RouteOptimizationRequest):
    """Compare all optimization algorithms side-by-side"""
    try:
        # Prepare delivery points
        delivery_points = [{'id': 0, 'address': 'Depot', 'latitude': 6.9271, 
                           'longitude': 79.8612, 'parcels': 0, 'urgent': 0}]
        
        for idx, delivery in enumerate(request.deliveries, start=1):
            delivery_points.append({
                'id': idx,
                'address': delivery.address,
                'latitude': delivery.latitude,
                'longitude': delivery.longitude,
                'parcels': delivery.parcels or 1,
                'urgent': 1 if delivery.priority == 'urgent' else 0,
                'time_window': 4.0 if delivery.priority == 'urgent' else 8.0
            })
        
        scenario = {
            'delivery_points': delivery_points,
            'traffic_factor': get_traffic_factor(request.traffic_level),
            'weather_factor': get_weather_factor(request.weather_condition),
            'traffic_level': request.traffic_level,
            'weather_condition': request.weather_condition
        }
        
        # Run all methods
        methods = ['nearest_neighbor', 'urgent_priority', '2opt', 'q_learning']
        results = route_optimizer.optimize_route(scenario, methods)
        
        # Format comparison
        comparison = []
        for method in methods:
            result = results['results'][method]
            comparison.append({
                'method': method,
                'display_name': result['method'],
                'distance_km': result['total_distance_km'],
                'time_hours': result['total_time_hours'],
                'urgent_success': result['urgent_on_time'],
                'improvement_pct': result.get('improvement_pct', 0),
                'route': format_route_for_map(result['route'], delivery_points),
                'is_best': method == results['best_method']
            })
        
        return {
            'comparison': comparison,
            'best_method': results['best_method'],
            'scenario': scenario
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ml/model-info")
def get_model_info():
    """Get information about loaded ML models"""
    return {
        'priority_classifier': {
            'loaded': priority_classifier.is_trained,
            'model_type': 'XGBoost',
            'features': len(priority_classifier.feature_names) if priority_classifier.is_trained else 0,
            'mail_types': len(priority_classifier.MAIL_TYPES),
            'sender_types': len(priority_classifier.SENDER_TYPES)
        },
        'route_optimizer': {
            'algorithms': ['Nearest Neighbor', 'Urgent Priority', '2-Opt', 'Q-Learning'],
            'q_table_size': len(route_optimizer.q_table),
            'learning_rate': route_optimizer.learning_rate,
            'discount_factor': route_optimizer.discount_factor
        },
        'rerouting_system': {
            'active_relocations': len(relocation_tracker.active_relocations),
            'rerouting_history': len(dynamic_rerouter.rerouting_history)
        }
    }

@app.get("/api/route-statistics")
def get_route_statistics():
    """Get overall route statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_routes,
                AVG(total_distance) as avg_distance,
                AVG(estimated_time) as avg_time
            FROM optimized_routes
        """)
        
        stats = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) as total_deliveries FROM deliveries")
        delivery_stats = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return {
            "total_routes": stats['total_routes'] or 0,
            "total_deliveries": delivery_stats['total_deliveries'] or 0,
            "avg_distance_km": round(stats['avg_distance'] or 0, 2),
            "avg_time_minutes": round(stats['avg_time'] or 0, 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)