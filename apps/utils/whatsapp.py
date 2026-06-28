# apps/utils/whatsapp.py
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def send_whatsapp_message(to_phone, message_body):
    
    # Read credentials safely from environment variables set in Railway
    ACCESS_TOKEN = getattr(settings, "WHATSAPP_ACCESS_TOKEN", None)
    PHONE_NUMBER_ID = getattr(settings, "WHATSAPP_PHONE_NUMBER_ID", None)
    
    # Fallback for local development or sandbox staging before credentials are set
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        logger.warning(f"WhatsApp API credentials missing. Simulating outbound text to +{to_phone}: '{message_body}'")
        return False

    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message_body
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response_data = response.json()
        
        if response.status_code == 200:
            logger.info(f"WhatsApp message delivered successfully to +{to_phone}")
            return True
        else:
            logger.error(f"Meta API Error ({response.status_code}): {response_data}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to Meta Graph API network: {str(e)}")
        return False