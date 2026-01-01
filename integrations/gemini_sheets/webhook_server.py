#!/usr/bin/env python3
"""
webhook_server.py – Simple Flask server to receive real‑time updates from Google Apps Script
and trigger an immediate sync of Google Sheets data into BRAIN.json.

Expected POST payload (JSON) can be empty – the server only cares that a request arrived.
An optional secret token can be set via the GIO_WEBHOOK_SECRET environment variable for
basic authentication.
"""
import os
import logging
from pathlib import Path
from flask import Flask, request, jsonify

# Ensure project root is on PYTHONPATH for imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
import sys
sys.path.append(str(PROJECT_ROOT))

from integrations.gemini_sheets.sync_brain import sync_once
from integrations.gemini_sheets.sheets_client import SheetsClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Optional secret token for simple security
# (secret will be read per request)

@app.route("/gio-update", methods=["POST"])
def gio_update():
    # Verify secret if set
    secret = os.getenv("GIO_WEBHOOK_SECRET")
    if secret:
        token = request.headers.get("X-Webhook-Token")
        if token != secret:
            logger.warning("Invalid webhook token received")
            return jsonify({"error": "Invalid token"}), 403
    logger.info("Received GIO webhook – triggering sync")
    client = SheetsClient()
    try:
        sync_once(client)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        return jsonify({"error": str(e)}), 500


