from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect


def home(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    if request.user.role == 'patient':
        return redirect('/patient-portal/')
    return redirect('/dashboard/')


urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', home),
    path('accounts/',      include('accounts.urls')),
    path('dashboard/',     include('dashboard.urls')),
    path('donors/',        include('donors.urls')),
    path('donations/',     include('donations.urls')),
    path('inventory/',     include('inventory.urls')),
    path('patients/',      include('patients.urls')),
    path('requests/',      include('blood_requests.urls')),
    path('reports/',       include('reports.urls')),
    path('patient-portal/', include('patients.portal_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
