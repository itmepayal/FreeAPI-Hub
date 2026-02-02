# core/email/services.py

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_email(*, to_email: str, template_id: str, dynamic_data: dict, subject: str | None = None,):
    """
    Send an email using SendGrid Dynamic Templates.
    """
    try:
        mail = Mail(
            from_email=settings.EMAIL_FROM,
            to_emails=to_email,
        )
        
        # Optional Subject
        if subject:
            mail.subject = subject

        # MUST be string
        mail.template_id = template_id

        # Dynamic template variables
        mail.dynamic_template_data = dynamic_data

        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(mail)

        if response.status_code not in (200, 202):
            logger.error(
                f"SendGrid failed: {response.status_code} {response.body}"
            )

        return response

    except Exception as e:
        if hasattr(e, "body"):
            logger.error(e.body.decode())
        logger.exception("SendGrid template email error")
        raise
