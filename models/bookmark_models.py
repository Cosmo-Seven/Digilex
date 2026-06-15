from django.db import models
from models.base_models import BaseModel

class BookmarkModel(BaseModel):
    user = models.ForeignKey(
        "core.UserModel", on_delete=models.CASCADE, related_name="bookmarks"
    )
    section = models.ForeignKey(
        "core.SectionModel", on_delete=models.CASCADE, related_name="bookmarks"
    )

    class Meta:
        app_label = "core"
        db_table = "bookmarks"
        unique_together = ("user", "section")

    def __str__(self):
        return f"{self.user.email} bookmarked {self.section.section_number}"
