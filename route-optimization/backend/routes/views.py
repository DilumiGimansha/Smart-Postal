# backend/routes/views.py - Complete File

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import csv
import io
import numpy as np
import time

from .models import Address, MailItem, Route, TrainingLog, TrafficData
from .serializers import (
    AddressSerializer, MailItemSerializer, RouteSerializer,
    TrainingLogSerializer, CSVUploadSerializer,
    RouteOptimizationRequestSerializer, TrafficDataSerializer,
    MailItemCreateSerializer
)
from .ml_models.q_learning import QLearningRouteOptimizer
from .ml_models.route_optimizer import RouteOptimizer

class MailItemViewSet(viewsets.ModelViewSet):
    queryset = MailItem.objects.all()
    serializer_class = MailItemSerializer
    
    @action(detail=False, methods=['post'])
    def create_manual(self, request):
        """Create mail item manually with auto-geocoding"""
        serializer = MailItemCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        optimizer = RouteOptimizer()
        
        # Auto-geocode if coordinates not provided
        if not data.get('latitude') or not data.get('longitude'):
            print(f"Geocoding address: {data['address']}, {data.get('city', 'Colombo')}")
            lat, lng = optimizer.geocode_address(data['address'], data.get('city', 'Colombo'))
            print(f"Got coordinates: {lat}, {lng}")
        else:
            lat, lng = data['latitude'], data['longitude']
        
        # Create address
        address = Address.objects.create(
            address_line=data['address'],
            city=data.get('city', 'Colombo'),
            postal_code=data['postal_code'],
            latitude=lat,
            longitude=lng
        )
        
        # Create mail item
        mail_item = MailItem.objects.create(
            tracking_number=data['tracking_number'],
            recipient_name=data['recipient_name'],
            destination_address=address,
            priority=data.get('priority', 'regular')
        )
        
        return Response(
            MailItemSerializer(mail_item).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['post'])
    def upload_csv(self, request):
        """Upload CSV file with mail items (auto-geocoding if lat/lng missing)"""
        serializer = CSVUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        csv_file = request.FILES['file']
        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        
        created_items = []
        optimizer = RouteOptimizer()
        
        for row in reader:
            # Auto-geocode if coordinates not in CSV
            if 'latitude' not in row or 'longitude' not in row or not row.get('latitude'):
                print(f"Geocoding: {row['address']}, {row.get('city', 'Colombo')}")
                lat, lng = optimizer.geocode_address(
                    row['address'], 
                    row.get('city', 'Colombo')
                )
                print(f"Got: {lat}, {lng}")
                time.sleep(1)  # Rate limiting for Nominatim
            else:
                lat = float(row['latitude'])
                lng = float(row['longitude'])
            
            # Create address
            address, _ = Address.objects.get_or_create(
                address_line=row['address'],
                city=row.get('city', 'Colombo'),
                postal_code=row.get('postal_code', '00000'),
                defaults={
                    'latitude': lat,
                    'longitude': lng
                }
            )
            
            # Update coordinates if address already exists
            if address.latitude != lat or address.longitude != lng:
                address.latitude = lat
                address.longitude = lng
                address.save()
            
            # Create mail item
            mail_item = MailItem.objects.create(
                tracking_number=row['tracking_number'],
                recipient_name=row['recipient_name'],
                destination_address=address,
                priority=row.get('priority', 'regular')
            )
            created_items.append(mail_item)
        
        return Response({
            'message': f'{len(created_items)} mail items created with auto-geocoded coordinates',
            'items': MailItemSerializer(created_items, many=True).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['patch'])
    def update_priority(self, request, pk=None):
        """Update priority of a mail item"""
        mail_item = self.get_object()
        priority = request.data.get('priority')
        
        if priority not in ['urgent', 'regular']:
            return Response(
                {'error': 'Invalid priority. Must be "urgent" or "regular"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        mail_item.priority = priority
        mail_item.save()
        
        return Response(MailItemSerializer(mail_item).data)

class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    
    @action(detail=False, methods=['post'])
    def optimize(self, request):
        """Optimize route using Q-Learning with map coordinates"""
        serializer = RouteOptimizationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        mail_item_ids = serializer.validated_data['mail_item_ids']
        route_name = serializer.validated_data['route_name']
        
        mail_items = MailItem.objects.filter(id__in=mail_item_ids)
        
        if not mail_items.exists():
            return Response(
                {'error': 'No mail items found with provided IDs'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create route
        route = Route.objects.create(
            route_name=route_name,
            status='pending'
        )
        route.mail_items.set(mail_items)
        
        # Extract coordinates and priorities
        addresses = [(route.depot_latitude, route.depot_longitude)]
        priorities = [False]
        
        for item in mail_items:
            addr = item.destination_address
            addresses.append((addr.latitude, addr.longitude))
            priorities.append(item.priority == 'urgent')
        
        # Calculate distance matrix
        optimizer = RouteOptimizer()
        distance_matrix = optimizer.calculate_distance_matrix(addresses)
        
        # Train Q-Learning model
        n_locations = len(addresses)
        ql_model = QLearningRouteOptimizer(n_locations=n_locations)
        
        print(f"Training Q-Learning model for {n_locations} locations...")
        training_logs = ql_model.train(
            distance_matrix=distance_matrix,
            priorities=priorities,
            n_episodes=1000
        )
        print("Training complete!")
        
        # Save training logs
        for log in training_logs:
            TrainingLog.objects.create(**log)
        
        # Get optimized route
        optimized_route = ql_model.get_optimized_route(distance_matrix, priorities)
        baseline_route = optimizer.get_baseline_route(n_locations)
        
        # Get coordinates for visualization
        optimized_coords = optimizer.get_route_coordinates(optimized_route, addresses)
        baseline_coords = optimizer.get_route_coordinates(baseline_route, addresses)
        
        # Calculate metrics
        optimized_metrics = optimizer.calculate_route_metrics(
            optimized_route, distance_matrix
        )
        baseline_metrics = optimizer.calculate_route_metrics(
            baseline_route, distance_matrix
        )
        
        # Calculate improvement
        distance_saved = baseline_metrics['total_distance'] - optimized_metrics['total_distance']
        fuel_saving_percentage = (distance_saved / baseline_metrics['total_distance']) * 100 if baseline_metrics['total_distance'] > 0 else 0
        
        # Update route
        route.optimized_sequence = optimized_route
        route.baseline_sequence = baseline_route
        route.optimized_coordinates = optimized_coords
        route.baseline_coordinates = baseline_coords
        route.total_distance = optimized_metrics['total_distance']
        route.estimated_time = optimized_metrics['estimated_time']
        route.fuel_saving_percentage = round(fuel_saving_percentage, 2)
        route.status = 'optimized'
        route.save()
        
        return Response({
            'route': RouteSerializer(route).data,
            'optimized_metrics': optimized_metrics,
            'baseline_metrics': baseline_metrics,
            'improvement': {
                'distance_saved_km': round(distance_saved, 2),
                'fuel_saving_percentage': round(fuel_saving_percentage, 2),
                'time_saved_minutes': baseline_metrics['estimated_time'] - optimized_metrics['estimated_time']
            },
            'coordinates': {
                'optimized': optimized_coords,
                'baseline': baseline_coords
            }
        })
    
    @action(detail=True, methods=['get'])
    def traffic_data(self, request, pk=None):
        """Get traffic data for route"""
        route = self.get_object()
        mail_items = list(route.mail_items.all())
        
        if not route.optimized_sequence:
            return Response(
                {'error': 'Route not optimized yet'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        optimizer = RouteOptimizer()
        traffic_data_list = []
        
        addresses = [(route.depot_latitude, route.depot_longitude)]
        for item in mail_items:
            addr = item.destination_address
            addresses.append((addr.latitude, addr.longitude))
        
        # Get traffic for each segment
        for i in range(len(route.optimized_sequence) - 1):
            idx1 = route.optimized_sequence[i]
            idx2 = route.optimized_sequence[i + 1]
            
            origin = addresses[idx1]
            destination = addresses[idx2]
            
            traffic_info = optimizer.get_traffic_data(origin, destination)
            
            if traffic_info:
                traffic_data = TrafficData.objects.create(
                    route=route,
                    segment_start=f"Location {idx1}",
                    segment_end=f"Location {idx2}",
                    traffic_level=traffic_info['traffic_level'],
                    delay_minutes=int(traffic_info.get('duration_in_traffic', 0) - traffic_info.get('duration', 0))
                )
                traffic_data_list.append(traffic_data)
        
        return Response(TrafficDataSerializer(traffic_data_list, many=True).data)

class TrainingLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TrainingLog.objects.all()
    serializer_class = TrainingLogSerializer
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest training logs"""
        logs = TrainingLog.objects.order_by('-training_time')[:20]
        return Response(TrainingLogSerializer(logs, many=True).data)