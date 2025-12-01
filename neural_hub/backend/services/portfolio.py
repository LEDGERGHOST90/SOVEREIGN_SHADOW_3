#!/usr/bin/env python3
"""
Portfolio Service - Manages portfolio data
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

class PortfolioService:
    """Service for portfolio management"""

    def __init__(self):
        self.brain_file = PROJECT_ROOT / "BRAIN.json"

    async def get_portfolio(self) -> Dict:
        """Get current portfolio from BRAIN.json"""
        try:
            if self.brain_file.exists():
                data = json.loads(self.brain_file.read_text())
                portfolio = data.get("portfolio", {})

                return {
                    "net_worth": portfolio.get("net_worth", 0),
                    "snapshot_time": portfolio.get("snapshot_time", ""),
                    "ledger": portfolio.get("ledger", {}),
                    "exchanges": portfolio.get("exchanges", {}),
                    "aave": portfolio.get("aave", {}),
                    "allocation": portfolio.get("allocation", {}),
                    "trading_capital": 500,  # December campaign
                }

            return {"error": "BRAIN.json not found"}

        except Exception as e:
            return {"error": str(e)}

    async def get_history(self, days: int = 30) -> List[Dict]:
        """Get portfolio history (mock for now)"""
        # Would need actual historical tracking
        return []

    async def update_portfolio(self, updates: Dict) -> bool:
        """Update portfolio data"""
        try:
            if self.brain_file.exists():
                data = json.loads(self.brain_file.read_text())
                data["portfolio"].update(updates)
                data["portfolio"]["snapshot_time"] = datetime.now().isoformat()
                self.brain_file.write_text(json.dumps(data, indent=2))
                return True
            return False
        except:
            return False
