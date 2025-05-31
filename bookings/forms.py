from django import forms
from .models import Appointment, UserProfile
from datetime import datetime
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointment_date']
        widgets = {
            'appointment_date': forms.HiddenInput(),
        }

class CustomUserCreationForm(UserCreationForm):
    consent = forms.BooleanField(label="I agree to the privacy policy (GDPR)", required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "consent")

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['address', 'phone', 'heating_system_photo']
