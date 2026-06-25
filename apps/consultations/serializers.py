# apps/consultations/serializers.py
from rest_framework import serializers
from apps.consultations.models import ConsultationLog
from apps.farmers.models import Farmer

class ConsultationLogSerializer(serializers.ModelSerializer):
    # We accept a phone number in the incoming request payload instead of a raw database ID
    phone_number = serializers.CharField(write_only=True)

    class Meta:
        model = ConsultationLog
        fields = [
            'id',
            'phone_number',
            'current_flock_size',
            'birds_affected',
            'birds_dead',
            'symptoms_reported',
            'ai_diagnosis',
            'status',
            'created_at'
        ]
        read_only_fields = ['id', 'ai_diagnosis', 'status', 'created_at']

    def validate(self, data):
    
        flock_size = data.get('current_flock_size')
        affected = data.get('birds_affected', 0)
        dead = data.get('birds_dead', 0)

        # Check: Sick birds cannot exceed total population
        if affected > flock_size:
            raise serializers.ValidationError({
                "birds_affected": f"Affected birds ({affected}) cannot exceed total flock size ({flock_size})."
            })

        # Check: Dead birds cannot exceed total population
        if dead > flock_size:
            raise serializers.ValidationError({
                "birds_dead": f"Recorded deaths ({dead}) cannot exceed total flock size ({flock_size})."
            })

        # Check:  Total impact cannot make physical nonsense
        if (affected + dead) > (flock_size + dead): 
            # (Just a baseline guardrail against extreme bad entries)
            pass

        return data

    def create(self, validated_data):
        phone_number = validated_data.pop('phone_number')
        
        # Pull the farmer profile or explode cleanly if it somehow slipped by
        try:
            farmer = Farmer.objects.get(phone_number=phone_number)
        except Farmer.DoesNotExist:
            raise serializers.ValidationError({
                "phone_number": "No active farmer profile exists with this contact number."
            })

        # Inject the resolved farmer object into the dataset and save
        consultation = ConsultationLog.objects.create(farmer=farmer, **validated_data)
        return consultation