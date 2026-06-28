import uuid
from django.db import models

class BaseModel(models.Model):
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Secure universally unique identifier substituting standard integers."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp automatically recorded upon database record initialization."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp automatically overwritten whenever row values change."
    )

    # Prevent Django from creating a physical 'core_basemodel' table
    class Meta:
        abstract = True  