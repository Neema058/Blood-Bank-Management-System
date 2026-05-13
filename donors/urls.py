from django.urls import path
from . import views

urlpatterns = [
    path('',                    views.donor_list,       name='donor_list'),
    path('add/',                views.add_donor,        name='add_donor'),
    path('<int:did>/',          views.donor_detail,     name='donor_detail'),
    path('<int:did>/edit/',     views.edit_donor,       name='edit_donor'),
    path('<int:did>/eligibility/', views.check_eligibility, name='check_eligibility'),
]
