from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

from .models import Appointment
from .forms import AppointmentForm
from datetime import datetime, timedelta, date
from calendar import monthrange
from django.http import JsonResponse

MAX_BOOKINGS_PER_DAY = 5

@login_required
def booking_view(request):
    return render(request, 'bookings/booking.html')

def check_availability(request):
    date_str = request.GET.get('date')
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    num_booked = Appointment.objects.filter(appointment_date__date=date).count()

    base_price = 50
    price = base_price + (num_booked * 10)
    available = num_booked < MAX_BOOKINGS_PER_DAY

    return JsonResponse({'available': available, 'price': price})

@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.customer = request.user

            date = appointment.appointment_date.date()
            num_existing = Appointment.objects.filter(appointment_date__date=date).count()

            if num_existing >= MAX_BOOKINGS_PER_DAY:
                form.add_error(None, "Sorry, no appointments available for this day.")
            else:
                appointment.price = 50 + num_existing * 10
                appointment.save()
                return redirect('booking_success')

    else:
        date_str = request.GET.get('date')
        date = datetime.strptime(date_str, "%Y-%m-%d")
        form = AppointmentForm(initial={'appointment_date': date})

        num_existing = Appointment.objects.filter(appointment_date__date=date.date()).count()
        price = 50 + num_existing * 10

    return render(request, 'bookings/book_appointment.html', {
        'form': form,
        'date': date_str,
        'price': price,
    })

@login_required
def booking_success(request):
    return render(request, 'bookings/appointment_success.html')

@require_GET
def monthly_pricing(request):
    year = int(request.GET.get('year'))
    month = int(request.GET.get('month'))

    start_date = date(year, month, 1)
    end_date = date(year, month, monthrange(year, month)[1])

    appointments = Appointment.objects.filter(
        appointment_date__date__range=[start_date, end_date]
    )

    appointments_count = {}
    for appointment in appointments:
        day = appointment.appointment_date.date()
        appointments_count[day] = appointments_count.get(day, 0) + 1

    base_price = 50
    pricing_data = []

    current_date = start_date
    while current_date <= end_date:
        num_booked = appointments_count.get(current_date, 0)
        price = base_price + (num_booked * 10)
        available = num_booked < MAX_BOOKINGS_PER_DAY
        pricing_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'price': price,
            'available': available
        })
        current_date += timedelta(days=1)

    return JsonResponse({'pricing': pricing_data})
