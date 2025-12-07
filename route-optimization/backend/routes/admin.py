from django.contrib import admin
from .models import Address, MailItem, Route, TrainingLog, TrafficData

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['address_line', 'city', 'postal_code', 'latitude', 'longitude']
    search_fields = ['address_line', 'city', 'postal_code']
    list_filter = ['city']

@admin.register(MailItem)
class MailItemAdmin(admin.ModelAdmin):
    list_display = ['tracking_number', 'recipient_name', 'priority', 'is_delivered', 'created_at']
    list_filter = ['priority', 'is_delivered', 'created_at']
    search_fields = ['tracking_number', 'recipient_name']
    date_hierarchy = 'created_at'

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['route_name', 'status', 'total_distance', 'estimated_time', 'fuel_saving_percentage', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['route_name']
    date_hierarchy = 'created_at'

@admin.register(TrainingLog)
class TrainingLogAdmin(admin.ModelAdmin):
    list_display = ['episode', 'total_reward', 'epsilon', 'average_distance', 'training_time']
    list_filter = ['training_time']
    date_hierarchy = 'training_time'

@admin.register(TrafficData)
class TrafficDataAdmin(admin.ModelAdmin):
    list_display = ['route', 'segment_start', 'segment_end', 'traffic_level', 'delay_minutes', 'timestamp']
    list_filter = ['traffic_level', 'timestamp']
    date_hierarchy = 'timestamp'