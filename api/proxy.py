import os
import requests


# Vercel expects a top-level callable named `handler`
def handler(request):
    target = os.getenv("TARGET_URL")

    if not target:
        return {
            "statusCode": 500,
            "headers": {"content-type": "text/plain"},
            "body": "TARGET_URL not configured",
        }

    if request.method != "POST":
        return {
            "statusCode": 405,
            "headers": {"Allow": "POST", "content-type": "text/plain"},
            "body": "Only POST allowed",
        }

    try:
        headers = {
            k: v
            for k, v in request.headers.items()
            if k.lower() not in ("host", "content-length", "connection")
        }

        data = getattr(request, "body", None)
        if data is None and hasattr(request, "get_data"):
            data = request.get_data()

        resp = requests.post(
            target, headers=headers, params=request.args, data=data, timeout=9
        )

        return {
            "statusCode": resp.status_code,
            "headers": {
                "content-type": resp.headers.get("content-type", "text/plain")
            },
            "body": resp.text,
        }

    except Exception as e:
        print("❌ proxy error:", e)
        return {
            "statusCode": 502,
            "headers": {"content-type": "text/plain"},
            "body": f"Proxy error: {e}",
        }
