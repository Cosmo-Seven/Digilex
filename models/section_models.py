from django.db import models
from models.base_models import BaseModel
from core.models import ChapterModel

class SectionModel(BaseModel):
    chapter = models.ForeignKey(ChapterModel, on_delete=models.CASCADE, related_name='sections')
    section_number = models.CharField(max_length=50)
    title = models.CharField(max_length=255, blank=True, null=True)
    offense = models.TextField()
    penalty = models.TextField()
    note = models.TextField(blank=True, null=True)
    case_law = models.TextField(blank=True, null=True)
    directive = models.TextField(blank=True, null=True)

    class Meta:
        app_label = "core"
        db_table = "sections"
        verbose_name = "Section"
        verbose_name_plural = "Sections"

    def __str__(self):
        return f"Section {self.section_number} ({self.chapter.law.title})"