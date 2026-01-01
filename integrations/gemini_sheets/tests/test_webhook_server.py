import unittest
import os
from unittest.mock import patch, MagicMock
from flask import Flask

# Ensure project root is on PYTHONPATH
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.append(str(PROJECT_ROOT))

from integrations.gemini_sheets import webhook_server

class TestWebhookServer(unittest.TestCase):
    @patch('integrations.gemini_sheets.webhook_server.sync_once')
    def test_gio_update_success(self, mock_sync):
        # Create a test client for the Flask app
        app = webhook_server.app
        app.testing = True
        client = app.test_client()
        response = client.post('/gio-update')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'success', response.data)
        mock_sync.assert_called_once()

    @patch('integrations.gemini_sheets.webhook_server.sync_once')
    def test_gio_update_invalid_token(self, mock_sync):
        os.environ['GIO_WEBHOOK_SECRET'] = 'secret123'
        app = webhook_server.app
        app.testing = True
        client = app.test_client()
        # No token header
        response = client.post('/gio-update')
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Invalid token', response.data)
        mock_sync.assert_not_called()
        # Clean up env
        del os.environ['GIO_WEBHOOK_SECRET']

if __name__ == '__main__':
    unittest.main()
