from flask import Flask, request, jsonify
from datetime import datetime, timezone
from collections import deque
import os

app = Flask(__name__)
reports = deque(maxlen=100)

@app.get("/")
def health():
    return jsonify({"status": "running"})

@app.post("/webhook")
def webhook():
    if request.headers.get("X-Webhook-Token") != os.environ.get("WEBHOOK_TOKEN"):
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

if __name__ == "__main__":
    app.run()
