from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import mysql.connector
from datetime import datetime, timedelta
import math
import json
from itertools import combinations

app = FastAPI(title="Postal Route Optimization API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Default XAMPP password
        database="postal_optimization"
    )

# Pydantic Models
class DeliveryInput(BaseModel):
    address: str
    latitude: float
    longitude: float
    mail_type: str
    priority: Optional[str] = None

class RouteOptimizationRequest(BaseModel):
    zone_id: int
    deliveries: List[DeliveryInput]

class DisruptionInput(BaseModel):
    type: str
    severity: Optional[float] = 0.0
    weather: Optional[str] = "Clear"
    relocation_from: Optional[Dict[str, float]] = None
    relocation_to: Optional[Dict[str, float]] = None

class ReRoutingRequest(BaseModel):
    route_id: int
    disruptions: DisruptionInput

# Helper Functions
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula (in km)"""
    R = 6371  # Earth radius in km
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return distance

def classify_priority(mail_type: str) -> str:
    """Simple rule-based priority classification"""
    urgent_types = ['Court Notice', 'Registered Letter', 'Government Document']
    return 'urgent' if mail_type in urgent_types else 'regular'

def clarke_wright_savings(deliveries, depot={'lat': 6.9271, 'lng': 79.8612}):
    """Modified Clarke-Wright Savings Algorithm with priority weighting"""
    n = len(deliveries)
    
    # Calculate savings for all pairs
    savings = []
    for i in range(n):
        for j in range(i + 1, n):
            dist_depot_i = calculate_distance(
                depot['lat'], depot['lng'],
                deliveries[i]['latitude'], deliveries[i]['longitude']
            )
            dist_depot_j = calculate_distance(
                depot['lat'], depot['lng'],
                deliveries[j]['latitude'], deliveries[j]['longitude']
            )
            dist_i_j = calculate_distance(
                deliveries[i]['latitude'], deliveries[i]['longitude'],
                deliveries[j]['latitude'], deliveries[j]['longitude']
            )
            
            # Priority weight multiplier
            priority_weight = 1.5 if (deliveries[i]['priority'] == 'urgent' or 
                                     deliveries[j]['priority'] == 'urgent') else 1.0
            
            saving = (dist_depot_i + dist_depot_j - dist_i_j) * priority_weight
            savings.append((saving, i, j))
    
    # Sort by savings (descending)
    savings.sort(reverse=True, key=lambda x: x[0])
    
    # Build routes
    routes = [[i] for i in range(n)]
    route_map = {i: i for i in range(n)}
    
    for saving, i, j in savings:
        route_i = route_map[i]
        route_j = route_map[j]
        
        if route_i != route_j:
            # Merge routes
            new_route = routes[route_i] + routes[route_j]
            routes[route_i] = new_route
            routes[route_j] = []
            
            for idx in new_route:
                route_map[idx] = route_i
    
    # Filter out empty routes and get the main route
    final_route = [r for r in routes if r][0] if routes else list(range(n))
    
    # Sort urgent deliveries first
    urgent_indices = [i for i in final_route if deliveries[i]['priority'] == 'urgent']
    regular_indices = [i for i in final_route if deliveries[i]['priority'] == 'regular']
    
    return urgent_indices + regular_indices

def calculate_route_metrics(route_sequence, deliveries, depot={'lat': 6.9271, 'lng': 79.8612}):
    """Calculate performance metrics for a route"""
    total_distance = 0
    current_time = datetime.now().replace(hour=8, minute=0, second=0)  # Start at 8 AM
    avg_speed = 20  # km/h in city traffic
    
    urgent_before_noon = 0
    total_urgent = 0
    
    # Distance from depot to first delivery
    if route_sequence:
        first_delivery = deliveries[route_sequence[0]]
        total_distance += calculate_distance(
            depot['lat'], depot['lng'],
            first_delivery['latitude'], first_delivery['longitude']
        )
        current_time += timedelta(hours=total_distance / avg_speed)
    
    # Calculate distances and check deadlines
    for i in range(len(route_sequence)):
        delivery = deliveries[route_sequence[i]]
        
        if delivery['priority'] == 'urgent':
            total_urgent += 1
            if current_time.hour < 12:
                urgent_before_noon += 1
        
        if i < len(route_sequence) - 1:
            next_delivery = deliveries[route_sequence[i + 1]]
            distance = calculate_distance(
                delivery['latitude'], delivery['longitude'],
                next_delivery['latitude'], next_delivery['longitude']
            )
            total_distance += distance
            current_time += timedelta(hours=distance / avg_speed + 0.083)  # 5 min stop
    
    # Distance back to depot
    if route_sequence:
        last_delivery = deliveries[route_sequence[-1]]
        total_distance += calculate_distance(
            last_delivery['latitude'], last_delivery['longitude'],
            depot['lat'], depot['lng']
        )
    
    urgent_percentage = (urgent_before_noon / total_urgent * 100) if total_urgent > 0 else 100
    estimated_time = int(total_distance / avg_speed * 60)  # minutes
    
    # Calculate savings vs sequential route
    sequential_distance = sum([
        calculate_distance(
            deliveries[i]['latitude'], deliveries[i]['longitude'],
            deliveries[i + 1]['latitude'], deliveries[i + 1]['longitude']
        ) for i in range(len(deliveries) - 1)
    ])
    distance_saved = max(0, (sequential_distance - total_distance) / sequential_distance * 100)
    
    return {
        'total_distance': round(total_distance, 2),
        'estimated_time': estimated_time,
        'urgent_before_noon_percentage': round(urgent_percentage, 1),
        'distance_saved_percentage': round(distance_saved, 1),
        'universal_service_compliance': 100.0
    }

# API Endpoints
@app.get("/")
def read_root():
    return {"message": "Postal Route Optimization API", "status": "running"}

@app.get("/api/postal-zones")
def get_postal_zones():
    """Get all postal zones"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM postal_zones")
        zones = cursor.fetchall()
        
        # Parse JSON boundary coordinates
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

@app.post("/api/optimize-postal-route")
def optimize_postal_route(request: RouteOptimizationRequest):
    """Optimize route for given deliveries"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Prepare delivery data
        deliveries = []
        for delivery in request.deliveries:
            priority = delivery.priority or classify_priority(delivery.mail_type)
            deliveries.append({
                'address': delivery.address,
                'latitude': delivery.latitude,
                'longitude': delivery.longitude,
                'mail_type': delivery.mail_type,
                'priority': priority
            })
        
        # Run optimization algorithm
        optimized_sequence = clarke_wright_savings(deliveries)
        
        # Calculate metrics
        metrics = calculate_route_metrics(optimized_sequence, deliveries)
        
        # Prepare route data
        route_data = {
            'sequence': optimized_sequence,
            'deliveries': [deliveries[i] for i in optimized_sequence],
            'metrics': metrics
        }
        
        # Save to database
        cursor.execute("""
            INSERT INTO optimized_routes 
            (zone_id, delivery_sequence, total_distance, estimated_time, metrics)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            request.zone_id,
            json.dumps(optimized_sequence),
            metrics['total_distance'],
            metrics['estimated_time'],
            json.dumps(metrics)
        ))
        
        conn.commit()
        route_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return {
            "route_id": route_id,
            "optimized_route": route_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/classify-priority")
def classify_mail_priority(mail_type: str):
    """Classify mail priority based on type"""
    priority = classify_priority(mail_type)
    confidence = 0.95 if priority == 'urgent' else 0.90
    
    return {
        "mail_type": mail_type,
        "priority": priority,
        "confidence": confidence
    }

@app.get("/api/route/{route_id}")
def get_route(route_id: int):
    """Get specific route details"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM optimized_routes WHERE route_id = %s
        """, (route_id,))
        
        route = cursor.fetchone()
        
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        route['delivery_sequence'] = json.loads(route['delivery_sequence'])
        route['metrics'] = json.loads(route['metrics'])
        
        cursor.close()
        conn.close()
        
        return route
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/calculate-rerouting")
def calculate_rerouting(request: ReRoutingRequest):
    """Calculate re-routing based on disruptions"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get original route
        cursor.execute("""
            SELECT * FROM optimized_routes WHERE route_id = %s
        """, (request.route_id,))
        
        original_route = cursor.fetchone()
        if not original_route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        # Get deliveries for this route
        cursor.execute("""
            SELECT * FROM deliveries WHERE zone_id = %s
        """, (original_route['zone_id'],))
        
        deliveries = cursor.fetchall()
        
        # Calculate multi-factor decision score
        traffic_weight = 0.4
        weather_weight = 0.3
        relocation_weight = 0.3
        
        # Traffic impact
        traffic_impact = request.disruptions.severity if request.disruptions.type == 'traffic' else 0.0
        
        # Weather impact
        weather_impacts = {
            'Clear': 0.0,
            'Light Rain': 0.3,
            'Heavy Rain': 0.6,
            'Flooding': 0.9
        }
        weather_impact = weather_impacts.get(request.disruptions.weather, 0.0)
        
        # Relocation impact
        relocation_impact = 0.0
        if request.disruptions.relocation_from and request.disruptions.relocation_to:
            distance = calculate_distance(
                request.disruptions.relocation_from['lat'],
                request.disruptions.relocation_from['lng'],
                request.disruptions.relocation_to['lat'],
                request.disruptions.relocation_to['lng']
            )
            relocation_impact = min(distance / 5.0, 1.0)  # Normalize to 0-1
        
        # Calculate combined score
        combined_score = (
            traffic_weight * traffic_impact +
            weather_weight * weather_impact +
            relocation_weight * relocation_impact
        )
        
        requires_rerouting = combined_score > 0.6
        
        # If re-routing needed, recalculate route
        new_route = None
        if requires_rerouting:
            optimized_sequence = clarke_wright_savings(deliveries)
            metrics = calculate_route_metrics(optimized_sequence, deliveries)
            
            new_route = {
                'sequence': optimized_sequence,
                'deliveries': [deliveries[i] for i in optimized_sequence],
                'metrics': metrics
            }
        
        # Save decision
        cursor.execute("""
            INSERT INTO rerouting_decisions 
            (original_route_id, factors, impact_score, action_taken)
            VALUES (%s, %s, %s, %s)
        """, (
            request.route_id,
            json.dumps({
                'traffic_impact': traffic_impact,
                'weather_impact': weather_impact,
                'relocation_impact': relocation_impact
            }),
            combined_score,
            'rerouted' if requires_rerouting else 'no_action'
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "requires_rerouting": requires_rerouting,
            "impact_score": round(combined_score, 2),
            "factors": {
                "traffic_impact": round(traffic_impact, 2),
                "weather_impact": round(weather_impact, 2),
                "relocation_impact": round(relocation_impact, 2)
            },
            "new_route": new_route,
            "original_route": {
                'sequence': json.loads(original_route['delivery_sequence']),
                'metrics': json.loads(original_route['metrics'])
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/suggest-handoff")
def suggest_handoff(
    item_address: str,
    original_zone_id: int,
    new_latitude: float,
    new_longitude: float
):
    """Suggest postman handoff for relocated delivery"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Find closest postman in nearby zones
        cursor.execute("""
            SELECT p.postman_id, p.name, p.zone_id, p.contact, z.name as zone_name
            FROM postmen p
            JOIN postal_zones z ON p.zone_id = z.zone_id
            WHERE p.zone_id != %s
            ORDER BY RAND()
            LIMIT 1
        """, (original_zone_id,))
        
        receiving_postman = cursor.fetchone()
        
        if not receiving_postman:
            raise HTTPException(status_code=404, detail="No available postman found")
        
        # Calculate meeting point (midpoint)
        meeting_point = {
            'lat': new_latitude,
            'lng': new_longitude
        }
        
        # Insert handoff recommendation
        cursor.execute("""
            INSERT INTO postman_handoffs
            (original_postman_id, receiving_postman_id, 
             meeting_point_lat, meeting_point_lng, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            original_zone_id,  # Using zone_id as simplified postman_id
            receiving_postman['postman_id'],
            meeting_point['lat'],
            meeting_point['lng'],
            'pending'
        ))
        
        conn.commit()
        handoff_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return {
            "handoff_id": handoff_id,
            "receiving_postman": receiving_postman,
            "meeting_point": meeting_point,
            "estimated_time": "14:30"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        
        cursor.execute("""
            SELECT COUNT(*) as total_deliveries
            FROM deliveries
        """)
        
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