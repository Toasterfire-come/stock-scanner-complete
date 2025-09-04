"""
Email service for sending transactional and marketing emails
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
import jinja2
from datetime import datetime
import asyncio
import aiosmtplib
from email.message import EmailMessage
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class EmailService:
    """
    Production-ready email service with templates and queue
    """
    
    def __init__(self):
        # Email configuration
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@stockscanner.com')
        self.from_name = os.getenv('FROM_NAME', 'Stock Scanner')
        
        # Template configuration
        template_dir = Path(__file__).parent.parent / 'templates' / 'emails'
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(template_dir)),
            autoescape=True
        )
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        reply_to: Optional[str] = None
    ) -> bool:
        """
        Send email asynchronously
        """
        try:
            message = EmailMessage()
            message['From'] = f"{self.from_name} <{self.from_email}>"
            message['To'] = to_email
            message['Subject'] = subject
            
            if cc:
                message['Cc'] = ', '.join(cc)
            if bcc:
                message['Bcc'] = ', '.join(bcc)
            if reply_to:
                message['Reply-To'] = reply_to
            
            # Add content
            if text_content:
                message.set_content(text_content)
            if html_content:
                message.add_alternative(html_content, subtype='html')
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    with open(attachment['path'], 'rb') as f:
                        file_data = f.read()
                        message.add_attachment(
                            file_data,
                            maintype='application',
                            subtype='octet-stream',
                            filename=attachment['filename']
                        )
            
            # Send email
            async with aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=True
            ) as smtp:
                await smtp.login(self.smtp_user, self.smtp_password)
                await smtp.send_message(message)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> tuple[str, str]:
        """
        Render email template with context
        """
        # Add common context
        context.update({
            'app_name': 'Stock Scanner',
            'app_url': os.getenv('APP_URL', 'https://stockscanner.com'),
            'support_email': os.getenv('SUPPORT_EMAIL', 'support@stockscanner.com'),
            'current_year': datetime.now().year
        })
        
        # Render HTML template
        html_template = self.jinja_env.get_template(f"{template_name}.html")
        html_content = html_template.render(**context)
        
        # Render text template if exists
        text_content = None
        try:
            text_template = self.jinja_env.get_template(f"{template_name}.txt")
            text_content = text_template.render(**context)
        except jinja2.TemplateNotFound:
            pass
        
        return html_content, text_content
    
    async def send_verification_email(self, email: str, name: str, verification_token: str):
        """
        Send email verification link
        """
        verification_url = f"{os.getenv('APP_URL')}/verify-email?token={verification_token}"
        
        html_content, text_content = self.render_template('verification', {
            'name': name,
            'verification_url': verification_url,
            'expires_in': '7 days'
        })
        
        return await self.send_email(
            to_email=email,
            subject='Verify Your Email - Stock Scanner',
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_password_reset_email(self, email: str, name: str, reset_token: str):
        """
        Send password reset link
        """
        reset_url = f"{os.getenv('APP_URL')}/reset-password?token={reset_token}"
        
        html_content, text_content = self.render_template('password_reset', {
            'name': name,
            'reset_url': reset_url,
            'expires_in': '1 hour'
        })
        
        return await self.send_email(
            to_email=email,
            subject='Password Reset Request - Stock Scanner',
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_welcome_email(self, email: str, name: str, plan: str):
        """
        Send welcome email after successful registration
        """
        html_content, text_content = self.render_template('welcome', {
            'name': name,
            'plan': plan,
            'dashboard_url': f"{os.getenv('APP_URL')}/dashboard",
            'documentation_url': f"{os.getenv('APP_URL')}/docs",
            'support_url': f"{os.getenv('APP_URL')}/support"
        })
        
        return await self.send_email(
            to_email=email,
            subject='Welcome to Stock Scanner!',
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_payment_confirmation(
        self,
        email: str,
        name: str,
        plan: str,
        amount: float,
        invoice_id: str
    ):
        """
        Send payment confirmation email
        """
        html_content, text_content = self.render_template('payment_confirmation', {
            'name': name,
            'plan': plan,
            'amount': amount,
            'invoice_id': invoice_id,
            'invoice_url': f"{os.getenv('APP_URL')}/invoices/{invoice_id}",
            'billing_url': f"{os.getenv('APP_URL')}/billing"
        })
        
        return await self.send_email(
            to_email=email,
            subject=f'Payment Confirmation - Invoice #{invoice_id}',
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_subscription_expiring_email(
        self,
        email: str,
        name: str,
        plan: str,
        expires_date: datetime
    ):
        """
        Send subscription expiring reminder
        """
        html_content, text_content = self.render_template('subscription_expiring', {
            'name': name,
            'plan': plan,
            'expires_date': expires_date.strftime('%B %d, %Y'),
            'renew_url': f"{os.getenv('APP_URL')}/billing/renew"
        })
        
        return await self.send_email(
            to_email=email,
            subject='Your Subscription is Expiring Soon',
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_security_alert(
        self,
        email: str,
        name: str,
        alert_type: str,
        ip_address: str,
        location: str,
        timestamp: datetime
    ):
        """
        Send security alert email
        """
        html_content, text_content = self.render_template('security_alert', {
            'name': name,
            'alert_type': alert_type,
            'ip_address': ip_address,
            'location': location,
            'timestamp': timestamp.strftime('%B %d, %Y at %I:%M %p'),
            'security_url': f"{os.getenv('APP_URL')}/security"
        })
        
        return await self.send_email(
            to_email=email,
            subject=f'Security Alert: {alert_type}',
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_bulk_email(
        self,
        recipients: List[Dict[str, str]],
        subject: str,
        template_name: str,
        common_context: Dict[str, Any]
    ):
        """
        Send bulk emails with personalization
        """
        tasks = []
        
        for recipient in recipients:
            # Merge recipient data with common context
            context = {**common_context, **recipient}
            
            html_content, text_content = self.render_template(template_name, context)
            
            task = self.send_email(
                to_email=recipient['email'],
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            tasks.append(task)
        
        # Send emails concurrently with rate limiting
        results = []
        for i in range(0, len(tasks), 10):  # Send 10 at a time
            batch = tasks[i:i+10]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            results.extend(batch_results)
            await asyncio.sleep(1)  # Rate limiting
        
        return results

# Email queue for background processing
class EmailQueue:
    """
    Queue emails for background processing
    """
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0))
        )
    
    def enqueue(self, email_data: Dict[str, Any]):
        """
        Add email to queue
        """
        import json
        self.redis_client.lpush('email_queue', json.dumps(email_data))
    
    async def process_queue(self):
        """
        Process emails from queue
        """
        email_service = EmailService()
        
        while True:
            # Get email from queue
            email_data = self.redis_client.rpop('email_queue')
            
            if not email_data:
                await asyncio.sleep(1)
                continue
            
            try:
                import json
                data = json.loads(email_data)
                
                await email_service.send_email(
                    to_email=data['to_email'],
                    subject=data['subject'],
                    html_content=data['html_content'],
                    text_content=data.get('text_content')
                )
            except Exception as e:
                logger.error(f"Failed to process email from queue: {str(e)}")