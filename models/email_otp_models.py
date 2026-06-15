from django.db import models
from models.base_models import BaseModel
from django.utils import timezone
import datetime

class EmailOTPModel(BaseModel):
    user = models.ForeignKey("core.UserModel", on_delete=models.CASCADE, related_name="otps", blank=True, null=True)
    created_by = models.ForeignKey("core.UserModel", on_delete=models.SET_NULL, null=True, related_name="created_otps")
    
    code = models.CharField(max_length=6)
    expires_at = models.DateTimeField(blank=True)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + datetime.timedelta(minutes=15)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at
    
    class Meta:
        app_label = "core"