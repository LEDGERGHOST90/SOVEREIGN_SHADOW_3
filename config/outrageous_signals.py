"""
OUTRAGEOUS SIGNALS CONFIG
=========================
Only execute when the market is screaming at us.
Everything must align. No exceptions.

Philosophy: "I don't want to trade. I want the trade to be undeniable."
"""

# =============================================================================
# SIGNAL THRESHOLDS - All must be TRUE for execution
# =============================================================================

# =============================================================================
# TIERED EXECUTION - Don't miss opportunities, but size appropriately
# =============================================================================
#
# OUTRAGEOUS (85%+):  Full size, auto-execute, max conviction
# STRONG (70-84%):    75% size, auto-execute, high conviction
# MODERATE (55-69%):  50% size, execute but alert, decent setup
# WEAK (<55%):        Log only, wait for better
#
# This way we catch real opportunities without requiring perfection
# =============================================================================

SIGNAL_TIERS = {
    "OUTRAGEOUS": {
        "min_confidence": 85,
        "position_multiplier": 1.0,     # Full size
        "auto_execute": True,
        "description": "Undeniable - market screaming at us"
    },
    "STRONG": {
        "min_confidence": 70,
        "position_multiplier": 0.75,    # 75% size
        "auto_execute": True,
        "description": "High conviction - solid setup"
    },
    "MODERATE": {
        "min_confidence": 55,
        "position_multiplier": 0.50,    # 50% size
        "auto_execute": True,           # Still execute, just smaller
        "description": "Decent setup - worth a smaller position"
    },
    "WEAK": {
        "min_confidence": 0,
        "position_multiplier": 0.0,     # No trade
        "auto_execute": False,
        "description": "Not enough edge - log and wait"
    }
}

OUTRAGEOUS_REQUIREMENTS = {

    # 1. MOONDEV CONSENSUS (Relaxed - 2/3 strategies is enough)
    "moondev_min_score": 0.8,           # Weighted score, not 1.5
    "moondev_min_strategies": 2,        # 2 of 3 is enough
    "moondev_min_confidence": 0.55,     # Each strategy 55%+ confident

    # 2. MANUS RESEARCH ALIGNMENT (Nice to have, not required)
    "require_regime_alignment": False,  # Bonus, not requirement
    "require_watchlist_match": False,   # Bonus, not requirement
    "require_sector_alignment": False,  # Bonus, not requirement
    "manus_alignment_bonus": 10,        # +10% if aligned

    # 3. WHALE CONFIRMATION (Bonus, not blocker)
    "require_whale_accumulation": False, # Bonus, not requirement
    "whale_bonus": 5,                    # +5% if whales aligned

    # 4. MULTI-AGENT CONSENSUS (Relaxed)
    "min_agents_agreeing": 3,           # 3 of 7 is minimum
    "agent_consensus_min": 0.50,        # 50% agreement
    "agent_bonus_per_extra": 3,         # +3% per agent above minimum

    # 5. TECHNICAL REQUIREMENTS (Core - these matter)
    "rsi_oversold_max": 40,             # RSI < 40 for longs (not 35)
    "rsi_overbought_min": 60,           # RSI > 60 for shorts
    "require_volume_spike": False,      # Nice to have
    "require_support_bounce": False,    # Nice to have
    "require_trend_alignment": True,    # This one matters - 4H and 15M

    # 6. FINAL CONFIDENCE (Tiered - see SIGNAL_TIERS above)
    "final_confidence_min": 55,         # Minimum to even consider

    # 7. RISK/REWARD (Reasonable)
    "min_risk_reward": 2.0,             # 2:1 minimum (not 3:1)

    # 8. CONTRARIAN BONUS
    "fear_greed_extreme_threshold": 25,
    "extreme_fear_confidence_boost": 10,
}

# =============================================================================
# POSITION SIZING - Conservative even on outrageous signals
# =============================================================================

POSITION_CONFIG = {
    "max_position_usd": 200,            # Never more than $200 per trade
    "risk_per_trade_pct": 1.5,          # 1.5% risk (not 2%)
    "max_concurrent_positions": 3,       # Max 3 open positions
    "max_daily_trades": 2,              # Even outrageous signals, max 2/day
    "max_exposure_pct": 15,             # Never more than 15% of portfolio at risk
}

# =============================================================================
# EXECUTION MODE
# =============================================================================

EXECUTION_CONFIG = {
    "mode": "paper",                    # Start paper, graduate to live
    "require_human_approval": False,    # When signal is outrageous, just execute
    "notification_channels": [
        "ntfy",                         # Push notification
        "log",                          # Local log
        "replit",                       # Dashboard update
    ],
    "execution_delay_seconds": 30,      # 30s delay to catch any issues
    "dry_run_first": True,              # Always simulate before real execution
}

# =============================================================================
# WHAT QUALIFIES AS "OUTRAGEOUS"
# =============================================================================

"""
An OUTRAGEOUS signal looks like this:

┌─────────────────────────────────────────────────────────────┐
│ OUTRAGEOUS SIGNAL DETECTED                                  │
├─────────────────────────────────────────────────────────────┤
│ Symbol: ENA                                                 │
│ Direction: LONG                                             │
│                                                             │
│ MOONDEV STRATEGIES:                                         │
│   ✓ MomentumBreakout:   STRONG_BUY (85%)  - Golden Cross   │
│   ✓ BandedMACD:         BUY (78%)         - MACD Cross Up  │
│   ✓ VolCliffArbitrage:  STRONG_BUY (82%)  - Vol Cliff Long │
│   Consensus Score: 1.8 (need 1.5) ✓                        │
│                                                             │
│ MANUS RESEARCH:                                             │
│   ✓ Regime: ACCUMULATE (matches LONG)                      │
│   ✓ Watchlist: ENA is IMMEDIATE priority                   │
│   ✓ Sector: DeFi rated HIGH                                │
│   ✓ Hayes Rotation: ENA in active rotation                 │
│                                                             │
│ WHALE ACTIVITY:                                             │
│   ✓ Exchange Flow: ACCUMULATION (+$2.3M)                   │
│   ✓ Smart Money: 73% confidence bullish                    │
│                                                             │
│ AGENT COUNCIL (6/7 agree):                                  │
│   ✓ ReflectAgent:    LONG (validated reasoning)            │
│   ✓ WhaleAgent:      LONG (OI increasing)                  │
│   ✓ SwarmAgent:      LONG (5/6 models agree)               │
│   ✓ RiskAgent:       APPROVED (within limits)              │
│   ✓ PortfolioAgent:  APPROVED (fits allocation)            │
│   ✓ SentimentAgent:  LONG (social momentum)                │
│   ○ FundingAgent:    NEUTRAL (rates flat)                  │
│                                                             │
│ TECHNICALS:                                                 │
│   ✓ RSI: 28 (oversold)                                     │
│   ✓ Volume: 2.1x average (spike)                           │
│   ✓ Price: At $0.95 support (bouncing)                     │
│   ✓ 4H Trend: Bullish                                      │
│   ✓ 15M Setup: Pullback bounce confirmed                   │
│                                                             │
│ CONTRARIAN:                                                 │
│   ✓ Fear & Greed: 18 (EXTREME FEAR)                        │
│   ✓ Contrarian Boost: +10%                                 │
│                                                             │
│ FINAL CONFIDENCE: 94%                                       │
│ RISK/REWARD: 1:3.5                                          │
│                                                             │
│ >>> EXECUTING: BUY 150 ENA @ $0.95                         │
│ >>> Stop Loss: $0.90 | Take Profit: $1.12                  │
│ >>> Risk: $7.50 (1.5% of portfolio)                        │
└─────────────────────────────────────────────────────────────┘

This is what we wait for. Not "pretty good". UNDENIABLE.
"""


def is_outrageous(signal: dict) -> tuple[bool, list[str]]:
    """
    Check if a signal meets ALL outrageous requirements.
    Returns (is_outrageous, list_of_reasons_why_or_why_not)
    """
    reasons = []
    passed = True

    # Check each requirement
    req = OUTRAGEOUS_REQUIREMENTS

    # MoonDev consensus
    if signal.get('moondev_score', 0) < req['moondev_min_score']:
        passed = False
        reasons.append(f"MoonDev score {signal.get('moondev_score', 0)} < {req['moondev_min_score']}")
    else:
        reasons.append(f"✓ MoonDev score {signal.get('moondev_score', 0)}")

    # Final confidence
    if signal.get('final_confidence', 0) < req['final_confidence_min']:
        passed = False
        reasons.append(f"Confidence {signal.get('final_confidence', 0)}% < {req['final_confidence_min']}%")
    else:
        reasons.append(f"✓ Confidence {signal.get('final_confidence', 0)}%")

    # Risk/Reward
    if signal.get('risk_reward', 0) < req['min_risk_reward']:
        passed = False
        reasons.append(f"R:R {signal.get('risk_reward', 0)} < {req['min_risk_reward']}")
    else:
        reasons.append(f"✓ R:R 1:{signal.get('risk_reward', 0)}")

    # Agent consensus
    if signal.get('agents_agreeing', 0) < req['min_agents_agreeing']:
        passed = False
        reasons.append(f"Agents {signal.get('agents_agreeing', 0)}/7 < {req['min_agents_agreeing']}/7")
    else:
        reasons.append(f"✓ Agents {signal.get('agents_agreeing', 0)}/7 agree")

    return passed, reasons


# Expected frequency: 1-3 signals per WEEK, not per day
# That's the point. We only trade when it's screaming at us.
