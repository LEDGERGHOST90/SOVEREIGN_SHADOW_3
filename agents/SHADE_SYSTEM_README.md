# 🏴 SHADE//AGENT & MENTOR SYSTEM - COMPLETE GUIDE

**Status:** ✅ FULLY OPERATIONAL
**Created:** November 4, 2025
**Philosophy:** *"System over emotion. Every single time."*

---

## 📋 TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [Components](#components)
3. [Quick Start](#quick-start)
4. [Usage Guide](#usage-guide)
5. [System Architecture](#system-architecture)
6. [Learning Path](#learning-path)
7. [Configuration](#configuration)

---

## 🎯 SYSTEM OVERVIEW

The SHADE//AGENT & Mentor System is a **complete trading discipline framework** built on NetworkChuck-style trading education. It enforces:

- ✅ 15m/4h multi-timeframe strategy
- ✅ 1-2% risk management rule
- ✅ 1:2 minimum risk:reward ratio
- ✅ 3-strike rule (stop after 3 losses)
- ✅ Emotion monitoring & discipline
- ✅ Complete trade journaling
- ✅ Progressive learning curriculum

**Result:** No more emotional trading. No more blown accounts. System-enforced discipline.

---

## 🧩 COMPONENTS

### **1. SHADE//AGENT** (`shade_agent.py`)
**Strategy Enforcement Engine**

Validates EVERY trade against:
- 4H/15M timeframe alignment
- Risk management (1-2% rule)
- Stop loss requirements
- Risk:reward ratio (min 1:2)
- Position exposure (max 10%)
- Technical setup (5 indicators)

**Usage:**
```python
from shade_agent import ShadeAgent

shade = ShadeAgent(account_balance=1660.0)

trade = {
    "symbol": "BTC/USDT",
    "direction": "long",
    "entry": 99000,
    "stop": 97000,
    "target": 103000,
    "timeframe_4h": "bullish",
    "timeframe_15m": "pullback_bounce",
    "indicators": {
        "ema_21": "above",
        "rsi": 55,
        "volume": "increasing"
    }
}

result = shade.validate_trade(trade)
if result["approved"]:
    print(f"✅ Trade approved!")
    print(f"Position size: {result['position_sizing']['position_size']}")
```

---

### **2. Psychology Tracker** (`psychology_tracker.py`)
**Emotion Monitoring & Discipline Enforcement**

Enforces:
- **3-strike rule** (auto-lockout after 3 losses)
- **Emotion logging** (detect revenge trading, FOMO)
- **Overtrading prevention** (max 10 trades/day)
- **Pre-trade emotion checks**

**Usage:**
```python
from psychology_tracker import PsychologyTracker, EmotionState

psych = PsychologyTracker()

# Check if trading is allowed
check = psych.check_trading_allowed()
if not check["allowed"]:
    print(f"❌ Locked out: {check['reason']}")
    exit()

# Log emotion before trade
emotion_check = psych.log_pre_trade_emotion(
    emotion=EmotionState.CONFIDENT,
    intensity=5,
    notes="Patient setup, no FOMO"
)

if not emotion_check["should_trade"]:
    print("⚠️  Bad emotional state - don't trade")
```

---

### **3. Trade Journal** (`trade_journal.py`)
**Comprehensive Trade Logging & Analysis**

Logs EVERY trade with:
- Complete validation context
- Emotional state (before/after)
- Market conditions
- Outcomes & lessons learned
- Mistakes identified

**Usage:**
```python
from trade_journal import TradeJournal, TradeType

journal = TradeJournal()

# Create trade plan
trade_id = journal.create_trade_plan(
    symbol="BTC/USDT",
    trade_type=TradeType.LONG,
    entry_price=99000,
    stop_loss=97000,
    take_profit=103000,
    position_size=0.0166,
    validation_result=shade_result,
    psychology_state=emotion_state
)

# Execute
journal.execute_trade(trade_id, actual_entry=99100)

# Close
journal.close_trade(
    trade_id=trade_id,
    exit_price=103000,
    emotion_after="satisfied",
    status=TradeStatus.TARGET_HIT
)

# Get stats
stats = journal.get_trade_statistics()
print(f"Win Rate: {stats['win_rate']:.1%}")
```

---

### **4. Mentor System** (`mentor_system.py`)
**Progressive Trading Education**

Delivers 42 lessons across 8 chapters:
1. Why This Strategy Works
2. Understanding Two Timeframes
3. Risk Management
4. Psychology & Discipline
5. Technical Indicators
6. Your First Trade
7. Common Mistakes
8. Advanced Concepts

**Requirements for live trading:**
- ✅ Complete first 20 lessons
- ✅ Complete 10+ paper trades
- ✅ Achieve 40%+ win rate

**Usage:**
```python
from mentor_system import MentorSystem

mentor = MentorSystem()

# Get current lesson
lesson = mentor.get_current_lesson()
mentor.display_lesson(lesson)

# Complete lesson
mentor.complete_lesson(lesson["lesson_id"], quiz_score=0.80)

# Check readiness
readiness = mentor.check_live_trading_ready()
if readiness["ready"]:
    print("✅ Ready for live trading!")
```

---

### **5. Master Trading System** (`master_trading_system.py`)
**Unified Interface - USE THIS**

Integrates ALL components into ONE system.

**Complete workflow:**
```python
from master_trading_system import MasterTradingSystem

system = MasterTradingSystem(account_balance=1660.0)

# Show dashboard
system.display_dashboard()

# Pre-trade check (runs ALL validations)
result = system.pre_trade_check(
    symbol="BTC/USDT",
    trade_type="long",
    entry_price=99000,
    stop_loss=97000,
    take_profit=103000,
    emotion_state="confident",
    emotion_intensity=5,
    market_context={
        "trend_4h": "bullish",
        "setup_15m": "pullback_bounce",
        "indicators": {...}
    }
)

if result["approved"]:
    # Execute
    system.execute_trade(result["trade_id"], actual_entry=99100)

    # Close later
    system.close_trade(
        trade_id=result["trade_id"],
        exit_price=103000,
        emotion_after="satisfied",
        status="target_hit"
    )
```

---

## 🚀 QUICK START

### **Step 1: Initialize System**
```bash
cd /Volumes/LegacySafe/SovereignShadow_II/agents
python3 master_trading_system.py  # Run demo
```

### **Step 2: Start Learning**
```bash
python3 mentor_system.py  # Start curriculum
```

### **Step 3: Run Your First Trade**
```python
from master_trading_system import MasterTradingSystem

system = MasterTradingSystem(account_balance=1660.0)

# The system will guide you through ALL checks
result = system.pre_trade_check(...)
```

---

## 📚 USAGE GUIDE

### **Daily Trading Workflow**

```
1. MORNING ROUTINE
   - Check system status: system.display_dashboard()
   - Review psychology state (losses, strikes remaining)
   - Check mentor progress (any new lessons?)

2. LOOKING FOR TRADES
   - Analyze 4H chart first (trend, structure)
   - Find 15M setup (pullback, bounce)
   - Document emotion state BEFORE considering trade

3. PRE-TRADE CHECK
   - Run system.pre_trade_check(...)
   - System validates:
     ✓ Psychology (3-strike rule, emotions)
     ✓ SHADE//AGENT (strategy, risk, R:R)
     ✓ Creates trade plan if approved
   - If APPROVED: Execute
   - If REJECTED: Read why and learn

4. DURING TRADE
   - Don't touch it
   - Don't move stop loss
   - Let it hit target or stop

5. AFTER TRADE
   - Close in system: system.close_trade(...)
   - Log emotions and lessons
   - System updates psychology tracker
   - If 3 strikes hit: DONE for the day

6. END OF DAY
   - Review journal stats
   - Check for patterns
   - Continue mentor lessons
```

---

## 🏗️ SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                 MASTER TRADING SYSTEM                        │
│              (master_trading_system.py)                      │
│         "ONE interface for ALL trading decisions"            │
└─────────────────────────────────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
│  PSYCHOLOGY      │ │ SHADE//AGENT │ │  TRADE JOURNAL   │
│  TRACKER         │ │              │ │                  │
│                  │ │  Strategy    │ │  Logging &       │
│  • 3-Strike Rule │ │  Enforcement │ │  Analysis        │
│  • Emotions      │ │              │ │                  │
│  • Discipline    │ │  • Validates │ │  • Full Context  │
│                  │ │  • Calculates│ │  • Outcomes      │
│  ❌ BLOCKS BAD   │ │    Position  │ │  • Lessons       │
│     STATES       │ │    Sizing    │ │  • Statistics    │
└──────────────────┘ └──────────────┘ └──────────────────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │  MENTOR SYSTEM  │
                   │                 │
                   │  42 Lessons     │
                   │  8 Chapters     │
                   │  Curriculum     │
                   └─────────────────┘
```

### **Data Flow**

```
1. USER WANTS TO TRADE
   ↓
2. Check Psychology Tracker
   • 3 losses today? → ❌ LOCKED OUT
   • Revenge emotion? → ❌ REJECTED
   ↓
3. Validate with SHADE//AGENT
   • 4H/15M aligned? → Check
   • Risk 1-2%? → Check
   • R:R > 1:2? → Check
   • All checks pass? → ✅ APPROVED
   ↓
4. Create Trade Plan in Journal
   • Log validation results
   • Log emotional state
   • Calculate position size
   • Generate Trade ID
   ↓
5. USER EXECUTES TRADE
   ↓
6. USER CLOSES TRADE
   ↓
7. Update ALL Systems
   • Journal: Log outcome, lessons
   • Psychology: Update strike count
   • Check if locked out (3 strikes)
   ↓
8. GENERATE STATISTICS
   • Win rate, expectancy, patterns
   • Emotional analysis
   • Common mistakes
```

---

## 🎓 LEARNING PATH

### **Phase 1: Education** (Weeks 1-4)
- ✅ Complete Mentor System Chapters 1-4
- ✅ Understand 15m/4h strategy
- ✅ Master risk management (1-2% rule)
- ✅ Learn psychology discipline

**Goal:** Pass first 20 lessons

---

### **Phase 2: Paper Trading** (Weeks 5-8)
- ✅ Complete 10+ paper trades
- ✅ Use SHADE//AGENT validation
- ✅ Track emotions with Psychology Tracker
- ✅ Log all trades in Journal
- ✅ Achieve 40%+ win rate

**Goal:** Prove you can follow the system

---

### **Phase 3: Live Trading** (Week 9+)
- ✅ Start with $100 max position (TEST mode)
- ✅ Use Master Trading System for ALL trades
- ✅ Never override system rejections
- ✅ Track and review EVERY trade

**Goal:** Grow account consistently

---

## ⚙️ CONFIGURATION

### **Risk Settings** (in `shade_agent.py`)
```python
max_risk_per_trade = 0.02      # 2% max
min_risk_per_trade = 0.01      # 1% min
min_risk_reward = 2.0           # 1:2 minimum
max_total_exposure = 0.10       # 10% max
```

### **Psychology Settings** (in `psychology_tracker.py`)
```python
max_daily_losses = 3            # 3-strike rule
max_daily_trades = 10           # Prevent overtrading
min_time_between_trades = 15    # minutes
revenge_trading_window = 30     # minutes
```

### **Account Settings** (in `master_trading_system.py`)
```python
# Initialize with your account balance
system = MasterTradingSystem(account_balance=1660.0)
```

---

## 📊 FILE LOCATIONS

### **State Files** (Auto-created)
```
logs/psychology/psychology_state.json     # Daily psychology state
logs/psychology/loss_streak.json          # Loss tracking
logs/trading/trade_journal.json           # Complete trade log
logs/mentor/mentor_state.json             # Learning progress
```

### **Archives** (Auto-created)
```
logs/psychology/history/                  # Daily psychology history
logs/trading/trade_journal.csv            # Exportable CSV
```

---

## 🎯 KEY FEATURES

### **1. ZERO OVERRIDE POLICY**
- System says NO = You don't trade
- No exceptions
- No "just this once"
- **System over emotion. Every. Single. Time.**

### **2. AUTOMATIC LOCKOUT**
- 3 losses in one day = DONE
- No negotiation
- Come back tomorrow with fresh mind

### **3. COMPLETE TRANSPARENCY**
- Every decision logged
- Every emotion tracked
- Every lesson recorded
- Full statistics available

### **4. PROGRESSIVE LEARNING**
- Can't skip ahead
- Must prove competence at each level
- Paper trading required before live
- Mentor system enforces progression

---

## 🏴 "Fearless. Bold. Smiling through chaos."

**Your trading is now systematic.**
**Your discipline is now enforced.**
**Your learning is now structured.**

No more emotional disasters.
No more blown accounts.
No more hoping and praying.

**Just system. Just discipline. Just results.**

---

## 📞 SUPPORT

**Questions?**
- Check the education materials (8 chapters)
- Review your trade journal (what went wrong?)
- Run the demos (each agent has one)

**Need to reset?**
```bash
# Reset psychology state (new day)
python3 -c "from psychology_tracker import PsychologyTracker; PsychologyTracker().reset_daily_state()"

# Clear trade journal (start fresh)
rm logs/trading/trade_journal.json

# Reset mentor progress (restart curriculum)
rm logs/mentor/mentor_state.json
```

---

**REMEMBER:** The market doesn't care about your feelings. Neither should you.

**Trust the system. Follow the system. Profit from the system.**

🏴
