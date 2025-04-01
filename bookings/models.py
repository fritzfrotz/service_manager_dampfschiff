from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('customer', 'Customer'),
        ('agent', 'Service Agent'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Appointment(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'customer'},
        related_name='appointments'
    )
    appointment_date = models.DateTimeField()
    # Allow blank and null so our save() method can compute it
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Pricing parameters
    base_price = 50
    increment = 10

    def save(self, *args, **kwargs):
        # Only calculate the price if it's not manually set (and if this is a new object)
        if self.price is None:
            # Extract the date portion from the appointment_date
            date_only = self.appointment_date.date()
            # Count appointments already scheduled for this day
            count = Appointment.objects.filter(appointment_date__date=date_only).count()
            self.price = self.base_price + count * self.increment
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Appointment for {self.customer.username} on {self.appointment_date}"

class ServiceAgentAvailability(models.Model):
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'agent'},
        related_name='availabilities'
    )
    available_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.agent.username} available on {self.available_date} from {self.start_time} to {self.end_time}"
