#!/usr/bin/env python3
"""
📊 LIVE DASHBOARD - SOVEREIGNSHADOW.AI
Real-time system monitoring with professional interface
"""

import json
import time
import os
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class LiveDashboard:
    def __init__(self):
        self.system_root = Path("/Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]")
        self.state_file = self.system_root / "state" / "monitoring_status.json"
        self.hedge_file = self.system_root / "state" / "hedge_execution_final.json"
        self.log_file = self.system_root / "logs" / "shadow_hedge_log.json"
        
        # Create directories if they don't exist
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def read_system_state(self) -> dict:
        """Read current system state from JSON files"""
        state = {
            "system_status": "UNKNOWN",
            "portfolio_value": 0.0,
            "daily_pnl": 0.0,
            "win_rate": 0.0,
            "total_trades": 0,
            "risk_level": "UNKNOWN",
            "timestamp": datetime.now().isoformat(),
            "mode": "PAPER_TRADING" if os.getenv('DRY_RUN', '1') == '1' else "LIVE"
        }
        
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    file_state = json.load(f)
                    state.update(file_state)
        except Exception as e:
            console.print(f"[red]Error reading state: {e}[/red]")
        
        return state
    
    def create_status_table(self, state: dict) -> Table:
        """Create system status table"""
        table = Table(title="🚀 SovereignShadow.Ai Live Status")
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Value", style="green", width=15)
        table.add_column("Status", style="yellow", width=20)
        
        # System Status
        status_color = "🟢" if state.get("system_status") == "ACTIVE" else "🔴"
        table.add_row("System", "SovereignShadow.Ai", f"{status_color} {state.get('system_status', 'UNKNOWN')}")
        
        # Trading Mode
        mode_color = "🧪" if state.get("mode") == "PAPER_TRADING" else "🚀"
        table.add_row("Mode", state.get("mode", "UNKNOWN"), mode_color)
        
        # Portfolio Value
        portfolio_value = state.get("portfolio_value", 0.0)
        table.add_row("Portfolio", f"${portfolio_value:,.2f}", "📈")
        
        # Daily P&L
        daily_pnl = state.get("daily_pnl", 0.0)
        pnl_color = "📈" if daily_pnl >= 0 else "📉"
        table.add_row("Daily P&L", f"${daily_pnl:,.2f}", pnl_color)
        
        # Win Rate
        win_rate = state.get("win_rate", 0.0)
        win_color = "🎯" if win_rate >= 0.6 else "⚠️" if win_rate >= 0.5 else "❌"
        table.add_row("Win Rate", f"{win_rate:.1%}", win_color)
        
        # Total Trades
        total_trades = state.get("total_trades", 0)
        table.add_row("Total Trades", str(total_trades), "📊")
        
        # Risk Level
        risk_level = state.get("risk_level", "UNKNOWN")
        risk_color = "🟢" if risk_level == "LOW" else "🟡" if risk_level == "MEDIUM" else "🔴"
        table.add_row("Risk Level", risk_level, risk_color)
        
        # Last Update
        last_update = state.get("timestamp", datetime.now().isoformat())
        table.add_row("Last Update", last_update.split('T')[1][:8], "🕐")
        
        return table
    
    def create_validation_table(self, state: dict) -> Table:
        """Create paper trading validation table"""
        table = Table(title="🧪 Paper Trading Validation")
        table.add_column("Criteria", style="cyan", width=25)
        table.add_column("Current", style="green", width=15)
        table.add_column("Target", style="yellow", width=15)
        table.add_column("Status", style="white", width=15)
        
        # Validation criteria
        win_rate = state.get("win_rate", 0.0)
        total_trades = state.get("total_trades", 0)
        days_running = self._calculate_days_running()
        
        # Win Rate
        win_status = "✅" if win_rate >= 0.55 else "⏳" if win_rate > 0 else "❌"
        table.add_row("Win Rate", f"{win_rate:.1%}", "≥55%", win_status)
        
        # Total Trades
        trades_status = "✅" if total_trades >= 20 else "⏳"
        table.add_row("Total Trades", str(total_trades), "≥20", trades_status)
        
        # Days Running
        days_status = "✅" if days_running >= 14 else "⏳"
        table.add_row("Days Running", str(days_running), "≥14", days_status)
        
        # Risk Management
        risk_ok = state.get("risk_level") in ["LOW", "MEDIUM"]
        risk_status = "✅" if risk_ok else "❌"
        table.add_row("Risk Management", "OK" if risk_ok else "ISSUE", "Compliant", risk_status)
        
        # Overall Status
        overall_ready = win_rate >= 0.55 and total_trades >= 20 and days_running >= 14 and risk_ok
        overall_status = "🚀 READY" if overall_ready else "⏳ VALIDATING"
        table.add_row("Overall Status", overall_status, "READY", "🎯")
        
        return table
    
    def _calculate_days_running(self) -> int:
        """Calculate days since validation started"""
        try:
            if self.log_file.exists():
                with open(self.log_file, 'r') as f:
                    logs = json.load(f)
                    if logs and len(logs) > 0:
                        first_entry = logs[0]
                        start_date = datetime.fromisoformat(first_entry.get("timestamp", datetime.now().isoformat()))
                        return (datetime.now() - start_date).days
        except:
            pass
        return 0
    
    def create_recommendation_panel(self, state: dict) -> Panel:
        """Create recommendation panel"""
        win_rate = state.get("win_rate", 0.0)
        total_trades = state.get("total_trades", 0)
        days_running = self._calculate_days_running()
        risk_level = state.get("risk_level", "UNKNOWN")
        
        if win_rate >= 0.55 and total_trades >= 20 and days_running >= 14 and risk_level in ["LOW", "MEDIUM"]:
            recommendation = "🚀 READY FOR LIVE TRADING"
            color = "green"
            details = [
                "✅ All validation criteria met",
                "✅ Win rate above 55%",
                "✅ Sufficient trade history",
                "✅ Risk management validated",
                "",
                "Next steps:",
                "1. Configure live API keys",
                "2. Set starting capital ($100-500)",
                "3. Deploy production environment"
            ]
        else:
            recommendation = "⏳ CONTINUE VALIDATION"
            color = "yellow"
            details = [
                "Paper trading validation in progress",
                "",
                "Requirements:",
                f"• Win rate: {win_rate:.1%} / 55% target",
                f"• Trades: {total_trades} / 20 minimum",
                f"• Days: {days_running} / 14 minimum",
                f"• Risk: {risk_level}",
                "",
                "Continue monitoring until all criteria met"
            ]
        
        return Panel(
            "\n".join(details),
            title=recommendation,
            border_style=color
        )
    
    def create_layout(self, state: dict) -> Layout:
        """Create dashboard layout"""
        layout = Layout()
        
        layout.split_column(
            Layout(Panel(self.create_status_table(state), border_style="blue"), name="status"),
            Layout(Panel(self.create_validation_table(state), border_style="green"), name="validation"),
            Layout(self.create_recommendation_panel(state), name="recommendation")
        )
        
        layout["status"].size = 12
        layout["validation"].size = 10
        layout["recommendation"].size = 8
        
        return layout
    
    def run_dashboard(self):
        """Run live dashboard"""
        console.print("[bold blue]🚀 Starting SovereignShadow.Ai Live Dashboard[/bold blue]")
        console.print("[dim]Press Ctrl+C to stop[/dim]")
        
        try:
            with Live(self.create_layout(self.read_system_state()), refresh_per_second=1, screen=True) as live:
                while True:
                    state = self.read_system_state()
                    live.update(self.create_layout(state))
                    time.sleep(5)  # Update every 5 seconds
                    
        except KeyboardInterrupt:
            console.print("\n[yellow]Dashboard stopped by user[/yellow]")

def main():
    """Main function"""
    dashboard = LiveDashboard()
    dashboard.run_dashboard()

if __name__ == "__main__":
    main()
