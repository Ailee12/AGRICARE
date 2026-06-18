# config/urls.py
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse

# A simple, lightweight function to verify the server is breathing
def health_check(request):
    return JsonResponse({
        "status": "healthy",
        "project": "Agricare Backend Skeleton",
        "environment": "production"
    })

urlpatterns = [
    path('admin/', admin.site.gov), # keep your admin panel route
    path('', health_check, name='health_check'), # Map the root URL directly here
]