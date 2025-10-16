import os
import requests

def handler(request):
    print("🔹 Function started")

    try:
        target = os.getenv("TARGET_URL")
        print("🔹 TARGET_URL:", target)

        if not target:
            return {
                "statusCode": 500,
                "headers": {"content-type": "text/plain"},
                "body": "TARGET_URL not configured",
            }

        print("🔹 Method:", request.method)

        if request.method != "POST":
            return {
                "statusCode": 405,
                "headers": {"Allow": "POST", "content-type": "text/plain"},
                "body": "Only POST allowed",
            }

        # Some Vercel request objects don’t have get_data()
        data = getattr(request, "body", None)
        print("🔹 Raw body:", data)
        if data is None and hasattr(request, "get_data"):
            data = request.get_data()

        headers = {
            k: v
            for k, v in request.headers.items()
            if k.lower() not in ("host", "content-length", "connection")
        }

        print("🔹 Forwarding to target:", target)

        resp = requests.post(
            target, headers=headers, params=request.args, data=data, timeout=9
        )

        print("🔹 Got response:", resp.status_code)

        return {
            "statusCode": resp.status_code,
            "headers": {
                "content-type": resp.headers.get("content-type", "text/plain")
            },
            "body": resp.text,
        }

    except Exception as e:
        print("❌ Proxy error:", repr(e))
        return {
            "statusCode": 502,
            "headers": {"content-type": "text/plain"},
            "body": f"Proxy error: {e}",
        }
