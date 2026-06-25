# apps/farmers/urls.py
from django.urls import path
from apps.farmers.views import FarmerIdentifyView

app_name = 'farmers'

urlpatterns = [
    path('identify/', FarmerIdentifyView.as_view(), name='farmer-identify'),
]