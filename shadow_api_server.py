"""
SS_III Web API Server
Provides REST endpoints for AlphaRunner and other frontends.

Endpoints:
- GET  /api/              - Health check
- GET  /api/portfolio     - Current portfolio from BRAIN.json
- GET  /api/signals       - Trading signals from alpha_executor
- GET  /api/pending       - Pending approvals
- POST /api/approve/<idx> - Approve pending signal
- POST /api/reject/<idx>  - Reject pending signal
- GET  /api/regime        - Current market regime
- GET  /api/watchlist     - Current watchlist

Run: python web_api/app.py
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS

# Add project root to path
SS3_ROOT = Path("/Volumes/LegacySafe/SS_III")
sys.path.insert(0, str(SS3_ROOT))

app = Flask(__name__)
CORS(app)  # Enable CORS for AlphaRunner

# Paths
BRAIN_JSON = SS3_ROOT / "BRAIN.json"
PENDING_QUEUE = SS3_ROOT / "data" / "pending_approvals.json"
ALPHA_BIAS = SS3_ROOT / "config" / "alpha_bias.json"


def load_brain() -> dict:
    """Load BRAIN.json."""
    if BRAIN_JSON.exists():
        with open(BRAIN_JSON) as f:
            return json.load(f)
    return {}


def load_pending() -> list:
    """Load pending approvals."""
    if PENDING_QUEUE.exists():
        with open(PENDING_QUEUE) as f:
            return json.load(f)
    return []


def save_pending(queue: list):
    """Save pending approvals."""
    PENDING_QUEUE.parent.mkdir(parents=True, exist_ok=True)
    with open(PENDING_QUEUE, 'w') as f:
        json.dump(queue, f, indent=2)


def load_alpha_bias() -> dict:
    """Load alpha bias config."""
    if ALPHA_BIAS.exists():
        with open(ALPHA_BIAS) as f:
            return json.load(f)
    return {}


# ========== ENDPOINTS ==========

@app.route('/api/', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "online",
        "system": "Sovereign Shadow 3",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """
    Get current portfolio for AlphaRunner Dashboard.
    Returns exact LegacyLoopData format expected by frontend types.ts.
    """
    brain = load_brain()

    # Extract data from BRAIN.json
    portfolio_data = brain.get("portfolio", {})
    aave = portfolio_data.get("aave", {})
    mission = brain.get("mission", {})
    live_trades = brain.get("live_trades", [])
    ledger = portfolio_data.get("ledger", {})
    exchanges = portfolio_data.get("exchanges", {})

    # Build allocation data
    current_allocation = {}
    for asset, value in ledger.items():
        if asset != "total" and isinstance(value, (int, float)):
            current_allocation[asset] = current_allocation.get(asset, 0) + value

    cb = exchanges.get("coinbase", {}).get("values", {})
    for asset, value in cb.items():
        if isinstance(value, (int, float)):
            current_allocation[asset] = current_allocation.get(asset, 0) + value

    # Get last trade
    last_trade = live_trades[-1] if live_trades else {}

    # Build exact LegacyLoopData structure (matches types.ts)
    response = {
        "version": brain.get("version", "3.0"),
        "last_updated": brain.get("last_updated", ""),
        "portfolio": {
            "net_worth": portfolio_data.get("net_worth", 0),
            "aave": {
                "collateral": aave.get("collateral", 0),
                "debt": aave.get("debt", 0),
                "net": aave.get("collateral", 0) - aave.get("debt", 0),
                "health_factor": aave.get("health_factor", 0),
                "status": "ACTIVE" if aave.get("health_factor", 0) > 1.5 else "WARNING"
            },
            "allocation": {
                "current": current_allocation,
                "target": brain.get("target_allocation", {})
            }
        },
        "trading": {
            "last_trade": {
                "symbol": last_trade.get("symbol", ""),
                "type": last_trade.get("action", ""),
                "pnl": last_trade.get("pnl_usd", 0),
                "notes": last_trade.get("status", ""),
                "date": last_trade.get("timestamp", "")
            },
            "active_orders": []  # Could populate from pending queue
        },
        "december_campaign": {
            "debt_repayment": mission.get("target_usd", 662.0),
            "start_date": "2025-12-01"
        }
    }

    return jsonify(response)


@app.route('/api/signals', methods=['GET'])
def get_signals():
    """
    Get trading signals for AlphaRunner.
    Returns TradingAlert[] format.
    """
    brain = load_brain()
    pending = load_pending()
    alpha_bias = load_alpha_bias()

    signals = []

    # Add pending approvals as signals
    for p in pending:
        signals.append({
            "id": f"pending_{pending.index(p)}",
            "symbol": p.get("symbol", ""),
            "side": p.get("side", "BUY"),
            "confidence": p.get("confidence", 50),
            "position_size_usd": p.get("position_size_usd", 0),
            "entry_price": p.get("entry_price", 0),
            "stop_loss": p.get("stop_loss", 0),
            "take_profit_1": p.get("take_profit_1", 0),
            "tier": p.get("tier", "queue"),
            "source": p.get("source", "overnight_runner"),
            "status": "pending",
            "timestamp": p.get("timestamp", datetime.now().isoformat())
        })

    # Add watchlist items as potential signals
    watchlist = alpha_bias.get("watchlist", {})
    immediate = watchlist.get("immediate", [])
    for token in immediate:
        signals.append({
            "id": f"watch_{token}",
            "symbol": token,
            "side": "WATCH",
            "confidence": 70,
            "source": "watchlist",
            "status": "watching",
            "timestamp": datetime.now().isoformat()
        })

    return jsonify(signals)


@app.route('/api/pending', methods=['GET'])
def get_pending():
    """Get pending approvals."""
    pending = load_pending()
    return jsonify({
        "count": len(pending),
        "signals": pending
    })


@app.route('/api/approve/<int:idx>', methods=['POST'])
def approve_signal(idx: int):
    """Approve a pending signal."""
    pending = load_pending()

    if 0 <= idx < len(pending):
        approved = pending.pop(idx)
        save_pending(pending)

        # Log to executed (could trigger actual execution here)
        approved["status"] = "approved"
        approved["approved_at"] = datetime.now().isoformat()

        return jsonify({
            "success": True,
            "message": f"Approved {approved.get('symbol')} {approved.get('side')}",
            "signal": approved
        })

    return jsonify({
        "success": False,
        "error": f"Invalid index: {idx}"
    }), 400


@app.route('/api/reject/<int:idx>', methods=['POST'])
def reject_signal(idx: int):
    """Reject a pending signal."""
    pending = load_pending()

    if 0 <= idx < len(pending):
        rejected = pending.pop(idx)
        save_pending(pending)

        return jsonify({
            "success": True,
            "message": f"Rejected {rejected.get('symbol')} {rejected.get('side')}",
            "signal": rejected
        })

    return jsonify({
        "success": False,
        "error": f"Invalid index: {idx}"
    }), 400


@app.route('/api/regime', methods=['GET'])
def get_regime():
    """Get current market regime from alpha bias."""
    alpha_bias = load_alpha_bias()
    brain = load_brain()

    # Combine alpha_bias regime with BRAIN market analysis
    regime = alpha_bias.get("market_regime", {})
    market_analysis = brain.get("market_analysis", {})

    return jsonify({
        "regime": regime,
        "cycle_indicators": market_analysis.get("cycle_indicators", {}),
        "key_levels": market_analysis.get("key_levels", {}),
        "opportunities": market_analysis.get("opportunities_2026", [])[:5]
    })


@app.route('/api/watchlist', methods=['GET'])
def get_watchlist():
    """Get current watchlist."""
    alpha_bias = load_alpha_bias()
    return jsonify(alpha_bias.get("watchlist", {}))


@app.route('/api/brain', methods=['GET'])
def get_brain():
    """Get full BRAIN.json (for debugging)."""
    return jsonify(load_brain())


@app.route('/api/alpha-bias', methods=['GET'])
def get_alpha_bias():
    """Get alpha bias config."""
    return jsonify(load_alpha_bias())


@app.route('/api/moondev', methods=['GET'])
@app.route('/api/moondev/<symbol>', methods=['GET'])
def get_moondev_signals(symbol: str = 'BTC'):
    """
    Get MoonDev strategy signals for a symbol.
    Uses the 3 proven strategies: MomentumBreakout, BandedMACD, VolCliffArbitrage
    """
    try:
        from core.signals.moondev_signals import MoonDevSignals
        import pandas as pd

        df = None

        # Skip LiveDataPipeline (Coinbase auth issues), go straight to Binance US
        # Fallback to Binance US (public, no auth needed for OHLCV)
        if df is None or (hasattr(df, 'empty') and df.empty):
            try:
                import ccxt
                exchange = ccxt.binanceus()
                pair = f"{symbol}/USD"
                ohlcv = exchange.fetch_ohlcv(pair, '1h', limit=200)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
            except Exception:
                pass

        if df is None or df.empty:
            return jsonify({
                "error": f"No OHLCV data for {symbol}",
                "symbol": symbol
            }), 404

        # Generate signals
        signals = MoonDevSignals()
        result = signals.get_consensus(df)

        return jsonify({
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "consensus": result['consensus'].name if hasattr(result['consensus'], 'name') else str(result['consensus']),
            "action": result['action'],
            "score": result['score'],
            "confidence": result['confidence'],
            "entry": result.get('entry'),
            "stop_loss": result.get('stop_loss'),
            "take_profit": result.get('take_profit'),
            "signals": result['signals'],
            "reasons": result.get('reasons', [])
        })

    except ImportError as e:
        return jsonify({
            "error": f"Module not available: {e}",
            "symbol": symbol
        }), 500
    except Exception as e:
        return jsonify({
            "error": str(e),
            "symbol": symbol
        }), 500


@app.route('/api/cycle', methods=['POST'])
def run_cycle():
    """
    Trigger one overnight_runner cycle manually.
    Returns signals and opportunities.
    """
    try:
        from bin.overnight_runner import OvernightRunner

        runner = OvernightRunner(interval_minutes=15, paper_mode=True)
        result = runner.run_cycle()

        return jsonify({
            "success": True,
            "cycle": result.get('cycle'),
            "timestamp": result.get('timestamp'),
            "signals": result.get('signals', {}),
            "opportunities": result.get('opportunities', []),
            "council_opinion": result.get('council_opinion')
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("API_PORT", 8000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"

    print("Starting SS_III Web API Server...")
    print(f"Port: {port}")
    print("Endpoints:")
    print(f"  GET  http://localhost:{port}/api/          - Health")
    print(f"  GET  http://localhost:{port}/api/portfolio - Portfolio")
    print(f"  GET  http://localhost:{port}/api/signals   - Signals")
    print(f"  GET  http://localhost:{port}/api/regime    - Market Regime")
    print("")
    app.run(host="0.0.0.0", port=port, debug=debug)
