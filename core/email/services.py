# Import the SendGrid SDK
import sendgrid

# Helper classes to construct an email object
from sendgrid.helpers.mail import Mail, Email, To

# Django settings to safely access API keys and configs
from django.conf import settings

# Python logging module for error tracking
import logging

# Logger configuration for this module
logger = logging.getLogger(__name__)

# -------------------------------------------------
# SendGrid Email
# -------------------------------------------------
def send_email(
    to_email: str,
    template_id: str,
    dynamic_data: dict,
):
    """
    Send an email using SendGrid Dynamic Templates.
    """
    try:
        # Initialize SendGrid client using API key
        sg = sendgrid.SendGridAPIClient(
            api_key=settings.SENDGRID_API_KEY
        )

        # Create email object with sender and recipient
        mail = Mail(
            from_email=Email(settings.EMAIL_FROM),
            to_emails=To(to_email),
        )

        # Assign SendGrid dynamic template
        mail.template_id = template_id

        # Inject dynamic data into template placeholders
        mail.dynamic_template_data = dynamic_data

        # Send email via SendGrid API
        response = sg.send(mail)

        # Validate SendGrid response
        if response.status_code not in (200, 202):
            logger.error(
                f"SendGrid template email failed: "
                f"{response.status_code} {response.body}"
            )

    except Exception:
        # Log full exception details for debugging
        logger.exception("SendGrid template email error")

        # Re-raise exception for caller handling
        raise
