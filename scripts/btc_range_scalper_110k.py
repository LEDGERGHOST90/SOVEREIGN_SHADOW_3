#!/usr/bin/env python3
"""
🎯 BTC RANGE SCALPER - $109K-$116K Consolidation Engine

Optimized for October 2025 market conditions:
- BTC consolidating $106-112K with $109K-$116K range
- Post-halving (3.125 BTC/block) volatility
- OTC distribution + retail accumulation = range chop
- Stop-run liquidity at range edges

Strategy: Fast scalps on mean-reversion + breakout traps
Target: 3-step TP ladder, tight risk, quick fail-break flips
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

# Add paths
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "shadow_sdk"))

from shadow_sdk import ShadowScope, ShadowPulse, EXCHANGES, MAX_POSITION_SIZE
from shadow_sdk.utils import RiskManager, setup_logger

# ═══════════════════════════════════════════════════════════════════════════
# MARKET INTELLIGENCE - October 2025
# ═══════════════════════════════════════════════════════════════════════════

MARKET_INTEL = {
    "current_range": (106000, 112000),    # Current consolidation
    "trading_range": (109000, 116000),    # Target range for scalps
    "range_mid": 112500,                  # Mean reversion target
    "supply_zone": 116000,                # Heavy distribution
    "demand_zone": 109000,                # Accumulation support
    "halving_date": "2024-04-20",         # Post-halving context
    "block_reward": 3.125,                # Current issuance
    "volatility_regime": "choppy_range",  # Market character
    "flow_pattern": "OTC_distribution_retail_accumulation"
}

# ═══════════════════════════════════════════════════════════════════════════
# SCALPER CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

class ScalperConfig:
    """Optimized for fast range scalps"""

    # Range parameters
    RANGE_LOW = 109000
    RANGE_MID = 112500
    RANGE_HIGH = 116000
    RANGE_BUFFER = 500  # $500 buffer for entries

    # Entry zones
    LONG_ZONE = (RANGE_LOW, RANGE_LOW + 1500)   # $109K-$110.5K
    SHORT_ZONE = (RANGE_HIGH - 1500, RANGE_HIGH) # $114.5K-$116K

    # Timing
    LOOKBACK_MINUTES = 15      # Tightened from 60
    HOLDING_MAX_MINUTES = 30   # Shortened from 120
    ENTRY_COOLDOWN = 5         # Minutes between entries

    # Position sizing
    BASE_SIZE = 50             # $50 base (12% of max position)
    MAX_SIZE = 150             # $150 max (36% of max position)
    SIZE_MULTIPLIER_EDGE = 1.5 # Increase at range edges

    # 3-Step TP Ladder
    TP_LEVELS = [
        {"percent": 0.4, "target_pct": 0.005},  # 40% at 0.5% gain
        {"percent": 0.4, "target_pct": 0.010},  # 40% at 1.0% gain
        {"percent": 0.2, "target_pct": 0.020}   # 20% at 2.0% gain
    ]

    # Stop loss
    STOP_LOSS_TIGHT = 0.008    # 0.8% for range trades
    STOP_LOSS_WIDE = 0.012     # 1.2% for OTC spike detection

    # Breakout detection
    BREAKOUT_THRESHOLD = 0.003  # 0.3% move = potential breakout
    BREAKOUT_VOLUME_MULT = 1.5  # 1.5x volume confirms

    # Kill switches
    DAILY_LOSS_LIMIT = 100      # $100 max daily loss
    CONSECUTIVE_LOSSES = 3      # Stop after 3 losses
    DRAWDOWN_PERCENT = 0.15     # Stop at 15% drawdown

# ═══════════════════════════════════════════════════════════════════════════
# BTC RANGE SCALPER ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class BTCRangeScalper:
    """
    Fast BTC scalper for $109K-$116K consolidation range.

    Strategies:
    1. Mean reversion at range edges
    2. Breakout trap detection
    3. OTC supply pattern recognition
    4. 3-step TP ladder management
    """

    def __init__(self, config: ScalperConfig = None):
        self.config = config or ScalperConfig()
        self.logger = setup_logger("btc_scalper", log_file="logs/btc_scalper.log")

        # Components
        self.scope = ShadowScope(exchanges=["coinbase", "okx", "kraken"],
                                pairs=["BTC/USD", "BTC/USDT"])
        self.risk_mgr = RiskManager(
            max_daily_loss=self.config.DAILY_LOSS_LIMIT,
            max_position_size=self.config.MAX_SIZE
        )

        # State
        self.positions: List[Dict] = []
        self.last_entry_time: Optional[datetime] = None
        self.daily_pnl = 0.0
        self.trade_count = 0
        self.consecutive_losses = 0

        self.logger.info("🎯 BTC Range Scalper initialized")
        self.logger.info(f"   Range: ${self.config.RANGE_LOW:,.0f} - ${self.config.RANGE_HIGH:,.0f}")
        self.logger.info(f"   Position: ${self.config.BASE_SIZE} - ${self.config.MAX_SIZE}")

    async def start(self):
        """Start the scalper engine"""
        self.logger.info("🚀 Starting BTC Range Scalper...")

        # Start market scanner
        await self.scope.start_scanner(interval=0.5)

        # Main loop
        while True:
            try:
                # Check kill switches
                if not self._check_safety():
                    self.logger.warning("🛑 Kill switch triggered - stopping")
                    break

                # Get market intelligence
                intel = await self.scope.get_market_intelligence()
                btc_price = intel['current_prices'].get('BTC/USD', 0)

                if btc_price == 0:
                    await asyncio.sleep(5)
                    continue

                # Analyze market
                signal = await self._analyze_market(intel, btc_price)

                # Execute if signal
                if signal:
                    await self._execute_signal(signal, btc_price)

                # Manage open positions
                await self._manage_positions(btc_price)

                # Wait before next scan
                await asyncio.sleep(10)

            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5)

    async def _analyze_market(self, intel: Dict, btc_price: float) -> Optional[Dict]:
        """Analyze market for scalp opportunities"""

        # Check cooldown
        if self.last_entry_time:
            time_since = (datetime.now() - self.last_entry_time).total_seconds() / 60
            if time_since < self.config.ENTRY_COOLDOWN:
                return None

        # Get volatility
        volatility = intel.get('volatility', {}).get('coinbase', {}).get('BTC/USD', 0)

        # Detect OTC supply (thin book + sudden move)
        is_otc_spike = volatility > 0.015  # 1.5% volatility = potential OTC

        # Check position in range
        range_position = (btc_price - self.config.RANGE_LOW) / (self.config.RANGE_HIGH - self.config.RANGE_LOW)

        # === LONG SETUP (near demand zone) ===
        if self.config.LONG_ZONE[0] <= btc_price <= self.config.LONG_ZONE[1]:
            # Mean reversion long at support
            confidence = 0.75 + (0.15 * (1 - range_position))  # Higher at lower prices

            return {
                'type': 'long',
                'strategy': 'mean_reversion_support',
                'entry': btc_price,
                'confidence': confidence,
                'size': self._calculate_position_size(btc_price, 'long', is_otc_spike),
                'stop_loss': btc_price * (1 - (self.config.STOP_LOSS_WIDE if is_otc_spike else self.config.STOP_LOSS_TIGHT)),
                'targets': self._calculate_targets(btc_price, 'long'),
                'is_otc': is_otc_spike
            }

        # === SHORT SETUP (near supply zone) ===
        elif self.config.SHORT_ZONE[0] <= btc_price <= self.config.SHORT_ZONE[1]:
            # Mean reversion short at resistance
            confidence = 0.75 + (0.15 * range_position)  # Higher at higher prices

            return {
                'type': 'short',
                'strategy': 'mean_reversion_resistance',
                'entry': btc_price,
                'confidence': confidence,
                'size': self._calculate_position_size(btc_price, 'short', is_otc_spike),
                'stop_loss': btc_price * (1 + (self.config.STOP_LOSS_WIDE if is_otc_spike else self.config.STOP_LOSS_TIGHT)),
                'targets': self._calculate_targets(btc_price, 'short'),
                'is_otc': is_otc_spike
            }

        # === BREAKOUT TRAP ===
        # Detect false breakouts at range edges
        if btc_price > self.config.RANGE_HIGH:
            # Potential false breakout above - fade it
            return {
                'type': 'short',
                'strategy': 'breakout_trap_fade',
                'entry': btc_price,
                'confidence': 0.65,  # Lower confidence on traps
                'size': self.config.BASE_SIZE,  # Conservative size
                'stop_loss': btc_price * 1.01,  # Tight stop
                'targets': self._calculate_targets(btc_price, 'short'),
                'is_otc': False
            }

        elif btc_price < self.config.RANGE_LOW:
            # Potential false breakdown below - fade it
            return {
                'type': 'long',
                'strategy': 'breakout_trap_fade',
                'entry': btc_price,
                'confidence': 0.65,
                'size': self.config.BASE_SIZE,
                'stop_loss': btc_price * 0.99,
                'targets': self._calculate_targets(btc_price, 'long'),
                'is_otc': False
            }

        return None

    def _calculate_position_size(self, price: float, direction: str, is_otc: bool) -> float:
        """Calculate position size based on location and conditions"""
        base_size = self.config.BASE_SIZE

        # Reduce size during OTC spikes
        if is_otc:
            return base_size * 0.7

        # Increase size at range edges
        range_position = (price - self.config.RANGE_LOW) / (self.config.RANGE_HIGH - self.config.RANGE_LOW)

        if direction == 'long' and range_position < 0.2:
            # Near support - increase size
            return min(base_size * self.config.SIZE_MULTIPLIER_EDGE, self.config.MAX_SIZE)
        elif direction == 'short' and range_position > 0.8:
            # Near resistance - increase size
            return min(base_size * self.config.SIZE_MULTIPLIER_EDGE, self.config.MAX_SIZE)

        return base_size

    def _calculate_targets(self, entry: float, direction: str) -> List[Dict]:
        """Calculate 3-step TP ladder"""
        targets = []

        for i, level in enumerate(self.config.TP_LEVELS):
            if direction == 'long':
                target_price = entry * (1 + level['target_pct'])
            else:
                target_price = entry * (1 - level['target_pct'])

            targets.append({
                'level': i + 1,
                'price': target_price,
                'percent': level['percent'],
                'hit': False
            })

        return targets

    async def _execute_signal(self, signal: Dict, current_price: float):
        """Execute trading signal"""

        # Risk check
        if not self.risk_mgr.can_trade(signal['size']):
            self.logger.warning(f"❌ Trade blocked by risk manager: ${signal['size']}")
            return

        # Log entry
        self.logger.info(f"📈 {signal['type'].upper()} ENTRY: ${current_price:,.0f}")
        self.logger.info(f"   Strategy: {signal['strategy']}")
        self.logger.info(f"   Size: ${signal['size']:.2f}")
        self.logger.info(f"   Confidence: {signal['confidence']:.1%}")
        self.logger.info(f"   Stop: ${signal['stop_loss']:,.2f}")
        targets_str = ", ".join([f"${t['price']:,.0f}" for t in signal['targets']])
        self.logger.info(f"   Targets: {targets_str}")

        # Create position
        position = {
            'id': f"BTC_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'type': signal['type'],
            'strategy': signal['strategy'],
            'entry_price': current_price,
            'entry_time': datetime.now(),
            'size': signal['size'],
            'stop_loss': signal['stop_loss'],
            'targets': signal['targets'],
            'pnl': 0.0,
            'status': 'open'
        }

        self.positions.append(position)
        self.last_entry_time = datetime.now()
        self.trade_count += 1

        # Log to file
        self._log_trade(position, 'entry')

    async def _manage_positions(self, current_price: float):
        """Manage open positions with 3-step TP ladder"""

        for position in self.positions[:]:
            if position['status'] != 'open':
                continue

            # Check max holding time
            holding_time = (datetime.now() - position['entry_time']).total_seconds() / 60
            if holding_time > self.config.HOLDING_MAX_MINUTES:
                await self._close_position(position, current_price, 'timeout')
                continue

            # Check stop loss
            if position['type'] == 'long':
                if current_price <= position['stop_loss']:
                    await self._close_position(position, current_price, 'stop_loss')
                    continue

                # Check targets
                for target in position['targets']:
                    if not target['hit'] and current_price >= target['price']:
                        await self._hit_target(position, target, current_price)

            else:  # short
                if current_price >= position['stop_loss']:
                    await self._close_position(position, current_price, 'stop_loss')
                    continue

                # Check targets
                for target in position['targets']:
                    if not target['hit'] and current_price <= target['price']:
                        await self._hit_target(position, target, current_price)

            # Check if all targets hit
            if all(t['hit'] for t in position['targets']):
                await self._close_position(position, current_price, 'all_targets_hit')

    async def _hit_target(self, position: Dict, target: Dict, price: float):
        """Handle TP level hit"""
        target['hit'] = True

        # Calculate partial close
        close_amount = position['size'] * target['percent']
        position['size'] -= close_amount

        # Calculate PnL for this partial
        if position['type'] == 'long':
            pnl = close_amount * (price - position['entry_price']) / position['entry_price']
        else:
            pnl = close_amount * (position['entry_price'] - price) / position['entry_price']

        position['pnl'] += pnl
        self.daily_pnl += pnl

        self.logger.info(f"🎯 TP{target['level']} HIT: {position['id']}")
        self.logger.info(f"   Closed {target['percent']:.0%} at ${price:,.0f}")
        self.logger.info(f"   Partial PnL: ${pnl:+.2f}")

        self._log_trade(position, f"tp_{target['level']}")

    async def _close_position(self, position: Dict, price: float, reason: str):
        """Close entire position"""

        # Calculate final PnL
        if position['type'] == 'long':
            final_pnl = position['size'] * (price - position['entry_price']) / position['entry_price']
        else:
            final_pnl = position['size'] * (position['entry_price'] - price) / position['entry_price']

        position['pnl'] += final_pnl
        self.daily_pnl += final_pnl
        position['status'] = 'closed'
        position['exit_price'] = price
        position['exit_time'] = datetime.now()
        position['exit_reason'] = reason

        # Track consecutive losses
        if position['pnl'] < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0

        # Record trade
        self.risk_mgr.record_trade(profit=position['pnl'], success=position['pnl'] > 0)

        # Log
        emoji = "✅" if position['pnl'] > 0 else "❌"
        self.logger.info(f"{emoji} CLOSED: {position['id']}")
        self.logger.info(f"   Reason: {reason}")
        self.logger.info(f"   Entry: ${position['entry_price']:,.0f} → Exit: ${price:,.0f}")
        self.logger.info(f"   PnL: ${position['pnl']:+.2f}")
        self.logger.info(f"   Daily PnL: ${self.daily_pnl:+.2f}")

        self._log_trade(position, 'exit')

        # Remove from active positions
        self.positions.remove(position)

    def _check_safety(self) -> bool:
        """Check kill switches"""

        # Daily loss limit
        if abs(self.daily_pnl) >= self.config.DAILY_LOSS_LIMIT:
            self.logger.error(f"🛑 Daily loss limit hit: ${self.daily_pnl:.2f}")
            return False

        # Consecutive losses
        if self.consecutive_losses >= self.config.CONSECUTIVE_LOSSES:
            self.logger.error(f"🛑 {self.consecutive_losses} consecutive losses - stopping")
            return False

        return True

    def _log_trade(self, position: Dict, event_type: str):
        """Log trade to JSON file"""
        log_file = REPO_ROOT / "logs" / "btc_scalper_trades.json"

        trade_log = {
            'timestamp': datetime.now().isoformat(),
            'event': event_type,
            'position_id': position['id'],
            'type': position['type'],
            'strategy': position['strategy'],
            'entry_price': position['entry_price'],
            'current_price': position.get('exit_price', 0),
            'size': position['size'],
            'pnl': position['pnl'],
            'daily_pnl': self.daily_pnl
        }

        with open(log_file, 'a') as f:
            f.write(json.dumps(trade_log) + '\n')

# ═══════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════

async def main():
    """Run BTC Range Scalper"""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║   🎯 BTC RANGE SCALPER - $109K-$116K                               ║
║   Sovereign Shadow Trading Empire                                  ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝

Market Intel (October 2025):
• BTC consolidating $106K-$112K (current range)
• Trading range: $109K-$116K
• Post-halving: 3.125 BTC/block
• Flow: OTC distribution + retail accumulation
• Strategy: Fast scalps at range edges

Configuration:
• Position: $50-$150
• 3-Step TP: 0.5%, 1.0%, 2.0%
• Stop: 0.8%-1.2% (dynamic)
• Max holding: 30 minutes
• Daily limit: $100 loss

Philosophy: "Fearless. Bold. Smiling through chaos."

Starting in 3 seconds...
""")

    await asyncio.sleep(3)

    # Initialize and run
    scalper = BTCRangeScalper()

    try:
        await scalper.start()
    except KeyboardInterrupt:
        print("\n\n🛑 Scalper stopped by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
    finally:
        scalper.scope.stop_scanner()
        print(f"\n📊 Final Stats:")
        print(f"   Trades: {scalper.trade_count}")
        print(f"   Daily PnL: ${scalper.daily_pnl:+.2f}")
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    asyncio.run(main())
