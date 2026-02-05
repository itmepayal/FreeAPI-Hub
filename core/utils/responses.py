# =============================================================
# Third-Party
# =============================================================
from rest_framework.response import Response
from rest_framework import status

# =============================================================
# API Response Helper
# =============================================================
def api_response(
    *,
    message: str,
    data=None,
    errors=None,
    status_code: int = status.HTTP_200_OK
):
    # Step 1 — Determine success based on status code
    success = 200 <= status_code < 300

    # Step 2 — Build base response payload
    payload = {
        "success": success,
        "message": message,
    }

    # Step 3 — Add optional data if provided
    if data is not None:
        payload["data"] = data

    # Step 4 — Add optional errors if provided
    if errors is not None:
        payload["errors"] = errors

    # Step 5 — Return DRF Response object
    return Response(payload, status=status_code)
