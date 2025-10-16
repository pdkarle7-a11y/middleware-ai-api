import os
import requests

def handler(request):
    TARGET_URL = os.getenv("TARGET_URL")  # e.g. https://your-droplet-domain.com/api/endpoint

    if not TARGET_URL:
        return {"statusCode": 500, "body": "TARGET_URL not configured"}

    # Rebuild the request headers (except a few hop-by-hop ones)
    forward_headers = {k: v for k, v in request.headers.items()
                       if k.lower() not in ("host", "content-length", "connection")}

    try:
        # Prepare request body if any
        data = None
        if request.method not in ("GET", "HEAD"):
            # raw body for binary or JSON
            data = request.get_data() if hasattr(request, "get_data") else request.body

        # Forward the request
        resp = requests.request(
            method=request.method,
            url=TARGET_URL,
            headers=forward_headers,
            params=request.args,      # forward query parameters
            data=data,
            timeout=9,                # <= 10s limit on free plan
        )

        # Return the upstream response as-is
        return {
            "statusCode": resp.status_code,
            "headers": dict(resp.headers),
            "body": resp.text,
        }

    except requests.exceptions.Timeout:
        return {"statusCode": 504, "body": "Upstream request timed out"}
    except Exception as e:
        return {"statusCode": 502, "body": f"Upstream error: {e}"}
