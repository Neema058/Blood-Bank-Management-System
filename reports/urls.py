from django.urls import path
from . import views

urlpatterns = [
    path('',          views.reports_home,     name='reports_home'),
    path('donors/',   views.donor_report,     name='donor_report'),
    path('inventory/',views.inventory_report, name='inventory_report'),
    path('requests/', views.request_report,   name='request_report'),
    path('monthly/',  views.monthly_report,   name='monthly_report'),
]
