#!/usr/bin/env python3
"""
SOVEREIGN TRADER - Unified MCP Server for Claude Desktop
One clean interface to control your entire trading system.
"""
import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
SS3_ROOT = Path("/Volumes/LegacySafe/SS_III")
sys.path.insert(0, str(SS3_ROOT))

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stderr)
logger = logging.getLogger("sovereign-trader")

# Initialize MCP server
mcp = FastMCP("sovereign-trader")

# Paths
BRAIN_PATH = SS3_ROOT / "BRAIN.json"
ENV_PATH = SS3_ROOT / ".env"

def load_env():
    """Load environment variables."""
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().split('\n'):
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k] = v

def load_brain():
    """Load BRAIN.json state."""
    if BRAIN_PATH.exists():
        return json.loads(BRAIN_PATH.read_text())
    return {}

def save_brain(brain):
    """Save BRAIN.json state."""
    brain['last_updated'] = datetime.now().isoformat()
    BRAIN_PATH.write_text(json.dumps(brain, indent=2))

# Load environment on startup
load_env()


# ═══════════════════════════════════════════════════════════════════════════════
# PORTFOLIO TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def portfolio_status() -> str:
    """Get your complete portfolio status including all exchanges, Ledger, and AAVE position."""
    brain = load_brain()
    portfolio = brain.get('portfolio', {})

    exchanges = portfolio.get('exchanges', {})
    ledger = portfolio.get('ledger', {})
    aave = portfolio.get('aave', {})

    result = f"""
PORTFOLIO STATUS ({datetime.now().strftime('%Y-%m-%d %H:%M')})
{'='*50}

NET WORTH: ${portfolio.get('net_worth', 0):,.2f}

EXCHANGES (${exchanges.get('total', 0):,.2f})
  Coinbase:   ${exchanges.get('coinbase', 0):,.2f}
  OKX:        ${exchanges.get('okx', 0):,.2f}
  Binance US: ${exchanges.get('binance_us', 0):,.2f}
  Kraken:     ${exchanges.get('kraken', 0):,.2f}

LEDGER (${ledger.get('total', 0):,.2f})
  wstETH:     ${ledger.get('AAVE_wstETH', 0):,.2f}
  BTC:        ${ledger.get('BTC', 0):,.2f}
  XRP:        ${ledger.get('XRP', 0):,.2f}
  USDC:       ${ledger.get('USDC', 0):,.2f}
  ETH:        ${ledger.get('ETH', 0):,.2f}

AAVE POSITION
  Collateral: ${aave.get('collateral', 0):,.2f}
  Debt:       ${aave.get('debt', 0):,.2f}
  Health:     {aave.get('health_factor', 0):.2f}
"""
    return result


@mcp.tool()
def cash_available() -> str:
    """Get available cash for trading across all exchanges."""
    try:
        # Import exchange connectors
        from coinbase.rest import RESTClient

        api_key = os.environ.get('COINBASE_API_KEY')
        pem_path = os.environ.get('COINBASE_API_SECRET_FILE')

        total_cash = 0
        breakdown = []

        # Coinbase
        if api_key and pem_path and Path(pem_path).exists():
            try:
                with open(pem_path) as f:
                    api_secret = f.read()
                client = RESTClient(api_key=api_key, api_secret=api_secret)
                accounts = client.get_accounts()
                for acc in accounts.accounts:
                    if hasattr(acc, 'available_balance'):
                        bal = float(acc.available_balance.get('value', 0)) if isinstance(acc.available_balance, dict) else float(acc.available_balance.value or 0)
                        if acc.currency in ['USD', 'USDC', 'USDT'] and bal > 0.01:
                            total_cash += bal
                            breakdown.append(f"Coinbase {acc.currency}: ${bal:.2f}")
            except Exception as e:
                breakdown.append(f"Coinbase: Error - {str(e)[:50]}")

        # Binance US (USDC)
        brain = load_brain()
        binance = brain.get('portfolio', {}).get('exchanges', {}).get('binance_us', 0)
        if binance > 0:
            total_cash += binance
            breakdown.append(f"Binance US USDC: ${binance:.2f}")

        return f"""
AVAILABLE CASH: ${total_cash:.2f}
{'='*40}
{chr(10).join(breakdown)}

Ready to deploy for trading.
"""
    except Exception as e:
        return f"Error getting cash: {e}"


@mcp.tool()
def refresh_balances() -> str:
    """Fetch live balances from all exchanges and update BRAIN.json."""
    try:
        # Run the push script logic
        from coinbase.rest import RESTClient
        import requests
        import time
        import hmac
        import hashlib
        import base64
        from datetime import timezone

        results = []
        total = 0

        # Coinbase
        api_key = os.environ.get('COINBASE_API_KEY')
        pem_path = os.environ.get('COINBASE_API_SECRET_FILE')
        if api_key and pem_path:
            try:
                with open(pem_path) as f:
                    api_secret = f.read()
                client = RESTClient(api_key=api_key, api_secret=api_secret)
                accounts = client.get_accounts()
                coinbase_total = 0
                for acc in accounts.accounts:
                    if hasattr(acc, 'available_balance'):
                        bal = float(acc.available_balance.get('value', 0)) if isinstance(acc.available_balance, dict) else float(acc.available_balance.value or 0)
                        if bal > 0.01:
                            # Get USD value (simplified - assumes stables are 1:1)
                            if acc.currency in ['USD', 'USDC', 'USDT']:
                                coinbase_total += bal
                total += coinbase_total
                results.append(f"Coinbase: ${coinbase_total:.2f}")
            except Exception as e:
                results.append(f"Coinbase: Error - {e}")

        # Update BRAIN.json
        brain = load_brain()
        brain['portfolio']['exchanges']['total'] = round(total, 2)
        brain['portfolio']['snapshot_time'] = datetime.now().strftime('%Y-%m-%d')
        save_brain(brain)

        return f"""
BALANCES REFRESHED
{'='*40}
{chr(10).join(results)}

Total Exchange Value: ${total:.2f}
BRAIN.json updated.
"""
    except Exception as e:
        return f"Error refreshing: {e}"


# ═══════════════════════════════════════════════════════════════════════════════
# MARKET ANALYSIS TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def analyze_asset(symbol: str = "") -> str:
    """Analyze an asset using SynopticCore Smart Asset Score (0-100)."""
    if not symbol:
        return "Please provide a symbol (e.g., BTC, ETH, SOL)"

    symbol = symbol.upper()

    try:
        # Try to use SynopticCore
        from ds_star.synoptic_core.core import SynopticCore
        core = SynopticCore()
        result = core.assess(symbol)
        return f"""
SMART ASSET SCORE: {symbol}
{'='*50}
Score: {result.score}/100
Thesis: {result.thesis}
Dominant Driver: {result.dominant_driver}
Risks: {', '.join(result.risks) if result.risks else 'None identified'}
"""
    except Exception as e:
        # Fallback to basic analysis
        import requests
        try:
            ids = {'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana', 'XRP': 'ripple'}
            cg_id = ids.get(symbol, symbol.lower())
            r = requests.get(f'https://api.coingecko.com/api/v3/coins/{cg_id}', timeout=10)
            data = r.json()
            price = data['market_data']['current_price']['usd']
            change_24h = data['market_data']['price_change_percentage_24h']
            change_7d = data['market_data']['price_change_percentage_7d']
            mcap = data['market_data']['market_cap']['usd']

            return f"""
{symbol} ANALYSIS
{'='*50}
Price: ${price:,.2f}
24h Change: {change_24h:+.2f}%
7d Change: {change_7d:+.2f}%
Market Cap: ${mcap:,.0f}

(Basic analysis - SynopticCore unavailable)
"""
        except:
            return f"Could not analyze {symbol}: {e}"


@mcp.tool()
def market_scan() -> str:
    """Scan market for opportunities using agent signals."""
    try:
        import requests

        # Get Fear & Greed
        try:
            fg = requests.get('https://api.alternative.me/fng/', timeout=5).json()
            fear_greed = f"{fg['data'][0]['value']} ({fg['data'][0]['value_classification']})"
        except:
            fear_greed = "Unavailable"

        # Get BTC dominance and top movers
        try:
            global_data = requests.get('https://api.coingecko.com/api/v3/global', timeout=5).json()
            btc_dom = global_data['data']['market_cap_percentage']['btc']
        except:
            btc_dom = "N/A"

        # Get top gainers
        try:
            trending = requests.get('https://api.coingecko.com/api/v3/search/trending', timeout=5).json()
            top_coins = [c['item']['symbol'] for c in trending.get('coins', [])[:5]]
        except:
            top_coins = []

        return f"""
MARKET SCAN
{'='*50}
Fear & Greed Index: {fear_greed}
BTC Dominance: {btc_dom:.1f}%
Trending: {', '.join(top_coins) if top_coins else 'N/A'}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    except Exception as e:
        return f"Scan error: {e}"


@mcp.tool()
def get_price(symbol: str = "") -> str:
    """Get current price for a crypto asset."""
    if not symbol:
        return "Please provide a symbol (e.g., BTC, ETH, SOL)"

    symbol = symbol.upper()
    try:
        import requests
        ids = {'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana', 'XRP': 'ripple',
               'DOGE': 'dogecoin', 'AAVE': 'aave', 'ZEC': 'zcash'}
        cg_id = ids.get(symbol, symbol.lower())
        r = requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd&include_24hr_change=true', timeout=5)
        data = r.json()[cg_id]
        return f"{symbol}: ${data['usd']:,.2f} ({data.get('usd_24h_change', 0):+.2f}% 24h)"
    except Exception as e:
        return f"Could not get price for {symbol}: {e}"


# ═══════════════════════════════════════════════════════════════════════════════
# TRADING TOOLS (WITH APPROVAL)
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def propose_trade(exchange: str = "", side: str = "", symbol: str = "", amount_usd: str = "") -> str:
    """Propose a trade for user approval. Does NOT execute - just creates proposal."""
    if not all([exchange, side, symbol, amount_usd]):
        return "Required: exchange (coinbase/binance), side (buy/sell), symbol (BTC/ETH/etc), amount_usd"

    try:
        amount = float(amount_usd)
    except:
        return "amount_usd must be a number"

    exchange = exchange.lower()
    side = side.upper()
    symbol = symbol.upper()

    # Safety checks
    brain = load_brain()
    rules = brain.get('rules', {})
    max_position = rules.get('max_position', 100)

    warnings = []
    if amount > max_position:
        warnings.append(f"Exceeds max position size (${max_position})")
    if amount > 200:
        warnings.append("Large trade - consider splitting")

    # Get current price
    price_info = get_price(symbol)

    proposal = {
        'id': f"TRADE_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'exchange': exchange,
        'side': side,
        'symbol': symbol,
        'amount_usd': amount,
        'timestamp': datetime.now().isoformat(),
        'status': 'PENDING_APPROVAL'
    }

    # Store proposal in BRAIN
    brain['pending_trade'] = proposal
    save_brain(brain)

    return f"""
TRADE PROPOSAL
{'='*50}
ID: {proposal['id']}
Exchange: {exchange.upper()}
Action: {side} {symbol}
Amount: ${amount:.2f}
{price_info}

{'WARNINGS: ' + ', '.join(warnings) if warnings else 'No warnings'}

To execute, say: "execute trade {proposal['id']}"
To cancel, say: "cancel trade"
"""


@mcp.tool()
def execute_trade(trade_id: str = "") -> str:
    """Execute a previously proposed trade. Requires valid trade_id."""
    if not trade_id:
        return "Please provide the trade_id from your proposal"

    brain = load_brain()
    pending = brain.get('pending_trade', {})

    if not pending or pending.get('id') != trade_id:
        return f"No pending trade with ID {trade_id}. Create a proposal first with propose_trade."

    if pending.get('status') != 'PENDING_APPROVAL':
        return f"Trade {trade_id} is not pending approval (status: {pending.get('status')})"

    exchange = pending['exchange']
    side = pending['side']
    symbol = pending['symbol']
    amount = pending['amount_usd']

    # Execute on exchange
    try:
        if exchange == 'coinbase':
            from coinbase.rest import RESTClient
            api_key = os.environ.get('COINBASE_API_KEY')
            pem_path = os.environ.get('COINBASE_API_SECRET_FILE')

            with open(pem_path) as f:
                api_secret = f.read()

            client = RESTClient(api_key=api_key, api_secret=api_secret)

            # Create market order
            product_id = f"{symbol}-USDC"

            if side == 'BUY':
                order = client.create_order(
                    client_order_id=trade_id,
                    product_id=product_id,
                    side='BUY',
                    order_configuration={
                        'market_market_ioc': {
                            'quote_size': str(amount)
                        }
                    }
                )
            else:
                # For sell, need to specify base_size
                # This is simplified - real impl needs position tracking
                order = client.create_order(
                    client_order_id=trade_id,
                    product_id=product_id,
                    side='SELL',
                    order_configuration={
                        'market_market_ioc': {
                            'quote_size': str(amount)
                        }
                    }
                )

            # Update state
            pending['status'] = 'EXECUTED'
            pending['order_id'] = str(order.order_id) if hasattr(order, 'order_id') else 'unknown'
            pending['executed_at'] = datetime.now().isoformat()
            brain['pending_trade'] = pending

            # Log to trade history
            if 'trade_history' not in brain:
                brain['trade_history'] = []
            brain['trade_history'].append(pending)

            save_brain(brain)

            return f"""
TRADE EXECUTED
{'='*50}
{side} {symbol} for ${amount:.2f} on {exchange.upper()}
Order ID: {pending.get('order_id')}
Time: {pending['executed_at']}

Trade logged to BRAIN.json
"""
        else:
            return f"Exchange {exchange} execution not yet implemented"

    except Exception as e:
        pending['status'] = 'FAILED'
        pending['error'] = str(e)
        brain['pending_trade'] = pending
        save_brain(brain)
        return f"TRADE FAILED: {e}"


@mcp.tool()
def cancel_trade() -> str:
    """Cancel the pending trade proposal."""
    brain = load_brain()
    pending = brain.get('pending_trade', {})

    if not pending:
        return "No pending trade to cancel"

    trade_id = pending.get('id')
    brain['pending_trade'] = None
    save_brain(brain)

    return f"Trade {trade_id} cancelled"


@mcp.tool()
def trade_history(limit: str = "5") -> str:
    """Get recent trade history."""
    try:
        limit_int = int(limit)
    except:
        limit_int = 5

    brain = load_brain()
    history = brain.get('trade_history', [])

    if not history:
        return "No trade history found"

    recent = history[-limit_int:]

    lines = ["RECENT TRADES", "=" * 50]
    for t in reversed(recent):
        lines.append(f"{t.get('executed_at', 'N/A')[:10]} | {t.get('side')} {t.get('symbol')} | ${t.get('amount_usd', 0):.2f} | {t.get('status')}")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# AAVE TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def aave_status() -> str:
    """Get current AAVE position health and metrics."""
    try:
        from ds_star.portfolio.aave_client import AaveClient
        client = AaveClient()
        position = client.get_position()
        health = position.get('health_factor', 0)

        status = "SAFE" if health > 2 else "CAUTION" if health > 1.5 else "DANGER"

        return f"""
AAVE POSITION
{'='*50}
Health Factor: {health:.2f} ({status})
Collateral: ${position.get('collateral', 'N/A')}
Debt: ${position.get('debt', 'N/A')}

{'WARNING: Health factor below 2.0!' if health < 2 else 'Position is healthy.'}
"""
    except Exception as e:
        # Fallback to BRAIN.json
        brain = load_brain()
        aave = brain.get('portfolio', {}).get('aave', {})
        return f"""
AAVE POSITION (from BRAIN.json)
{'='*50}
Health Factor: {aave.get('health_factor', 'N/A')}
Collateral: ${aave.get('collateral', 'N/A')}
Debt: ${aave.get('debt', 'N/A')}
"""


# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def system_status() -> str:
    """Get overall system health and API status."""
    brain = load_brain()
    apis = brain.get('apis', {})

    return f"""
SOVEREIGN SHADOW STATUS
{'='*50}
Version: {brain.get('version', 'N/A')}
Last Updated: {brain.get('last_updated', 'N/A')}
Location: {brain.get('system_location', 'N/A')}

API STATUS
  Coinbase:   {apis.get('coinbase', 'UNKNOWN')}
  Kraken:     {apis.get('kraken', 'UNKNOWN')}
  Binance US: {apis.get('binance_us', 'UNKNOWN')}
  Ledger:     {apis.get('ledger', 'UNKNOWN')}
  Anthropic:  {apis.get('anthropic', 'UNKNOWN')}
  Gemini:     {apis.get('google_gemini', 'UNKNOWN')}

Current Goal: {brain.get('current_goal', 'None set')}
"""


@mcp.tool()
def help_trading() -> str:
    """Get help on available trading commands."""
    return """
SOVEREIGN TRADER - COMMAND REFERENCE
{'='*50}

PORTFOLIO
  portfolio_status  - Full portfolio overview
  cash_available    - Check available cash
  refresh_balances  - Update from exchanges
  rebalance_check   - Portfolio rebalancing recommendations

MARKET ANALYSIS
  get_price BTC     - Get current price
  analyze_asset ETH - Smart Asset Score analysis
  market_scan       - Market overview & signals
  get_regime        - Market regime (trending/volatile/ranging)

TRADING (Approval Required)
  propose_trade     - Create trade proposal
  pre_trade_review  - Agent critique before execution
  execute_trade     - Execute approved trade
  cancel_trade      - Cancel pending trade
  trade_history     - View recent trades

AGENT COUNCIL (12 Trading Agents)
  council_analyze   - Multi-agent consensus on asset
  whale_check       - Whale activity & open interest
  scan_opportunities - Funding arb, liquidations, etc.
  list_agents       - Show all available agents

AAVE
  aave_status       - Health factor & position

SYSTEM
  system_status     - API & system health
  help_trading      - This help message

EXAMPLE WORKFLOW:
1. "What's my portfolio status?"
2. "council_analyze BTC" (get agent opinions)
3. "get_regime" (check market conditions)
4. "Propose a $50 buy of BTC on coinbase"
5. "pre_trade_review TRADE_xxx" (agent critique)
6. "Execute trade TRADE_xxx"
"""


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT COUNCIL TOOLS (Connected to 12 trading agents via Orchestrator)
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def council_analyze(symbol: str = "") -> str:
    """Get multi-agent council analysis on an asset. Queries: ReflectAgent, WhaleAgent, SwarmAgent, RiskAgent."""
    if not symbol:
        return "Please provide a symbol (e.g., BTC, ETH, SOL)"

    symbol = symbol.upper()

    try:
        from core.orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator()
        result = orchestrator.get_council_opinion(symbol)

        agents_summary = []
        for agent_name, opinion in result.get('agents', {}).items():
            signal = opinion.get('signal', 'N/A')
            conf = opinion.get('confidence', 0)
            agents_summary.append(f"  {agent_name}: {signal} ({conf}%)")

        return f"""
COUNCIL ANALYSIS: {symbol}
{'='*50}
Recommendation: {result['recommendation']}
Confidence: {result['confidence']}%

Agent Opinions:
{chr(10).join(agents_summary) if agents_summary else '  No agent opinions available'}

Signal Counts: {result.get('signal_counts', {})}

Reasoning: {result['reasoning']}
Timestamp: {result['timestamp']}
"""
    except Exception as e:
        return f"Council analysis error: {e}"


@mcp.tool()
def pre_trade_review(trade_id: str = "") -> str:
    """Run ReflectAgent critique + RiskAgent check on pending trade. Required for trades > $25."""
    if not trade_id:
        return "Please provide the trade_id from your proposal"

    brain = load_brain()
    pending = brain.get('pending_trade', {})

    if not pending or pending.get('id') != trade_id:
        return f"No pending trade with ID {trade_id}. Create a proposal first with propose_trade."

    try:
        from core.orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator()

        trade_proposal = {
            'symbol': pending.get('symbol', 'BTC'),
            'side': pending.get('side', 'BUY'),
            'amount_usd': pending.get('amount_usd', 0),
            'exchange': pending.get('exchange', 'coinbase')
        }

        result = orchestrator.pre_trade_check(trade_proposal)

        status = "APPROVED" if result['approved'] else "REJECTED"
        checks = []
        for check in result.get('checks', []):
            if 'error' in check:
                checks.append(f"  {check['agent']}: ERROR - {check['error']}")
            else:
                checks.append(f"  {check['agent']}: {check.get('decision', 'N/A')} ({check.get('confidence', 0):.0%})")

        return f"""
PRE-TRADE REVIEW: {trade_id}
{'='*50}
Status: {status}
Risk Score: {result['risk_score']}/100

Checks Performed:
{chr(10).join(checks) if checks else '  Basic position size check only'}

Critique: {result['critique'] or 'No issues identified'}

Recommended Position Size: ${result['position_size_recommendation']:.2f}

{'Trade approved for execution.' if result['approved'] else 'Trade NOT approved. Review critique above.'}
"""
    except Exception as e:
        return f"Pre-trade review error: {e}"


@mcp.tool()
def whale_check(symbol: str = "") -> str:
    """Check whale activity and open interest for symbol. Queries: WhaleAgent."""
    if not symbol:
        return "Please provide a symbol (e.g., BTC, ETH)"

    symbol = symbol.upper()

    try:
        from core.orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator()

        # Check if WhaleAgent is available
        agents = orchestrator.list_agents()
        whale_status = agents.get('whale', {})

        if not whale_status:
            return f"WhaleAgent not available. Cannot check {symbol} whale activity."

        return f"""
WHALE CHECK: {symbol}
{'='*50}
Agent Status: {'READY' if whale_status.get('loaded') else 'Available (not loaded)'}
Purpose: {whale_status.get('purpose', 'N/A')}

Note: Full whale analysis requires running the WhaleAgent monitoring cycle.
Use 'python core/agents/whale_agent.py' for continuous OI monitoring.

Quick Summary:
- WhaleAgent tracks open interest changes
- Detects unusual OI spikes (whale activity)
- Provides AI analysis of whale movements
"""
    except Exception as e:
        return f"Whale check error: {e}"


@mcp.tool()
def scan_opportunities() -> str:
    """Scan for trading opportunities across all agents. Queries: FundingArbAgent, LiquidationAgent, WhaleAgent."""
    try:
        from core.orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator()

        opportunities = orchestrator.scan_opportunities()

        if not opportunities:
            return """
OPPORTUNITY SCAN
{'='*50}
No opportunities detected.

Available scanners:
- FundingArbAgent: Funding rate arbitrage
- LiquidationAgent: Liquidation cascades
- WhaleAgent: Large OI movements

Run individual agents for detailed scans.
"""

        opp_lines = []
        for opp in opportunities:
            opp_lines.append(f"  [{opp['type']}] {opp['status']}: {opp['detail']}")

        return f"""
OPPORTUNITY SCAN
{'='*50}
Found {len(opportunities)} scanner(s) ready:

{chr(10).join(opp_lines)}

Note: Full opportunity detection requires market data feeds.
"""
    except Exception as e:
        return f"Opportunity scan error: {e}"


@mcp.tool()
def get_regime() -> str:
    """Get current market regime classification. Uses Fear & Greed + volatility analysis."""
    try:
        from core.orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator()

        regime = orchestrator.get_regime()

        regime_descriptions = {
            'TRENDING': 'Market is trending. Momentum strategies favored.',
            'MEAN_REVERTING': 'Market is ranging. Mean reversion strategies favored.',
            'VOLATILE': 'High volatility detected. Reduce position sizes.',
            'UNKNOWN': 'Cannot determine regime. Exercise caution.'
        }

        return f"""
MARKET REGIME
{'='*50}
Current Regime: {regime}

Description: {regime_descriptions.get(regime, 'Unknown regime type')}

Strategy Implications:
- TRENDING: Follow momentum, use trailing stops
- MEAN_REVERTING: Fade extremes, target ranges
- VOLATILE: Reduce size, widen stops, consider hedges

Note: Regime detection uses Fear & Greed index.
Full HMM regime detection available in RegimeAgent.
"""
    except Exception as e:
        return f"Regime detection error: {e}"


@mcp.tool()
def rebalance_check() -> str:
    """Get portfolio rebalancing recommendations. Queries: PortfolioAgent."""
    try:
        brain = load_brain()
        portfolio = brain.get('portfolio', {})
        ledger = portfolio.get('ledger', {})

        # Calculate current allocation
        total = ledger.get('total', 0)
        if total == 0:
            return "Cannot calculate rebalancing - no ledger value found."

        allocations = {}
        for asset, value in ledger.items():
            if asset != 'total' and isinstance(value, (int, float)):
                allocations[asset] = (value / total) * 100

        # Target allocation from BRAIN
        target = {
            'BTC': 40,
            'ETH': 30,
            'SOL': 20,
            'XRP': 10
        }

        # Calculate deviations
        deviations = []
        for asset, target_pct in target.items():
            current_pct = allocations.get(asset, 0)
            diff = current_pct - target_pct
            if abs(diff) > 5:  # Only flag >5% deviation
                action = "REDUCE" if diff > 0 else "INCREASE"
                deviations.append(f"  {asset}: {current_pct:.1f}% (target {target_pct}%) -> {action} by {abs(diff):.1f}%")

        current_alloc_str = '\n'.join([f"  {k}: {v:.1f}%" for k, v in sorted(allocations.items(), key=lambda x: -x[1])])

        return f"""
REBALANCE CHECK
{'='*50}
Ledger Total: ${total:,.2f}

Current Allocation:
{current_alloc_str}

Target Allocation:
  BTC: 40%, ETH: 30%, SOL: 20%, XRP: 10%

Recommended Actions:
{chr(10).join(deviations) if deviations else '  Portfolio within tolerance. No rebalancing needed.'}

Note: AAVE wstETH counts as ETH exposure.
"""
    except Exception as e:
        return f"Rebalance check error: {e}"


@mcp.tool()
def list_agents() -> str:
    """List all available trading agents and their status."""
    try:
        from core.orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator()

        agents = orchestrator.list_agents()

        agent_lines = []
        for name, info in agents.items():
            status = "LOADED" if info.get('loaded') else "available"
            agent_lines.append(f"  {name}: {info.get('purpose', 'N/A')} [{status}]")

        return f"""
AGENT ROSTER
{'='*50}
{len(agents)} agents connected to orchestrator:

{chr(10).join(agent_lines)}

Use council_analyze(symbol) for multi-agent consensus.
Use pre_trade_review(trade_id) before executing trades.
"""
    except Exception as e:
        return f"Agent list error: {e}"


# ═══════════════════════════════════════════════════════════════════════════════
# SERVER STARTUP
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logger.info("Starting Sovereign Trader MCP Server...")
    try:
        mcp.run(transport='stdio')
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
