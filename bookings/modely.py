from django.conf import settings
from django.db import models

class Appointment(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'customer'},
        related_name='appointments'
    )
    appointment_date = models.DateTimeField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

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
