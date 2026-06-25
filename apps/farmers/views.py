from django.shortcuts import render

# apps/farmers/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.farmers.models import Farmer
from apps.farmers.serializers import FarmerSerializer

class FarmerIdentifyView(APIView):
    """
    API entry anchor for inbound webhooks. 
    Checks if a phone number exists, initializes a profile if it doesn't, 
    and passes routing states to steer the automated WhatsApp conversation.
    """
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        
        if not phone_number:
            return Response(
                {"error": "The 'phone_number' field is explicitly required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # High-speed atomic lookup or creation
        farmer, created = Farmer.objects.get_or_create(
            phone_number=phone_number
        )
        
        serializer = FarmerSerializer(farmer)
        
        # Build state metrics to guide the conversation tree logic
        response_data = {
            "is_new_user": created,
            "consent_accepted": farmer.consent_accepted,
            "onboarding_completed": farmer.onboarding_completed,
            "farmer_profile": serializer.data
        }
        
        return Response(
            response_data, 
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
