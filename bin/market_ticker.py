#!/usr/bin/env python3
"""
SOVEREIGN SHADOW - 24/7 MARKET TICKER WATCHER
Birdeye.io style heatmap with exchange sections + Ledger portfolio

Features:
- Real-time price updates with color-coded % changes
- Exchange sections: Coinbase, Binance.US, Kraken
- Portfolio totals including Ledger cold storage
- Heat map visualization (green = up, red = down)
- Auto-refresh every 10 seconds
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional

# Rich for beautiful terminal UI
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.style import Style
    from rich import box
except ImportError:
    print("Installing rich library...")
    os.system("pip3 install rich")
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.style import Style
    from rich import box

console = Console()

# Your holdings from BRAIN.json
LEDGER_HOLDINGS = {
    "BTC": {"amount": 0.0157, "address": "bc1q...ledger"},
    "ETH": {"amount": 0.0042, "address": "0x...ledger"},  # As wstETH in Aave
    "XRP": {"amount": 456.0, "address": "r...ledger"},
    "USDC": {"amount": 53.61, "address": "0x...ledger"},
    "wstETH": {"amount": 0.897, "address": "0x...aave"}  # Aave collateral
}

AAVE_DEBT = 360.94  # GHO debt

# Exchange API endpoints
APIS = {
    "coinbase": "https://api.coinbase.com/v2/prices/{}-USD/spot",
    "binance": "https://api.binance.us/api/v3/ticker/24hr?symbol={}USDT",
    "kraken": "https://api.kraken.com/0/public/Ticker?pair={}USD",
    "coingecko": "https://api.coingecko.com/api/v3/simple/price?ids={}&vs_currencies=usd&include_24hr_change=true"
}

# Watchlist by exchange
WATCHLIST = {
    "coinbase": ["BTC", "ETH", "SOL", "XRP", "AVAX", "LINK", "DOT", "UNI", "AAVE", "MATIC"],
    "binance_us": ["BTC", "ETH", "SOL", "XRP", "BNB", "DOGE", "ADA", "SHIB", "LTC", "ATOM"],
    "kraken": ["BTC", "ETH", "SOL", "XRP", "DOT", "ADA", "LINK", "MATIC", "ATOM", "ALGO"]
}

# CoinGecko ID mapping
COINGECKO_IDS = {
    "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "XRP": "ripple",
    "BNB": "binancecoin", "DOGE": "dogecoin", "ADA": "cardano", "AVAX": "avalanche-2",
    "LINK": "chainlink", "DOT": "polkadot", "SHIB": "shiba-inu", "LTC": "litecoin",
    "UNI": "uniswap", "AAVE": "aave", "MATIC": "matic-network", "ATOM": "cosmos",
    "ALGO": "algorand", "wstETH": "wrapped-steth"
}

@dataclass
class AssetData:
    symbol: str
    price: float
    change_24h: float
    volume_24h: float = 0
    exchange: str = ""

def get_coingecko_prices(symbols: List[str]) -> Dict[str, AssetData]:
    """Get prices from CoinGecko (free, reliable)"""
    results = {}

    # Build ID list
    ids = [COINGECKO_IDS.get(s, s.lower()) for s in symbols if s in COINGECKO_IDS]
    if not ids:
        return results

    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies=usd&include_24hr_change=true"
        resp = requests.get(url, timeout=10)
        data = resp.json()

        for symbol in symbols:
            cg_id = COINGECKO_IDS.get(symbol, symbol.lower())
            if cg_id in data:
                results[symbol] = AssetData(
                    symbol=symbol,
                    price=data[cg_id].get("usd", 0),
                    change_24h=data[cg_id].get("usd_24h_change", 0)
                )
    except Exception as e:
        pass

    return results

def get_binance_prices(symbols: List[str]) -> Dict[str, AssetData]:
    """Get prices from Binance.US"""
    results = {}

    try:
        resp = requests.get("https://api.binance.us/api/v3/ticker/24hr", timeout=10)
        data = resp.json()

        for item in data:
            symbol = item["symbol"].replace("USDT", "").replace("USD", "")
            if symbol in symbols:
                results[symbol] = AssetData(
                    symbol=symbol,
                    price=float(item["lastPrice"]),
                    change_24h=float(item["priceChangePercent"]),
                    volume_24h=float(item["volume"]),
                    exchange="binance"
                )
    except:
        pass

    return results

def get_coinbase_prices(symbols: List[str]) -> Dict[str, AssetData]:
    """Get prices from Coinbase"""
    results = {}

    for symbol in symbols:
        try:
            # Spot price
            resp = requests.get(f"https://api.coinbase.com/v2/prices/{symbol}-USD/spot", timeout=5)
            spot = resp.json()
            price = float(spot["data"]["amount"])

            # Try to get 24h change from exchange rates
            results[symbol] = AssetData(
                symbol=symbol,
                price=price,
                change_24h=0,  # Coinbase doesn't give 24h change in free API
                exchange="coinbase"
            )
        except:
            pass

    return results

def color_for_change(change: float) -> str:
    """Get color based on price change"""
    if change >= 5:
        return "bold bright_green"
    elif change >= 2:
        return "green"
    elif change >= 0:
        return "dim green"
    elif change >= -2:
        return "dim red"
    elif change >= -5:
        return "red"
    else:
        return "bold bright_red"

def format_price(price: float) -> str:
    """Format price nicely"""
    if price >= 1000:
        return f"${price:,.2f}"
    elif price >= 1:
        return f"${price:.2f}"
    elif price >= 0.01:
        return f"${price:.4f}"
    else:
        return f"${price:.6f}"

def format_change(change: float) -> Text:
    """Format change with color"""
    color = color_for_change(change)
    arrow = "▲" if change >= 0 else "▼"
    return Text(f"{arrow} {abs(change):.2f}%", style=color)

def create_exchange_table(name: str, assets: Dict[str, AssetData], emoji: str = "📊") -> Table:
    """Create a table for an exchange"""
    table = Table(
        title=f"{emoji} {name}",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        border_style="dim"
    )

    table.add_column("Asset", style="bold white", width=6)
    table.add_column("Price", justify="right", width=12)
    table.add_column("24h", justify="right", width=10)
    table.add_column("Heat", justify="center", width=5)

    for symbol, data in sorted(assets.items(), key=lambda x: abs(x[1].change_24h), reverse=True):
        # Heat indicator
        change = data.change_24h
        if change >= 5:
            heat = "🟢🟢"
        elif change >= 2:
            heat = "🟢"
        elif change >= 0:
            heat = "⚪"
        elif change >= -2:
            heat = "🔴"
        else:
            heat = "🔴🔴"

        table.add_row(
            symbol,
            format_price(data.price),
            format_change(change),
            heat
        )

    return table

def create_portfolio_table(prices: Dict[str, AssetData]) -> Table:
    """Create portfolio summary table"""
    table = Table(
        title="💎 LEDGER COLD STORAGE",
        box=box.DOUBLE,
        show_header=True,
        header_style="bold yellow",
        border_style="yellow"
    )

    table.add_column("Asset", style="bold white", width=8)
    table.add_column("Amount", justify="right", width=12)
    table.add_column("Price", justify="right", width=12)
    table.add_column("Value", justify="right", width=12)
    table.add_column("24h", justify="right", width=10)

    total_value = 0
    total_change = 0

    for symbol, holding in LEDGER_HOLDINGS.items():
        amount = holding["amount"]

        # Get price
        if symbol in prices:
            price = prices[symbol].price
            change = prices[symbol].change_24h
        elif symbol == "wstETH" and "ETH" in prices:
            # wstETH is roughly 1.16x ETH
            price = prices["ETH"].price * 1.16
            change = prices["ETH"].change_24h
        elif symbol == "USDC":
            price = 1.0
            change = 0
        else:
            price = 0
            change = 0

        value = amount * price
        total_value += value
        total_change += value * (change / 100)

        table.add_row(
            symbol,
            f"{amount:.4f}",
            format_price(price),
            format_price(value),
            format_change(change)
        )

    # Add totals
    table.add_row("", "", "", "", "", style="dim")
    table.add_row(
        "TOTAL",
        "",
        "",
        Text(format_price(total_value), style="bold green"),
        Text(f"${total_change:+.2f}", style="green" if total_change >= 0 else "red")
    )

    # AAVE debt
    table.add_row(
        "DEBT",
        "GHO",
        "",
        Text(f"-${AAVE_DEBT:.2f}", style="bold red"),
        ""
    )

    # Net worth
    net = total_value - AAVE_DEBT
    table.add_row(
        "NET",
        "",
        "",
        Text(format_price(net), style="bold bright_green"),
        ""
    )

    return table

def create_smart_signals_panel(prices: Dict[str, AssetData]) -> Panel:
    """Create smart signals summary"""
    # Load latest smart signals if available
    signals_text = ""

    try:
        with open("/Volumes/LegacySafe/SOVEREIGN_SHADOW_3/logs/smart_signals.json") as f:
            data = json.load(f)
            fng = data["market_state"]["fear_greed"]

            # Fear & Greed indicator
            fng_val = fng["value"]
            if fng_val <= 25:
                fng_color = "bold bright_green"
                fng_status = "🟢 OPTIMAL BUY"
            elif fng_val <= 40:
                fng_color = "green"
                fng_status = "🟢 Accumulate"
            elif fng_val >= 75:
                fng_color = "bold bright_red"
                fng_status = "🔴 TAKE PROFITS"
            elif fng_val >= 60:
                fng_color = "red"
                fng_status = "🔴 Caution"
            else:
                fng_color = "yellow"
                fng_status = "⚪ Neutral"

            signals_text = f"[{fng_color}]Fear & Greed: {fng_val} ({fng['classification']})[/]\n"
            signals_text += f"[white]Status: {fng_status}[/]\n\n"

            # Best signal
            for sig in data.get("signals", [])[:2]:
                emoji = "🟢" if "BUY" in sig["action"] else "🔴" if "SELL" in sig["action"] else "⚪"
                signals_text += f"{emoji} {sig['symbol']}: {sig['action']} ({sig['confidence']}%)\n"
    except:
        signals_text = "[dim]Run smart_signals.py to generate[/]"

    return Panel(
        signals_text,
        title="🧠 SMART SIGNALS",
        border_style="cyan"
    )

def create_market_overview() -> Layout:
    """Create the full market overview layout"""
    layout = Layout()

    # Get all prices
    all_symbols = set()
    for symbols in WATCHLIST.values():
        all_symbols.update(symbols)
    all_symbols.update(LEDGER_HOLDINGS.keys())

    # Fetch prices (CoinGecko is most reliable for all)
    prices = get_coingecko_prices(list(all_symbols))

    # Supplement with Binance for volume data
    binance_data = get_binance_prices(WATCHLIST["binance_us"])
    for symbol, data in binance_data.items():
        if symbol in prices:
            prices[symbol].volume_24h = data.volume_24h
            prices[symbol].change_24h = data.change_24h  # Binance has better 24h data

    # Create tables
    coinbase_assets = {s: prices[s] for s in WATCHLIST["coinbase"] if s in prices}
    binance_assets = {s: prices[s] for s in WATCHLIST["binance_us"] if s in prices}
    kraken_assets = {s: prices[s] for s in WATCHLIST["kraken"] if s in prices}

    # Build output
    console.clear()

    # Header
    header = Panel(
        f"[bold cyan]SOVEREIGN SHADOW III[/] - 24/7 Market Ticker\n"
        f"[dim]Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/]",
        border_style="cyan"
    )
    console.print(header)
    console.print()

    # Exchange tables side by side
    from rich.columns import Columns

    exchange_tables = Columns([
        create_exchange_table("COINBASE", coinbase_assets, "🟠"),
        create_exchange_table("BINANCE.US", binance_assets, "🟡"),
        create_exchange_table("KRAKEN", kraken_assets, "🟣")
    ], equal=True, expand=True)

    console.print(exchange_tables)
    console.print()

    # Portfolio and signals
    portfolio_signals = Columns([
        create_portfolio_table(prices),
        create_smart_signals_panel(prices)
    ], equal=False)

    console.print(portfolio_signals)

    # Footer with hotkeys
    console.print()
    console.print(Panel(
        "[dim]Press Ctrl+C to exit | Auto-refresh every 10s | Run smart_signals.py for AI analysis[/]",
        border_style="dim"
    ))

    return prices

def main():
    """Main loop - 24/7 ticker"""
    console.print("[bold cyan]Starting Sovereign Shadow Market Ticker...[/]")
    console.print("[dim]Fetching initial data...[/]")

    try:
        while True:
            try:
                create_market_overview()
                time.sleep(10)  # Refresh every 10 seconds
            except KeyboardInterrupt:
                raise
            except Exception as e:
                console.print(f"[red]Error: {e}[/]")
                time.sleep(5)
    except KeyboardInterrupt:
        console.print("\n[yellow]Ticker stopped. Stay sovereign! 👑[/]")

if __name__ == "__main__":
    main()
