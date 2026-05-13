from django.urls import path
from . import views

urlpatterns = [
    path('',              views.request_list,   name='request_list'),
    path('add/',          views.add_request,    name='add_request'),
    path('<int:rid>/',    views.request_detail, name='request_detail'),
    path('<int:rid>/action/', views.approve_request, name='approve_request'),
]
