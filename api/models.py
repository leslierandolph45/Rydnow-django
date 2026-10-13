from django.db import models




# Create your models here.




class Rider(models.Model):
    SERVICE_CHOICES = [
        ('okada', 'Okada Rider'),
        ('dispatch', 'Dispatch Rider'),
        ('eco', 'Eco Tricycle'),
        ('waste', 'Waste Collector'),
    ]
    
    STATUS_CHOICES = [
        ('offline', 'Offline'),
        ('online', 'Online'),
        ('busy', 'Busy'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    
    # ✅ Service type — for smart matching
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES, default='okada')
    vehicle_type = models.CharField(max_length=50, blank=True, null=True)
    vehicle_plate = models.CharField(max_length=50, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    current_location = models.JSONField(blank=True, null=True)
    total_rides = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # ✅ Location coordinates for distance calculation
    current_lat = models.FloatField(blank=True, null=True)
    current_lng = models.FloatField(blank=True, null=True)
    
    # ✅ Performance stats for better matching
    rating = models.FloatField(default=5.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name




class Booking(models.Model):
    TYPE_CHOICES = [
        ('okada', 'Okada Ride'),
        ('rider', 'Delivery'),
        ('parcel', 'Parcel'),
        ('eco', 'Eco'),
        ('waste-bin', 'Waste Collection'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('searching_rider', 'Searching Rider'),
        ('auto_assigned', 'Auto-Assigned'),
        ('accepted', 'Accepted'),
        ('assigned', 'Assigned'),
        ('rider_accepted', 'Rider Accepted'),
        ('manual_accepted', 'Manual Acceptance'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    pickup = models.CharField(max_length=255)
    pickup_lat = models.FloatField(blank=True, null=True)
    pickup_lng = models.FloatField(blank=True, null=True)
    destination = models.CharField(max_length=255)
    dest_lat = models.FloatField(blank=True, null=True)
    dest_lng = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    
    price = models.CharField(max_length=20, blank=True, null=True)
    fare = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    distance_km = models.FloatField(blank=True, null=True)
    estimated_time = models.CharField(max_length=50, blank=True, null=True)
    
    item_details = models.TextField(blank=True, null=True)
    item_category = models.CharField(max_length=100, blank=True, null=True)
    preferred_time = models.DateTimeField(blank=True, null=True)
    
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    
    rider = models.ForeignKey(Rider, on_delete=models.SET_NULL, blank=True, null=True, related_name='bookings')
    rider_name = models.CharField(max_length=100, blank=True, null=True)
    rider_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # ✅ Assignment tracking — auto vs manual
    assignment_method = models.CharField(max_length=20, blank=True, null=True)  # 'auto' or 'manual'
    
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    payment_status = models.CharField(max_length=30, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_type_display()} — {self.pickup} → {self.destination}"




class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='transaction')
    transaction_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_id} — GH₵{self.amount}"




class Withdrawal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    bank_name = models.CharField(max_length=200, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    account_name = models.CharField(max_length=100, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.rider.name} — GH₵{self.amount}"
