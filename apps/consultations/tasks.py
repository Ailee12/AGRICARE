# apps/consultations/tasks.py
import os
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
        
        detected_lang = case.farmer.preferred_language if (case.farmer and case.farmer.preferred_language) else "en"
        ai_diagnosis = consult_agrocare_ai(case.symptoms_reported, detected_lang)

        ai_text = ai_diagnosis.get("answer", "")
        urgency_level = ai_diagnosis.get("urgency", "GREEN")
        should_escalate = ai_diagnosis.get("escalate", False)
        detected_disease = ai_diagnosis.get("disease_name", "Condition Evaluated")

        # --- FIXED: Use actual model fields ---
        case.ai_diagnosis = f"[{detected_disease}] | Urgency: {urgency_level} | {ai_text}"
        
        if should_escalate or urgency_level in ["RED", "HIGH"]:
            case.status = "escalated"
            case.save()
            delivery_msg = f"AGROCARE ALERT ({detected_disease}):\n{ai_text}\n\nA vet representative will call you directly."
        else:
            case.status = "processed"
            case.save()
            delivery_msg = f"AgroCare AI Advice for {detected_disease}:\n{ai_text}"

        # --- FIXED: Use case.farmer.phone_number ---
        send_whatsapp_message(case.farmer.phone_number, delivery_msg)
        return f"SUCCESS_WHATSAPP_{case_id}"
    
    except ConsultationLog.DoesNotExist:
        logger.error(f"WhatsApp task received missing log ID: {case_id}")
        return "FAILURE"
    except Exception as err:
        logger.error(f"WhatsApp task breakdown for case {case_id}: {str(err)}")
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
        logger.info(f"Worker processing logged case ID {case.id} — Symptoms: '{case.symptoms_reported}'")
        
        detected_lang = case.farmer.preferred_language if (case.farmer and case.farmer.preferred_language) else "en"
        
        ai_diagnosis = consult_agrocare_ai(case.symptoms_reported, detected_lang)

        ai_text = ai_diagnosis.get("answer", "")
        urgency_level = ai_diagnosis.get("urgency", "GREEN")
        should_escalate = ai_diagnosis.get("escalate", False)
        detected_disease = ai_diagnosis.get("disease_name", "Condition Evaluated")

        case.ai_diagnosis = f"[{detected_disease}] | Urgency: {urgency_level} | {ai_text}"
        
        if should_escalate or urgency_level in ["RED", "HIGH"]:
            case.status = "escalated"
            case.save()
            delivery_msg = f"AGROCARE ALERT ({detected_disease}):\n{ai_text}\n\nA vet representative will call you directly."
        else:
            case.status = "processed"
            case.save()
            delivery_msg = f"AgroCare AI Advice for {detected_disease}:\n{ai_text}"

        send_outbound_sms(case.farmer.phone_number, delivery_msg)
        return f"SUCCESS_USSD_{case_id}"
    
    except ConsultationLog.DoesNotExist:
        logger.error(f"Task received missing consultation log target record ID: {case_id}")
        return "FAILURE"
    except Exception as general_err:
        logger.error(f"Task runtime execution breakdown for case {case_id}: {str(general_err)}")
        return "FAILURE"
    

@shared_task(name="apps.consultations.tasks.process_farmer_case")
def process_farmer_case(case_id):
    try:
        case = ConsultationLog.objects.get(id=case_id)
        
        # --- FIXED: Use relation language fallback ---
        detected_lang = case.farmer.preferred_language if (case.farmer and case.farmer.preferred_language) else "en"
        ai_result = consult_agrocare_ai(case.symptoms_reported, detected_lang)
        
        ai_text = ai_result.get("answer", "")
        urgency_level = ai_result.get("urgency", "GREEN")
        should_escalate = ai_result.get("escalate", False)
        detected_disease = ai_result.get("disease_name", "Condition Evaluated")

        # --- FIXED: Use actual model fields ---
        case.ai_diagnosis = f"[{detected_disease}] | Urgency: {urgency_level} | {ai_text}"

        if should_escalate or urgency_level in ["RED", "HIGH"]:
            case.status = "escalated"
            case.save()
            delivery_msg = f"AGROCARE ALERT ({detected_disease}):\n{ai_text}\n\nA vet representative will call you immediately."
        else:
            case.status = "processed"
            case.save()
            delivery_msg = f"AgroCare AI Advice for {detected_disease}:\n{ai_text}"

        # --- FIXED: Use case.farmer.phone_number ---
        if case.channel == "USSD":
            send_outbound_sms(case.farmer.phone_number, delivery_msg)
        elif case.channel == "WHATSAPP":
            send_whatsapp_message(case.farmer.phone_number, delivery_msg)
        
        return f"SUCCESS_LOG_{case_id}"

    except ConsultationLog.DoesNotExist:
        logger.error(f"Case ID {case_id} not found in database registry.")
        return "FAILURE"
    except Exception as general_err:
        logger.error(f"General task breakdown for case {case_id}: {str(general_err)}")
        return "FAILURE"
