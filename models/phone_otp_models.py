from django.db import models
from models.base_models import BaseModel
from django.utils import timezone
import datetime


class PhoneOTPModel(BaseModel):
    phone = models.CharField(max_length=50)
    code = models.CharField(max_length=6)
    expires_at = models.DateTimeField(blank=True)
    is_verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + datetime.timedelta(minutes=15)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    class Meta:
        app_label = "core"
        db_table = "phone_otps"
        verbose_name = "Phone OTP"
        verbose_name_plural = "Phone OTPs"
