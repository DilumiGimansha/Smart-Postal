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
            'limit': 1,
            'addressdetails': 1
        }
        headers = {
            'User-Agent': 'DeliverySystemApp/1.0 (your-email@example.com)',
            'Accept-Language': 'en'
        }
        
        try:
            # Add delay to respect Nominatim usage policy (max 1 request per second)
            time.sleep(1)
            
            response = requests.get(
                url, 
                params=params, 
                headers=headers, 
                timeout=10
            )
            
            # Check response status
            if response.status_code == 200:
                results = response.json()
                
                if results and len(results) > 0:
                    result = results[0]
                    return Response({
                        'valid': True,
                        'latitude': result['lat'],
                        'longitude': result['lon'],
                        'display_name': result.get('display_name', ''),
                        'address_details': result.get('address', {})
                    })
                else:
                    return Response({
                        'valid': False,
                        'message': 'Address not found. Please check the address details.'
                    })
            
            elif response.status_code == 429:
                return Response({
                    'valid': False,
                    'message': 'Too many requests. Please wait a moment and try again.',
                    'error': 'rate_limit'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            else:
                return Response({
                    'valid': False,
                    'message': f'Geocoding service returned error: {response.status_code}',
                    'error': 'service_error'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
        except requests.exceptions.Timeout:
            return Response({
                'valid': False,
                'message': 'Request timeout. The geocoding service is taking too long to respond.',
                'error': 'timeout'
            }, status=status.HTTP_504_GATEWAY_TIMEOUT)
            
        except requests.exceptions.ConnectionError:
            return Response({
                'valid': False,
                'message': 'Cannot connect to geocoding service. Please check your internet connection.',
                'error': 'connection_error'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        except Exception as e:
            return Response({
                'valid': False,
                'message': f'Unexpected error: {str(e)}',
                'error': 'unknown_error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get delivery statistics"""
        from django.db.models import Count
        
        total = DeliveryAddress.objects.count()
        urgent = DeliveryAddress.objects.filter(priority='urgent').count()
        regular = DeliveryAddress.objects.filter(priority='regular').count()
        geocoded = DeliveryAddress.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        ).count()
        
        return Response({
            'total': total,
            'urgent': urgent,
            'regular': regular,
            'geocoded': geocoded,
            'not_geocoded': total - geocoded
        })
    
    @action(detail=False, methods=['get'])
    def by_city(self, request):
        """Get addresses grouped by city"""
        from django.db.models import Count
        
        cities = DeliveryAddress.objects.values('city').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response(list(cities))