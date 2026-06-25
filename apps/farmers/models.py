# apps/farmers/models.py
from django.db import models
from django.core.validators import MinValueValidator
from apps.core.models import BaseModel  

class Farmer(BaseModel):
    """
    Core profile model for AgroCare farmers.
    Tracks the persistent onboarding state, baseline operational scale, 
    and regulatory privacy approvals. 
    
    Historical event logs/snapshots are maintained in separate event tables.
    """
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('yo', 'Yoruba'),
        ('ha', 'Hausa'),
        ('ig', 'Igbo'),
    ]

    # 1. IDENTIFIER (The primary API lookup anchor)
    phone_number = models.CharField(
        max_length=20, 
        unique=True, 
        db_index=True,
        help_text="International format string used as the webhook lookup key (e.g., +2348012345678)"
    )

    # 2. BASELINE FARM PROFILE (Current State Metadata)
    preferred_language = models.CharField(
        max_length=2, 
        choices=LANGUAGE_CHOICES, 
        default='en',
        help_text="Preferred language code for outbound automated WhatsApp message routing"
    )
    
    flock_size = models.PositiveIntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="The latest known total number of poultry birds on the farm (Acts as current baseline)"
    )
    
    location = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        help_text="State or local region in Nigeria where the poultry farm is located"
    )

    # 3. STATE AND WORKFLOW MANAGEMENT FLAGS
    onboarding_completed = models.BooleanField(
        default=False,
        help_text="Flips to True once the initial profile data gathering script is fully complete"
    )
    
    consent_accepted = models.BooleanField(
        default=False,
        help_text="NDPR Privacy compliance toggle. Must be set to True before processing health telemetry data"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Farmer Profile"
        verbose_name_plural = "Farmer Profiles"

    def __str__(self):
        return f"Farmer {self.phone_number} | Baseline: {self.flock_size or 'Unknown'} birds"
