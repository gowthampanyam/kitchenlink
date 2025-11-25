from django.db import models
from django.utils import timezone

class Notification(models.Model):
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField(default="No message here!")
    email_type = models.CharField(max_length=100, default="Account Notifications")
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.subject
