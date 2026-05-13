from django.urls import path
from . import views

urlpatterns = [
    path('',           views.donation_list,   name='donation_list'),
    path('add/',       views.add_donation,    name='add_donation'),
    path('<int:did>/', views.donation_detail, name='donation_detail'),
]
