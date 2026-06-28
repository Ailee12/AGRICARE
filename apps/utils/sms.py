import os
import africastalking
import requests


def send_outbound_sms(to_phone, message_body):

    USERNAME = os.getenv("AT_USERNAME", "sandbox")
    API_KEY = os.getenv("AT_API_KEY", "")
    
    if not API_KEY:
        logger.warning(f"SMS credentials dropped. Simulating SMS text to {to_phone}: '{message_body}'")
        return False

    # --- FIXED: Dynamically route sandbox requests vs live production requests ---
    if USERNAME.lower() == "sandbox":
        url = "https://api.sandbox.africastalking.com/version1/messaging"
    else:
        url = "https://api.africastalking.com/version1/messaging"

    headers = {
        "ApiKey": API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "username": USERNAME,
        "to": to_phone,
        "message": message_body
    }

    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        # Note: Africa's Talking replies with a 201 Created status code on successful queue
        if response.status_code == 201:
            logger.info(f"Outbound text payload deployed safely to {to_phone}")
            return True
        logger.error(f"Telecom grid rejection ({response.status_code}): {response.text}")
        return False
    except Exception as e:
        logger.error(f"SMS Gateway network outage: {str(e)}")
        return False
