# apps/consultations/urls.py
from django.urls import path
from . import views

app_name = 'consultations'  

urlpatterns = [
    path('log-case/', views.ConsultationCreateView.as_view(), name='consultation-log-case'),
    path('webhooks/whatsapp/', views.WhatsAppWebhookView.as_view(), name='whatsapp-webhook'),
    path('webhooks/ussd/', views.USSDWebhookView.as_view(), name='ussd-webhook'),
]