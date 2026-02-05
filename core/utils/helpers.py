# =============================================================
# Client IP Extractor
# =============================================================
def get_client_ip(request) -> str | None:
    # Step 1 — Check forwarded header (proxy / load balancer)
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        # Step 2 — Return first IP in chain
        return x_forwarded_for.split(",")[0].strip()

    # Step 3 — Fallback to direct remote address
    return request.META.get("REMOTE_ADDR")
