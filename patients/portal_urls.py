from django.urls import path
from . import views

urlpatterns = [
    path('', views.patient_portal, name='patient_portal'),
]
