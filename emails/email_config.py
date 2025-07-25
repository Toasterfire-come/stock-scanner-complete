"""
Email Configuration for Stock Scanner
IONOS Hosting Compatible Email Settings
"""

import os
from django.conf import settings

# Email Backend Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Gmail SMTP Settings
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com') # Gmail SMTP server
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587')) # TLS port
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False # Use TLS instead of SSL for port 587

# Authentication
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'noreply.retailtradescanner@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'mzqmvhsjqeqrjmjv') # Gmail App Password

# Default sender settings
DEFAULT_FROM_EMAIL = f'Stock Scanner <{EMAIL_HOST_USER}>'
SERVER_EMAIL = f'Stock Scanner Server <{EMAIL_HOST_USER}>'

# Admin email settings
ADMINS = [
('Stock Scanner Admin', os.getenv('ADMIN_EMAIL', 'noreply.retailtradescanner@gmail.com')),
]

# Email timeout settings
EMAIL_TIMEOUT = 30 # 30 seconds timeout

# Email template settings
EMAIL_SUBJECT_PREFIX = '[Stock Scanner] '

# Email rate limiting (to avoid Gmail limits)
EMAIL_RATE_LIMIT = {
'max_emails_per_hour': 250, # Gmail limit is 500/day, so 250/hour is safe
'max_emails_per_day': 500, # Gmail daily limit
'delay_between_emails': 1, # 1 second delay between emails
}

# Email content settings
EMAIL_TEMPLATES = {
'stock_alert': {
'subject': 'Stock Alert: {ticker} - {alert_type}',
'template': 'emails/stock_alert.html',
'text_template': 'emails/stock_alert.txt',
},
'welcome': {
'subject': 'Welcome to Stock Scanner!',
'template': 'emails/welcome.html',
'text_template': 'emails/welcome.txt',
},
'subscription_confirmation': {
'subject': 'Subscription Confirmed - {category}',
'template': 'emails/subscription_confirmation.html',
'text_template': 'emails/subscription_confirmation.txt',
},
'password_reset': {
'subject': 'Password Reset - Stock Scanner',
'template': 'emails/password_reset.html',
'text_template': 'emails/password_reset.txt',
},
}

# Email verification settings
EMAIL_VERIFICATION = {
'required': True,
'token_expiry_hours': 24,
'resend_limit': 3,
}

# Unsubscribe settings
UNSUBSCRIBE_URL = os.getenv('SITE_URL', 'https://retailtradescan.net') + '/unsubscribe/{token}/'

def get_email_settings():
"""Return email configuration dictionary for Django settings"""
return {
'EMAIL_BACKEND': EMAIL_BACKEND,
'EMAIL_HOST': EMAIL_HOST,
'EMAIL_PORT': EMAIL_PORT,
'EMAIL_USE_TLS': EMAIL_USE_TLS,
'EMAIL_USE_SSL': EMAIL_USE_SSL,
'EMAIL_HOST_USER': EMAIL_HOST_USER,
'EMAIL_HOST_PASSWORD': EMAIL_HOST_PASSWORD,
'DEFAULT_FROM_EMAIL': DEFAULT_FROM_EMAIL,
'SERVER_EMAIL': SERVER_EMAIL,
'ADMINS': ADMINS,
'EMAIL_TIMEOUT': EMAIL_TIMEOUT,
'EMAIL_SUBJECT_PREFIX': EMAIL_SUBJECT_PREFIX,
}

def validate_email_config():
"""Validate email configuration"""
errors = []

if not EMAIL_HOST_USER:
errors.append("EMAIL_HOST_USER is required")

if not EMAIL_HOST_PASSWORD:
errors.append("EMAIL_HOST_PASSWORD is required")

if not EMAIL_HOST:
errors.append("EMAIL_HOST is required")

return errors

def test_email_connection():
"""Test email connection"""
from django.core.mail import get_connection
from django.core.mail.backends.smtp import EmailBackend

try:
connection = get_connection(
backend=EMAIL_BACKEND,
host=EMAIL_HOST,
port=EMAIL_PORT,
username=EMAIL_HOST_USER,
password=EMAIL_HOST_PASSWORD,
use_tls=EMAIL_USE_TLS,
use_ssl=EMAIL_USE_SSL,
timeout=EMAIL_TIMEOUT,
)

# Test connection
connection.open()
connection.close()
return True, "Email connection successful"

except Exception as e:
return False, f"Email connection failed: {str(e)}"

# Rate limiting helper
class EmailRateLimit:
"""Simple email rate limiting"""

def __init__(self):
self.email_count = 0
self.last_reset = None

def can_send_email(self):
"""Check if we can send an email within rate limits"""
import datetime

now = datetime.datetime.now()

# Reset counter every hour
if (self.last_reset is None or 
(now - self.last_reset).seconds > 3600):
self.email_count = 0
self.last_reset = now

# Check rate limit
if self.email_count >= EMAIL_RATE_LIMIT['max_emails_per_hour']:
return False

return True

def record_email_sent(self):
"""Record that an email was sent"""
self.email_count += 1

# Global rate limiter instance
email_rate_limiter = EmailRateLimit()

# Gmail specific settings
GMAIL_SETTINGS = {
'smtp_host': 'smtp.gmail.com',
'smtp_port': 587,
'imap_host': 'imap.gmail.com',
'imap_port': 993,
'pop3_host': 'pop.gmail.com',
'pop3_port': 995,
'webmail_url': 'https://mail.google.com',
'max_attachment_size': '25MB',
'daily_send_limit': 500,
'hourly_send_limit': 250,
}

def get_gmail_settings():
"""Get Gmail specific email settings"""
return GMAIL_SETTINGS

# Email queue management for high volume
class EmailQueue:
"""Simple email queue for batch processing"""

def __init__(self):
self.queue = []

def add_email(self, to_email, subject, message, html_message=None):
"""Add email to queue"""
self.queue.append({
'to': to_email,
'subject': subject,
'message': message,
'html_message': html_message,
'timestamp': datetime.datetime.now()
})

def process_queue(self, batch_size=10):
"""Process queued emails in batches"""
from django.core.mail import send_mail
import time

processed = 0
errors = []

while self.queue and processed < batch_size:
if not email_rate_limiter.can_send_email():
break

email_data = self.queue.pop(0)

try:
send_mail(
subject=email_data['subject'],
message=email_data['message'],
from_email=DEFAULT_FROM_EMAIL,
recipient_list=[email_data['to']],
html_message=email_data.get('html_message'),
fail_silently=False
)

email_rate_limiter.record_email_sent()
processed += 1

# Add delay between emails
time.sleep(EMAIL_RATE_LIMIT['delay_between_emails'])

except Exception as e:
errors.append(f"Failed to send to {email_data['to']}: {str(e)}")

return processed, errors

def get_queue_size(self):
"""Get current queue size"""
return len(self.queue)

# Global email queue instance
email_queue = EmailQueue()