import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Ensure project root is on PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

from integrations.gemini_sheets import sync_brain
from integrations.gemini_sheets.sheets_client import SheetsClient

class TestSyncBrain(unittest.TestCase):
    @patch('integrations.gemini_sheets.sheets_client.SheetsClient')
    @patch('integrations.gemini_sheets.sync_brain.load_brain')
    @patch('integrations.gemini_sheets.sync_brain.write_brain')
    def test_sync_once_success(self, mock_write, mock_load, mock_client_cls):
        # Mock client instance
        mock_client = MagicMock()
        mock_client.connect.return_value = True
        mock_client.get_all_data.return_value = {
            'portfolio': {'positions': [], 'total_value': 0},
            'signals': [],
            'research': [],
            'fetched_at': '2025-01-01T00:00:00Z',
            'sheet_id': 'dummy_id',
            'sheet_url': 'https://example.com'
        }
        mock_client_cls.return_value = mock_client
        mock_load.return_value = {}

        sync_brain.sync_once(mock_client)
        # Verify that write_brain was called with merged data
        self.assertTrue(mock_write.called)
        written_data = mock_write.call_args[0][0]
        self.assertIn('portfolio', written_data)
        self.assertIn('signals', written_data)
        self.assertIn('research', written_data)
        self.assertEqual(written_data['last_sync'], '2025-01-01T00:00:00Z')

    @patch('integrations.gemini_sheets.sheets_client.SheetsClient')
    def test_sync_once_no_connection(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client.connect.return_value = False
        mock_client_cls.return_value = mock_client
        # sync_once should simply return without exception
        sync_brain.sync_once(mock_client)
        # Ensure get_all_data was never called
        self.assertFalse(mock_client.get_all_data.called)

if __name__ == '__main__':
    unittest.main()
