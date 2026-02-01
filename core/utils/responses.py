from rest_framework.response import Response
from rest_framework import status

def api_response(
    *,
    message: str,
    data=None,
    errors=None,
    status_code: int = status.HTTP_200_OK
):
    success = 200 <= status_code < 300
    payload = {
        "success": success,
        "message": message,
    }
    if data is not None:
        payload["data"] = data

    if errors is not None:
        payload["errors"] = errors
    
    return Response(payload, status=status_code)
