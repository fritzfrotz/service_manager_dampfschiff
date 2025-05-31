from django.urls import path
from .views import register, profile, delete_account, dashboard

urlpatterns = [
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
    path('delete/', delete_account, name='delete_account'),
    path('dashboard/', dashboard, name='dashboard'),
]
