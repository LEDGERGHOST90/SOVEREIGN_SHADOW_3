# MANUS TASK: Wire 12 Trading Agents to MCP Server

**Project:** SOVEREIGN SHADOW III
**Location:** `/Volumes/LegacySafe/SS_III/`
**Objective:** Connect 12 dormant trading agents to the sovereign-trader MCP server

---

## CONTEXT

We have a working MCP server (`mcp-servers/sovereign_trader/server.py`) that Claude Desktop uses for trading commands. We also have 12 trading agents built but **not connected** to anything. Your task is to wire them together.

---

## CURRENT STATE

### Working MCP Server
**File:** `mcp-servers/sovereign_trader/server.py`

Current tools exposed:
- `portfolio_status` - Portfolio overview
- `cash_available` - Trading capital
- `refresh_balances` - Live exchange fetch
- `get_price` - Price check
- `analyze_asset` - Basic analysis
- `market_scan` - Market overview
- `propose_trade` - Create trade proposal
- `execute_trade` - Execute approved trade
- `cancel_trade` - Cancel pending
- `aave_status` - Health factor
- `system_status` - API health
- `help_trading` - Command reference

### Dormant Agents (12 total)
**Location:** `core/agents/`

| Agent | File | Purpose |
|-------|------|---------|
| TradingAgent | `trading_agent.py` | Dual-mode AI trading decisions |
| SwarmAgent | `swarm_agent.py` | Multi-model consensus (Claude + Gemini + GPT) |
| WhaleAgent | `whale_agent.py` | Open interest & whale wallet tracking |
| ReflectAgent | `reflect_agent.py` | Self-critique before trade execution |
| FundingArbAgent | `fundingarb_agent.py` | Funding rate arbitrage detection |
| LiquidationAgent | `liquidation_agent.py` | Liquidation cascade detection |
| RBIAgent | `rbi_agent.py` | Risk/reward analysis & position sizing |
| MemeAgent | `meme_agent.py` | Meme coin scanner (DexScreener, PumpFun) |
| RegimeAgent | `regime_agent.py` | Market regime detection (HMM) |
| MomentumAgent | `momentum_agent.py` | Trend following signals |
| ArbitrageAgent | `arbitrage_agent.py` | Cross-exchange arbitrage |
| PortfolioAgent | `portfolio_agent.py` | Rebalancing recommendations |

---

## DELIVERABLES

### 1. Agent Orchestration Layer
**Create:** `core/orchestrator.py`

```python
"""
Agent Orchestrator - Coordinates all 12 agents
"""

class AgentOrchestrator:
    def __init__(self):
        self.agents = {}
        self._load_agents()

    def _load_agents(self):
        # Load all 12 agents
        pass

    def get_council_opinion(self, symbol: str) -> dict:
        """
        Query relevant agents and synthesize opinion
        Returns: {
            'recommendation': 'BUY' | 'SELL' | 'HOLD',
            'confidence': 0-100,
            'agents': {agent_name: opinion, ...},
            'reasoning': str
        }
        """
        pass

    def pre_trade_check(self, trade_proposal: dict) -> dict:
        """
        Run ReflectAgent + RBIAgent before trade
        Returns: {
            'approved': bool,
            'risk_score': 0-100,
            'critique': str,
            'position_size_recommendation': float
        }
        """
        pass

    def get_regime(self) -> str:
        """
        Get current market regime from RegimeAgent
        Returns: 'TRENDING' | 'MEAN_REVERTING' | 'VOLATILE' | 'UNKNOWN'
        """
        pass

    def scan_opportunities(self) -> list:
        """
        Query MemeAgent, FundingArbAgent, ArbitrageAgent for opportunities
        Returns: list of opportunity dicts
        """
        pass
```

### 2. New MCP Tools
**Add to:** `mcp-servers/sovereign_trader/server.py`

```python
@mcp.tool()
async def council_analyze(symbol: str) -> str:
    """
    Get multi-agent council analysis on an asset.
    Queries: TradingAgent, SwarmAgent, RegimeAgent, MomentumAgent
    """
    pass

@mcp.tool()
async def pre_trade_review(trade_id: str) -> str:
    """
    Run ReflectAgent critique + RBIAgent risk check on pending trade.
    Must be called before execute_trade for trades > $25.
    """
    pass

@mcp.tool()
async def whale_check(symbol: str) -> str:
    """
    Check whale activity and open interest for symbol.
    Queries: WhaleAgent
    """
    pass

@mcp.tool()
async def scan_opportunities() -> str:
    """
    Scan for trading opportunities across all agents.
    Queries: MemeAgent, FundingArbAgent, ArbitrageAgent, LiquidationAgent
    """
    pass

@mcp.tool()
async def get_regime() -> str:
    """
    Get current market regime classification.
    Queries: RegimeAgent (HMM model)
    """
    pass

@mcp.tool()
async def rebalance_check() -> str:
    """
    Get portfolio rebalancing recommendations.
    Queries: PortfolioAgent
    """
    pass
```

### 3. Updated Trade Flow

**Current flow:**
```
User → propose_trade → execute_trade → Done
```

**New flow with agents:**
```
User → propose_trade → pre_trade_review (auto) → execute_trade → Done
                              ↓
                        ReflectAgent critiques
                        RBIAgent sizes position
                        RegimeAgent validates timing
```

---

## AGENT INTERFACE STANDARD

Each agent should implement this interface:

```python
class BaseAgent:
    def __init__(self, brain_path: str = None):
        self.brain = self._load_brain(brain_path)

    def analyze(self, symbol: str, context: dict = None) -> dict:
        """
        Analyze a symbol
        Returns: {
            'signal': 'BUY' | 'SELL' | 'HOLD' | 'NEUTRAL',
            'confidence': 0-100,
            'reasoning': str,
            'data': dict  # agent-specific data
        }
        """
        raise NotImplementedError

    def _load_brain(self, path):
        import json
        path = path or '/Volumes/LegacySafe/SS_III/BRAIN.json'
        with open(path) as f:
            return json.load(f)
```

---

## FILES TO READ FIRST

1. **MCP Server (current implementation):**
   ```
   mcp-servers/sovereign_trader/server.py
   ```

2. **Sample Agent (see structure):**
   ```
   core/agents/trading_agent.py
   core/agents/reflect_agent.py
   ```

3. **BRAIN.json (state management):**
   ```
   /Volumes/LegacySafe/SS_III/BRAIN.json
   ```

4. **Exchange connectors (for data):**
   ```
   exchanges/coinbase_connector.py
   ```

---

## CONSTRAINTS

1. **No API credentials in code** - Read from `.env` or `BRAIN.json`
2. **No external API calls in agents** - Agents analyze data, don't fetch it
3. **Fail gracefully** - If an agent fails, return neutral signal, don't crash
4. **Log to BRAIN.json** - All agent decisions should be logged
5. **Keep MCP tools simple** - Complex logic goes in orchestrator

---

## EXAMPLE USAGE (After Implementation)

```
User: "Analyze BTC with the council"
Claude: [calls council_analyze("BTC")]

Response:
Council Analysis for BTC:
- RegimeAgent: TRENDING (bullish)
- TradingAgent: BUY (confidence 72%)
- MomentumAgent: BUY (RSI 45, MACD bullish)
- WhaleAgent: NEUTRAL (no significant whale movement)

Consensus: BUY with 68% confidence
Recommended position: $35 (70% of max)

User: "Propose a $35 buy of BTC on Coinbase"
Claude: [calls propose_trade(...)]
Claude: [auto-calls pre_trade_review(trade_id)]

Pre-Trade Review:
- ReflectAgent: APPROVED - Entry timing good, regime supports trend following
- RBIAgent: Position size OK - Risk/reward 1:2.1, stop at $101,500

Trade TRADE_xxx ready for execution.

User: "Execute"
Claude: [calls execute_trade(trade_id)]
```

---

## SUCCESS CRITERIA

1. All 12 agents importable without errors
2. `council_analyze` returns multi-agent consensus
3. `pre_trade_review` blocks bad trades
4. `scan_opportunities` finds at least funding arb opportunities
5. `get_regime` returns valid regime classification
6. All new MCP tools appear in Claude Desktop

---

## DO NOT

- Execute real trades (no exchange API calls)
- Store API credentials in agent code
- Make agents dependent on each other (loose coupling)
- Change existing working MCP tools
- Delete any existing files

---

## TIMELINE ESTIMATE

This is a code integration task, not a research task. The agents exist, the MCP server exists. You're wiring them together.

Deliverables:
1. `core/orchestrator.py` - New file
2. `mcp-servers/sovereign_trader/server.py` - Add 6 new tools
3. Agent standardization (if needed) - Modify existing agents to match interface

---

*This task is for Manus AI. Do not handle API credentials. Focus on code structure and integration.*
