import os
import requests

def handler(request):
    TARGET_URL = os.getenv("TARGET_URL")  # e.g. https://your-droplet-domain.com/api/endpoint

    if not TARGET_URL:
        return {"statusCode": 500, "body": "TARGET_URL not configured"}

    # Allow only POST requests
    if request.method != "POST":
        return {
            "statusCode": 405,
            "headers": {"Allow": "POST"},
            "body": "Only POST requests are allowed."
        }

    # Copy incoming headers except hop-by-hop ones
    forward_headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in ("host", "content-length", "connection", "accept-encoding")
    }

    try:
        # Forward the POST body exactly as received
        data = request.get_data() if hasattr(request, "get_data") else getattr(request, "body", None)

        resp = requests.post(
            TARGET_URL,
            headers=forward_headers,
            params=request.args,   # forward query params if any
            data=data,
            timeout=9,             # stay under Vercel 10s limit
        )

        # Forward the exact upstream response back to client
        return {
            "statusCode": resp.status_code,
            "headers": dict(resp.headers),
            "body": resp.text,
        }

    except requests.exceptions.Timeout:
        return {"statusCode": 504, "body": "Upstream request timed out"}
    except Exception as e:
        return {"statusCode": 502, "body": f"Upstream error: {e}"}
