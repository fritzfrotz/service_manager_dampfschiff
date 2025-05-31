from django.urls import path
from . import views

urlpatterns = [
    path('booking/', views.booking_view, name='booking'),
    path('api/check/', views.check_availability, name='check_availability'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('success/', views.booking_success, name='booking_success'),
    path('api/monthly-pricing/', views.monthly_pricing, name='monthly_pricing'),
    path('api/hourly-pricing/', views.hourly_pricing, name='hourly_pricing'),
    path('api/book-hour/', views.book_hour, name='book_hour'),
    path('api/optimized-booking/', views.optimized_booking, name='optimized_booking'),
    path('api/cancel-booking/', views.cancel_booking, name='cancel_booking'),
]
