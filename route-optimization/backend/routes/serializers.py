from rest_framework import serializers
from .models import Address, MailItem, Route, TrainingLog, TrafficData

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class MailItemSerializer(serializers.ModelSerializer):
    destination_address = AddressSerializer(read_only=True)
    
    class Meta:
        model = MailItem
        fields = '__all__'

class MailItemCreateSerializer(serializers.Serializer):
    tracking_number = serializers.CharField(max_length=50)
    recipient_name = serializers.CharField(max_length=200)
    address = serializers.CharField(max_length=255)
    city = serializers.CharField(max_length=100, default='Colombo')
    postal_code = serializers.CharField(max_length=10)
    priority = serializers.ChoiceField(choices=['urgent', 'regular'], default='regular')
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)

class RouteSerializer(serializers.ModelSerializer):
    mail_items = MailItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Route
        fields = '__all__'

class TrainingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingLog
        fields = '__all__'

class TrafficDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrafficData
        fields = '__all__'

class CSVUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    
class RouteOptimizationRequestSerializer(serializers.Serializer):
    mail_item_ids = serializers.ListField(child=serializers.IntegerField())
    route_name = serializers.CharField(max_length=100)