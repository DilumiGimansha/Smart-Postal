
from django.db import models
from django.utils import timezone

class MailItem(models.Model):
    MAIL_TYPE_CHOICES = [
        ('court_notice', 'Court Notice'),
        ('legal_document', 'Legal Document'),
        ('registered_letter', 'Registered Letter'),
        ('speed_post', 'Speed Post'),
        ('express_mail', 'Express Mail'),
        ('tax_document', 'Tax Document'),
        ('government_letter', 'Government Letter'),
        ('bank_document', 'Bank Document'),
        ('medical_report', 'Medical Report'),
        ('insurance_document', 'Insurance Document'),
        ('certificate', 'Certificate'),
        ('parcel', 'Parcel'),
        ('standard_letter', 'Standard Letter'),
        ('magazine', 'Magazine'),
        ('bill', 'Bill'),
        ('advertisement', 'Advertisement'),
    ]

    SENDER_TYPE_CHOICES = [
        ('court', 'Court'),
        ('law_firm', 'Law Firm'),
        ('government_office', 'Government Office'),
        ('tax_office', 'Tax Office'),
        ('bank', 'Bank'),
        ('hospital', 'Hospital'),
        ('insurance_company', 'Insurance Company'),
        ('educational_institute', 'Educational Institute'),
        ('business', 'Business'),
        ('individual', 'Individual'),
        ('ngo', 'NGO'),
    ]

    PRIORITY_CHOICES = [
        ('urgent', 'Urgent'),
        ('regular', 'Regular'),
    ]

    mail_id = models.CharField(max_length=20, unique=True)
    mail_type = models.CharField(max_length=50, choices=MAIL_TYPE_CHOICES)
    sender_type = models.CharField(max_length=50, choices=SENDER_TYPE_CHOICES)
    recipient_type = models.CharField(max_length=50, choices=SENDER_TYPE_CHOICES)
    time_received = models.TimeField()
    day_of_week = models.CharField(max_length=10)
    predicted_priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    confidence = models.FloatField()
    probability_urgent = models.FloatField()
    probability_regular = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.mail_id} - {self.predicted_priority}"


class DeliveryLocation(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    parcels = models.IntegerField(default=0)
    urgent_parcels = models.IntegerField(default=0)
    time_window = models.FloatField(null=True, blank=True)  # Hours
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class DeliveryRoute(models.Model):
    METHOD_CHOICES = [
        ('nearest_neighbor', 'Nearest Neighbor'),
        ('urgent_priority', 'Urgent Priority'),
        ('2opt', '2-Opt'),
        ('q_learning', 'Q-Learning'),
    ]

    route_id = models.CharField(max_length=20, unique=True)
    method = models.CharField(max_length=30, choices=METHOD_CHOICES)
    route_sequence = models.JSONField()  # List of location IDs
    total_distance_km = models.FloatField()
    total_time_hours = models.FloatField()
    urgent_success = models.IntegerField()
    traffic_factor = models.FloatField()
    weather_factor = models.FloatField()
    traffic_level = models.CharField(max_length=20)
    weather_condition = models.CharField(max_length=30)
    is_optimal = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.route_id} - {self.method}"


class AddressRelocation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
    ]

    relocation_id = models.CharField(max_length=20, unique=True)
    location = models.ForeignKey(DeliveryLocation, on_delete=models.CASCADE)
    old_latitude = models.FloatField()
    old_longitude = models.FloatField()
    new_latitude = models.FloatField()
    new_longitude = models.FloatField()
    distance_change_km = models.FloatField()
    reason = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    impact_analysis = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.relocation_id} - {self.status}"