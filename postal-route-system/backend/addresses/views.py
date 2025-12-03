from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import DeliveryAddress
from .serializers import DeliveryAddressSerializer, BulkUploadSerializer
import csv
import io
import requests
import time

class DeliveryAddressViewSet(viewsets.ModelViewSet):
    queryset = DeliveryAddress.objects.all()
    serializer_class = DeliveryAddressSerializer
    
    def list(self, request, *args, **kwargs):
        """List all delivery addresses"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Create a single delivery address"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """Handle CSV upload for bulk address entry"""
        serializer = BulkUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        csv_file = serializer.validated_data['file']
        created_by = serializer.validated_data['created_by']
        
        if not csv_file.name.endswith('.csv'):
            return Response(
                {'error': 'Only CSV files are accepted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            created_addresses = []
            errors = []
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Map CSV columns to model fields
                    address_data = {
                        'recipient_name': row.get('recipient_name', '').strip(),
                        'recipient_phone': row.get('recipient_phone', '').strip(),
                        'recipient_email': row.get('recipient_email', '').strip(),
                        'address_line1': row.get('address_line1', '').strip(),
                        'address_line2': row.get('address_line2', '').strip(),
                        'city': row.get('city', '').strip(),
                        'state': row.get('state', '').strip(),
                        'postal_code': row.get('postal_code', '').strip(),
                        'priority': row.get('priority', 'regular').lower().strip(),
                        'delivery_time_start': row.get('delivery_time_start', '').strip() or None,
                        'delivery_time_end': row.get('delivery_time_end', '').strip() or None,
                        'notes': row.get('notes', '').strip(),
                        'created_by': created_by
                    }
                    
                    address_serializer = DeliveryAddressSerializer(data=address_data)
                    if address_serializer.is_valid():
                        address_serializer.save()
                        created_addresses.append(address_serializer.data)
                    else:
                        errors.append({
                            'row': row_num,
                            'errors': address_serializer.errors
                        })
                        
                except Exception as e:
                    errors.append({
                        'row': row_num,
                        'error': str(e)
                    })
            
            return Response({
                'created': len(created_addresses),
                'errors': errors,
                'addresses': created_addresses
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'File processing error: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def validate_address(self, request):
        """Validate and geocode a single address"""
        address = request.query_params.get('address', '')
        
        if not address:
            return Response(
                {'error': 'Address parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use Nominatim for geocoding
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address,
            'format': 'json',
            'limit': 1
        }
        headers = {'User-Agent': 'DeliverySystemApp/1.0'}
        
        try:
            time.sleep(1)  # Respect usage policy
            response = requests.get(url, params=params, headers=headers, timeout=5)
            if response.status_code == 200 and response.json():
                result = response.json()[0]
                return Response({
                    'valid': True,
                    'latitude': result['lat'],
                    'longitude': result['lon'],
                    'display_name': result['display_name']
                })
            else:
                return Response({
                    'valid': False,
                    'message': 'Address not found'
                })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )