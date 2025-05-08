from django.db import models
from datetime import datetime

class Part(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=50)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Vehicle(models.Model):
    owner_name = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    service_date = models.DateField()
    parts_used = models.ManyToManyField(Part, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def parts_used_display(self):
        return ", ".join([part.name for part in self.parts_used.all()])

    def get_parts_used(self):
        return ", ".join([part.name for part in self.parts_used.all()])

    def __str__(self):
        return f"{self.owner_name} - {self.model} ({self.registration_number})"

class Bill(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    bill_number = models.CharField(max_length=50)
    customer_name = models.CharField(max_length=100)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Add this to your Bill model
    parts_used = models.ManyToManyField(Part, blank=True, related_name='bills')
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bill_number} - {self.customer_name}"
