#!/usr/bin/env python3
"""
SOVEREIGN SHADOW III - MASTER WORKFLOW AUTOMATION
Orchestrates the entire trading ecosystem through Neural Hub API

WORKFLOW:
1. START SERVICES -> Neural Hub API on port 8000
2. GENERATE SIGNALS -> Smart signals (Fear & Greed, Funding, DEX)
3. SCAN SWARM -> Trading swarm scans 70+ assets
4. VALIDATE -> Ladder system validates with ray score
5. PRESENT -> Show opportunities for approval
6. EXECUTE -> Paper/Live trade through exchanges
7. TRACK -> Profit tracker monitors P&L
8. SIPHON -> Auto-withdraw 30% to Ledger

USAGE:
    python bin/sovereign_workflow.py                 # Full workflow
    python bin/sovereign_workflow.py --signals       # Just signals
    python bin/sovereign_workflow.py --ticker        # Live ticker
    python bin/sovereign_workflow.py --portfolio     # Portfolio status
    python bin/sovereign_workflow.py --workflow      # Show workflow guide
"""

import os
import sys
import json
import time
import argparse
import requests
from datetime import datetime
from pathlib import Path

API_BASE = "http://localhost:8000"
PROJECT_ROOT = Path(__file__).parent.parent

# Rich for beautiful output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
except ImportError:
    os.system("pip3 install rich")
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box

console = Console()


def check_api_health():
    """Check if Neural Hub is running"""
    try:
        resp = requests.get(f"{API_BASE}/", timeout=5)
        return resp.status_code == 200
    except:
        return False


def start_neural_hub():
    """Start the Neural Hub if not running"""
    if check_api_health():
        console.print("[green]Neural Hub already running[/]")
        return True

    console.print("[yellow]Starting Neural Hub...[/]")
    import subprocess
    subprocess.Popen(
        ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=str(PROJECT_ROOT / "neural_hub" / "backend"),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(3)
    return check_api_health()


def get_smart_signals():
    """Get smart signals from proven alpha sources"""
    console.print("\n[cyan]Fetching Smart Signals...[/]")

    # First try to get existing signals
    resp = requests.get(f"{API_BASE}/api/swarm/smart-signals", timeout=15)
    data = resp.json()

    if "error" in data:
        # Generate fresh signals
        console.print("[yellow]Generating fresh signals...[/]")
        resp = requests.post(f"{API_BASE}/api/swarm/smart-signals/generate", timeout=60)
        data = resp.json().get("signals", {})

    return data


def get_best_signals():
    """Get best signals from 70-asset scan"""
    console.print("\n[cyan]Fetching Best Signals (70 assets)...[/]")
    resp = requests.get(f"{API_BASE}/api/swarm/best-signals", timeout=15)
    return resp.json()


def get_swarm_status():
    """Get trading swarm status"""
    resp = requests.get(f"{API_BASE}/api/swarm/status", timeout=10)
    return resp.json()


def get_market_ticker():
    """Get market ticker prices"""
    resp = requests.get(f"{API_BASE}/api/ticker/prices", timeout=15)
    return resp.json()


def get_portfolio_ticker():
    """Get portfolio with real-time values"""
    resp = requests.get(f"{API_BASE}/api/ticker/portfolio", timeout=15)
    return resp.json()


def display_signals(smart_signals, best_signals):
    """Display signals in a nice format"""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]SOVEREIGN SHADOW III - SIGNAL CENTER[/]",
        border_style="cyan"
    ))

    # Smart Signals (Proven Alpha)
    if "market_state" in smart_signals:
        fng = smart_signals["market_state"]["fear_greed"]
        fng_val = fng["value"]

        if fng_val <= 25:
            fng_style = "bold bright_green"
            fng_status = "OPTIMAL BUY ZONE"
        elif fng_val <= 40:
            fng_style = "green"
            fng_status = "Accumulation"
        elif fng_val >= 75:
            fng_style = "bold bright_red"
            fng_status = "TAKE PROFITS"
        elif fng_val >= 60:
            fng_style = "red"
            fng_status = "Caution"
        else:
            fng_style = "yellow"
            fng_status = "Neutral"

        console.print(f"\n[{fng_style}]Fear & Greed: {fng_val} ({fng['classification']}) - {fng_status}[/]")

        # Signal table
        table = Table(title="Smart Signals (Proven Alpha)", box=box.ROUNDED)
        table.add_column("Asset", style="bold")
        table.add_column("Action", justify="center")
        table.add_column("Confidence", justify="right")
        table.add_column("ROI", justify="center")
        table.add_column("Reasons")

        for sig in smart_signals.get("signals", []):
            action = sig["action"]
            color = "green" if "BUY" in action else "red" if "SELL" in action else "white"
            table.add_row(
                sig["symbol"],
                f"[{color}]{action}[/]",
                f"{sig['confidence']}%",
                sig["roi_potential"],
                sig["reasons"][0] if sig["reasons"] else ""
            )

        console.print(table)

    # Best Signals (70 Assets)
    if "buy_signals" in best_signals or "sell_signals" in best_signals:
        console.print()

        buy_sigs = best_signals.get("buy_signals", [])
        sell_sigs = best_signals.get("sell_signals", [])

        if buy_sigs:
            table = Table(title=f"Best BUY Signals ({len(buy_sigs)} found)", box=box.ROUNDED)
            table.add_column("Asset", style="bold green")
            table.add_column("Confidence", justify="right")
            table.add_column("Risk", justify="center")

            for sig in buy_sigs[:5]:
                table.add_row(sig["symbol"], f"{sig['confidence']}%", sig.get("risk_level", ""))
            console.print(table)

        if sell_sigs:
            table = Table(title=f"SELL Signals ({len(sell_sigs)} found)", box=box.ROUNDED)
            table.add_column("Asset", style="bold red")
            table.add_column("Confidence", justify="right")
            table.add_column("Reasoning")

            for sig in sell_sigs[:5]:
                table.add_row(sig["symbol"], f"{sig['confidence']}%", sig.get("reasoning", "")[:50] + "...")
            console.print(table)


def display_portfolio(portfolio):
    """Display portfolio status"""
    console.print()
    console.print(Panel.fit(
        "[bold yellow]LEDGER COLD STORAGE[/]",
        border_style="yellow"
    ))

    table = Table(box=box.DOUBLE)
    table.add_column("Asset", style="bold")
    table.add_column("Amount", justify="right")
    table.add_column("Price", justify="right")
    table.add_column("Value", justify="right")
    table.add_column("24h", justify="right")

    for symbol, data in portfolio.get("holdings", {}).items():
        change = data.get("change_24h", 0)
        change_style = "green" if change >= 0 else "red"
        table.add_row(
            symbol,
            f"{data['amount']:.4f}",
            f"${data['price']:,.2f}",
            f"${data['value']:,.2f}",
            f"[{change_style}]{change:+.2f}%[/]"
        )

    table.add_row("", "", "", "", "")
    table.add_row("TOTAL", "", "", f"[bold]${portfolio.get('total_value', 0):,.2f}[/]", "")
    table.add_row("DEBT", "GHO", "", f"[red]-${portfolio.get('aave_debt', 0):,.2f}[/]", "")
    table.add_row("NET", "", "", f"[bold green]${portfolio.get('net_worth', 0):,.2f}[/]", "")

    console.print(table)


def display_ticker(ticker):
    """Display market ticker with heat map"""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]MARKET HEAT MAP[/]",
        border_style="cyan"
    ))

    prices = ticker.get("prices", {})

    # Sort by change
    sorted_prices = sorted(prices.items(), key=lambda x: x[1].get("change_24h", 0), reverse=True)

    table = Table(box=box.ROUNDED)
    table.add_column("Asset", style="bold")
    table.add_column("Price", justify="right")
    table.add_column("24h Change", justify="right")
    table.add_column("Heat", justify="center")

    for symbol, data in sorted_prices:
        change = data.get("change_24h", 0)
        heat = data.get("heat", "")

        if change >= 5:
            change_style = "bold bright_green"
            heat_icon = " HOT"
        elif change >= 0:
            change_style = "green"
            heat_icon = " WARM"
        elif change >= -5:
            change_style = "red"
            heat_icon = " COOL"
        else:
            change_style = "bold bright_red"
            heat_icon = " COLD"

        table.add_row(
            symbol,
            f"${data['price']:,.2f}" if data['price'] >= 1 else f"${data['price']:.6f}",
            f"[{change_style}]{change:+.2f}%[/]",
            heat_icon
        )

    console.print(table)


def show_workflow_guide():
    """Show the complete workflow guide"""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]SOVEREIGN SHADOW III - COMPLETE API WORKFLOW[/]",
        border_style="cyan"
    ))

    guide = """
[bold]COMPLETE ENDPOINT REFERENCE[/]

[bold cyan]CORE ENDPOINTS:[/]
  GET  /api/sovereign/unified      - Portfolio + prices + signals
  GET  /api/sovereign/complete     - EVERYTHING in one call
  GET  /api/sovereign/brain        - Direct BRAIN.json access

[bold yellow]SIPHON PROTOCOL (30% to Ledger):[/]
  GET  /api/sovereign/siphon           - Status + addresses
  POST /api/sovereign/siphon/dry-run   - Simulate withdrawal
  POST /api/sovereign/siphon/execute   - LIVE (confirm=true)

[bold green]PROFIT TRACKING:[/]
  GET  /api/sovereign/profit              - P&L across exchanges
  GET  /api/sovereign/profit/recommendations - What to withdraw

[bold magenta]LADDER SYSTEM (Entry/Exit Tiers):[/]
  GET  /api/sovereign/ladder           - Active ladder status
  POST /api/sovereign/ladder/validate  - Validate with ray score
  POST /api/sovereign/ladder/deploy    - Deploy 6-tier ladder

[bold blue]TRADING SWARM:[/]
  GET  /api/swarm/status               - Swarm config + psychology
  POST /api/swarm/scan?scan_type=X     - Run swarm scan
  GET  /api/swarm/intelligence         - AI swarm P&L
  GET  /api/swarm/smart-signals        - Proven alpha signals
  POST /api/swarm/smart-signals/generate - Fresh signals
  GET  /api/swarm/best-signals         - 70-asset scan results

[bold red]MARKET TICKER:[/]
  GET  /api/ticker/prices              - Heat map prices
  GET  /api/ticker/portfolio           - Portfolio values

[bold]ALPHA SOURCES:[/]
  GET  /api/alpha/sentiment            - Fear & Greed + social
  GET  /api/alpha/onchain              - DEX volume + TVL
  GET  /api/alpha/sniper/{chain}       - New token launches
  GET  /api/alpha/combined             - All alpha combined

[bold cyan]EXAMPLE WORKFLOW:[/]

1. Check market state:
   curl http://localhost:8000/api/swarm/smart-signals

2. If Fear & Greed < 30 (buy zone):
   curl -X POST http://localhost:8000/api/swarm/scan?scan_type=full

3. Validate signal:
   curl -X POST http://localhost:8000/api/sovereign/ladder/validate \\
     -H "Content-Type: application/json" \\
     -d '{"symbol":"BTC","entry_price":95000,"tp1_price":100000}'

4. If valid (ray score > 7), deploy paper ladder:
   curl -X POST "http://localhost:8000/api/sovereign/ladder/deploy?capital=50&mode=paper"

5. Monitor with ticker:
   python3 bin/market_ticker.py

6. After profit, run siphon:
   curl -X POST http://localhost:8000/api/sovereign/siphon/dry-run
"""

    console.print(guide)


def run_full_workflow():
    """Run the complete workflow"""
    console.print(Panel.fit(
        f"[bold cyan]SOVEREIGN SHADOW III - TRADING WORKFLOW[/]\n"
        f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/]",
        border_style="cyan"
    ))

    # Step 1: Check API
    if not check_api_health():
        console.print("[red]Neural Hub not running. Starting...[/]")
        if not start_neural_hub():
            console.print("[bold red]Failed to start Neural Hub![/]")
            console.print("Run: cd neural_hub/backend && uvicorn main:app --port 8000")
            return

    console.print("[green]Neural Hub online[/]")

    # Step 2: Check swarm status
    swarm = get_swarm_status()
    psych = swarm.get("psychology", {})
    if not psych.get("trading_allowed", True):
        console.print(f"[bold red]TRADING LOCKED - {psych.get('strikes', 0)}/3 strikes today[/]")
        return

    console.print(f"[green]Trading allowed - {psych.get('strikes', 0)}/3 strikes[/]")

    # Step 3: Get signals
    smart_signals = get_smart_signals()
    best_signals = get_best_signals()

    # Step 4: Display
    display_signals(smart_signals, best_signals)

    # Step 5: Portfolio
    portfolio = get_portfolio_ticker()
    display_portfolio(portfolio)

    # Step 6: Recommendation
    console.print()
    console.print(Panel.fit(
        "[bold]RECOMMENDATION[/]",
        border_style="white"
    ))

    fng = smart_signals.get("market_state", {}).get("fear_greed", {}).get("value", 50)
    if fng <= 25:
        console.print("[bold bright_green]EXTREME FEAR - Historically best buy zone![/]")
        console.print("Consider accumulating BTC, ETH, SOL")
    elif fng <= 40:
        console.print("[green]FEAR - Good accumulation zone[/]")
    elif fng >= 75:
        console.print("[bold bright_red]EXTREME GREED - Take profits![/]")
    else:
        console.print("[yellow]Neutral - Wait for extremes for high-ROI[/]")


def main():
    parser = argparse.ArgumentParser(description="Sovereign Shadow Workflow")
    parser.add_argument("--signals", action="store_true", help="Just show signals")
    parser.add_argument("--ticker", action="store_true", help="Show market ticker")
    parser.add_argument("--portfolio", action="store_true", help="Show portfolio")
    parser.add_argument("--workflow", action="store_true", help="Show workflow guide")
    parser.add_argument("--live-ticker", action="store_true", help="Run live ticker (24/7)")

    args = parser.parse_args()

    if args.workflow:
        show_workflow_guide()
    elif args.signals:
        if not check_api_health():
            console.print("[red]Neural Hub not running![/]")
            return
        smart = get_smart_signals()
        best = get_best_signals()
        display_signals(smart, best)
    elif args.ticker:
        if not check_api_health():
            console.print("[red]Neural Hub not running![/]")
            return
        ticker = get_market_ticker()
        display_ticker(ticker)
    elif args.portfolio:
        if not check_api_health():
            console.print("[red]Neural Hub not running![/]")
            return
        portfolio = get_portfolio_ticker()
        display_portfolio(portfolio)
    elif args.live_ticker:
        # Run the market ticker script
        import subprocess
        subprocess.run(["python3", str(PROJECT_ROOT / "bin" / "market_ticker.py")])
    else:
        run_full_workflow()


if __name__ == "__main__":
    main()
