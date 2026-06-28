# apps/consultations/tasks.py
from celery import shared_task
import logging
from apps.consultations.models import ConsultationLog
from apps.utils.ai_client import consult_agrocare_ai
from apps.utils.whatsapp import send_whatsapp_message
from apps.utils.sms import send_outbound_sms



logger = logging.getLogger(__name__)

@shared_task(name="apps.consultations.tasks.process_whatsapp_message")
def process_whatsapp_message(case_id):
   
    try:
        case = ConsultationLog.objects.get(id=case_id)
        
        # INJECTING MILESTONE 4 SIMULATION
        ai_diagnosis = consult_agrocare_ai(case.raw_query,case.language)

        ai_text = ai_diagnosis.get("answer", "")
        urgency_level = ai_diagnosis.get("urgency", "GREEN")
        should_escalate = ai_diagnosis.get("escalate", False)
        detected_disease = ai_diagnosis.get("disease_name", "Condition Evaluated")

        case.ai_response = ai_text
        case.detected_disease_name = detected_disease
        
        # 3. Handle dashboard emergency tracking states
        if should_escalate or urgency_level in ["RED", "HIGH"]:
            case.status = "escalated"
            case.save()
            delivery_msg = f"AGROCARE ALERT ({detected_disease}):\n{ai_text}\n\nA vet representative will call you directly."
        else:
            case.status = "processed"
            case.save()
            delivery_msg = f"AgroCare AI Advice for {detected_disease}:\n{ai_text}"

        # 4. Use your existing WhatsApp utility function to reply to their phone
        send_whatsapp_message(case.phone_number, delivery_msg)
        return f"SUCCESS_WHATSAPP_{case_id}"
    
    except ConsultationLog.DoesNotExist:
        return "FAILURE"
    


@shared_task(name="apps.consultations.tasks.process_ussd_consultation")
def process_ussd_consultation(case_id):
    """
    Asynchronous Analysis Engine.
    Grabs database logs, runs AI diagnostic logic, checks for high-risk outbreaks,
    and deploys real-time warning frameworks or default advice strings.
    """
    try:
        case = ConsultationLog.objects.get(id=case_id)
        logger.info(f"Worker processing logged case ID {case.id} — Symptoms: '{case.raw_query}'")
        
        # 🧠 INJECTING MILESTONE 4 SIMULATION
        ai_diagnosis = consult_agrocare_ai(case.raw_query,case.language)

        ai_text = ai_diagnosis.get("answer", "")
        urgency_level = ai_diagnosis.get("urgency", "GREEN")
        should_escalate = ai_diagnosis.get("escalate", False)
        detected_disease = ai_diagnosis.get("disease_name", "Condition Evaluated")

        case.ai_response = ai_text
        case.detected_disease_name = detected_disease
        
        # 3. Handle dashboard emergency tracking states
        if should_escalate or urgency_level in ["RED", "HIGH"]:
            case.status = "escalated"
            case.save()
            delivery_msg = f"AGROCARE ALERT ({detected_disease}):\n{ai_text}\n\nA vet representative will call you directly."
        else:
            case.status = "processed"
            case.save()
            delivery_msg = f"AgroCare AI Advice for {detected_disease}:\n{ai_text}"

        # 4. Use your existing WhatsApp utility function to reply to their phone
        send_outbound_sms(case.phone_number, delivery_msg)
        return f"SUCCESS_USSD_{case_id}"
    
    except ConsultationLog.DoesNotExist:
        return "FAILURE"
    

@shared_task(name="apps.consultations.tasks.process_farmer_case")
def process_farmer_case(case_id):
    
    try:
        # 1. Pull the case details from your PostgreSQL Database
        case = ConsultationLog.objects.get(id=case_id)
        
        # 2. Get the diagnostic response from your live Railway AI service
        ai_result = consult_agrocare_ai(case.raw_query, case.language)
        
        ai_text = ai_result.get("answer")
        urgency_level = ai_result.get("urgency", "GREEN")
        should_escalate = ai_result.get("escalate", False)
        detected_disease = ai_result.get("disease_name", "Condition Evaluated")

        # 3. Update the permanent PostgreSQL database tracking record
        case.ai_response = ai_text
        case.detected_disease_name = detected_disease

        # Emergency Interception System (Check for critical outbreaks)
        if should_escalate or urgency_level in ["RED", "HIGH"]:
            case.status = "escalated"
            case.save()
            delivery_msg = f"AGROCARE ALERT ({detected_disease}):\n{ai_text}\n\nA vet representative will call you immediately."
        else:
            case.status = "processed"
            case.save()
            delivery_msg = f"AgroCare AI Advice for {detected_disease}:\n{ai_text}"

        # 4. Smart Router: Send the message back via the channels they used
        if case.channel == "USSD":
            send_outbound_sms(case.phone_number, delivery_msg)
        elif case.channel == "WHATSAPP":
            send_whatsapp_message(case.phone_number, delivery_msg)
        
        return f"SUCCESS_LOG_{case_id}"

    except ConsultationLog.DoesNotExist:
        logger.error(f" Case ID {case_id} not found in database registry.")
        return "FAILURE"