from flask import Flask, request, jsonify
from datetime import datetime, timezone
from collections import deque
import os
import hmac

app = Flask(__name__)
reports = deque(maxlen=100)

@app.get("/")
def health():
    return jsonify({"status": "running"})

@app.post("/webhook")
def webhook():
    expected_token = os.environ.get("WEBHOOK_TOKEN")

    if not expected_token:
        return jsonify({"error": "Server configuration error"}), 500

    provided_token = (
        request.headers.get("X-Webhook-Token")
        or request.args.get("token", "")
    )

    if not hmac.compare_digest(provided_token, expected_token):
        return jsonify({"error": "Unauthorized"}), 401

    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify({"error": "Expected JSON object"}), 400

    reports.append({
        "received_at": datetime.now(timezone.utc).isoformat(),
        "payload": payload
    })

    print("Campaign report received:", payload, flush=True)

    return jsonify({"status": "received"}), 200

@app.get("/reports")
def get_reports():
    if request.headers.get("X-Webhook-Token") != os.environ.get("WEBHOOK_TOKEN"):
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify(list(reports))
    
@app.delete("/reports")
def clear_reports():
    expected_token = os.environ.get("WEBHOOK_TOKEN")

    if not expected_token:
        return jsonify({"error": "Server configuration error"}), 500

    provided_token = request.headers.get("X-Webhook-Token", "")

    if not hmac.compare_digest(provided_token, expected_token):
        return jsonify({"error": "Unauthorized"}), 401

    deleted_count = len(reports)
    reports.clear()

    return jsonify({
        "status": "success",
        "message": "All previous reports cleared",
        "deleted_count": deleted_count
    }), 200
    
if __name__ == "__main__":
    app.run()
