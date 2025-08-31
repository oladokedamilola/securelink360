import secrets
import string
from django.db import models
from django.utils import timezone
from cryptography.fernet import Fernet
from django.conf import settings

class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    domain = models.CharField(max_length=255, unique=True)  # e.g. "acme.com"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

fernet = Fernet(settings.SECRET_KEY[:32].encode("utf-8").ljust(32, b"0"))

class License(models.Model):
    PLAN_CHOICES = [
        ("basic", "Basic"),
        ("pro", "Pro"),
        ("enterprise", "Enterprise"),
    ]

    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name="license")
    key_encrypted = models.BinaryField()
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="basic")
    seats = models.PositiveIntegerField(default=10)  # number of allowed users
    expiry_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True) 

    def set_key(self, raw_key: str):
        self.key_encrypted = fernet.encrypt(raw_key.encode("utf-8"))

    def get_key(self):
        return fernet.decrypt(self.key_encrypted).decode("utf-8")   

    def is_active(self):
        return self.expiry_date >= timezone.now()

    def __str__(self):
        return f"{self.company.name} - {self.plan} License"
    
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self._generate_license_key()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_key():
        """Generate a secure random license key like COMP-XXXX-YYYY-ZZZZ"""
        parts = [
            ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
            for _ in range(3)
        ]
        return f"COMP-{parts[0]}-{parts[1]}-{parts[2]}"
    

    def __str__(self):
        return f"{self.company.name} - {self.plan} ({self.key})"

class Announcement(models.Model):
    SCOPE_CHOICES = [
        ("company", "Company-wide"),
        ("team", "Team-only"),
    ]
    manager = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="announcements"
    )
    company = models.ForeignKey("companies.Company", on_delete=models.CASCADE, related_name="announcements")
    message = models.TextField()
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default="team")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_scope_display()}] {self.message[:30]}"

    


class Task(models.Model):
    assigned_by = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="assigned_tasks"
    )
    assigned_to = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="tasks"
    )
    description = models.TextField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Task for {self.assigned_to.email} (Due: {self.due_date or 'N/A'})"
    def mark_completed(self):
        self.completed = True
        self.save()
    def mark_incomplete(self):
        self.completed = False
        self.save()
    def is_overdue(self):
        return self.due_date and timezone.now() > self.due_date
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        indexes = [
            models.Index(fields=['assigned_to', 'completed']),
            models.Index(fields=['due_date']),
        ]
        permissions = [
            ("can_assign_task", "Can assign tasks to users"),
            ("can_view_all_tasks", "Can view all tasks in the company"),
        ]
        get_latest_by = 'created_at'
        unique_together = ('assigned_to', 'description', 'created_at')
        constraints = [
            models.CheckConstraint(check=models.Q(due_date__gte=models.F('created_at')), name='due_date_after_created_at')
        ]
        default_related_name = 'tasks'
        abstract = False
        managed = True
        db_table = 'company_tasks'

class Notification(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.email} - {'Read' if self.read else 'Unread'}"  