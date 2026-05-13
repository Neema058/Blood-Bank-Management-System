from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Donation
from donors.models import Donor
from inventory.models import BloodUnit
import datetime

# Only admin and lab_technician can record/view donations
DONATION_ROLES = ('admin', 'lab_technician')

@login_required
def donation_list(request):
    if request.user.role not in DONATION_ROLES:
        if request.user.role == 'patient':
            return redirect('/patient-portal/')
        messages.error(request, 'Access denied! Only Admin and Lab Technician can view donations.')
        return redirect('/dashboard/')
    donations = Donation.objects.all().order_by('-donation_date')
    return render(request, 'donations/list.html', {'donations': donations})

@login_required
def add_donation(request):
    if request.user.role not in DONATION_ROLES:
        if request.user.role == 'patient':
            return redirect('/patient-portal/')
        messages.error(request, 'Access denied! Only Admin and Lab Technician can record donations.')
        return redirect('/dashboard/')
    donors = Donor.objects.filter(is_active=True).order_by('full_name')
    if request.method == 'POST':
        donor_id = request.POST.get('donor_id')
        donor = get_object_or_404(Donor, donor_id=donor_id)
        if not donor.is_eligible():
            messages.error(request, f'{donor.full_name} is not eligible yet. {donor.days_until_eligible()} days remaining.')
            return render(request, 'donations/add.html', {'donors': donors})
        hiv  = request.POST.get('hiv_test', 'pass')
        hepb = request.POST.get('hep_b_test', 'pass')
        hepc = request.POST.get('hep_c_test', 'pass')
        mal  = request.POST.get('malaria_test', 'pass')
        syph = request.POST.get('syphilis_test', 'pass')
        all_pass = all([hiv=='pass', hepb=='pass', hepc=='pass', mal=='pass', syph=='pass'])
        status = 'accepted' if all_pass else 'rejected'
        date_str = request.POST.get('donation_date', '')
        donation_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.date.today()

        donation = Donation.objects.create(
            donor         = donor,
            donation_date = donation_date,
            volume_ml     = request.POST.get('volume_ml', 450),
            blood_group   = donor.blood_group,
            hiv_test      = hiv,
            hep_b_test    = hepb,
            hep_c_test    = hepc,
            malaria_test  = mal,
            syphilis_test = syph,
            status        = status,
            recorded_by   = request.user,
            notes         = request.POST.get('notes', ''),
        )
        donor.last_donation = donation.donation_date
        donor.save()
        if status == 'accepted':
            exp_date = donation.donation_date + datetime.timedelta(days=35)
            BloodUnit.objects.create(
                donation       = donation,
                blood_group    = donor.blood_group,
                collected_date = donation.donation_date,
                expiry_date    = exp_date,
                status         = 'available',
            )
            messages.success(request, f'Donation recorded & added to inventory! Expiry: {exp_date}')
        else:
            messages.warning(request, 'Donation recorded but REJECTED due to failed tests. Not added to inventory.')
        return redirect('/donations/')
    return render(request, 'donations/add.html', {'donors': donors})

@login_required
def donation_detail(request, did):
    if request.user.role not in DONATION_ROLES:
        if request.user.role == 'patient':
            return redirect('/patient-portal/')
        messages.error(request, 'Access denied!')
        return redirect('/dashboard/')
    donation = get_object_or_404(Donation, id=did)
    return render(request, 'donations/detail.html', {'donation': donation})
