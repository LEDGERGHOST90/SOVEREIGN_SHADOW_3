#!/usr/bin/env python3
"""
SOVEREIGN SHADOW - Trading Profiles

Unified configuration for different trading styles.
Used by: overnight_runner, live_data_pipeline, swing_trade_engine

Profiles:
- SNIPER: 3-5% scalps on majors (BTC, ETH)
- SWING: 15% SL, 30%/75% TP for position trades
- MEME: Aggressive 20% SL, 50%/100% TP for meme plays
- CONSERVATIVE: Tight 2% SL, 4% TP, high win rate

Usage:
    from core.config.trading_profiles import get_profile, PROFILES, ProfileType

    profile = get_profile(ProfileType.SWING)
    sl = entry_price * (1 - profile.stop_loss_pct / 100)
    tp1 = entry_price * (1 + profile.tp1_pct / 100)
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ProfileType(Enum):
    SNIPER = "sniper"           # Quick scalps on majors
    SWING = "swing"             # Position trades, matches DECEMBER_BATTLE_PLAN
    MEME = "meme"               # Meme coin hunting
    CONSERVATIVE = "conservative"  # High win rate, small gains


@dataclass
class TradingProfile:
    """Configuration for a trading style"""
    name: str
    description: str

    # Entry criteria
    min_confidence: int = 50      # Minimum signal confidence (0-100)
    min_ray_score: float = 40.0   # Minimum Ray Score

    # Exit rules
    stop_loss_pct: float = 3.0    # Stop loss percentage
    tp1_pct: float = 5.0          # Take profit 1 percentage
    tp2_pct: float = 10.0         # Take profit 2 percentage
    tp1_sell_pct: float = 50.0    # Sell % at TP1

    # Trailing stop (activates after reaching trail_activate_pct)
    use_trailing_stop: bool = False
    trail_activate_pct: float = 20.0   # Activate trailing stop at +20%
    trail_distance_pct: float = 10.0   # Trail by 10%

    # Time stop
    use_time_stop: bool = False
    time_stop_hours: int = 24     # Exit after X hours if no movement
    time_stop_min_pnl: float = 0  # Only time stop if PnL < this %

    # Position sizing
    risk_per_trade_pct: float = 2.0   # Risk 2% of capital per trade
    max_position_pct: float = 10.0    # Max 10% of capital in one position

    # Asset filters (empty = all)
    allowed_symbols: List[str] = None

    def get_stop_loss(self, entry_price: float, direction: str = "LONG") -> float:
        """Calculate stop loss price"""
        if direction == "LONG":
            return entry_price * (1 - self.stop_loss_pct / 100)
        return entry_price * (1 + self.stop_loss_pct / 100)

    def get_tp1(self, entry_price: float, direction: str = "LONG") -> float:
        """Calculate TP1 price"""
        if direction == "LONG":
            return entry_price * (1 + self.tp1_pct / 100)
        return entry_price * (1 - self.tp1_pct / 100)

    def get_tp2(self, entry_price: float, direction: str = "LONG") -> float:
        """Calculate TP2 price"""
        if direction == "LONG":
            return entry_price * (1 + self.tp2_pct / 100)
        return entry_price * (1 - self.tp2_pct / 100)


# =============================================================================
# PROFILE DEFINITIONS
# =============================================================================

PROFILES = {
    ProfileType.SNIPER: TradingProfile(
        name="Sniper Scalp",
        description="Quick 3-5% scalps on major pairs. Limit orders, tight stops.",
        min_confidence=40,
        min_ray_score=40.0,
        stop_loss_pct=3.0,      # Tight 3% stop
        tp1_pct=5.0,            # First target 5%
        tp2_pct=8.0,            # Second target 8%
        tp1_sell_pct=50.0,
        use_trailing_stop=False,
        use_time_stop=True,
        time_stop_hours=12,     # Exit after 12h if no movement
        time_stop_min_pnl=-1.0, # Only if losing
        risk_per_trade_pct=2.0,
        max_position_pct=5.0,
        allowed_symbols=["BTC", "ETH", "SOL", "XRP", "AAVE"]
    ),

    ProfileType.SWING: TradingProfile(
        name="Swing Trade",
        description="Position trades with 15% SL, 30%/75% TP. From DECEMBER_BATTLE_PLAN.",
        min_confidence=50,
        min_ray_score=50.0,
        stop_loss_pct=15.0,     # 15% stop from notes
        tp1_pct=30.0,           # TP1 at +30%, sell 50%
        tp2_pct=75.0,           # TP2 at +75%, sell rest
        tp1_sell_pct=50.0,
        use_trailing_stop=True,
        trail_activate_pct=20.0,  # Activate at +20%
        trail_distance_pct=10.0,  # Trail by 10%
        use_time_stop=True,
        time_stop_hours=24,     # Exit after 24h if sideways
        time_stop_min_pnl=0,
        risk_per_trade_pct=2.0,
        max_position_pct=15.0,
    ),

    ProfileType.MEME: TradingProfile(
        name="Meme Hunter",
        description="Aggressive targets for meme coins. High risk, high reward.",
        min_confidence=60,       # Higher confidence for memes
        min_ray_score=70.0,      # Stricter scoring
        stop_loss_pct=20.0,      # Wider 20% stop (meme volatility)
        tp1_pct=50.0,            # TP1 at +50%
        tp2_pct=100.0,           # TP2 at +100%
        tp1_sell_pct=50.0,
        use_trailing_stop=True,
        trail_activate_pct=30.0,
        trail_distance_pct=15.0,
        use_time_stop=False,     # Memes can take time
        risk_per_trade_pct=1.0,  # Lower risk per trade
        max_position_pct=5.0,    # Smaller positions
        allowed_symbols=["DOGE", "SHIB", "PEPE", "BONK", "WIF", "TURBO", "FLOKI"]
    ),

    ProfileType.CONSERVATIVE: TradingProfile(
        name="Conservative",
        description="High win rate, small gains. Capital preservation focus.",
        min_confidence=70,
        min_ray_score=60.0,
        stop_loss_pct=2.0,       # Very tight 2% stop
        tp1_pct=4.0,             # First target 4%
        tp2_pct=6.0,             # Second target 6%
        tp1_sell_pct=60.0,       # Sell more at TP1
        use_trailing_stop=False,
        use_time_stop=True,
        time_stop_hours=6,       # Quick timeout
        time_stop_min_pnl=-0.5,
        risk_per_trade_pct=1.0,
        max_position_pct=5.0,
    ),
}


def get_profile(profile_type: ProfileType) -> TradingProfile:
    """Get a trading profile by type"""
    return PROFILES.get(profile_type, PROFILES[ProfileType.SNIPER])


def get_profile_for_symbol(symbol: str) -> TradingProfile:
    """Auto-select profile based on symbol"""
    symbol = symbol.upper()

    # Meme coins
    if symbol in ["DOGE", "SHIB", "PEPE", "BONK", "WIF", "TURBO", "FLOKI"]:
        return PROFILES[ProfileType.MEME]

    # Major pairs - sniper scalps
    if symbol in ["BTC", "ETH"]:
        return PROFILES[ProfileType.SNIPER]

    # Default to swing for everything else
    return PROFILES[ProfileType.SWING]


def get_active_profile() -> TradingProfile:
    """Get currently active profile from BRAIN.json"""
    import json
    from pathlib import Path

    brain_path = Path("/Volumes/LegacySafe/SS_III/BRAIN.json")
    try:
        with open(brain_path) as f:
            brain = json.load(f)

        profile_name = brain.get("trading", {}).get("active_profile", "sniper")
        profile_type = ProfileType(profile_name)
        return PROFILES.get(profile_type, PROFILES[ProfileType.SNIPER])
    except:
        return PROFILES[ProfileType.SNIPER]


# =============================================================================
# CLI FOR TESTING
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Trading Profiles")
    parser.add_argument("--profile", type=str, default="sniper",
                        choices=["sniper", "swing", "meme", "conservative"])
    parser.add_argument("--symbol", type=str, help="Auto-select profile for symbol")
    parser.add_argument("--price", type=float, default=100.0, help="Entry price for calculations")

    args = parser.parse_args()

    if args.symbol:
        profile = get_profile_for_symbol(args.symbol)
        print(f"Auto-selected profile for {args.symbol}: {profile.name}")
    else:
        profile = get_profile(ProfileType(args.profile))

    price = args.price

    print(f"\n{'='*60}")
    print(f"PROFILE: {profile.name}")
    print(f"{'='*60}")
    print(f"Description: {profile.description}")
    print(f"\n[ENTRY CRITERIA]")
    print(f"  Min Confidence: {profile.min_confidence}%")
    print(f"  Min Ray Score: {profile.min_ray_score}")
    print(f"\n[EXIT RULES] @ Entry ${price:,.2f}")
    print(f"  Stop Loss: {profile.stop_loss_pct}% → ${profile.get_stop_loss(price):,.2f}")
    print(f"  TP1: +{profile.tp1_pct}% → ${profile.get_tp1(price):,.2f} (sell {profile.tp1_sell_pct}%)")
    print(f"  TP2: +{profile.tp2_pct}% → ${profile.get_tp2(price):,.2f}")

    if profile.use_trailing_stop:
        print(f"\n[TRAILING STOP]")
        print(f"  Activates at: +{profile.trail_activate_pct}%")
        print(f"  Trails by: {profile.trail_distance_pct}%")

    if profile.use_time_stop:
        print(f"\n[TIME STOP]")
        print(f"  Hours: {profile.time_stop_hours}h")
        print(f"  Min PnL trigger: {profile.time_stop_min_pnl}%")

    print(f"\n[POSITION SIZING]")
    print(f"  Risk/Trade: {profile.risk_per_trade_pct}%")
    print(f"  Max Position: {profile.max_position_pct}%")

    if profile.allowed_symbols:
        print(f"\n[ALLOWED SYMBOLS]")
        print(f"  {', '.join(profile.allowed_symbols)}")
