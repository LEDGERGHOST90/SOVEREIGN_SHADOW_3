"""
SS3 BRAIN - Gemini/Google Sheets Integration

This module provides bidirectional sync between:
- Google Sheets (managed by GIO/Gemini)
- BRAIN.json (local state file)

Components:
- sheets_client.py: Google Sheets API wrapper
- sync_brain.py: Sync script (once or daemon mode)
- webhook_server.py: Real-time update receiver

Usage:
    from integrations.gemini_sheets import SheetsClient, BrainSync

    # Read from sheets
    client = SheetsClient()
    client.connect()
    portfolio = client.get_portfolio()

    # Sync to BRAIN.json
    from integrations.gemini_sheets.sync_brain import sync_once
    sync_once(client)
"""

from .sheets_client import SheetsClient

__all__ = ['SheetsClient']
