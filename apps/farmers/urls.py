# apps/farmers/urls.py
from django.urls import path
import apps.farmers.views  

app_name = 'farmers'

urlpatterns = [
    path('identify/', apps.farmers.views.FarmerIdentifyView.as_view(), name='farmer-identify'),
    path('update/', apps.farmers.views.FarmerUpdateView.as_view(), name='farmer-update'),
]