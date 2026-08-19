import os
import subprocess
import sys

import sentry_sdk
import structlog
from flask import Flask, jsonify, request
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_dsn = os.environ.get("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0
    )

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

app = Flask(__name__)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "online", "service": "Biscuit Scraper Cloud Engine"}), 200

@app.route("/trigger", methods=["POST"])
def trigger():
    """
    Webhook chamado pelo site para disparar a raspagem em nuvem no Google Cloud Run.
    """
    try:
        data = request.json or {}
        plataforma = data.get("plataforma", "todos")
        user_id = data.get("user_id") or os.environ.get("SUPABASE_USER_ID")

        logger.info("webhook_received", plataforma=plataforma, user_id=user_id)

        # Executa o main.py em subprocesso na nuvem
        cmd = [sys.executable, "src/main.py", "--plataforma", plataforma]
        if user_id:
            env = os.environ.copy()
            env["SUPABASE_USER_ID"] = user_id
            proc = subprocess.Popen(cmd, env=env)
        else:
            proc = subprocess.Popen(cmd)

        return jsonify({
            "success": True,
            "message": "Raspagem iniciada com sucesso no Google Cloud!",
            "pid": proc.pid
        }), 200

    except Exception as e:
        logger.error("webhook_error", error=str(e), exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
