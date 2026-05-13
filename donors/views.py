from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Donor

# Lab tech + Admin can view donors; Receptionist + Admin can add/edit
DONOR_VIEW_ROLES  = ('admin', 'lab_technician', 'receptionist')
DONOR_EDIT_ROLES  = ('admin', 'receptionist')

@login_required
def donor_list(request):
    if request.user.role not in DONOR_VIEW_ROLES:
        return redirect('/patient-portal/' if request.user.role == 'patient' else '/')
    donors = Donor.objects.all().order_by('-registered_at')
    q  = request.GET.get('q', '')
    bg = request.GET.get('blood_group', '')
    if q:
        donors = donors.filter(
            Q(full_name__icontains=q) | Q(cnic__icontains=q) |
            Q(phone__icontains=q) | Q(donor_id__icontains=q)
        )
    if bg:
        donors = donors.filter(blood_group=bg)
    return render(request, 'donors/list.html', {'donors': donors, 'q': q, 'bg': bg})

@login_required
def add_donor(request):
    if request.user.role not in DONOR_EDIT_ROLES:
        messages.error(request, 'Access denied!')
        return redirect('/')
    if request.method == 'POST':
        cnic = request.POST.get('cnic', '').strip()
        if Donor.objects.filter(cnic=cnic).exists():
            messages.error(request, 'A donor with this CNIC already exists!')
            return render(request, 'donors/add.html')
        age = int(request.POST.get('age', 0))
        if age < 18 or age > 65:
            messages.error(request, 'Donor age must be between 18 and 65!')
            return render(request, 'donors/add.html')
        Donor.objects.create(
            full_name      = request.POST.get('full_name', '').strip(),
            cnic           = cnic,
            age            = age,
            gender         = request.POST.get('gender', 'M'),
            blood_group    = request.POST.get('blood_group', ''),
            phone          = request.POST.get('phone', '').strip(),
            email          = request.POST.get('email', '').strip(),
            address        = request.POST.get('address', '').strip(),
            medical_history= request.POST.get('medical_history', '').strip(),
        )
        messages.success(request, 'Donor registered successfully!')
        return redirect('/donors/')
    return render(request, 'donors/add.html')

@login_required
def donor_detail(request, did):
    if request.user.role not in DONOR_VIEW_ROLES:
        return redirect('/patient-portal/' if request.user.role == 'patient' else '/')
    donor = get_object_or_404(Donor, donor_id=did)
    donations = donor.donation_set.all().order_by('-donation_date')
    return render(request, 'donors/detail.html', {'donor': donor, 'donations': donations})

@login_required
def edit_donor(request, did):
    if request.user.role not in DONOR_EDIT_ROLES:
        messages.error(request, 'Access denied!')
        return redirect('/')
    donor = get_object_or_404(Donor, donor_id=did)
    if request.method == 'POST':
        donor.full_name       = request.POST.get('full_name', donor.full_name)
        donor.phone           = request.POST.get('phone', donor.phone)
        donor.email           = request.POST.get('email', donor.email)
        donor.address         = request.POST.get('address', donor.address)
        donor.medical_history = request.POST.get('medical_history', donor.medical_history)
        donor.save()
        messages.success(request, 'Donor updated successfully!')
        return redirect(f'/donors/{did}/')
    return render(request, 'donors/edit.html', {'donor': donor})

@login_required
def check_eligibility(request, did):
    if request.user.role not in DONOR_VIEW_ROLES:
        return redirect('/')
    donor = get_object_or_404(Donor, donor_id=did)
    return render(request, 'donors/eligibility.html', {'donor': donor})
