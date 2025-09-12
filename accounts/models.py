#accounts/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from companies.models import Company


class CustomUserManager(BaseUserManager):
    """Manager where email is the unique identifier for authentication"""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Roles.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "admin", _("Admin")
        MANAGER = "manager", _("Manager")
        VIEWER = "viewer", _("Viewer")
        EMPLOYEE = "employee", _("Employee")

    username = None  # we don’t need the username field
    email = models.EmailField(_("email address"), unique=True)

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users"
    )
    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.EMPLOYEE
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # removes username from createsuperuser

    objects = CustomUserManager()

    def is_company_admin(self):
        return self.role == self.Roles.ADMIN

    def is_manager(self):
        return self.role == self.Roles.MANAGER

    def is_viewer(self):
        return self.role == self.Roles.VIEWER


class UserInvite(models.Model):
    ROLE_CHOICES = [
        ("employee", "Employee"),
        ("manager", "Manager"),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="invites")
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="employee")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_invites")
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def is_expired(self):
        return self.created_at < timezone.now() - timezone.timedelta(days=7)  # 7-day expiry

    def __str__(self):
        return f"Invite for {self.email} ({self.get_role_display()}) - {'Accepted' if self.accepted else 'Pending'}"
