from django.urls import path
from . import views

urlpatterns = [
    path('',                  views.patient_list,   name='patient_list'),
    path('add/',              views.add_patient,    name='add_patient'),
    path('<int:pid>/',        views.patient_detail, name='patient_detail'),
    path('<int:pid>/edit/',   views.edit_patient,   name='edit_patient'),
]
