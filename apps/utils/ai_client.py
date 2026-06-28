# apps/utils/ai_client.py
import os
import logging
import requests

logger = logging.getLogger(__name__)

def consult_agrocare_ai(farmer_text: str, language_code: str) -> dict:
    # Using your exact live production domain on Railway
    AI_ENGINE_URL = os.getenv("AI_ENGINE_URL")
    API_KEY = os.getenv("AGRICARE_API_KEY")

    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": farmer_text,
        "history": None  
    }

    try:
        logger.info(f"🧠 Sending text to live AI Engine: '{farmer_text}'")
        response = requests.post(AI_ENGINE_URL, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        
        logger.error(f"AI Engine error {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to reach AI Engine on Railway: {str(e)}")
        
    # Fallback to keep the app running if your AI service ever goes offline
    return {
        "answer": "Please isolate the sick birds immediately and give them clean water while our vets review your case.",
        "urgency": "GREEN",
        "escalate": False,
        "disease_name": "Under Review"
    }