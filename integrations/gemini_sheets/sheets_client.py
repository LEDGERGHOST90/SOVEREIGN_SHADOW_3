#!/usr/bin/env python3
"""
SS3 BRAIN - Google Sheets Client
Handles all interactions with Google Sheets API
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    print("Missing dependencies. Run: pip install gspread google-auth")
    raise

logger = logging.getLogger(__name__)

# Google Sheets API scopes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file'
]


class SheetsClient:
    """
    Google Sheets API client for SS3 BRAIN integration.

    Handles reading/writing portfolio data, signals, and research
    from the SS3_BRAIN Google Sheet.
    """

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        sheet_id: Optional[str] = None
    ):
        """
        Initialize the Sheets client.

        Args:
            credentials_path: Path to Google service account JSON key
            sheet_id: Google Sheets document ID
        """
        self.credentials_path = credentials_path or os.getenv(
            'GOOGLE_CREDENTIALS_PATH',
            'integrations/gemini_sheets/credentials/google_sheets_key.json'
        )
        self.sheet_id = sheet_id or os.getenv('GOOGLE_SHEETS_ID')

        self.client: Optional[gspread.Client] = None
        self.spreadsheet: Optional[gspread.Spreadsheet] = None

        # Sheet tab names
        self.PORTFOLIO_SHEET = 'Portfolio'
        self.SIGNALS_SHEET = 'Signals'
        self.RESEARCH_SHEET = 'Research'
        self.CONFIG_SHEET = 'Config'

    def connect(self) -> bool:
        """
        Establish connection to Google Sheets.

        Returns:
            bool: True if connection successful
        """
        try:
            # Load credentials
            creds_path = Path(self.credentials_path)
            if not creds_path.exists():
                logger.error(f"Credentials not found: {creds_path}")
                return False

            credentials = Credentials.from_service_account_file(
                str(creds_path),
                scopes=SCOPES
            )

            # Create client
            self.client = gspread.authorize(credentials)

            # Open spreadsheet
            if self.sheet_id:
                self.spreadsheet = self.client.open_by_key(self.sheet_id)
            else:
                # Try to find by name
                self.spreadsheet = self.client.open('SS3_BRAIN')

            logger.info(f"Connected to: {self.spreadsheet.title}")
            return True

        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def get_portfolio(self) -> Dict[str, Any]:
        """
        Fetch current portfolio from Google Sheets.

        Returns:
            Dict containing positions and total value
        """
        if not self.spreadsheet:
            raise ConnectionError("Not connected to Google Sheets")

        try:
            sheet = self.spreadsheet.worksheet(self.PORTFOLIO_SHEET)
            records = sheet.get_all_records()

            positions = []
            total_value = 0

            for row in records:
                if not row.get('Asset'):
                    continue

                value = float(row.get('Value USD', 0) or 0)
                total_value += value

                # Parse P&L percentage
                pnl_str = str(row.get('P&L %', '0'))
                pnl_pct = float(pnl_str.replace('%', '').strip() or 0)

                positions.append({
                    'symbol': row.get('Asset', ''),
                    'quantity': float(row.get('Quantity', 0) or 0),
                    'entry_price': float(row.get('Entry Price', 0) or 0),
                    'current_price': float(row.get('Current Price', 0) or 0),
                    'value_usd': value,
                    'pnl_pct': pnl_pct,
                    'exchange': row.get('Exchange', ''),
                    'last_updated': row.get('Last Updated', '')
                })

            return {
                'positions': positions,
                'total_value': round(total_value, 2),
                'fetched_at': datetime.utcnow().isoformat() + 'Z'
            }

        except Exception as e:
            logger.error(f"Failed to get portfolio: {e}")
            return {'positions': [], 'total_value': 0, 'error': str(e)}

    def get_signals(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch recent signals from Google Sheets.

        Args:
            limit: Maximum number of signals to return

        Returns:
            List of signal dictionaries
        """
        if not self.spreadsheet:
            raise ConnectionError("Not connected to Google Sheets")

        try:
            sheet = self.spreadsheet.worksheet(self.SIGNALS_SHEET)
            records = sheet.get_all_records()

            signals = []
            for row in records[:limit]:
                if not row.get('Timestamp'):
                    continue

                signals.append({
                    'timestamp': row.get('Timestamp', ''),
                    'asset': row.get('Asset', ''),
                    'action': row.get('Action', ''),
                    'confidence': int(row.get('Confidence', 0) or 0),
                    'reasoning': row.get('Reasoning', ''),
                    'status': row.get('Status', 'PENDING')
                })

            return signals

        except Exception as e:
            logger.error(f"Failed to get signals: {e}")
            return []

    def get_research(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch recent research entries from Google Sheets.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of research dictionaries
        """
        if not self.spreadsheet:
            raise ConnectionError("Not connected to Google Sheets")

        try:
            sheet = self.spreadsheet.worksheet(self.RESEARCH_SHEET)
            records = sheet.get_all_records()

            research = []
            for row in records[:limit]:
                if not row.get('Timestamp'):
                    continue

                research.append({
                    'timestamp': row.get('Timestamp', ''),
                    'topic': row.get('Topic', ''),
                    'summary': row.get('Summary', ''),
                    'insights': row.get('Key Insights', ''),
                    'action_items': row.get('Action Items', '')
                })

            return research

        except Exception as e:
            logger.error(f"Failed to get research: {e}")
            return []

    def update_position(
        self,
        symbol: str,
        quantity: float,
        entry_price: float,
        current_price: float,
        exchange: str = ''
    ) -> bool:
        """
        Update or add a position in the portfolio sheet.

        Args:
            symbol: Asset symbol (e.g., 'BTC')
            quantity: Amount held
            entry_price: Average entry price
            current_price: Current market price
            exchange: Exchange name

        Returns:
            bool: True if successful
        """
        if not self.spreadsheet:
            raise ConnectionError("Not connected to Google Sheets")

        try:
            sheet = self.spreadsheet.worksheet(self.PORTFOLIO_SHEET)

            # Find existing row for symbol
            cell = sheet.find(symbol.upper())

            value_usd = quantity * current_price
            pnl_pct = ((current_price - entry_price) / entry_price * 100) if entry_price > 0 else 0

            row_data = [
                symbol.upper(),
                quantity,
                entry_price,
                current_price,
                round(value_usd, 2),
                f"{pnl_pct:.2f}%",
                exchange,
                datetime.utcnow().isoformat() + 'Z'
            ]

            if cell:
                # Update existing row
                row_num = cell.row
                sheet.update(f'A{row_num}:H{row_num}', [row_data])
            else:
                # Append new row
                sheet.append_row(row_data)

            logger.info(f"Updated position: {symbol}")
            return True

        except Exception as e:
            logger.error(f"Failed to update position: {e}")
            return False

    def add_signal(
        self,
        asset: str,
        action: str,
        confidence: int,
        reasoning: str
    ) -> bool:
        """
        Add a new signal to the signals sheet.

        Args:
            asset: Asset symbol
            action: BUY, SELL, or HOLD
            confidence: 0-100 confidence score
            reasoning: Analysis text

        Returns:
            bool: True if successful
        """
        if not self.spreadsheet:
            raise ConnectionError("Not connected to Google Sheets")

        try:
            sheet = self.spreadsheet.worksheet(self.SIGNALS_SHEET)

            row_data = [
                datetime.utcnow().isoformat() + 'Z',
                asset.upper(),
                action.upper(),
                confidence,
                reasoning,
                'PENDING'
            ]

            # Insert at row 2 (after header)
            sheet.insert_row(row_data, 2)

            logger.info(f"Added signal: {action} {asset}")
            return True

        except Exception as e:
            logger.error(f"Failed to add signal: {e}")
            return False

    def add_research(
        self,
        topic: str,
        summary: str,
        insights: str,
        action_items: str = ''
    ) -> bool:
        """
        Add a research entry to the research sheet.

        Args:
            topic: Research topic
            summary: Brief summary
            insights: Key insights
            action_items: Recommended actions

        Returns:
            bool: True if successful
        """
        if not self.spreadsheet:
            raise ConnectionError("Not connected to Google Sheets")

        try:
            sheet = self.spreadsheet.worksheet(self.RESEARCH_SHEET)

            row_data = [
                datetime.utcnow().isoformat() + 'Z',
                topic,
                summary,
                insights,
                action_items
            ]

            # Insert at row 2 (after header)
            sheet.insert_row(row_data, 2)

            logger.info(f"Added research: {topic}")
            return True

        except Exception as e:
            logger.error(f"Failed to add research: {e}")
            return False

    def update_signal_status(self, timestamp: str, new_status: str) -> bool:
        """
        Update the status of a signal.

        Args:
            timestamp: Signal timestamp to find
            new_status: New status (EXECUTED, IGNORED, etc.)

        Returns:
            bool: True if successful
        """
        if not self.spreadsheet:
            raise ConnectionError("Not connected to Google Sheets")

        try:
            sheet = self.spreadsheet.worksheet(self.SIGNALS_SHEET)
            cell = sheet.find(timestamp)

            if cell:
                sheet.update_cell(cell.row, 6, new_status)  # Column F
                logger.info(f"Updated signal status: {new_status}")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to update signal status: {e}")
            return False

    def get_all_data(self) -> Dict[str, Any]:
        """
        Fetch all data from all sheets.

        Returns:
            Dict containing portfolio, signals, and research
        """
        return {
            'portfolio': self.get_portfolio(),
            'signals': self.get_signals(),
            'research': self.get_research(),
            'fetched_at': datetime.utcnow().isoformat() + 'Z',
            'sheet_id': self.sheet_id,
            'sheet_url': f"https://docs.google.com/spreadsheets/d/{self.sheet_id}"
        }


# ============================================
# CLI Interface
# ============================================
if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description='Google Sheets Client for SS3')
    parser.add_argument('--portfolio', action='store_true', help='Get portfolio')
    parser.add_argument('--signals', action='store_true', help='Get signals')
    parser.add_argument('--research', action='store_true', help='Get research')
    parser.add_argument('--all', action='store_true', help='Get all data')

    args = parser.parse_args()

    client = SheetsClient()

    if not client.connect():
        print("Failed to connect to Google Sheets")
        exit(1)

    if args.portfolio:
        data = client.get_portfolio()
        print(json.dumps(data, indent=2))
    elif args.signals:
        data = client.get_signals()
        print(json.dumps(data, indent=2))
    elif args.research:
        data = client.get_research()
        print(json.dumps(data, indent=2))
    elif args.all:
        data = client.get_all_data()
        print(json.dumps(data, indent=2))
    else:
        # Default: show portfolio summary
        portfolio = client.get_portfolio()
        print(f"\nPortfolio Total: ${portfolio['total_value']:,.2f}")
        print(f"Positions: {len(portfolio['positions'])}")
        for pos in portfolio['positions']:
            print(f"  {pos['symbol']}: {pos['quantity']} @ ${pos['current_price']:.4f} = ${pos['value_usd']:.2f}")
