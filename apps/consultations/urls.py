# apps/consultations/urls.py
from django.urls import path
from apps.consultations.views import ConsultationCreateView

app_name = 'consultations'  

urlpatterns = [
    path('log-case/', ConsultationCreateView.as_view(), name='consultation-log-case'),
]