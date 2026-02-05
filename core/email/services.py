# =============================================================
# Standard Library
# =============================================================
import logging

# =============================================================
# Third-Party
# =============================================================
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# =============================================================
# Django Settings
# =============================================================
from django.conf import settings

# =============================================================
# Logger
# =============================================================
logger = logging.getLogger(__name__)


# =============================================================
# SendGrid Email Sender
# =============================================================
def send_email(
    *,
    to_email: str,
    template_id: str,
    dynamic_data: dict,
    subject: str | None = None,
):
    try:
        # Step 1 — Create Mail object
        mail = Mail(
            from_email=settings.EMAIL_FROM,  
            to_emails=to_email,          
        )

        # Step 2 — Optionally set email subject
        if subject:
            mail.subject = subject

        # Step 3 — Set dynamic template ID
        mail.template_id = template_id

        # Step 4 — Provide dynamic template data
        mail.dynamic_template_data = dynamic_data

        # Step 5 — Initialize SendGrid client
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)

        # Step 6 — Send the email
        response = sg.send(mail)

        # Step 7 — Log non-success responses
        if response.status_code not in (200, 202):
            logger.error(
                "SendGrid failed: %s %s",
                response.status_code,
                response.body.decode() if hasattr(response.body, "decode") else response.body,
            )

        # Step 8 — Return SendGrid response object
        return response

    except Exception as e:
        # Step 9 — Log the error body if available
        if hasattr(e, "body") and e.body:
            logger.error(
                "SendGrid error body: %s",
                e.body.decode() if hasattr(e.body, "decode") else e.body
            )

        # Step 10 — Log full exception traceback
        logger.exception("SendGrid template email error")

        # Step 11 — Raise clean RuntimeError for service layer
        raise RuntimeError("Failed to send email via SendGrid") from e
