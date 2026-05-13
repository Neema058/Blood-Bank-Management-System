from django.urls import path
from . import views

urlpatterns = [
    path('login/',              views.login_view,       name='login'),
    path('logout/',             views.logout_view,      name='logout'),
    path('register/',           views.patient_register, name='patient_register'),
    path('change-password/',    views.change_password,  name='change_password'),
    path('users/',              views.manage_users,     name='manage_users'),
    path('users/add/',          views.add_user,         name='add_user'),
    path('users/toggle/<int:uid>/', views.toggle_user,  name='toggle_user'),
]
