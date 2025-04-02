from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Appointment
from .forms import AppointmentForm
from datetime import datetime
from django.http import JsonResponse, HttpResponse


@login_required
def booking_view(request):
    return render(request, 'bookings/booking.html')

def check_availability(request):
    date_str = request.GET.get('date')
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    num_booked = Appointment.objects.filter(appointment_date__date=date).count()

    base_price = 50
    price = base_price + (num_booked * 10)

    return JsonResponse({
        'available': True,
        'price': price
    })

@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.customer = request.user

            # Calculate price
            date = appointment.appointment_date.date()
            num_existing = Appointment.objects.filter(appointment_date__date=date).count()
            appointment.price = 50 + num_existing * 10

            appointment.save()
            return redirect('booking_success')  # you can make this later
    else:
        date_str = request.GET.get('date')
        date = datetime.strptime(date_str, "%Y-%m-%d")
        form = AppointmentForm(initial={'appointment_date': date})

        # calculate price
        num_existing = Appointment.objects.filter(appointment_date__date=date.date()).count()
        price = 50 + num_existing * 10

    return render(request, 'bookings/book_appointment.html', {
        'form': form,
        'date': date_str,
        'price': price,
    })

def booking_success(request):
    return HttpResponse("<h2>Appointment successfully booked!</h2><p><a href='/booking/'>Back to calendar</a></p>")
