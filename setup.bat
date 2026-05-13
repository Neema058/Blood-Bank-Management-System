@echo off
echo =====================================================
echo   Blood Bank Management System - Setup
echo =====================================================
echo.
echo [1/5] Installing packages...
pip install Django==4.2.7
pip install PyMySQL==1.1.0
pip install Pillow==10.4.0
pip install reportlab==4.2.2
echo.
echo [2/5] Running database migrations...
python manage.py makemigrations accounts
python manage.py makemigrations donors
python manage.py makemigrations donations
python manage.py makemigrations inventory
python manage.py makemigrations patients
python manage.py makemigrations blood_requests
python manage.py makemigrations reports
python manage.py makemigrations dashboard
python manage.py migrate
echo.
echo [3/5] Creating Admin account...
python manage.py shell -c "from accounts.models import CustomUser; CustomUser.objects.filter(username='admin').exists() or CustomUser.objects.create_superuser(username='admin', password='admin123', role='admin', first_name='Admin', last_name='User')"
echo [4/5] Creating Lab Technician account...
python manage.py shell -c "from accounts.models import CustomUser; CustomUser.objects.filter(username='labtech').exists() or CustomUser.objects.create_user(username='labtech', password='lab123', role='lab_technician', first_name='Lab', last_name='Technician')"
echo [5/5] Creating Receptionist account...
python manage.py shell -c "from accounts.models import CustomUser; CustomUser.objects.filter(username='reception').exists() or CustomUser.objects.create_user(username='reception', password='rec123', role='receptionist', first_name='Reception', last_name='Staff')"
echo.
echo =====================================================
echo   SETUP COMPLETE!
echo.
echo   Ek saath multiple users kholne ke liye:
echo   Har role ke liye ALAG .bat file chalayein:
echo.
echo   Admin       : run_admin.bat      (port 8000)
echo   Lab Tech    : run_labtech.bat    (port 8001)
echo   Receptionist: run_reception.bat  (port 8002)
echo   Patient     : run_patient.bat    (port 8003)
echo.
echo   Patient register: http://127.0.0.1:8003/accounts/register/
echo =====================================================
pause
