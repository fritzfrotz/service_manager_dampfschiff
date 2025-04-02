from django import forms
from .models import Appointment
from datetime import datetime

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointment_date']
        widgets = {
            'appointment_date': forms.HiddenInput(),
        }
