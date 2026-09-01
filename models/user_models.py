from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from managers.user_managers import UserManager
from models.base_models import BaseModel
from django.utils.timezone import now
from datetime import timedelta
from django.utils.text import slugify
from helpers.translation import register_key


class UserModel(AbstractBaseUser, PermissionsMixin, BaseModel):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    role = models.ForeignKey(
        "core.RoleModel", on_delete=models.SET_NULL, null=True, blank=True
    )
    phone = models.CharField(max_length=50, unique=True)
    payment_proof = models.FileField(upload_to="payment_proofs", null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    subscription_law = models.ForeignKey(
        "core.LawModel", on_delete=models.SET_NULL, null=True, blank=True
    )
    profile = models.ImageField(upload_to="profile", null=True, blank=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_developer = models.BooleanField(default=False)

    last_active = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["username", "email"]

    objects = UserManager()

    def __str__(self):
        return self.username or self.phone or self.email or f"User {self.id}"

    class Meta:
        app_label = "core"
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def save(self, *args, **kwargs):
        key = slugify(self.username).replace("-", "_").lower()
        register_key(key, self.username)
        super().save(*args, **kwargs)

    @property
    def translation_key(self):
        return slugify(self.username).replace("-", "_").lower()

    def has_permission(self, perm_codename):
        if self.is_superuser:
            return True
        return (
            self.role and self.role.permissions.filter(codename=perm_codename).exists()
        )

    def has_module_perms(self, app_label):
        return (
            self.role
            and self.role.permissions.filter(content_type__app_label=app_label).exists()
        )

    def get_all_permission_ids(self):
        role_perms = set()
        if self.role:
            role_perms = set(self.role.permissions.values_list("id", flat=True))
            user_perms = set(self.user_permissions.values_list("id", flat=True))
            return role_perms.union(user_perms)

    def is_online(self):
        return self.last_active >= now() - timedelta(minutes=5)


class SearchHistoryModel(BaseModel):
    user = models.ForeignKey(
        "core.UserModel", on_delete=models.CASCADE, related_name="search_history"
    )
    query = models.CharField(max_length=255)

    class Meta:
        app_label = "core"
        db_table = "search_history"
        constraints = [
            models.UniqueConstraint(fields=("user", "query"), name="unique_user_search_query")
        ]

    def __str__(self):
        return f"{self.user.email}: {self.query}"


class UserHistoryModel(BaseModel):
    user = models.ForeignKey(
        "core.UserModel", on_delete=models.CASCADE, related_name="user_history"
    )
    law = models.ForeignKey(
        "core.LawModel", on_delete=models.CASCADE, related_name="history_entries", null=True, blank=True
    )
    chapter = models.ForeignKey(
        "core.ChapterModel", on_delete=models.CASCADE, related_name="history_entries", null=True, blank=True
    )
    section = models.ForeignKey(
        "core.SectionModel", on_delete=models.CASCADE, related_name="history_entries", null=True, blank=True
    )

    class Meta:
        app_label = "core"
        db_table = "user_history"
        constraints = [
            models.UniqueConstraint(fields=("user", "law"), condition=Q(law__isnull=False), name="unique_user_law_history"),
            models.UniqueConstraint(fields=("user", "chapter"), condition=Q(chapter__isnull=False), name="unique_user_chapter_history"),
            models.UniqueConstraint(fields=("user", "section"), condition=Q(section__isnull=False), name="unique_user_section_history"),
        ]

    def __str__(self):
        target = self.section or self.chapter or self.law
        return f"{self.user.email}: {target}"
