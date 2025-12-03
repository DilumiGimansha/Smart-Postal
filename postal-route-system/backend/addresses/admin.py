from django.contrib import admin
from .models import DeliveryAddress

@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ['recipient_name', 'city', 'state', 'priority', 'created_at']
    list_filter = ['priority', 'city', 'state', 'created_at']
    search_fields = ['recipient_name', 'address_line1', 'city', 'postal_code']
    ordering = ['-created_at']