# apps/farmers/urls.py
from django.urls import path
from . import views

app_name = 'farmers'

urlpatterns = [
    path('identify/', views.FarmerIdentifyView.as_view(), name='farmer-identify'),
    path('update/', views.FarmerUpdateView.as_view(), name='farmer-update'),
]