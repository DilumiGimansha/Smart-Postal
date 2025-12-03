from django.db import models
from django.core.validators import RegexValidator

class DeliveryAddress(models.Model):
    PRIORITY_CHOICES = [
        ('urgent', 'Urgent'),
        ('regular', 'Regular'),
    ]
    
    # Recipient Information
    recipient_name = models.CharField(max_length=255)
    recipient_phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number')]
    )
    recipient_email = models.EmailField(blank=True, null=True)
    
    # Address Information
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='USA')
    
    # Geolocation
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Priority and Time Windows
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='regular')
    delivery_time_start = models.TimeField(null=True, blank=True)
    delivery_time_end = models.TimeField(null=True, blank=True)
    
    # Additional Information
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Delivery Address'
        verbose_name_plural = 'Delivery Addresses'
    
    def __str__(self):
        return f"{self.recipient_name} - {self.priority} - {self.city}"