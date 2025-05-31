from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth import login, logout

from .models import Appointment, UserProfile
from .forms import AppointmentForm, CustomUserCreationForm, UserProfileForm
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

    base_price = 50
    max_bookings_per_hour = 1  # should match hourly_pricing
    pricing_data = []

    current_date = start_date
    while current_date <= end_date:
        # Count bookings for the whole day
        day_bookings = Appointment.objects.filter(appointment_date__date=current_date).count()
        lowest_price = base_price + (day_bookings * 10)
        available = False
        booked_slots = 0
        for hour in range(9, 17):
            hour_start = datetime.combine(current_date, datetime.min.time()).replace(hour=hour)
            if timezone.is_naive(hour_start):
                hour_start = timezone.make_aware(hour_start)
            hour_end = hour_start + timedelta(hours=1)
            num_booked = Appointment.objects.filter(appointment_date__gte=hour_start, appointment_date__lt=hour_end).count()
            slot_available = num_booked < max_bookings_per_hour
            if slot_available:
                available = True
            if num_booked >= 1:
                booked_slots += 1
        pricing_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'price': lowest_price,
            'available': available,
            'booked_slots': booked_slots
        })
        current_date += timedelta(days=1)

    return JsonResponse({'pricing': pricing_data})

@require_GET
def hourly_pricing(request):
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Missing date parameter'}, status=400)
    try:
        day = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

    base_price = 50
    max_bookings_per_hour = 1  # adjust as needed
    pricing = {}
    day_bookings = Appointment.objects.filter(appointment_date__date=day).count()
    day_price = base_price + (day_bookings * 10)

    for hour in range(24):
        hour_start = datetime.combine(day, datetime.min.time()).replace(hour=hour)
        if timezone.is_naive(hour_start):
            hour_start = timezone.make_aware(hour_start)
        hour_end = hour_start + timedelta(hours=1)
        num_booked = Appointment.objects.filter(appointment_date__gte=hour_start, appointment_date__lt=hour_end).count()
        available = num_booked < max_bookings_per_hour
        booked_by_user = False
        if request.user.is_authenticated:
            booked_by_user = Appointment.objects.filter(customer=request.user, appointment_date__gte=hour_start, appointment_date__lt=hour_end).exists()

        hour_str = f"{hour:02d}:00"
        pricing[hour_str] = {'price': day_price, 'available': available, 'booked_by_user': booked_by_user}

    return JsonResponse({'pricing': pricing})

@csrf_exempt
@login_required
def book_hour(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST required'}, status=405)
    import json
    try:
        data = json.loads(request.body)
        date_str = data.get('date')
        hour_str = data.get('hour')
        if not date_str or not hour_str:
            return JsonResponse({'success': False, 'message': 'Missing date or hour'}, status=400)
        dt = datetime.strptime(f"{date_str} {hour_str}", "%Y-%m-%d %H:%M")
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Invalid data: {e}'}, status=400)

    # Check if slot is available
    max_bookings_per_hour = 1  # should match hourly_pricing
    hour_start = dt
    hour_end = hour_start + timedelta(hours=1)
    num_booked = Appointment.objects.filter(appointment_date__gte=hour_start, appointment_date__lt=hour_end).count()
    if num_booked >= max_bookings_per_hour:
        return JsonResponse({'success': False, 'message': 'This slot is already fully booked.'})

    # Calculate price based on total bookings for the day
    day_bookings = Appointment.objects.filter(appointment_date__date=dt.date()).count()
    price = 50 + day_bookings * 10
    Appointment.objects.create(
        customer=request.user,
        appointment_date=dt,
        price=price
    )
    return JsonResponse({'success': True, 'message': 'Booking successful!'})

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})

@login_required
def profile(request):
    user = request.user
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
    else:
        form = UserProfileForm(instance=profile)
    return render(request, "registration/profile.html", {"user": user, "form": form, "profile": profile})

@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        return redirect('booking')
    return render(request, "registration/delete_account_confirm.html")

@login_required
def dashboard(request):
    return render(request, "dashboard.html", {"user": request.user})

@require_GET
def optimized_booking(request):
    # Scan next 30 days, working hours 9-16
    today = timezone.localdate()
    base_price = 50
    max_bookings_per_hour = 1
    days_to_check = 30
    earliest = None
    lowest = None
    lowest_price = None
    for day_offset in range(days_to_check):
        day = today + timedelta(days=day_offset)
        day_bookings = Appointment.objects.filter(appointment_date__date=day).count()
        day_price = base_price + (day_bookings * 10)
        for hour in range(9, 17):
            hour_start = timezone.make_aware(datetime.combine(day, datetime.min.time()).replace(hour=hour))
            hour_end = hour_start + timedelta(hours=1)
            num_booked = Appointment.objects.filter(appointment_date__gte=hour_start, appointment_date__lt=hour_end).count()
            available = num_booked < max_bookings_per_hour
            if available:
                if not earliest:
                    earliest = {"date": day.strftime('%Y-%m-%d'), "hour": f"{hour:02d}:00", "price": day_price}
                if lowest_price is None or day_price < lowest_price:
                    lowest = {"date": day.strftime('%Y-%m-%d'), "hour": f"{hour:02d}:00", "price": day_price}
                    lowest_price = day_price
    return JsonResponse({"earliest": earliest, "lowest": lowest})

@csrf_exempt
@login_required
def cancel_booking(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST required'}, status=405)
    import json
    try:
        data = json.loads(request.body)
        date_str = data.get('date')
        hour_str = data.get('hour')
        if not date_str or not hour_str:
            return JsonResponse({'success': False, 'message': 'Missing date or hour'}, status=400)
        dt = datetime.strptime(f"{date_str} {hour_str}", "%Y-%m-%d %H:%M")
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Invalid data: {e}'}, status=400)

    # Find and delete the appointment for this user at this time
    try:
        appointment = Appointment.objects.get(customer=request.user, appointment_date=dt)
        appointment.delete()
        return JsonResponse({'success': True, 'message': 'Booking cancelled successfully.'})
    except Appointment.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'No booking found for this slot.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error cancelling booking: {e}'}, status=500)
