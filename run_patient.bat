@echo off
title Blood Bank - PATIENT Portal (Port 8003)
echo ==========================================
echo   Blood Bank - Patient Portal
echo   URL: http://127.0.0.1:8003
echo   Register: http://127.0.0.1:8003/accounts/register/
echo ==========================================
set DJANGO_PORT=8003
python manage.py runserver 8003
pause
