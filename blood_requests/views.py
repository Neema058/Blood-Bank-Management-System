from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import BloodRequest
from patients.models import Patient
from inventory.models import BloodUnit
import datetime


def _can_manage_requests(user):
    return user.role in ('admin', 'receptionist')


def _can_approve_requests(user):
    return user.role == 'admin'


def _can_view_all_requests(user):
    return user.role in ('admin', 'receptionist', 'lab_technician')


@login_required
def request_list(request):
    if request.user.role == 'patient':
        if not request.user.patient_id:
            messages.error(request, 'No patient record linked to your account.')
            return redirect('/patient-portal/')
        reqs = BloodRequest.objects.filter(
            patient_id=request.user.patient_id
        ).order_by('-request_date')
        return render(request, 'requests/list.html', {
            'requests': reqs,
            'emergency_count': 0,
            'is_patient_view': True,
        })

    if not _can_view_all_requests(request.user):
        messages.error(request, 'Access denied!')
        return redirect('/')

    reqs = BloodRequest.objects.all().order_by('-request_date')
    status_f  = request.GET.get('status', '')
    urgency_f = request.GET.get('urgency', '')
    if status_f:
        reqs = reqs.filter(status=status_f)
    if urgency_f:
        reqs = reqs.filter(urgency=urgency_f)

    emergency_count = BloodRequest.objects.filter(status='pending', urgency='emergency').count()
    ctx = {
        'requests':        reqs,
        'emergency_count': emergency_count,
        'status_f':        status_f,
        'urgency_f':       urgency_f,
        'is_patient_view': False,
    }
    return render(request, 'requests/list.html', ctx)


@login_required
def add_request(request):
    if request.user.role == 'patient':
        if not request.user.patient_id:
            messages.error(request, 'No patient record linked to your account.')
            return redirect('/patient-portal/')
        try:
            patient = Patient.objects.get(id=request.user.patient_id)
        except Patient.DoesNotExist:
            messages.error(request, 'Your patient record was not found.')
            return redirect('/patient-portal/')

        if request.method == 'POST':
            bg      = request.POST.get('blood_group', '') or patient.blood_group
            units   = int(request.POST.get('units_required', 1))
            urgency = request.POST.get('urgency', 'normal')
            notes   = request.POST.get('notes', '')
            available = BloodUnit.objects.filter(blood_group=bg, status='available').count()
            BloodRequest.objects.create(
                patient=patient, blood_group=bg, units_required=units,
                urgency=urgency, notes=notes, status='pending',
            )
            if urgency == 'emergency':
                messages.error(request, f'Emergency request submitted! {available} units of {bg} currently available.')
            else:
                messages.success(request, f'Blood request submitted! {available} units of {bg} currently available.')
            return redirect('/patient-portal/')
        return render(request, 'requests/add.html', {
            'patients':         [patient],
            'selected_patient': patient,
            'is_patient_view':  True,
        })

    if not _can_manage_requests(request.user):
        messages.error(request, 'Access denied! Only Admin or Receptionist can create requests.')
        return redirect('/')

    patients = Patient.objects.all().order_by('full_name')
    if request.method == 'POST':
        patient  = get_object_or_404(Patient, id=request.POST.get('patient_id'))
        bg       = request.POST.get('blood_group', '')
        units    = int(request.POST.get('units_required', 1))
        urgency  = request.POST.get('urgency', 'normal')
        notes    = request.POST.get('notes', '')
        available = BloodUnit.objects.filter(blood_group=bg, status='available').count()
        BloodRequest.objects.create(
            patient=patient, blood_group=bg, units_required=units,
            urgency=urgency, notes=notes, status='pending',
        )
        if urgency == 'emergency':
            messages.error(request, f'EMERGENCY REQUEST created for {patient.full_name}! {available} units of {bg} available.')
        else:
            messages.success(request, f'Blood request created! {available} units of {bg} currently available.')
        return redirect('/requests/')
    return render(request, 'requests/add.html', {'patients': patients, 'is_patient_view': False})


@login_required
def request_detail(request, rid):
    req = get_object_or_404(BloodRequest, id=rid)

    if request.user.role == 'patient':
        if req.patient_id != request.user.patient_id:
            messages.error(request, 'Access denied!')
            return redirect('/patient-portal/')

    available_units = BloodUnit.objects.filter(
        blood_group=req.blood_group, status='available'
    ).order_by('expiry_date')
    return render(request, 'requests/detail.html', {
        'req': req,
        'available_units': available_units,
        'can_approve': _can_approve_requests(request.user),
    })


@login_required
def approve_request(request, rid):
    if not _can_approve_requests(request.user):
        messages.error(request, 'Only Admin can approve or reject requests!')
        return redirect(f'/requests/{rid}/')

    req = get_object_or_404(BloodRequest, id=rid)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            available = BloodUnit.objects.filter(
                blood_group=req.blood_group, status='available'
            ).order_by('expiry_date')[:req.units_required]

            if available.count() < req.units_required:
                messages.error(request, f'Not enough units! Only {available.count()} of {req.units_required} available.')
                return redirect(f'/requests/{rid}/')

            for unit in available:
                unit.status      = 'issued'
                unit.issued_to   = req
                unit.issued_date = datetime.date.today()
                unit.save()

            req.status         = 'fulfilled'
            req.processed_by   = request.user
            req.fulfilled_date = datetime.date.today()
            req.save()
            messages.success(request, f'Request fulfilled! {req.units_required} units issued to {req.patient.full_name}.')

        elif action == 'reject':
            req.status           = 'rejected'
            req.processed_by     = request.user
            req.rejection_reason = request.POST.get('rejection_reason', '')
            req.save()
            messages.warning(request, 'Request rejected.')

    return redirect('/requests/')
