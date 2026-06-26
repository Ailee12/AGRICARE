# apps/consultations/views.py
from rest_framework.views import APIView
from django.http import HttpResponse
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
    

class WhatsAppWebhookView(APIView):
    """
    Gateway endpoint for Meta WhatsApp communications.
    Handles the verification handshake (GET) and incoming message traffic (POST).
    """
    
    def get(self, request, *args, **kwargs):
        
        # Secret password string .
        # We will type this exact same string into the Meta Dashboard.
        VERIFY_TOKEN = "agrocare_secret_token_2026"
        
        mode = request.query_params.get('hub.mode')
        token = request.query_params.get('hub.verify_token')
        challenge = request.query_params.get('hub.challenge')
        
        # Check if Meta's request matches our secret password token
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            # Return the raw challenge text as plain text with a 200 OK status
            return HttpResponse(challenge, content_type="text/plain", status=200)
            
        # If the tokens do not match, securely block the connection
        return HttpResponse("Verification token mismatch", status=403)

    def post(self, request, *args, **kwargs):
        
        payload = request.data
        
        try:
            # Navigating Meta's deeply nested JSON structure safely
            entry = payload.get('entry', [])[0]
            changes = entry.get('changes', [])[0]
            value = changes.get('value', {})
            messages = value.get('messages', [])
            
            if messages:
                message = messages[0]
                phone_number = message.get('from') # e.g., "2348012345678"
                message_text = message.get('text', {}).get('body', '').strip()
                
                # For Milestone 2 Step 5, we will trigger your Celery task here:
                # process_whatsapp_message.delay(phone_number, message_text)
                
                print(f"Webhook parsed text from +{phone_number}: '{message_text}'")
                
        except (IndexError, KeyError, TypeError):
            # Pass silently if the payload layout doesn't match a message text structure
            pass
            
        # Milestone 2 Step 4 Rule: Always return an immediate 200 OK to Meta
        # within 5 seconds so they don't loop duplicate retries on your server.
        return Response({"status": "received"}, status=status.HTTP_200_OK)