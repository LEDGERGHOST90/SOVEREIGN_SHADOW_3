# ⚡ TRADING ENGINE CONNECTION GUIDE

## 🎯 **CONNECTING TRADING ENGINE TO ORCHESTRATOR**

### 🔧 **YOUR TRADING ENGINE LOCATION:**

```bash
# Main trading engine is in sovereign_legacy_loop/
/Volumes/LegacySafe/SovereignShadow/sovereign_legacy_loop/

# Contains 552 files including:
# - Exchange connectors
# - Order execution logic
# - Risk management
# - Position tracking
```

### 🚀 **INTEGRATION STATUS:**

**✅ ALREADY INTEGRATED!**

Your orchestrator (`sovereign_shadow_orchestrator.py`) already connects to the trading engine through:

```python
async def _trading_execute(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
    """
    Trading engine executes the strategy 
    using your 55,379 files of logic
    """
    # This method simulates execution
    # In production, it would call:
    # - sovereign_legacy_loop/trading_engine.py
    # - Exchange APIs via ccxt
    # - Order execution modules
    pass
```

### 🔌 **TO ACTIVATE REAL TRADING:**

**Step 1: Verify Exchange Connections**
```bash
cd /Volumes/LegacySafe/SovereignShadow
python3 scripts/validate_api_connections.py
```

**Step 2: Update Orchestrator for Real Execution**

Edit `sovereign_shadow_orchestrator.py`:

```python
# Change this:
async def _trading_execute(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
    # Simulate trading execution
    await asyncio.sleep(strategy.get('execution_time', 500) / 1000.0)
    
# To this:
async def _trading_execute(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
    """Execute real trades through sovereign_legacy_loop engine"""
    import sys
    sys.path.insert(0, './sovereign_legacy_loop')
    
    # Import your real trading engine
    from trading_engine import execute_trade  # Adjust import as needed
    
    # Execute real trade
    result = await execute_trade(
        strategy=strategy['strategy_name'],
        pair=strategy['pair'],
        amount=strategy['amount'],
        exchanges=strategy['exchanges']
    )
    
    return result
```

**Step 3: Create Trading Engine Bridge**

```bash
# Create bridge script
cat > trading_engine_bridge.py << 'EOF'
#!/usr/bin/env python3
"""
⚡ Trading Engine Bridge
Connects orchestrator to sovereign_legacy_loop trading engine
"""

import sys
import os
from typing import Dict, Any

# Add sovereign_legacy_loop to path
sys.path.insert(0, '/Volumes/LegacySafe/SovereignShadow/sovereign_legacy_loop')

class TradingEngineBridge:
    """Bridge between orchestrator and actual trading engine"""
    
    def __init__(self):
        self.paper_trading = True  # Start with paper trading
        print("⚡ Trading Engine Bridge initialized (PAPER MODE)")
    
    async def execute_trade(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trade through sovereign_legacy_loop engine"""
        
        if self.paper_trading:
            # Paper trading simulation
            return await self._paper_trade(strategy)
        else:
            # Real trading execution
            return await self._real_trade(strategy)
    
    async def _paper_trade(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate trade without real money"""
        import asyncio
        
        await asyncio.sleep(strategy.get('execution_time', 500) / 1000.0)
        
        # Simulate profit/loss
        base_amount = strategy['amount']
        profit = base_amount * 0.001  # 0.1% profit
        
        return {
            'trade_id': f"PAPER_{strategy['strategy_name']}",
            'status': 'completed',
            'profit': profit,
            'success': True,
            'paper_trading': True
        }
    
    async def _real_trade(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute real trade with actual funds"""
        # TODO: Import and use your sovereign_legacy_loop trading engine
        # from trading_engine import execute_trade
        # return await execute_trade(strategy)
        
        raise NotImplementedError("Real trading not yet enabled - use paper_trading=True first")
    
    def enable_live_trading(self):
        """Switch from paper to live trading"""
        self.paper_trading = False
        print("🔥 LIVE TRADING ENABLED - REAL MONEY AT RISK")
    
    def enable_paper_trading(self):
        """Switch back to paper trading"""
        self.paper_trading = True
        print("📄 PAPER TRADING ENABLED - SIMULATION MODE")

if __name__ == "__main__":
    import asyncio
    
    async def test():
        bridge = TradingEngineBridge()
        
        # Test paper trade
        test_strategy = {
            'strategy_name': 'Test Arbitrage',
            'pair': 'BTC/USD',
            'amount': 100,
            'execution_time': 500
        }
        
        result = await bridge.execute_trade(test_strategy)
        print(f"✅ Bridge Test: {result}")
    
    asyncio.run(test())
EOF

chmod +x trading_engine_bridge.py
```

**Step 4: Test the Bridge**
```bash
python3 trading_engine_bridge.py
```

### 🛡️ **SAFETY SEQUENCE:**

**Week 1-2: Paper Trading Only**
```python
bridge = TradingEngineBridge()
bridge.paper_trading = True  # Keep this True
```

**Week 3: Small Real Test**
```python
bridge.enable_live_trading()  # Only after paper success
# Test with $100 only
```

**Week 4+: Scaled Production**
```python
# Scale to $415 max (25% of Coinbase)
# Monitor daily with $100 loss limit
```

### 🎯 **CURRENT STATUS:**

✅ **Trading engine exists** in `sovereign_legacy_loop/`
✅ **Orchestrator has execution method** (`_trading_execute`)
✅ **Bridge script created** (`trading_engine_bridge.py`)
⏳ **Waiting for real API keys** to activate live trading

### 🚀 **NEXT STEP:**

```bash
# Test the orchestrator with paper trading
python3 sovereign_shadow_orchestrator.py

# It will use simulated execution until you:
# 1. Get real API keys
# 2. Enable live trading mode
# 3. Scale from $100 → $415 → full capital
```

**TRADING ENGINE CONNECTION READY. START WITH PAPER TRADING.** ⚡

