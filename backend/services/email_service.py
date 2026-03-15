"""
Email notification service for sending transactional and notification emails.
Supports multiple providers (SendGrid, Gmail SMTP, etc.)
"""

import os
import logging
from typing import Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class EmailProvider(ABC):
    """Abstract base class for email providers"""

    @abstractmethod
    def send(self, recipient_email: str, subject: str, html_content: str) -> bool:
        """Send email through provider"""
        pass


class SendGridProvider(EmailProvider):
    """SendGrid email provider"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            self.SendGridAPIClient = SendGridAPIClient
            self.Mail = Mail
        except ImportError:
            logger.error("sendgrid package not installed. Install with: pip install sendgrid")
            raise

    def send(self, recipient_email: str, subject: str, html_content: str) -> bool:
        """
        Send email via SendGrid API.

        Args:
            recipient_email: Recipient email address
            subject: Email subject
            html_content: Email body in HTML format

        Returns:
            True if successful, False otherwise
        """
        try:
            client = self.SendGridAPIClient(self.api_key)

            message = self.Mail(
                from_email=os.getenv("EMAIL_FROM", "noreply@genai-genesis.com"),
                to_emails=recipient_email,
                subject=subject,
                html_content=html_content
            )

            response = client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"✓ Email sent to {recipient_email}")
                return True
            else:
                logger.error(f"SendGrid error: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Failed to send email via SendGrid: {str(e)}")
            return False


class SMTPProvider(EmailProvider):
    """Gmail/SMTP email provider"""

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        try:
            import smtplib
            self.smtplib = smtplib
        except ImportError:
            logger.error("smtplib not available")
            raise

    def send(self, recipient_email: str, subject: str, html_content: str) -> bool:
        """
        Send email via SMTP (Gmail, etc).

        Args:
            recipient_email: Recipient email address
            subject: Email subject
            html_content: Email body in HTML format

        Returns:
            True if successful, False otherwise
        """
        try:
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.email
            msg["To"] = recipient_email

            # Attach HTML
            part = MIMEText(html_content, "html")
            msg.attach(part)

            # Send via SMTP
            with self.smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.email, self.password)
                server.sendmail(self.email, recipient_email, msg.as_string())

            logger.info(f"✓ Email sent to {recipient_email} via SMTP")
            return True

        except Exception as e:
            logger.error(f"Failed to send email via SMTP: {str(e)}")
            return False


class EmailService:
    """
    Email service that manages provider selection and sends notifications.
    """

    def __init__(self):
        provider_type = os.getenv("EMAIL_PROVIDER", "sendgrid").lower()

        if provider_type == "sendgrid":
            api_key = os.getenv("SENDGRID_API_KEY")
            if not api_key:
                raise ValueError("SENDGRID_API_KEY not set in environment")
            self.provider = SendGridProvider(api_key)
            logger.info("✓ Email service initialized with SendGrid")

        elif provider_type == "smtp":
            email = os.getenv("SMTP_EMAIL")
            password = os.getenv("SMTP_PASSWORD")
            if not email or not password:
                raise ValueError("SMTP_EMAIL and SMTP_PASSWORD not set in environment")
            self.provider = SMTPProvider(email, password)
            logger.info("✓ Email service initialized with SMTP")

        else:
            logger.warning(f"Unknown EMAIL_PROVIDER: {provider_type}, defaulting to sendgrid")
            api_key = os.getenv("SENDGRID_API_KEY")
            if api_key:
                self.provider = SendGridProvider(api_key)
            else:
                raise ValueError("No email provider configured")

    def send_notification(
        self,
        recipient_email: str,
        subject: str,
        html_content: str
    ) -> bool:
        """
        Send a notification email.

        Args:
            recipient_email: Recipient email address
            subject: Email subject line
            html_content: Email body in HTML format

        Returns:
            True if successful, False otherwise
        """
        if not recipient_email or not subject or not html_content:
            logger.error("Missing required email parameters")
            return False

        return self.provider.send(recipient_email, subject, html_content)

    def send_welcome_email(self, email: str, name: str) -> bool:
        """Send welcome email to new user"""
        subject = "Welcome to Dear AI-ry! 🌱"

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2>Welcome to Dear AI-ry, {name}! 🌱</h2>
                    
                    <p>We're excited to have you join our journaling companion community.</p>
                    
                    <p>Your personal AI-ry helps you:</p>
                    <ul>
                        <li>💭 Reflect on your thoughts and emotions</li>
                        <li>📊 Track your mood patterns over time</li>
                        <li>🔍 Discover insights from your past entries</li>
                        <li>💡 Get personalized wellness suggestions</li>
                    </ul>
                    
                    <p><strong>Getting Started:</strong></p>
                    <ol>
                        <li>Log in to your account</li>
                        <li>Start with your first journal entry</li>
                        <li>Check in with your daily mood</li>
                        <li>Explore your insights on the dashboard</li>
                    </ol>
                    
                    <p>
                        <a href="https://app.genai-genesis.com" 
                           style="display: inline-block; padding: 10px 20px; background-color: #6366f1; 
                                  color: white; text-decoration: none; border-radius: 4px;">
                            Open Dear AI-ry
                        </a>
                    </p>
                    
                    <p>Happy journaling!<br>-Your New Personal Diary/p>
                </div>
            </body>
        </html>
        """

        return self.send_notification(email, subject, html_content)

    def send_daily_prompt(self, email: str, prompt: str) -> bool:
        """Send daily journaling prompt"""
        subject = "✍️ Your Daily Journaling Prompt"

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2>📝 Today's Journaling Prompt</h2>
                    
                    <div style="background-color: #f0f4ff; padding: 20px; border-left: 4px solid #6366f1; 
                               margin: 20px 0; border-radius: 4px;">
                        <p style="font-size: 18px; margin: 0;">
                            "{prompt}"
                        </p>
                    </div>
                    
                    <p>Take a few minutes to reflect on this question and write your thoughts.</p>
                    
                    <p>
                        <a href="https://app.genai-genesis.com/journal" 
                           style="display: inline-block; padding: 10px 20px; background-color: #6366f1; 
                                  color: white; text-decoration: none; border-radius: 4px;">
                            Start Journaling
                        </a>
                    </p>
                    
                    <p style="color: #666; font-size: 14px;">
                        You can customize your journal prompts in your preferences.
                    </p>
                </div>
            </body>
        </html>
        """

        return self.send_notification(email, subject, html_content)

    def send_mood_followup(
        self,
        email: str,
        mood: str,
        followup_message: str
    ) -> bool:
        """Send mood-triggered follow-up email"""
        subject = f"💭 We noticed you're feeling {mood}"

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2>💭 Personalized Wellness Check-in</h2>
                    
                    <p>We noticed you logged a mood check-in and wanted to follow up.</p>
                    
                    <div style="background-color: #f9f5f0; padding: 20px; border-radius: 4px; margin: 20px 0;">
                        <p>{followup_message}</p>
                    </div>
                    
                    <p><strong>Quick Suggestions:</strong></p>
                    <ul>
                        <li>📖 Journal about what you're feeling</li>
                        <li>🧘 Take 5 minutes for deep breathing</li>
                        <li>📱 Reach out to someone you trust</li>
                        <li>💪 Take a short walk or stretch</li>
                    </ul>
                    
                    <p>
                        <a href="https://app.genai-genesis.com" 
                           style="display: inline-block; padding: 10px 20px; background-color: #6366f1; 
                                  color: white; text-decoration: none; border-radius: 4px;">
                            View Your Dashboard
                        </a>
                    </p>
                    
                    <p style="color: #666; font-size: 14px;">
                        If you're in crisis, please reach out to a mental health professional.
                    </p>
                </div>
            </body>
        </html>
        """

        return self.send_notification(email, subject, html_content)

    def send_streak_reminder(self, email: str, streak_days: int) -> bool:
        """Send streak reminder email"""
        subject = f"🔥 Keep your {streak_days}-day streak going!"

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2>🔥 Amazing Streak!</h2>
                    
                    <p style="font-size: 18px;">
                        You've checked in for <strong>{streak_days} days in a row</strong>! 🎉
                    </p>
                    
                    <p>This consistency is building valuable self-awareness. Keep it up!</p>
                    
                    <div style="background-color: #f0fdf4; padding: 20px; border-radius: 4px; margin: 20px 0;">
                        <p>
                            The more you journal and check in, the better insights you'll discover about yourself.
                            Keep the momentum going! 💪
                        </p>
                    </div>
                    
                    <p>
                        <a href="https://app.genai-genesis.com/journal" 
                           style="display: inline-block; padding: 10px 20px; background-color: #6366f1; 
                                  color: white; text-decoration: none; border-radius: 4px;">
                            Add Today's Entry
                        </a>
                    </p>
                </div>
            </body>
        </html>
        """

        return self.send_notification(email, subject, html_content)


# Global instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get or initialize email service singleton"""
    global _email_service
    if _email_service is None:
        try:
            _email_service = EmailService()
        except Exception as e:
            logger.error(f"Failed to initialize email service: {str(e)}")
            logger.warning("Email notifications will not be available")
            return None
    return _email_service


if __name__ == "__main__":
    # Test email service
    try:
        service = get_email_service()
        if service:
            print("✓ Email service initialized successfully")
            print(f"Provider: {type(service.provider).__name__}")
        else:
            print("✗ Email service initialization failed")
    except Exception as e:
        print(f"✗ Error: {e}")
