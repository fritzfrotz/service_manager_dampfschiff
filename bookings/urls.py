from django.urls import path
from . import views

urlpatterns = [
    path('booking/', views.booking_view, name='booking'),
    path('api/check/', views.check_availability, name='check_availability'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('success/', views.booking_success, name='booking_success'),
    path('api/monthly-pricing/', views.monthly_pricing, name='monthly_pricing'),


]
