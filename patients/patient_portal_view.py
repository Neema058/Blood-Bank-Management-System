# This will be merged into patients/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Patient
from blood_requests.models import BloodRequest
from inventory.models import BloodUnit


@login_required
def patient_portal(request):
    """Patient's personal dashboard."""
    if request.user.role != 'patient':
        return redirect('/dashboard/')

    if not request.user.patient_id:
        return render(request, 'patients/portal_no_record.html')

    try:
        patient = Patient.objects.get(id=request.user.patient_id)
    except Patient.DoesNotExist:
        return render(request, 'patients/portal_no_record.html')

    my_requests = BloodRequest.objects.filter(patient=patient).order_by('-request_date')
    pending_count   = my_requests.filter(status='pending').count()
    fulfilled_count = my_requests.filter(status='fulfilled').count()
    rejected_count  = my_requests.filter(status='rejected').count()

    # Available stock for patient's blood group
    available_stock = BloodUnit.objects.filter(
        blood_group=patient.blood_group, status='available'
    ).count()

    return render(request, 'patients/portal.html', {
        'patient':         patient,
        'my_requests':     my_requests,
        'pending_count':   pending_count,
        'fulfilled_count': fulfilled_count,
        'rejected_count':  rejected_count,
        'available_stock': available_stock,
    })
