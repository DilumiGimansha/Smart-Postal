import googlemaps
import numpy as np
from typing import List, Dict, Tuple
import os
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time

class RouteOptimizer:
    def __init__(self):
        api_key = os.getenv('GOOGLE_MAPS_API_KEY', '')
        self.gmaps = googlemaps.Client(key=api_key) if api_key else None
        self.geolocator = Nominatim(user_agent="postal_system_v1")
    
    def geocode_address(self, address: str, city: str = "Colombo") -> Tuple[float, float]:
        """Convert address to coordinates using geocoding"""
        try:
            full_address = f"{address}, {city}, Sri Lanka"
            location = self.geolocator.geocode(full_address, timeout=10)
            
            if location:
                return (location.latitude, location.longitude)
            
            location = self.geolocator.geocode(f"{city}, Sri Lanka", timeout=10)
            if location:
                return (location.latitude, location.longitude)
            
            return (6.9271, 79.8612)
            
        except GeocoderTimedOut:
            time.sleep(1)
            return self.geocode_address(address, city)
        except Exception as e:
            print(f"Geocoding error: {e}")
            return (6.9271, 79.8612)
    
    def calculate_distance_matrix(self, addresses: List[Tuple[float, float]]) -> np.ndarray:
        """Calculate distance matrix between all addresses"""
        n = len(addresses)
        distance_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    distance_matrix[i][j] = self.haversine_distance(
                        addresses[i], addresses[j]
                    )
        
        return distance_matrix
    
    def haversine_distance(self, coord1: Tuple[float, float], 
                          coord2: Tuple[float, float]) -> float:
        """Calculate distance between two coordinates using Haversine formula"""
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        R = 6371
        
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        
        a = (np.sin(dlat/2)**2 + 
             np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * 
             np.sin(dlon/2)**2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        
        return R * c
    
    def get_baseline_route(self, n_locations: int) -> List[int]:
        """Generate simple sequential baseline route"""
        return list(range(n_locations))
    
    def calculate_route_metrics(self, route: List[int], 
                               distance_matrix: np.ndarray) -> Dict:
        """Calculate metrics for a given route"""
        total_distance = 0
        for i in range(len(route) - 1):
            total_distance += distance_matrix[route[i]][route[i+1]]
        
        total_distance += distance_matrix[route[-1]][route[0]]
        
        estimated_time = (total_distance / 30) * 60
        
        return {
            'total_distance': round(total_distance, 2),
            'estimated_time': int(estimated_time)
        }
    
    def get_route_coordinates(self, route: List[int], 
                            addresses: List[Tuple[float, float]]) -> List[Dict]:
        """Get coordinates for route visualization"""
        coordinates = []
        for idx in route:
            lat, lng = addresses[idx]
            coordinates.append({
                'lat': lat,
                'lng': lng,
                'index': idx
            })
        coordinates.append({
            'lat': addresses[0][0],
            'lng': addresses[0][1],
            'index': 0
        })
        return coordinates
    
    def get_traffic_data(self, origin: Tuple[float, float], 
                        destination: Tuple[float, float]) -> Dict:
        """Get real-time traffic data from Google Maps"""
        if not self.gmaps:
            return None
            
        try:
            directions = self.gmaps.directions(
                origin,
                destination,
                mode="driving",
                departure_time="now"
            )
            
            if directions:
                leg = directions[0]['legs'][0]
                return {
                    'distance': leg['distance']['value'] / 1000,
                    'duration': leg['duration']['value'] / 60,
                    'duration_in_traffic': leg.get('duration_in_traffic', {}).get('value', 0) / 60,
                    'traffic_level': self.determine_traffic_level(
                        leg['duration']['value'],
                        leg.get('duration_in_traffic', {}).get('value', 0)
                    )
                }
        except Exception as e:
            print(f"Traffic data error: {e}")
        
        return None
    
    def determine_traffic_level(self, normal_duration: int, 
                               traffic_duration: int) -> str:
        """Determine traffic level based on duration comparison"""
        if traffic_duration == 0:
            return 'unknown'
        
        ratio = traffic_duration / normal_duration
        
        if ratio < 1.2:
            return 'low'
        elif ratio < 1.5:
            return 'moderate'
        else:
            return 'heavy'