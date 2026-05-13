@echo off
title Blood Bank - LAB TECHNICIAN (Port 8001)
echo ==========================================
echo   Blood Bank - Lab Technician Panel
echo   URL: http://127.0.0.1:8001
echo   Login: labtech / lab123
echo ==========================================
set DJANGO_PORT=8001
python manage.py runserver 8001
pause
