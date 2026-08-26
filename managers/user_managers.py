from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class UserManager(BaseUserManager):

    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError("You must provide a valid email")

    def create_user(self, phone, username=None, password=None, **extra_fields):

        if not phone:
            raise ValueError("Base User: a phone number is required")

        email = extra_fields.pop("email", None)
        if email:
            email = self.normalize_email(email)
            self.email_validator(email)

        user = self.model(username=username, phone=phone, email=email, **extra_fields)

        user.set_password(password)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user.save()

        return user

    def create_superuser(self, phone, username=None, password=None, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusers must have is_superuser=True")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superusers must have is_staff=True")

        if not password:
            raise ValueError("Superusers must have a password")

        if not phone:
            raise ValueError("Admin User: a phone number is required")

        user = self.create_user(phone, username, password, **extra_fields)

        user.save()

        return user
