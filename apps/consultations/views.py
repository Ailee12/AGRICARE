# apps/consultations/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.farmers.models import Farmer
from apps.consultations.serializers import ConsultationLogSerializer

class ConsultationCreateView(APIView):
    
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        
        if not phone_number:
            return Response(
                {"error": "The 'phone_number' field is required to log a case."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Verify the farmer profile actually exists
        try:
            farmer = Farmer.objects.get(phone_number=phone_number)
        except Farmer.DoesNotExist:
            return Response(
                {"error": "No profile found. Farmer must be initialized via the identification gateway first."}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Enforce NDPR Privacy Consent Compliance
        if not farmer.consent_accepted:
            return Response(
                {
                    "error": "Privacy consent missing.",
                    "action_required": "PROMPT_PRIVACY_DISCLOSURE"
                }, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Serialize incoming data
        serializer = ConsultationLogSerializer(data=request.data)
        if serializer.is_valid():
            # The serializer's create method will link it to the farmer automatically
            consultation = serializer.save()
            
            # Future Step: This is exactly where we will drop our Celery task 
            # to offload 'consultation.id' to our background AI analyzer engine.
            
            return Response({
                "message": "Consultation case logged successfully. Processing diagnostic telemetry.",
                "case_id": consultation.id,
                "status": consultation.status
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)