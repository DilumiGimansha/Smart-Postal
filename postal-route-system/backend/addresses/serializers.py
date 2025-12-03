from rest_framework import serializers
from .models import DeliveryAddress
import requests
import time

class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        # Validate time windows for urgent deliveries
        if data.get('priority') == 'urgent':
            if not data.get('delivery_time_start') or not data.get('delivery_time_end'):
                raise serializers.ValidationError(
                    "Urgent deliveries must have time windows specified."
                )
            
            # Validate that end time is after start time
            if data['delivery_time_start'] >= data['delivery_time_end']:
                raise serializers.ValidationError(
                    "End time must be after start time."
                )
        
        return data
    
    def create(self, validated_data):
        # Auto-geocode if coordinates not provided
        if not validated_data.get('latitude') or not validated_data.get('longitude'):
            coords = self.geocode_address(validated_data)
            if coords:
                validated_data['latitude'] = coords['lat']
                validated_data['longitude'] = coords['lng']
        
        return super().create(validated_data)
    
    def geocode_address(self, data):
        """Geocode address using OpenStreetMap Nominatim"""
        address = f"{data['address_line1']}, {data['city']}, {data['state']} {data['postal_code']}"
        
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address,
            'format': 'json',
            'limit': 1
        }
        headers = {'User-Agent': 'DeliverySystemApp/1.0'}
        
        try:
            # Add delay to respect Nominatim usage policy
            time.sleep(1)
            response = requests.get(url, params=params, headers=headers, timeout=5)
            if response.status_code == 200 and response.json():
                result = response.json()[0]
                return {
                    'lat': float(result['lat']),
                    'lng': float(result['lon'])
                }
        except Exception as e:
            print(f"Geocoding error: {e}")
        
        return None


class BulkUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    created_by = serializers.CharField(max_length=100)