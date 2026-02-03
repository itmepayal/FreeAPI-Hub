# core/email/services.py

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
import logging

# Initialize logger for this module
logger = logging.getLogger(__name__)


def send_email(
    *,
    to_email: str,
    template_id: str,
    dynamic_data: dict,
    subject: str | None = None,
):
    """
    Send an email using SendGrid Dynamic Templates.

    Args:
        to_email (str): Recipient email address.
        template_id (str): SendGrid dynamic template ID.
        dynamic_data (dict): Dictionary containing template variables.
        subject (str, optional): Optional email subject. Defaults to None.

    Returns:
        sendgrid.Response: SendGrid API response object.

    Raises:
        RuntimeError: If sending the email fails for any reason.
    """
    try:
        # ------------------------------
        # Create the Mail object
        # ------------------------------
        mail = Mail(
            from_email=settings.EMAIL_FROM,  # Sender email from Django settings
            to_emails=to_email,              # Recipient email
        )

        # ------------------------------
        # Optional: Set email subject
        # ------------------------------
        if subject:
            mail.subject = subject

        # ------------------------------
        # Set the dynamic template ID
        # This tells SendGrid which template to render
        # ------------------------------
        mail.template_id = template_id

        # ------------------------------
        # Pass dynamic template data
        # Key-value pairs that replace template placeholders
        # ------------------------------
        mail.dynamic_template_data = dynamic_data

        # ------------------------------
        # Initialize SendGrid client
        # ------------------------------
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)

        # Send the email
        response = sg.send(mail)

        # ------------------------------
        # Log any non-successful responses
        # 200 or 202 indicates success
        # ------------------------------
        if response.status_code not in (200, 202):
            logger.error(
                "SendGrid failed: %s %s",
                response.status_code,
                response.body.decode() if hasattr(response.body, "decode") else response.body,
            )

        # Return SendGrid response object
        return response

    except Exception as e:
        # ------------------------------
        # Log the error body if available
        # ------------------------------
        if hasattr(e, "body") and e.body:
            logger.error("SendGrid error body: %s", e.body.decode() if hasattr(e.body, "decode") else e.body)
        
        # Log full exception with traceback
        logger.exception("SendGrid template email error")

        # Raise a clear RuntimeError for service layer handling
        raise RuntimeError("Failed to send email via SendGrid") from e
