from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Appointment, ServiceAgentAvailability

# Customize the CustomUser admin to show the 'role' field
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )

# Register Appointment model with a custom admin interface
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'appointment_date', 'price', 'created_at')
    list_filter = ('appointment_date', 'customer')
    search_fields = ('customer__username',)

# Register ServiceAgentAvailability model
@admin.register(ServiceAgentAvailability)
class ServiceAgentAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('agent', 'available_date', 'start_time', 'end_time')
    list_filter = ('available_date', 'agent')
