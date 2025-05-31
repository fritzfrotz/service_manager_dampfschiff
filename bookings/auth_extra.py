from django.urls import path
from .views import register, profile, delete_account

urlpatterns = [
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
    path('delete/', delete_account, name='delete_account'),
]
