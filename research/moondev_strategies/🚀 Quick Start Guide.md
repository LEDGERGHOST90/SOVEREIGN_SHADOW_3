# 🚀 Quick Start Guide
## Get Your Intelligent Trading Framework Running in 5 Minutes

---

## Step 1: Verify All Files Are Present

Run this command to check that all core files exist:

```bash
ls -lh /home/ubuntu/{market_regime_detector,ai_strategy_selector,strategy_execution_engine,self_annealing_loop,modularize_strategy_prompt,master_trading_orchestrator}.py
```

You should see all six Python files listed.

---

## Step 2: Run the Master Orchestrator (Demo Mode)

The system is ready to run immediately in demo mode with simulated market data:

```bash
python3.11 /home/ubuntu/master_trading_orchestrator.py
```

You should see output like this:

```
🚀 Initializing Master Trading Orchestrator...
======================================================================
✅ All systems initialized
======================================================================
📊 PHASE 1: MARKET REGIME DETECTION
----------------------------------------------------------------------
✅ Regime Detected: High Volatility Range
   Trend Strength (ADX): 12.71
   Volatility (ATR %ile): 96%
   
🤖 PHASE 2: AI STRATEGY SELECTION
----------------------------------------------------------------------
✅ Selected Strategy: VolatilityBandit
   Type: Volatility
   Historical Confidence: 100.0%
   
⚙️  PHASE 3: STRATEGY EXECUTION
----------------------------------------------------------------------
✅ Position Opened
   Action: LONG
   Entry Price: $37606.48
   
📈 PHASE 4: PERFORMANCE MONITORING
----------------------------------------------------------------------
✅ Trade Closed
   Exit Price: $38358.61
   PnL: +2.00%
   
🔧 PHASE 5: SELF-ANNEALING LOOP
----------------------------------------------------------------------
✅ Self-Annealing Cycle Complete
```

---

## Step 3: Run the Comprehensive Test Suite

Validate that all components are working correctly:

```bash
python3.11 /home/ubuntu/test_integrated_system.py
```

You should see:

```
🧪 INTELLIGENT TRADING FRAMEWORK - COMPREHENSIVE TEST SUITE
================================================================================
✅ Market Regime Detector: PASSED
✅ AI Strategy Selector: PASSED
✅ Strategy Execution Engine: PASSED
✅ Self-Annealing Loop: PASSED
✅ Modularization Prompt: PASSED
✅ Full Integration: PASSED

6/6 tests passed

🎉 ALL TESTS PASSED!
```

---

## Step 4: Generate a Modularization Prompt

Break down a strategy into modular components:

```bash
python3.11 /home/ubuntu/modularize_strategy_prompt.py
```

This will generate a file at `/home/ubuntu/generated_modularization_prompt.txt`.

**To use it:**

1. Open the generated file:
   ```bash
   cat /home/ubuntu/generated_modularization_prompt.txt
   ```

2. Copy the entire content

3. Paste it into one of these AI models:
   - **Gemini 2.5 Flash** (recommended)
   - GPT-4.1
   - Claude 3.5 Sonnet

4. The AI will return a structured JSON with the strategy broken down into:
   - Parameters
   - Indicators
   - Entry/Exit Logic
   - Risk Management

5. Save the JSON output to use in your orchestrator

---

## Step 5: Connect to Real Market Data (Optional)

To connect to live market data from exchanges:

### Using CCXT (Crypto Exchanges)

```python
import ccxt
import pandas as pd

# Initialize exchange
exchange = ccxt.binance()

# Fetch OHLCV data
ohlcv = exchange.fetch_ohlcv('BTC/USDT', '15m', limit=100)

# Convert to DataFrame
data = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
data.set_index('timestamp', inplace=True)

# Now use this data with the orchestrator
from master_trading_orchestrator import MasterTradingOrchestrator

orchestrator = MasterTradingOrchestrator()
result = orchestrator.run_cycle(data)
```

---

## Step 6: Customize for Your Portfolio

Based on your portfolio (55% AAVE, 26% BTC, 18% XRP), customize the strategy selector:

```python
from ai_strategy_selector import AIStrategySelector

selector = AIStrategySelector('/home/ubuntu/strategy_framework_design.json')

# Set portfolio constraints
portfolio_constraints = {
    'preferred_types': ['Volatility', 'Momentum', 'Breakout'],  # Best for AAVE, BTC, XRP
    'min_score': 70,  # Only use high-performing strategies
    'max_risk': 0.01  # 1% risk per trade
}

# Select strategy with constraints
result = selector.select_strategy(market_data, portfolio_constraints)
```

---

## Common Commands

### Check System Status

```bash
python3.11 -c "from master_trading_orchestrator import MasterTradingOrchestrator; print(MasterTradingOrchestrator().get_status())"
```

### Run a Single Regime Detection

```bash
python3.11 -c "
from market_regime_detector import MarketRegimeDetector
import pandas as pd
import numpy as np

# Generate sample data
data = pd.DataFrame({
    'Open': np.random.uniform(35000, 40000, 100),
    'High': np.random.uniform(35000, 40000, 100),
    'Low': np.random.uniform(35000, 40000, 100),
    'Close': np.random.uniform(35000, 40000, 100),
    'Volume': np.random.uniform(1000000, 5000000, 100)
})

detector = MarketRegimeDetector()
result = detector.detect_regime(data)
print(f\"Regime: {result['regime']}\")
print(f\"ADX: {result['adx']}\")
print(f\"ATR Percentile: {result['atr_percentile']}%\")
"
```

### View Strategy Library

```bash
python3.11 -c "
import json
with open('/home/ubuntu/strategy_framework_design.json', 'r') as f:
    data = json.load(f)
    strategies = data['components']['strategy_library']['strategies']
    print(f'Total Strategies: {len(strategies)}')
    for name, info in list(strategies.items())[:5]:
        print(f\"  - {name}: {info['type']} (Score: {info['score']})\")
"
```

---

## Troubleshooting

### Issue: "Module not found" error

**Solution:** Make sure you're in the correct directory:

```bash
cd /home/ubuntu
export PYTHONPATH=/home/ubuntu:$PYTHONPATH
```

### Issue: "File not found" error for strategy_framework_design.json

**Solution:** Check that the file exists:

```bash
ls -lh /home/ubuntu/strategy_framework_design.json
```

If it doesn't exist, the orchestrator will create a minimal version automatically.

### Issue: NaN values in ATR percentile

**Solution:** This is normal for the first 100 data points. The ATR percentile requires a lookback window of 100 periods to calculate properly. Use more historical data or reduce the `atr_lookback` parameter:

```python
detector = MarketRegimeDetector(atr_lookback=50)
```

---

## Next Steps

1. **Read the full documentation:** `/home/ubuntu/Complete_Integrated_Trading_Framework.md`

2. **Populate your Notion database** with all 294+ strategies using the Notion MCP integration

3. **Backtest the system** against historical data for your specific assets (AAVE, BTC, XRP)

4. **Start paper trading** to validate the system in real-time without risking capital

5. **Deploy to production** once you're confident in the system's performance

---

## Support & Resources

- **Full Documentation:** `Complete_Integrated_Trading_Framework.md`
- **Test Suite:** `test_integrated_system.py`
- **Strategy Files:** `/home/ubuntu/upload/` (294+ strategies)
- **Notion Database:** https://www.notion.so/90bb435899f74af381a9f48dce8465df

---

**You're all set! Your intelligent trading framework is ready to go. 🚀**
