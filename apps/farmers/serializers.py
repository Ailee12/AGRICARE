# apps/farmers/serializers.py
from rest_framework import serializers
from apps.farmers.models import Farmer

class FarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmer
        fields = [
            'id', 
            'phone_number', 
            'preferred_language', 
            'flock_size', 
            'location', 
            'onboarding_completed',
            'consent_accepted'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_phone_number(self, value):
        
        clean_value = value.strip()
        if not clean_value.startswith('+'):
            raise serializers.ValidationError(
                "Phone number must include an international country code prefix (e.g., +234)."
            )
        return clean_value