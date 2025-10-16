import os
import requests

# ✅ Entry point function Vercel looks for
def handler(request):
    TARGET_URL = os.getenv("TARGET_URL")

    if not TARGET_URL:
        return {
            "statusCode": 500,
            "headers": {"content-type": "text/plain"},
            "body": "TARGET_URL not configured"
        }

    if request.method != "POST":
        return {
            "statusCode": 405,
            "headers": {"Allow": "POST", "content-type": "text/plain"},
            "body": "Only POST requests are allowed"
        }

    try:
        # Forward headers safely
        headers = {k: v for k, v in request.headers.items()
                   if k.lower() not in ("host", "content-length", "connection", "accept-encoding")}
        
        # Get the body safely
        data = getattr(request, "body", None)
        if data is None and hasattr(request, "get_data"):
            data = request.get_data()

        # Forward to target
        resp = requests.post(
            TARGET_URL,
            headers=headers,
            params=request.args,
            data=data,
            timeout=9
        )

        return {
            "statusCode": resp.status_code,
            "headers": {"content-type": resp.headers.get("content-type", "text/plain")},
            "body": resp.text
        }

    except Exception as e:
        print(f"❌ Proxy error: {e}")
        return {
            "statusCode": 502,
            "headers": {"content-type": "text/plain"},
            "body": f"Proxy error: {e}"
        }
