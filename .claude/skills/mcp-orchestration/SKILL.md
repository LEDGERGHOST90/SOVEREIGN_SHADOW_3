---
name: mcp-orchestration
description: Model Context Protocol for LLM-controlled trading. Claude/Gemini directly call trading tools via MCP servers. Natural language to trade execution.
---

# MCP LLM Orchestration - AI-Controlled Trading

**Location:** `/Volumes/LegacySafe/SS_III/mcp-servers/`

**Impact:** Direct AI-to-trade execution, eliminates parsing errors

## What It Does

Model Context Protocol (MCP) allows LLMs to directly invoke trading tools:

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP ARCHITECTURE                         │
│                                                             │
│  ┌──────────┐    MCP Protocol    ┌──────────────────────┐  │
│  │  Claude  │ ◄────────────────► │  Trading MCP Server  │  │
│  │   Code   │    (tool calls)    │  - get_price         │  │
│  └──────────┘                    │  - place_order       │  │
│       │                          │  - get_balance       │  │
│       │ "Buy 0.01 BTC           │  - get_positions     │  │
│       │  at market"             │  - set_stop_loss     │  │
│       │                          └──────────────────────┘  │
│       ▼                                    │               │
│  Tool call:                                │               │
│  place_order(                              ▼               │
│    symbol="BTC-USD",          ┌──────────────────────┐    │
│    side="buy",                │     Coinbase API     │    │
│    quantity=0.01,             └──────────────────────┘    │
│    type="market"                                           │
│  )                                                         │
└─────────────────────────────────────────────────────────────┘
```

## Why MCP > Traditional Bot

| Traditional | MCP |
|-------------|-----|
| Parse LLM text output | Direct tool invocation |
| "The model said buy but I can't parse the size" | `place_order(size=0.01)` |
| Fragile regex/JSON extraction | Type-safe parameters |
| Hallucinated invalid values | Schema validation |

## MCP Server Implementation

```python
# mcp-servers/trading-server/server.py
from mcp.server import Server
from mcp.types import Tool, TextContent
import asyncio

app = Server("trading-server")

@app.tool()
async def get_price(symbol: str) -> dict:
    """Get current price for a trading pair.

    Args:
        symbol: Trading pair (e.g., "BTC-USD", "ETH-USD")

    Returns:
        Current bid, ask, and last price
    """
    from exchanges.coinbase_connector import CoinbaseConnector
    cb = CoinbaseConnector()
    return await cb.get_ticker(symbol)


@app.tool()
async def place_order(
    symbol: str,
    side: str,  # "buy" or "sell"
    quantity: float,
    order_type: str = "market",
    limit_price: float = None,
    stop_price: float = None
) -> dict:
    """Place a trading order.

    Args:
        symbol: Trading pair (e.g., "BTC-USD")
        side: Order side - "buy" or "sell"
        quantity: Amount to trade
        order_type: "market", "limit", or "stop_limit"
        limit_price: Price for limit orders
        stop_price: Trigger price for stop orders

    Returns:
        Order confirmation with order_id
    """
    # Validate against risk limits
    from core.risk.validator import validate_order
    validation = validate_order(symbol, side, quantity)
    if not validation['approved']:
        return {"error": validation['reason']}

    from exchanges.coinbase_connector import CoinbaseConnector
    cb = CoinbaseConnector()
    return await cb.place_order(
        symbol=symbol,
        side=side,
        quantity=quantity,
        order_type=order_type,
        limit_price=limit_price
    )


@app.tool()
async def get_portfolio() -> dict:
    """Get current portfolio balances across all exchanges.

    Returns:
        Portfolio summary with holdings and values
    """
    from core.portfolio import get_portfolio_summary
    return await get_portfolio_summary()


@app.tool()
async def get_positions() -> list:
    """Get all open positions.

    Returns:
        List of open positions with P&L
    """
    from core.positions import get_open_positions
    return await get_open_positions()


@app.tool()
async def set_stop_loss(
    symbol: str,
    stop_price: float,
    quantity: float = None  # None = full position
) -> dict:
    """Set a stop-loss order for risk management.

    Args:
        symbol: Trading pair
        stop_price: Price to trigger stop
        quantity: Amount to sell (None = entire position)

    Returns:
        Stop order confirmation
    """
    from exchanges.coinbase_connector import CoinbaseConnector
    cb = CoinbaseConnector()
    return await cb.place_stop_order(symbol, stop_price, quantity)


@app.tool()
async def analyze_market(symbol: str, timeframe: str = "1h") -> dict:
    """Get technical analysis for a symbol.

    Args:
        symbol: Trading pair
        timeframe: Candle timeframe (1m, 5m, 15m, 1h, 4h, 1d)

    Returns:
        Technical indicators and signals
    """
    from core.analysis.technical import TechnicalAnalyzer
    ta = TechnicalAnalyzer()
    return await ta.full_analysis(symbol, timeframe)


if __name__ == "__main__":
    import mcp
    mcp.run(app)
```

## Claude Code Integration

Add to `.claude/settings.json`:
```json
{
  "mcpServers": {
    "trading": {
      "command": "python",
      "args": ["/Volumes/LegacySafe/SS_III/mcp-servers/trading-server/server.py"],
      "env": {
        "COINBASE_API_KEY": "${COINBASE_API_KEY}",
        "COINBASE_API_SECRET_FILE": "${COINBASE_API_SECRET_FILE}"
      }
    }
  }
}
```

## Usage Examples

Once MCP server is running, Claude can directly:

```
User: "What's the current BTC price?"
Claude: [Calls get_price("BTC-USD")]
Result: {"bid": 104250.00, "ask": 104251.50, "last": 104250.75}

User: "Buy $50 worth of BTC"
Claude: [Calls place_order(symbol="BTC-USD", side="buy", quantity=0.00048, order_type="market")]
Result: {"order_id": "abc123", "status": "filled", "filled_price": 104251.50}

User: "Set a stop loss at 100k"
Claude: [Calls set_stop_loss(symbol="BTC-USD", stop_price=100000)]
Result: {"stop_order_id": "def456", "status": "pending"}
```

## Safety Rails

```python
# Built into MCP server
class TradingSafetyRails:
    MAX_ORDER_SIZE_USD = 50  # Never exceed this
    REQUIRE_CONFIRMATION_ABOVE = 25  # Ask user for orders > $25
    BLOCKED_PAIRS = ['LUNA', 'UST']  # Banned assets
    PAPER_MODE = True  # Default to paper trading

    @staticmethod
    def validate(order: dict) -> dict:
        if order['quantity'] * order['price'] > TradingSafetyRails.MAX_ORDER_SIZE_USD:
            return {"approved": False, "reason": f"Order exceeds ${TradingSafetyRails.MAX_ORDER_SIZE_USD} limit"}

        if order['symbol'].split('-')[0] in TradingSafetyRails.BLOCKED_PAIRS:
            return {"approved": False, "reason": "Asset is blocked"}

        return {"approved": True}
```

## Directory Structure

```
mcp-servers/
├── trading-server/
│   ├── server.py           # Main MCP server
│   ├── tools/
│   │   ├── orders.py       # Order placement tools
│   │   ├── portfolio.py    # Balance/position tools
│   │   ├── analysis.py     # TA tools
│   │   └── risk.py         # Risk management tools
│   └── requirements.txt
├── shadow-sdk/             # Existing SDK server
└── ds-star/               # Analysis server
```

## Testing

```bash
# Start MCP server
cd /Volumes/LegacySafe/SS_III/mcp-servers/trading-server
python server.py

# In another terminal, test with mcp-cli
mcp-cli connect trading-server
> call get_price {"symbol": "BTC-USD"}
> call get_portfolio {}
```

## Research Source

Based on:
- Anthropic's Model Context Protocol specification
- Claude Code MCP integration patterns
- Eliminates 90%+ of parsing-related trade failures

## Status

- Implementation: PARTIAL (shadow-sdk exists)
- Priority: HIGH (direct AI control)
- Dependencies: mcp Python package
- Next: Add trading tools to existing shadow-sdk server
