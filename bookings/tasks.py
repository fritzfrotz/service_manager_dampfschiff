from celery import shared_task
from .models import Appointment, ServiceAgentAvailability
import requests
from django.conf import settings

@shared_task
def optimize_routes():
    # Fetch all upcoming appointments
    appointments = Appointment.objects.filter(appointment_date__gte=datetime.now())

    # Prepare locations (example format)
    locations = [
        {
            "address": appt.customer.profile.address,  # assuming customers have address
            "appointment_id": appt.id
        }
        for appt in appointments
    ]

    # Call external routing API (e.g., Google Maps Routes API)
    API_KEY = settings.GOOGLE_MAPS_API_KEY
    url = f"https://routes.googleapis.com/directions/v2:computeRoutes?key={API_KEY}"

    # Example request body (customize as per your API)
    request_body = {
        "origin": {"address": "Service Center Address"},
        "destinations": [{"address": loc["address"]} for loc in locations],
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE"
    }

    response = requests.post(url, json=request_body)

    if response.status_code == 200:
        routes = response.json()
        # Process and store optimized routes (simplified)
        for route in routes.get("routes", []):
            print("Optimized route:", route)
    else:
        print("API error:", response.status_code, response.text)
