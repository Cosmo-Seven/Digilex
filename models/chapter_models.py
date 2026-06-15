from django.db import models
from models.base_models import BaseModel
from core.models import LawModel

class ChapterModel(BaseModel):
    law = models.ForeignKey(LawModel, on_delete=models.CASCADE, related_name='chapters')
    chapter_number = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        app_label = "core"
        db_table = "chapters"
        verbose_name = "Chapter"
        verbose_name_plural = "Chapters"

    def __str__(self):
        return f"{self.law.title} - {self.chapter_number}: {self.title}"