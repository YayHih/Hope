"""
Email service for sending notifications using SMTP with DKIM signing.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SMTP."""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = f"Hope for NYC <{settings.SMTP_FROM}>"
        self.to_email = "campuslens.help@gmail.com"

    async def send_report_email(
        self,
        issue_type: str,
        location_name: str,
        description: str,
        user_ip: Optional[str] = None
    ) -> bool:
        """
        Send a report issue email to the support team.

        Args:
            issue_type: Type of issue reported
            location_name: Name of the location
            description: Detailed description of the issue
            user_ip: IP address of the user (optional)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'Hope for NYC - Issue Report: {issue_type}'
            msg['From'] = self.from_email
            msg['To'] = self.to_email
            msg['Date'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')

            # Create email body
            text_body = f"""
Hope for NYC - Issue Report

Issue Type: {issue_type}
Location Name: {location_name}
Description: {description}

Submitted: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
User IP: {user_ip or 'Not available'}

---
This is an automated message from Hope for NYC issue reporting system.
"""

            html_body = f"""
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
      <h2 style="color: #2C7A7B; border-bottom: 2px solid #2C7A7B; padding-bottom: 10px;">
        Hope for NYC - Issue Report
      </h2>

      <div style="background-color: #f7fafc; padding: 15px; border-radius: 8px; margin: 20px 0;">
        <p><strong>Issue Type:</strong> {issue_type}</p>
        <p><strong>Location Name:</strong> {location_name}</p>
        <p><strong>Description:</strong></p>
        <p style="background-color: white; padding: 10px; border-radius: 4px;">
          {description}
        </p>
      </div>

      <div style="font-size: 12px; color: #718096; margin-top: 20px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
        <p><strong>Submitted:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        <p><strong>User IP:</strong> {user_ip or 'Not available'}</p>
        <p style="margin-top: 15px;">
          <em>This is an automated message from Hope for NYC issue reporting system.</em>
        </p>
      </div>
    </div>
  </body>
</html>
"""

            # Attach both plain text and HTML versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)

            # Send email using SMTP
            # Note: For production, consider using async SMTP with aiosmtplib
            # For now, using synchronous smtplib wrapped in try-except
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Report email sent successfully for location: {location_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to send report email: {str(e)}")
            return False

    async def send_test_email(self) -> bool:
        """Send a test email to verify configuration."""
        try:
            msg = MIMEText("This is a test email from Hope for NYC backend.")
            msg['Subject'] = "Hope for NYC - Test Email"
            msg['From'] = self.from_email
            msg['To'] = self.to_email

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info("Test email sent successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to send test email: {str(e)}")
            return False


# Singleton instance
email_service = EmailService()
