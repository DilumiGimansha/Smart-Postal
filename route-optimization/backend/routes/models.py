from django.db import models

class Address(models.Model):
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100, default='Colombo')
    postal_code = models.CharField(max_length=10)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.address_line}, {self.city}"
    
    class Meta:
        verbose_name_plural = "Addresses"

class MailItem(models.Model):
    PRIORITY_CHOICES = [
        ('urgent', 'Urgent'),
        ('regular', 'Regular'),
    ]
    
    tracking_number = models.CharField(max_length=50, unique=True)
    recipient_name = models.CharField(max_length=200)
    destination_address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='mail_items')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='regular')
    created_at = models.DateTimeField(auto_now_add=True)
    is_delivered = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.tracking_number} - {self.priority}"
    
    class Meta:
        ordering = ['-created_at']

class Route(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('optimized', 'Optimized'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    route_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    mail_items = models.ManyToManyField(MailItem, related_name='routes')
    
    depot_latitude = models.FloatField(default=6.9271)
    depot_longitude = models.FloatField(default=79.8612)
    
    total_distance = models.FloatField(null=True, blank=True)
    estimated_time = models.IntegerField(null=True, blank=True)
    fuel_saving_percentage = models.FloatField(null=True, blank=True)
    
    optimized_sequence = models.JSONField(null=True, blank=True)
    baseline_sequence = models.JSONField(null=True, blank=True)
    optimized_coordinates = models.JSONField(null=True, blank=True)
    baseline_coordinates = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.route_name} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']

class TrainingLog(models.Model):
    episode = models.IntegerField()
    total_reward = models.FloatField()
    epsilon = models.FloatField()
    average_distance = models.FloatField()
    training_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['episode']

class TrafficData(models.Model):
    TRAFFIC_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('heavy', 'Heavy'),
        ('unknown', 'Unknown'),
    ]
    
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='traffic_data')
    segment_start = models.CharField(max_length=255)
    segment_end = models.CharField(max_length=255)
    traffic_level = models.CharField(max_length=20, choices=TRAFFIC_LEVEL_CHOICES)
    delay_minutes = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Traffic Data"
        ordering = ['-timestamp']