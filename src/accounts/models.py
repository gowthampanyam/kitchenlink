# simple, beginner-friendly custom user + role model
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Role(models.Model):
    """
    Simple role model with a numeric level.
    Higher level = more privileges.
    """
    name = models.CharField(max_length=50, unique=True)
    level = models.PositiveIntegerField(help_text="Higher number = higher privilege")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class User(AbstractUser):
    """
    Custom user model. Extends Django's AbstractUser so we can add role and date_of_birth.
    - role: FK to Role (single role at a time).
    - date_of_birth: required by the project.
    """
    role = models.ForeignKey(Role, null=True, blank=True, on_delete=models.SET_NULL)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'date_of_birth']

    def role_level(self):
        if self.role:
            return self.role.level
        return 0
    
    def __str__(self):
        return self.username
