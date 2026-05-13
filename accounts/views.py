from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from patients.models import Patient


def login_view(request):
    if request.user.is_authenticated:
        return _role_redirect(request.user)
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return _role_redirect(user)
        messages.error(request, 'Invalid username or password!')
    return render(request, 'accounts/login.html')


def _role_redirect(user):
    """Redirect based on user role after login."""
    if user.role == 'patient':
        return redirect('/patient-portal/')
    return redirect('/dashboard/')


@login_required
def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')


@login_required
def change_password(request):
    if request.method == 'POST':
        old = request.POST.get('old_password')
        new = request.POST.get('new_password')
        con = request.POST.get('confirm_password')
        if not request.user.check_password(old):
            messages.error(request, 'Current password is incorrect!')
        elif new != con:
            messages.error(request, 'New passwords do not match!')
        elif len(new) < 6:
            messages.error(request, 'Password must be at least 6 characters!')
        else:
            request.user.set_password(new)
            request.user.save()
            messages.success(request, 'Password changed! Please login again.')
            return redirect('/accounts/login/')
    return render(request, 'accounts/change_password.html')


@login_required
def manage_users(request):
    if request.user.role != 'admin':
        messages.error(request, 'Admin access required!')
        return redirect('/')
    users = CustomUser.objects.all().order_by('role', 'first_name')
    return render(request, 'accounts/users.html', {'users': users})


@login_required
def add_user(request):
    if request.user.role != 'admin':
        return redirect('/')
    patients = Patient.objects.all().order_by('full_name')
    if request.method == 'POST':
        uname  = request.POST.get('username', '').strip()
        fname  = request.POST.get('first_name', '').strip()
        lname  = request.POST.get('last_name', '').strip()
        role   = request.POST.get('role', 'receptionist')
        phone  = request.POST.get('phone', '').strip()
        pwd    = request.POST.get('password', '')
        pat_id = request.POST.get('patient_id', '')

        if CustomUser.objects.filter(username=uname).exists():
            messages.error(request, 'Username already exists!')
        else:
            user = CustomUser.objects.create_user(
                username=uname, first_name=fname, last_name=lname,
                password=pwd, role=role, phone=phone
            )
            if role == 'patient' and pat_id:
                user.patient_id = int(pat_id)
                user.save()
            messages.success(request, f'User {fname} {lname} added successfully!')
            return redirect('/accounts/users/')
    return render(request, 'accounts/add_user.html', {'patients': patients})


@login_required
def toggle_user(request, uid):
    if request.user.role != 'admin':
        return redirect('/')
    u = get_object_or_404(CustomUser, id=uid)
    if u == request.user:
        messages.error(request, 'You cannot deactivate your own account!')
    else:
        u.is_active = not u.is_active
        u.save()
        messages.success(request, f'User {"activated" if u.is_active else "deactivated"}!')
    return redirect('/accounts/users/')


def patient_register(request):
    """Public page — patient khud apna account bana sakta hai."""
    if request.user.is_authenticated:
        return _role_redirect(request.user)

    from patients.models import Patient

    if request.method == 'POST':
        # --- Personal info ---
        fname    = request.POST.get('first_name', '').strip()
        lname    = request.POST.get('last_name', '').strip()
        uname    = request.POST.get('username', '').strip()
        pwd      = request.POST.get('password', '')
        cpwd     = request.POST.get('confirm_password', '')
        phone    = request.POST.get('phone', '').strip()

        # --- Patient record info ---
        full_name    = request.POST.get('full_name', '').strip() or f"{fname} {lname}".strip()
        age          = request.POST.get('age', '')
        gender       = request.POST.get('gender', 'M')
        blood_group  = request.POST.get('blood_group', '')
        hospital     = request.POST.get('hospital_name', '').strip() or 'Self / Home'
        doctor       = request.POST.get('doctor_name', '').strip()
        contact      = phone
        address      = request.POST.get('address', '').strip()

        # Validation
        if not uname or not pwd or not fname or not blood_group:
            messages.error(request, 'Please fill all required fields.')
        elif pwd != cpwd:
            messages.error(request, 'Passwords do not match!')
        elif len(pwd) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        elif CustomUser.objects.filter(username=uname).exists():
            messages.error(request, f'Username "{uname}" already taken. Choose another.')
        elif not age or not age.isdigit() or int(age) < 1 or int(age) > 120:
            messages.error(request, 'Please enter a valid age.')
        else:
            # Create patient record
            patient = Patient.objects.create(
                full_name    = full_name,
                age          = int(age),
                gender       = gender,
                blood_group  = blood_group,
                hospital_name= hospital,
                doctor_name  = doctor,
                contact      = contact,
                address      = address,
            )
            # Create user account linked to patient
            user = CustomUser.objects.create_user(
                username   = uname,
                first_name = fname,
                last_name  = lname,
                password   = pwd,
                role       = 'patient',
                phone      = phone,
                patient_id = patient.id,
            )
            messages.success(request, f'Account created! Welcome {fname}. Please log in.')
            return redirect('/accounts/login/')

    return render(request, 'accounts/patient_register.html')
