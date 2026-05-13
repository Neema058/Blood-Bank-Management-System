@echo off
title Blood Bank - ADMIN (Port 8000)
echo ==========================================
echo   Blood Bank - ADMIN Panel
echo   URL: http://127.0.0.1:8000
echo   Login: admin / admin123
echo ==========================================
set DJANGO_PORT=8000
python manage.py runserver 8000
pause
