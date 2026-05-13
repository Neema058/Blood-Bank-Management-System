@echo off
title Blood Bank - RECEPTIONIST (Port 8002)
echo ==========================================
echo   Blood Bank - Receptionist Panel
echo   URL: http://127.0.0.1:8002
echo   Login: reception / rec123
echo ==========================================
set DJANGO_PORT=8002
python manage.py runserver 8002
pause
