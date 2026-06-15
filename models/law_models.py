from django.db import models
from models.base_models import BaseModel

class LawModel(BaseModel):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_free = models.BooleanField(default=False, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "core"
        db_table = "laws"
        verbose_name = "Law"
        verbose_name_plural = "Laws"

    def __str__(self):
        return self.title