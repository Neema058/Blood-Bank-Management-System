from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from donors.models import Donor
from donations.models import Donation
from inventory.models import BloodUnit, BLOOD_GROUPS, RARE_GROUPS
from patients.models import Patient
from blood_requests.models import BloodRequest
import datetime
import json

@login_required
def dashboard(request):
    if request.user.role == 'patient':
        return redirect('/patient-portal/')
    BloodUnit.auto_expire()
    today = datetime.date.today()

    total_donors    = Donor.objects.filter(is_active=True).count()
    total_patients  = Patient.objects.count()
    total_donations = Donation.objects.filter(status='accepted').count()
    total_requests  = BloodRequest.objects.count()

    stock = BloodUnit.stock_by_group()
    total_available = sum(stock.values())

    emergency_requests = BloodRequest.objects.filter(
        status='pending', urgency='emergency'
    ).order_by('-request_date')

    near_expiry = BloodUnit.objects.filter(
        status='available',
        expiry_date__lte=today + datetime.timedelta(days=7),
        expiry_date__gte=today
    ).order_by('expiry_date')

    rare_alerts = []
    for bg in RARE_GROUPS:
        count = stock.get(bg, 0)
        if count < 3:
            rare_alerts.append({'blood_group': bg, 'count': count})

    critical_stock = [bg for bg, cnt in stock.items() if cnt < 5]

    recent_donations = Donation.objects.all().order_by('-created_at')[:5]
    recent_requests  = BloodRequest.objects.all().order_by('-request_date')[:5]
    pending_requests = BloodRequest.objects.filter(status='pending').count()

    stock_labels = list(stock.keys())
    stock_values = list(stock.values())

    monthly = []
    for m in range(1, 13):
        count = Donation.objects.filter(
            donation_date__year=today.year,
            donation_date__month=m,
            status='accepted'
        ).count()
        monthly.append(count)

    ctx = {
        'total_donors':    total_donors,
        'total_patients':  total_patients,
        'total_donations': total_donations,
        'total_requests':  total_requests,
        'total_available': total_available,
        'pending_requests':pending_requests,
        'stock':           stock,
        'emergency_requests': emergency_requests,
        'near_expiry':     near_expiry,
        'rare_alerts':     rare_alerts,
        'critical_stock':  critical_stock,
        'recent_donations':recent_donations,
        'recent_requests': recent_requests,
        'stock_labels':    json.dumps(stock_labels),
        'stock_values':    json.dumps(stock_values),
        'monthly_data':    json.dumps(monthly),
        'today':           today,
    }
    return render(request, 'dashboard/dashboard.html', ctx)
