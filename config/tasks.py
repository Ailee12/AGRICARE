import time
from celery import shared_task

@shared_task
def simulate_poultry_ai_processing(farmer_name):
    print(f"🤖 Starting heavy AI image analysis for {farmer_name}...")
    time.sleep(5)  # Simulate a 5-second heavy calculation delay
    print(f"✅ AI Analysis complete! Advice sent to {farmer_name}.")
    return f"Success for {farmer_name}"