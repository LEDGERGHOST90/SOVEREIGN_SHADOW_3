#!/usr/bin/env python3
"""
📝 NOTION AUTO-LOGGER
Automatically logs trading activities, AI insights, and system events to Notion

Integrates with:
- Sovereign Legacy Loop logs
- Neural consciousness insights
- Exchange activity
- Portfolio changes
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

class NotionLogger:
    """Automated Notion logging for Sovereign Shadow system"""
    
    def __init__(self, api_key: Optional[str] = None, database_id: Optional[str] = None):
        self.api_key = api_key or os.getenv("NOTION_API_KEY")
        self.database_id = database_id or os.getenv("NOTION_DATABASE_ID")
        self.base_url = "https://api.notion.com/v1"
        self.version = "2022-06-28"
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": self.version
        }
    
    def create_log_entry(self, 
                        phase: str,
                        vault_percent: float,
                        engine_pnl: float,
                        claude_signal: str,
                        system_events: List[str],
                        note_summary: str) -> Dict:
        """Create a new log entry in Notion database"""
        
        data = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Date": {
                    "date": {"start": datetime.utcnow().isoformat()}
                },
                "Phase": {
                    "select": {"name": phase}
                },
                "Vault %": {
                    "number": vault_percent
                },
                "Engine PnL": {
                    "number": engine_pnl
                },
                "Claude Signal": {
                    "rich_text": [{"text": {"content": claude_signal}}]
                },
                "System Event": {
                    "multi_select": [{"name": event} for event in system_events]
                },
                "Note Summary": {
                    "rich_text": [{"text": {"content": note_summary}}]
                }
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/pages",
                headers=self.headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Notion entry created: {phase}")
                return response.json()
            else:
                print(f"⚠️  Notion API error: {response.status_code}")
                print(f"   Response: {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Failed to create Notion entry: {e}")
            return {}
    
    def log_trade_execution(self, trade_data: Dict):
        """Log a trade execution to Notion"""
        
        phase = "Execute"
        vault_percent = trade_data.get("portfolio_growth", 0.0)
        engine_pnl = trade_data.get("pnl", 0.0)
        
        claude_signal = f"Detected {trade_data.get('spread', 0)*100:.2f}% spread on {trade_data.get('pair', 'BTC/USD')}"
        
        system_events = [
            f"{trade_data.get('exchange_buy', 'Exchange')} Buy",
            f"{trade_data.get('exchange_sell', 'Exchange')} Sell",
            "Arbitrage Executed"
        ]
        
        note_summary = (
            f"Executed arbitrage trade: {trade_data.get('pair', 'BTC/USD')}\n"
            f"Buy: {trade_data.get('exchange_buy')} @ ${trade_data.get('buy_price', 0):,.2f}\n"
            f"Sell: {trade_data.get('exchange_sell')} @ ${trade_data.get('sell_price', 0):,.2f}\n"
            f"Spread: {trade_data.get('spread', 0)*100:.2f}%\n"
            f"Net Profit: ${engine_pnl:.2f}"
        )
        
        return self.create_log_entry(
            phase=phase,
            vault_percent=vault_percent,
            engine_pnl=engine_pnl,
            claude_signal=claude_signal,
            system_events=system_events,
            note_summary=note_summary
        )
    
    def log_system_event(self, event_type: str, details: str):
        """Log a general system event"""
        
        return self.create_log_entry(
            phase="Monitor",
            vault_percent=0.0,
            engine_pnl=0.0,
            claude_signal=f"System event: {event_type}",
            system_events=[event_type],
            note_summary=details
        )
    
    def log_daily_summary(self, logs_dir: Path):
        """Parse logs and create daily summary in Notion"""
        
        # Parse recent log files
        log_files = sorted(logs_dir.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not log_files:
            print("No log files found")
            return
        
        latest_log = log_files[0]
        
        # Read last 100 lines
        with open(latest_log, 'r') as f:
            lines = f.readlines()[-100:]
        
        # Extract key information
        trades_executed = sum(1 for line in lines if "TRADE_EXECUTED" in line)
        opportunities_found = sum(1 for line in lines if "OPPORTUNITY" in line)
        errors = sum(1 for line in lines if "ERROR" in line)
        
        summary = (
            f"📊 Daily Summary for {datetime.now().strftime('%Y-%m-%d')}\n\n"
            f"Trades Executed: {trades_executed}\n"
            f"Opportunities Found: {opportunities_found}\n"
            f"Errors: {errors}\n\n"
            f"Philosophy: Fearless. Bold. Smiling through chaos."
        )
        
        events = []
        if trades_executed > 0:
            events.append("Trade Activity")
        if opportunities_found > 0:
            events.append("Opportunities Detected")
        if errors > 0:
            events.append("System Warnings")
        
        return self.create_log_entry(
            phase="Report",
            vault_percent=0.0,
            engine_pnl=0.0,
            claude_signal=f"Daily summary: {trades_executed} trades, {opportunities_found} opportunities",
            system_events=events or ["Daily Check"],
            note_summary=summary
        )
    
    def setup_database_template(self) -> str:
        """Generate Notion database template as Markdown"""
        
        template = """
# Notion Database Setup: Sovereign Shadow Logger

## Create New Database

1. Create a new database in Notion with the following properties:

### Properties:

| Property Name | Type | Options |
|--------------|------|---------|
| **Date** | Date | - |
| **Phase** | Select | Stabilize, Redeploy, Execute, Automate, Compound, Monitor, Report |
| **Vault %** | Number | Format: Percent |
| **Engine PnL** | Number | Format: Dollar |
| **Claude Signal** | Text | - |
| **System Event** | Multi-select | MCP Sync, OKX Trade, Siphon Triggered, Trade Activity, Opportunities Detected, System Warnings |
| **Note Summary** | Text | - |

## Integration Setup:

1. **Get Notion API Key:**
   - Go to https://www.notion.so/my-integrations
   - Click "New integration"
   - Name it "Sovereign Shadow Logger"
   - Copy the Internal Integration Token

2. **Get Database ID:**
   - Open your database in Notion
   - Click "..." menu → "Copy link"
   - Extract ID from URL: notion.so/YOUR_WORKSPACE/DATABASE_ID?v=...
   - Copy the DATABASE_ID part

3. **Share Database with Integration:**
   - Open database in Notion
   - Click "..." menu → "Add connections"
   - Select "Sovereign Shadow Logger"

4. **Add to .env.production:**
   ```
   NOTION_API_KEY=secret_XXXXXXXXXX
   NOTION_DATABASE_ID=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ENABLE_NOTION_LOGGING=true
   ```

## Usage:

```python
from scripts.notion_auto_logger import NotionLogger

# Initialize
logger = NotionLogger()

# Log a trade
logger.log_trade_execution({
    "pair": "BTC/USD",
    "exchange_buy": "Coinbase",
    "exchange_sell": "OKX",
    "buy_price": 125000,
    "sell_price": 125625,
    "spread": 0.005,
    "pnl": 25.50,
    "portfolio_growth": 0.31
})

# Log daily summary
logger.log_daily_summary(Path("/Volumes/LegacySafe/SovereignShadow/logs"))
```

## Automation (CRON):

Add to crontab for automated logging:
```bash
# Log daily summary at 11:59 PM
59 23 * * * cd /Volumes/LegacySafe/SovereignShadow && python3 scripts/notion_auto_logger.py --daily-summary

# Sync logs every 6 hours
0 */6 * * * cd /Volumes/LegacySafe/SovereignShadow && python3 scripts/notion_auto_logger.py --sync
```
"""
        return template


def main():
    """CLI interface for Notion logger"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Notion Auto-Logger for Sovereign Shadow")
    parser.add_argument("--daily-summary", action="store_true", help="Generate daily summary")
    parser.add_argument("--setup", action="store_true", help="Print setup instructions")
    parser.add_argument("--test", action="store_true", help="Test Notion connection")
    
    args = parser.parse_args()
    
    logger = NotionLogger()
    
    if args.setup:
        print(logger.setup_database_template())
        return
    
    if args.test:
        print("🧪 Testing Notion connection...")
        
        if not logger.api_key:
            print("❌ NOTION_API_KEY not set in environment")
            print("   Run with --setup for instructions")
            return
        
        if not logger.database_id:
            print("❌ NOTION_DATABASE_ID not set in environment")
            print("   Run with --setup for instructions")
            return
        
        # Test log entry
        result = logger.log_system_event(
            "System Test",
            "Testing Notion auto-logger integration. Philosophy: Smiling through chaos."
        )
        
        if result:
            print("✅ Notion connection successful!")
        else:
            print("⚠️  Connection test failed - check credentials")
        return
    
    if args.daily_summary:
        print("📊 Generating daily summary...")
        logs_dir = Path("/Volumes/LegacySafe/SovereignShadow/logs")
        logger.log_daily_summary(logs_dir)
        return
    
    # Default: show usage
    parser.print_help()


if __name__ == "__main__":
    main()

