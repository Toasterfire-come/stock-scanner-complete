from django.core.mail import send_mail
from django.conf import settings

def send_email_notification(subject, message, recipient_list):
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
        return True
    except Exception as e:
        print(f'Email failed: {e}')
        return False
