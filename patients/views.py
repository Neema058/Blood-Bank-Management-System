from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Patient

@login_required
def patient_list(request):
    if request.user.role == 'patient':
        return redirect('/patient-portal/')
    patients = Patient.objects.all().order_by('-registered_at')
    q = request.GET.get('q', '')
    if q:
        patients = patients.filter(
            Q(full_name__icontains=q) | Q(hospital_name__icontains=q) |
            Q(contact__icontains=q)
        )
    return render(request, 'patients/list.html', {'patients': patients, 'q': q})

@login_required
def add_patient(request):
    if request.user.role == 'patient':
        return redirect('/patient-portal/')
    if request.method == 'POST':
        Patient.objects.create(
            full_name    = request.POST.get('full_name', '').strip(),
            age          = request.POST.get('age', 0),
            gender       = request.POST.get('gender', 'M'),
            blood_group  = request.POST.get('blood_group', ''),
            hospital_name= request.POST.get('hospital_name', '').strip(),
            doctor_name  = request.POST.get('doctor_name', '').strip(),
            contact      = request.POST.get('contact', '').strip(),
            address      = request.POST.get('address', '').strip(),
        )
        messages.success(request, 'Patient registered successfully!')
        return redirect('/patients/')
    return render(request, 'patients/add.html')

@login_required
def patient_detail(request, pid):
    patient = get_object_or_404(Patient, id=pid)
    requests = patient.bloodrequest_set.all().order_by('-request_date')
    return render(request, 'patients/detail.html', {'patient': patient, 'requests': requests})

@login_required
def edit_patient(request, pid):
    patient = get_object_or_404(Patient, id=pid)
    if request.method == 'POST':
        patient.full_name     = request.POST.get('full_name', patient.full_name)
        patient.hospital_name = request.POST.get('hospital_name', patient.hospital_name)
        patient.doctor_name   = request.POST.get('doctor_name', patient.doctor_name)
        patient.contact       = request.POST.get('contact', patient.contact)
        patient.address       = request.POST.get('address', patient.address)
        patient.save()
        messages.success(request, 'Patient updated!')
        return redirect(f'/patients/{pid}/')
    return render(request, 'patients/edit.html', {'patient': patient})


@login_required
def patient_portal(request):
    """Patient's personal dashboard."""
    if request.user.role != 'patient':
        return redirect('/dashboard/')

    from blood_requests.models import BloodRequest
    from inventory.models import BloodUnit

    if not request.user.patient_id:
        return render(request, 'patients/portal_no_record.html')

    try:
        patient = Patient.objects.get(id=request.user.patient_id)
    except Patient.DoesNotExist:
        return render(request, 'patients/portal_no_record.html')

    my_requests     = BloodRequest.objects.filter(patient=patient).order_by('-request_date')
    pending_count   = my_requests.filter(status='pending').count()
    fulfilled_count = my_requests.filter(status='fulfilled').count()
    rejected_count  = my_requests.filter(status='rejected').count()
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
