# apps/consultations/tasks.py
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(name="apps.consultations.tasks.process_whatsapp_message")
def process_whatsapp_message(phone_number, message_text):
   
    logger.info(f"Celery worker picked up message from +{phone_number}")
    
    try:
        # FUTURE FARMER LOOKUP LOGIC:
        # This is where your 'identify_or_create' logic will run:
        # farmer, created = Farmer.objects.get_or_create(phone_number=phone_number)
        
        # Setting up the Echo String
        echo_response = f"AgroCare Confirmation — You said: '{message_text}'"
        
        logger.info(f"Echo text prepared: '{echo_response}'")
        
        # 📤 FUTURE OUTBOUND TELEMETRY:
        # This is where your Milestone 2, Step 6 'send_whatsapp_message' utility will be called:
        # send_whatsapp_message(phone_number, echo_response)
        
        return f"Processed echo for +{phone_number}"
        
    except Exception as e:
        logger.error(f"Error processing background task: {str(e)}")
        return f"Failure: {str(e)}"