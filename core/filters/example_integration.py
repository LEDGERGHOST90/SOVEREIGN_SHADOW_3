"""
Market Filters Integration Example
===================================
Shows how to integrate MarketFilters with SOVEREIGN_SHADOW_3 trading agents.

Author: SOVEREIGN_SHADOW_3
Created: 2025-12-14
"""

from market_filters import MarketFilters, Signal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedTradingAgent:
    """
    Example trading agent with market filters integration.

    Demonstrates:
    1. Pre-trade market condition checks
    2. Dynamic position sizing based on market confidence
    3. Alert generation for extreme conditions
    4. Stop-loss adjustment based on market sentiment
    """

    def __init__(self):
        self.filters = MarketFilters()
        self.base_position_size = 50  # Base: $50 per position
        self.base_stop_loss = 0.03  # Base: 3% stop loss

    def should_execute_trade(self, signal_type: str) -> bool:
        """
        Pre-trade filter: Check if market conditions support this trade.

        Args:
            signal_type: "LONG" or "SHORT"

        Returns:
            True if trade should proceed, False if blocked
        """
        market = self.filters.get_combined_filter()

        logger.info(f"Market Filter Check: {market['signal']} (confidence: {market['confidence']}%)")

        # Block longs in strong bearish markets
        if signal_type == "LONG":
            if market['signal'] == Signal.BEARISH.value and market['confidence'] > 75:
                logger.warning(f"LONG blocked: {market['recommendation']}")
                return False

        # Block shorts in strong bullish markets
        elif signal_type == "SHORT":
            if market['signal'] == Signal.BULLISH.value and market['confidence'] > 75:
                logger.warning(f"SHORT blocked: {market['recommendation']}")
                return False

        logger.info("Trade approved by market filter")
        return True

    def calculate_position_size(self) -> float:
        """
        Dynamic position sizing based on market confidence.

        Returns:
            Position size in dollars
        """
        market = self.filters.get_combined_filter()

        # Adjust size based on conviction
        if market['confidence'] > 80:
            # Strong conviction = increase size by 50%
            multiplier = 1.5
            logger.info(f"High confidence ({market['confidence']}%) - Increasing position size")

        elif market['confidence'] < 50:
            # Low conviction = reduce size by 50%
            multiplier = 0.5
            logger.info(f"Low confidence ({market['confidence']}%) - Reducing position size")

        else:
            # Normal conditions
            multiplier = 1.0

        position_size = self.base_position_size * multiplier

        logger.info(f"Position size: ${position_size:.2f} (base: ${self.base_position_size}, multiplier: {multiplier}x)")

        return position_size

    def calculate_stop_loss(self) -> float:
        """
        Adjust stop-loss based on market conditions.

        Returns:
            Stop-loss percentage (e.g., 0.03 = 3%)
        """
        market = self.filters.get_combined_filter()

        # Tighten stops in bearish markets (risk management)
        if market['signal'] == Signal.BEARISH.value and market['confidence'] > 70:
            stop_loss = self.base_stop_loss * 0.7  # 30% tighter
            logger.info(f"Bearish market - Tightening stop to {stop_loss*100:.1f}%")

        # Slightly wider stops in bullish markets (give room to run)
        elif market['signal'] == Signal.BULLISH.value and market['confidence'] > 70:
            stop_loss = self.base_stop_loss * 1.2  # 20% wider
            logger.info(f"Bullish market - Widening stop to {stop_loss*100:.1f}%")

        else:
            stop_loss = self.base_stop_loss
            logger.info(f"Neutral market - Using base stop: {stop_loss*100:.1f}%")

        return stop_loss

    def check_extreme_conditions(self):
        """
        Monitor for extreme market conditions and generate alerts.
        """
        fgi = self.filters.get_fear_greed()

        # Extreme Greed - Sell signal
        if fgi['value'] > 80:
            logger.warning("=" * 60)
            logger.warning("ALERT: EXTREME GREED DETECTED")
            logger.warning(f"Fear & Greed Index: {fgi['value']}/100")
            logger.warning("Recommendation: Consider taking profits")
            logger.warning("Research: FGI > 80 sell = 50% more profit (backtested)")
            logger.warning("=" * 60)
            return "EXTREME_GREED"

        # Extreme Fear - Buy signal
        elif fgi['value'] < 25:
            logger.warning("=" * 60)
            logger.warning("ALERT: EXTREME FEAR DETECTED")
            logger.warning(f"Fear & Greed Index: {fgi['value']}/100")
            logger.warning("Recommendation: Look for buying opportunities")
            logger.warning("Historical: Extreme fear = strong buying zones")
            logger.warning("=" * 60)
            return "EXTREME_FEAR"

        return "NORMAL"

    def get_market_summary(self) -> dict:
        """
        Get comprehensive market summary for dashboard/logging.

        Returns:
            Dict with market conditions and recommendations
        """
        fgi = self.filters.get_fear_greed()
        dxy = self.filters.get_dxy_signal()
        combined = self.filters.get_combined_filter()

        summary = {
            'overall_signal': combined['signal'],
            'confidence': combined['confidence'],
            'recommendation': combined['recommendation'],
            'fear_greed': {
                'value': fgi['value'],
                'classification': fgi['classification'],
                'signal': fgi['signal']
            },
            'dxy': {
                'change_7d': dxy.get('change_7d', 0),
                'signal': dxy['signal'],
                'interpretation': dxy.get('interpretation', 'N/A')
            },
            'suggested_position_size': self.calculate_position_size(),
            'suggested_stop_loss': self.calculate_stop_loss() * 100  # Convert to percentage
        }

        return summary


def example_trade_workflow():
    """
    Example: Full trade workflow with market filters.
    """
    print("\n" + "=" * 80)
    print("TRADE WORKFLOW EXAMPLE")
    print("=" * 80)

    agent = EnhancedTradingAgent()

    # Step 1: Check extreme conditions
    print("\n1. Checking for extreme market conditions...")
    extreme = agent.check_extreme_conditions()
    print(f"   Extreme condition status: {extreme}")

    # Step 2: Get market summary
    print("\n2. Market Summary:")
    summary = agent.get_market_summary()
    print(f"   Overall Signal: {summary['overall_signal']} (Confidence: {summary['confidence']}%)")
    print(f"   Fear & Greed: {summary['fear_greed']['value']}/100 ({summary['fear_greed']['classification']})")
    print(f"   DXY Change (7d): {summary['dxy']['change_7d']:+.2f}% - {summary['dxy']['interpretation']}")
    print(f"   Recommendation: {summary['recommendation']}")

    # Step 3: Attempt to execute a long trade
    print("\n3. Attempting LONG trade...")
    signal_type = "LONG"

    if agent.should_execute_trade(signal_type):
        position_size = agent.calculate_position_size()
        stop_loss = agent.calculate_stop_loss()

        print(f"   ✓ Trade APPROVED")
        print(f"   Position Size: ${position_size:.2f}")
        print(f"   Stop Loss: {stop_loss*100:.1f}%")
        print(f"   Take Profit: 5.0%")  # Fixed for example

    else:
        print(f"   ✗ Trade BLOCKED by market filter")

    print("\n" + "=" * 80)


def example_monitoring_loop():
    """
    Example: Continuous market monitoring (use in background thread).
    """
    print("\n" + "=" * 80)
    print("MARKET MONITORING EXAMPLE")
    print("=" * 80)

    agent = EnhancedTradingAgent()

    # In real implementation, this would run in a loop
    print("\nCurrent market snapshot:")

    summary = agent.get_market_summary()

    # Display dashboard-style output
    print("\n┌─ MARKET CONDITIONS ─────────────────────────────────────────┐")
    print(f"│ Overall Signal:    {summary['overall_signal']:>10} ({summary['confidence']:>3}% confidence)  │")
    print(f"│ Fear & Greed:      {summary['fear_greed']['value']:>10}/100 ({summary['fear_greed']['classification']:>15}) │")
    print(f"│ DXY Trend (7d):    {summary['dxy']['change_7d']:>+9.2f}%                          │")
    print("├─ SUGGESTED PARAMETERS ──────────────────────────────────────┤")
    print(f"│ Position Size:     ${summary['suggested_position_size']:>9.2f}                          │")
    print(f"│ Stop Loss:         {summary['suggested_stop_loss']:>10.1f}%                          │")
    print("├─ RECOMMENDATION ────────────────────────────────────────────┤")
    print(f"│ {summary['recommendation']:<58} │")
    print("└─────────────────────────────────────────────────────────────┘")

    # Check for alerts
    agent.check_extreme_conditions()

    print("\n" + "=" * 80)


if __name__ == "__main__":
    print("\n")
    print("*" * 80)
    print("MARKET FILTERS INTEGRATION EXAMPLES")
    print("SOVEREIGN_SHADOW_3 Trading System")
    print("*" * 80)

    # Run examples
    example_trade_workflow()
    example_monitoring_loop()

    print("\n" + "=" * 80)
    print("INTEGRATION TIPS")
    print("=" * 80)
    print("""
1. PRE-TRADE FILTERING:
   - Call should_execute_trade() before every trade
   - Prevents trading against strong market headwinds

2. POSITION SIZING:
   - Use calculate_position_size() to adjust risk based on confidence
   - Reduces exposure in uncertain markets

3. RISK MANAGEMENT:
   - Use calculate_stop_loss() to adjust stops dynamically
   - Tighter stops in bearish markets protect capital

4. MONITORING:
   - Run check_extreme_conditions() every 15-60 minutes
   - Generate alerts for FGI > 80 (extreme greed) or FGI < 25 (extreme fear)

5. DASHBOARD:
   - Display get_market_summary() on your trading dashboard
   - Update every hour (FGI updates daily, DXY more frequent)

6. BACKTESTING:
   - Use get_fgi_history() to get historical data
   - Test your strategies with historical market conditions
    """)
    print("=" * 80)
    print()
