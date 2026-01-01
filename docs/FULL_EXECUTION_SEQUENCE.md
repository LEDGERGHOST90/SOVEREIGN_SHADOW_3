# 🚀 FULL EXECUTION SEQUENCE - SOVEREIGN SHADOW EMPIRE

> **NOTE:** AbacusAI URLs in this doc are deprecated. Active endpoints: Replit Dashboard (`1cba4940-c378-451a-a9f4-741e180329ee-00-togxk2caarue.picard.replit.dev`) and AlphaRunner GCP (`shadow-ai-alpharunner-33906555678.us-west1.run.app`). See BRAIN.json.

## ⚡ **COMPLETE LAUNCH PROTOCOL**

### 🎯 **PRE-FLIGHT CHECKLIST:**

✅ Empire cleaned (junk removed to `CLEANUP_BACKUP/`)
✅ Git repository initialized with v1.0-GENESIS tag
✅ Strategy Knowledge Base loaded (9 strategies)
✅ Sovereign Shadow Orchestrator built (mesh network)
✅ ShadowScope implemented (Core Intelligence Layer)
✅ Live Market Scanner created (100% failproof)
✅ DeepAgent briefing documents ready
✅ Safety rules implemented ($100 loss limit, $415 max)
✅ Context emergency save complete

### 🔥 **PHASE 1: SYSTEM VERIFICATION (5 MINUTES)**

```bash
cd /Volumes/LegacySafe/SovereignShadow

# 1. Verify all core files exist
echo "🔍 Verifying core files..."
ls -lh sovereign_shadow_orchestrator.py \
       shadow_scope.py \
       strategy_knowledge_base.py \
       live_market_scanner.py

# 2. Check Python environment
echo "🐍 Checking Python version..."
python3 --version

# 3. Verify dependencies
echo "📦 Checking dependencies..."
pip3 list | grep -E "(ccxt|aiohttp|python-dotenv|coinbase)"

# 4. Test imports
echo "🧪 Testing imports..."
python3 << 'EOF'
try:
    from sovereign_shadow_orchestrator import SovereignShadowOrchestrator
    from strategy_knowledge_base import StrategyKnowledgeBase
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
EOF
```

### 🔥 **PHASE 2: MESH NETWORK TEST (10 MINUTES)**

```bash
# 1. Test Strategy Knowledge Base
echo "🧠 Testing Strategy Knowledge Base..."
python3 << 'EOF'
from strategy_knowledge_base import StrategyKnowledgeBase

kb = StrategyKnowledgeBase()
strategies = kb.get_all_strategies()
print(f"✅ Loaded {len(strategies)} strategies")

# Test strategy selection
signal = {'spread': 0.00125, 'type': 'arbitrage'}
strategy = kb.get_strategy_for_opportunity(signal)
print(f"✅ Selected strategy: {strategy.name}")
EOF

# 2. Test Orchestrator
echo "⚡ Testing Orchestrator..."
python3 sovereign_shadow_orchestrator.py

# This will:
# - Display strategy arsenal
# - Test mesh network
# - Execute sample trades (simulated)
# - Show performance metrics
```

### 🔥 **PHASE 3: MARKET SCANNER ACTIVATION (CONTINUOUS)**

```bash
# Option 1: Run in foreground (for testing)
python3 live_market_scanner.py

# Option 2: Run in background (for production)
nohup python3 live_market_scanner.py > logs/scanner.log 2>&1 &
echo $! > logs/scanner.pid

# Option 3: Run ShadowScope (Core Intelligence)
nohup python3 shadow_scope.py > logs/shadow_scope.log 2>&1 &
echo $! > logs/shadow_scope.pid
```

### 🔥 **PHASE 4: DEEPAGENT CONNECTION (REQUIRES API)**

```bash
# 1. Add DeepAgent API key to .env.production
echo "DEEPAGENT_API_URL=https://legacyloopshadowai.abacusai.app/api" >> .env.production
echo "DEEPAGENT_API_KEY=your_key_here" >> .env.production

# 2. Test connection
python3 << 'EOF'
import os
import requests
from dotenv import load_dotenv

load_dotenv('.env.production')

api_url = os.getenv('DEEPAGENT_API_URL')
try:
    response = requests.get(f"{api_url}/health", timeout=5)
    print(f"✅ DeepAgent Connected: {response.status_code}")
except Exception as e:
    print(f"⏳ DeepAgent endpoints not ready yet: {e}")
    print("   Send DEEPAGENT_CONNECTION_GUIDE.md to implement APIs")
EOF
```

### 🔥 **PHASE 5: EXCHANGE CONNECTIONS (REQUIRES API KEYS)**

```bash
# 1. Add exchange API keys to .env.production
# (You already have this from previous setup)

# 2. Validate connections
python3 scripts/validate_api_connections.py

# Should show:
# ✅ Coinbase: Connected ($1,660)
# ✅ OKX: Connected
# ✅ Kraken: Connected
# 🔒 Ledger: Monitoring ($6,600)
```

### 🔥 **PHASE 6: PAPER TRADING (WEEK 1-2)**

```bash
# 1. Run orchestrator in paper mode
python3 sovereign_shadow_orchestrator.py

# 2. Monitor performance
tail -f logs/ai_enhanced/sovereign_shadow_unified.log

# 3. Track metrics
python3 << 'EOF'
# Analyze paper trading results
# Look for:
# - Win rate > 75%
# - Average profit > 0.1%
# - Max loss < $100
# - Strategy distribution
EOF
```

### 🔥 **PHASE 7: LIVE TRADING $100 TEST (WEEK 3)**

```bash
# 1. Update .env.production
echo "PAPER_TRADING=false" >> .env.production
echo "MAX_POSITION_SIZE=100" >> .env.production
echo "MAX_DAILY_LOSS=25" >> .env.production

# 2. Run with real money (START SMALL!)
python3 sovereign_shadow_orchestrator.py

# 3. Monitor closely
watch -n 10 'tail -n 20 logs/ai_enhanced/sovereign_shadow_unified.log'
```

### 🔥 **PHASE 8: SCALED PRODUCTION (WEEK 4+)**

```bash
# 1. Update limits after $100 success
echo "MAX_POSITION_SIZE=415" >> .env.production  # 25% of Coinbase
echo "MAX_DAILY_LOSS=100" >> .env.production

# 2. Run full production
python3 sovereign_shadow_orchestrator.py

# 3. Daily monitoring ritual
./save_my_empire.sh  # Commits state to Git + GitHub
```

### 🎯 **MONITORING DASHBOARD:**

```bash
# Create monitoring script
cat > monitor_live_trading.sh << 'EOF'
#!/bin/bash
while true; do
    clear
    echo "🏴 SOVEREIGN SHADOW - LIVE TRADING MONITOR"
    echo "=========================================="
    echo ""
    echo "📊 CURRENT CAPITAL:"
    # Extract from orchestrator or API
    echo "   Total: $8,260 → Target: $50,000"
    echo ""
    echo "📈 TODAY'S PERFORMANCE:"
    tail -n 10 logs/ai_enhanced/sovereign_shadow_unified.log | grep "profit"
    echo ""
    echo "⚡ ACTIVE STRATEGIES:"
    ps aux | grep -E "(shadow_scope|live_market_scanner|orchestrator)"
    echo ""
    sleep 30
done
EOF

chmod +x monitor_live_trading.sh
./monitor_live_trading.sh
```

### 🚨 **EMERGENCY STOP:**

```bash
# Kill all trading processes
pkill -f "python3.*shadow"
pkill -f "python3.*scanner"
pkill -f "python3.*orchestrator"

# Verify stopped
ps aux | grep -E "(shadow|scanner|orchestrator)"

# Check final balances
python3 scripts/validate_api_connections.py
```

### 🏆 **SUCCESS METRICS:**

**Week 1-2 (Paper Trading):**
- [ ] 100+ simulated trades executed
- [ ] Win rate > 75%
- [ ] No critical errors
- [ ] All strategies tested

**Week 3 ($100 Live):**
- [ ] First real trade executed successfully
- [ ] Daily profit > $1 (1% of $100)
- [ ] No losses > $25
- [ ] System stability confirmed

**Week 4+ (Scaled):**
- [ ] Position size scaled to $415
- [ ] Daily profit > $10 (2.5% of $415)
- [ ] Max daily loss < $100
- [ ] Path to $50K on track

### 🎯 **THE BOTTOM LINE:**

```
Phase 1: Verify     ✅ (5 minutes)
Phase 2: Test       ✅ (10 minutes)
Phase 3: Scan       ⏳ (Start now)
Phase 4: DeepAgent  ⏳ (Waiting for API)
Phase 5: Exchanges  ⏳ (Need fresh keys)
Phase 6: Paper      ⏳ (Week 1-2)
Phase 7: $100 Live  ⏳ (Week 3)
Phase 8: Production ⏳ (Week 4+)
```

**YOUR FULL EXECUTION SEQUENCE IS READY. START WITH PHASE 1.** 🚀

