from django.core.mail import send_mail
from .models import Notification

def send_email_with_record(email, subject, message, email_type):
    try:
        send_mail(subject, message, "no-reply@restaurant.com", [email])
        status = "SENT"
    except Exception as e:
        print(e)
        status = "FAILED"

    Notification.objects.create(
        recipient_email=email,
        subject=subject,
        message=message,
        email_type=email_type,
        status=status
    )
