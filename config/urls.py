# config/urls.py
from django.contrib import admin
from django.urls import path,include
from django.http import JsonResponse

# A simple, lightweight function to verify the server is breathing
def health_check(request):
    return JsonResponse({
        "status": "healthy",
        "project": "Agricare Backend Skeleton",
        "environment": "production"
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', health_check, name='health_check'),
    path('api/v1/farmers/', include('apps.farmers.urls', namespace='farmers')),
]