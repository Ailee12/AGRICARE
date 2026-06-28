# apps/consultations/views.py
from rest_framework.views import APIView
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from apps.farmers.models import Farmer
from apps.consultations.serializers import ConsultationLogSerializer
from django.core.cache import cache
import logging
from apps.consultations.models import ConsultationLog
from apps.consultations.tasks import process_ussd_consultation
from apps.consultations.tasks import process_whatsapp_message

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
                
                # Trigger Celery task 
                if phone_number and message_text:

                    # Look up the farmer if they exist
                    farmer_obj = Farmer.objects.filter(phone_number=phone_number).first()

                    #Log it into the database right away
                    case_log = ConsultationLog.objects.create(
                        farmer=farmer_obj,
                        phone_number=phone_number,
                        channel="WHATSAPP",
                        raw_query=message_text,
                        language="english", # Default for WhatsApp entry
                        status="pending"
                    )
                    
                    # Fire off the updated shared task using the entry ID
                    process_whatsapp_message.delay(case_log.id)
                
                print(f"Webhook parsed text from +{phone_number}: '{message_text}'")
                
        except (IndexError, KeyError, TypeError):
            # Pass silently if the payload layout doesn't match a message text structure
            pass
            
        # Return an immediate 200 OK to Meta
        # within 5 seconds so they don't loop duplicate retries on your server.
        return Response({"status": "received"}, status=status.HTTP_200_OK)
    

logger = logging.getLogger(__name__)

class USSDWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            # Capture Form Parameters from Africa's Talking
            session_id = request.data.get("sessionId")
            phone_number = request.data.get("phoneNumber")
            text = request.data.get("text", "")

            logger.info(f"USSD Interaction — Session: {session_id} | Text: '{text}'")

            session_key = f"ussd_{session_id}"
            
            # --- POTENTIAL CRASH POINT 1: CACHE ---
            try:
                session_state = cache.get(session_key)
            except Exception as cache_err:
                return HttpResponse(f"END Server Configuration Error (Cache): {str(cache_err)}", content_type="text/plain")

            # State Initialization (Brand New Dial-in)
            if not session_state:
                try:
                    # --- POTENTIAL CRASH POINT 2: DATABASE LOOKUP ---
                    farmer = Farmer.objects.get(phone_number=phone_number)
                    first_name = farmer.name.split()[0]
                    welcome_msg = f"CON Welcome back, {first_name} to AgroCare.\n"
                except Farmer.DoesNotExist:
                    welcome_msg = "CON Welcome to AgroCare.\n"
                except Exception as db_lookup_err:
                    return HttpResponse(f"END Server Configuration Error (DB Query): {str(db_lookup_err)}", content_type="text/plain")

                session_state = {
                    "current_menu": "welcome",
                    "language": None,
                    "symptoms": "",
                    "welcome_msg": welcome_msg
                }
                cache.set(session_key, session_state, timeout=300)

            user_inputs = text.split("*") if text else []
            response_text = ""

            # Dynamic Menu State Machine Engine
            if not text:
                response_text = f"{session_state['welcome_msg']}Select Language:\n1. English\n2. Hausa\n3. Yoruba"
                session_state["current_menu"] = "language_selection"

            elif len(user_inputs) == 1:
                lang_choice = user_inputs[0]
                lang_map = {"1": "english", "2": "hausa", "3": "yoruba"}
                chosen_lang = lang_map.get(lang_choice, "english")
                
                session_state["language"] = chosen_lang
                session_state["current_menu"] = "symptom_input"
                
                if chosen_lang == "hausa":
                    response_text = "CON Da fatan za a rubuta alamomin cutar kaji a takaice:"
                elif chosen_lang == "yoruba":
                    response_text = "CON Jọ̀wọ́ kọ àwọn àmì àìsàn àwọn adìẹ rẹ ní ṣókí níhìn-ín:"
                else:
                    response_text = "CON Please briefly type your poultry symptoms below:"

            elif len(user_inputs) == 2:
                raw_symptoms = user_inputs[-1].strip()
                session_state["symptoms"] = raw_symptoms
                session_state["current_menu"] = "complete"

                try:
                    farmer_obj = Farmer.objects.filter(phone_number=phone_number).first()
                    
                    case_log = ConsultationLog.objects.create(
                        farmer=farmer_obj,
                        phone_number=phone_number,
                        channel="USSD",
                        raw_query=raw_symptoms,
                        language=session_state["language"],
                        status="pending" 
                    )

                    process_ussd_consultation.delay(case_log.id)
                    logger.info(f"Saved Consultation Log ID {case_log.id}. Dispatched to background queue.")
                    
                except Exception as db_err:
                    logger.error(f"Failed to compile production database entry: {str(db_err)}")

                if session_state["language"] == "hausa":
                    response_text = "END Mun gode! AgroCare AI yana nazarin bayanan ku. Za a aiko muku da sakon shawara ta SMS ba da jimawa ba."
                elif session_state["language"] == "yoruba":
                    response_text = "END O ṣeun! AgroCare AI ń yẹ ẹjọ́ rẹ wò. Wọn yóò kọ̀wé ránṣẹ́ sí ọ lórí tẹlifóònù rẹ láìpẹ́."
                else:
                    response_text = "END Thank you! AgroCare AI is evaluating your case. An advisory summary will be sent to your phone via SMS shortly."

                cache.delete(session_key)

            if session_state["current_menu"] != "complete":
                cache.set(session_key, session_state, timeout=300)

            return HttpResponse(response_text, content_type="text/plain")

        except Exception as general_err:
            # If absolutely anything else breaks, hijack the response format 
            # and render the Python text traceback directly onto the Africa's Talking screen
            return HttpResponse(f"END Global View Crash: {str(general_err)}", content_type="text/plain")
