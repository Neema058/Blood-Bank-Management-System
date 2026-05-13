from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import BloodUnit, BLOOD_GROUPS, RARE_GROUPS
import datetime

@login_required
def inventory_view(request):
    if request.user.role == 'patient':
        return redirect('/patient-portal/')
    if request.user.role not in ('admin', 'lab_technician', 'receptionist'):
        messages.error(request, 'Access denied!')
        return redirect('/dashboard/')
    BloodUnit.auto_expire()
    units = BloodUnit.objects.all().order_by('expiry_date')
    bg_filter     = request.GET.get('bg', '')
    status_filter = request.GET.get('status', 'available')
    if bg_filter:
        units = units.filter(blood_group=bg_filter)
    if status_filter:
        units = units.filter(status=status_filter)
    stock = BloodUnit.stock_by_group()
    near_expiry = BloodUnit.objects.filter(
        status='available',
        expiry_date__lte=datetime.date.today() + datetime.timedelta(days=7)
    ).order_by('expiry_date')
    rare_alerts = []
    for bg in RARE_GROUPS:
        count = stock.get(bg, 0)
        if count < 3:
            rare_alerts.append({'blood_group': bg, 'count': count})
    ctx = {
        'units': units, 'stock': stock, 'near_expiry': near_expiry,
        'rare_alerts': rare_alerts, 'bg_filter': bg_filter,
        'status_filter': status_filter, 'blood_groups': BLOOD_GROUPS,
    }
    return render(request, 'inventory/inventory.html', ctx)
