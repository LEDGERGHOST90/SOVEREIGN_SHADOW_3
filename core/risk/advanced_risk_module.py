import logging
from typing import Dict, List, Optional
import numpy as np
import pandas as pd # Assuming pandas for technical indicator calculations

logger = logging.getLogger(__name__)

class SentinelAdvancedRiskModule:
    """
    SENTINEL: Advanced Risk Module
    Integrates ATR, Kelly Criterion, and circuit breaker logic for dynamic risk management.
    """

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.atr_period = self.config.get("atr_period", 14)
        self.kelly_risk_factor = self.config.get("kelly_risk_factor", 0.5) # Fraction of Kelly bet
        self.breaker_threshold_pct = self.config.get("breaker_threshold_pct", 5.0) # 5% move
        self.breaker_duration_minutes = self.config.get("breaker_duration_minutes", 30)
        self.last_prices: Dict[str, float] = {} # Asset -> last close price
        self.high_prices: Dict[str, float] = {} # Asset -> daily high
        self.low_prices: Dict[str, float] = {} # Asset -> daily low
        self.current_atr: Dict[str, float] = {} # Asset -> current ATR
        self.is_circuit_broken: Dict[str, bool] = {} # Asset -> if circuit breaker is active
        self.breaker_release_time: Dict[str, datetime] = {} # Asset -> time when breaker releases

        logger.info("SENTINEL Advanced Risk Module initialized.")

    def update_price_data(self, asset: str, close_price: float, high_price: float, low_price: float):
        """
        Updates price data for ATR calculation and circuit breaker monitoring.
        Needs to be called with each new candle (e.g., daily or hourly close).
        """
        self.last_prices[asset] = close_price
        self.high_prices[asset] = high_price
        self.low_prices[asset] = low_price
        
        # Simple ATR for demonstration, in a real system this would use historical data.
        # For a true ATR, we need a history of True Ranges (TR).
        # TR = max[(High - Low), abs(High - PreviousClose), abs(Low - PreviousClose)]
        if asset in self.last_prices and asset in self.high_prices and asset in self.low_prices:
            # Placeholder for actual ATR calculation
            # For simplicity, we'll use a rolling average of (high-low) as a proxy
            # In a live system, this would be a proper EWMA or SMA of True Range.
            self.current_atr[asset] = (high_price - low_price) * 0.5 # Simplified
        else:
            self.current_atr[asset] = 0.0 # Or some initial value

        # Check circuit breaker
        self._check_circuit_breaker(asset, close_price)

        logger.debug(f"Updated {asset} price data: Close={close_price}, ATR={self.current_atr.get(asset, 'N/A')}")

    def calculate_atr_stop_loss(self, asset: str, multiplier: float = 2.0) -> Optional[float]:
        """
        Calculates a stop loss level based on Average True Range (ATR).
        """
        if asset not in self.current_atr or self.current_atr[asset] == 0.0:
            logger.warning(f"ATR not available for {asset}. Cannot calculate ATR stop loss.")
            return None
        return self.current_atr[asset] * multiplier

    def calculate_kelly_bet_size(self,
                                 win_probability: float,
                                 payout_ratio: float,
                                 current_capital: float) -> float:
        """
        Calculates optimal bet size using the Kelly Criterion.
        Kelly Formula: f = p - (1-p)/b
        where:
        f = fraction of capital to bet
        p = probability of winning
        b = payout ratio (profit per unit risked)
        """
        if not (0 < win_probability < 1) or payout_ratio <= 0:
            logger.warning(f"Invalid inputs for Kelly Criterion: win_prob={win_probability}, payout_ratio={payout_ratio}")
            return 0.0

        kelly_fraction = win_probability - (1 - win_probability) / payout_ratio
        
        if kelly_fraction <= 0:
            return 0.0
        
        # Apply risk factor to Kelly fraction
        adjusted_kelly_fraction = kelly_fraction * self.kelly_risk_factor
        bet_size = current_capital * adjusted_kelly_fraction
        
        logger.debug(f"Kelly bet size for {current_capital} capital (p={win_probability}, b={payout_ratio}): {bet_size:.2f}")
        return bet_size

    def _check_circuit_breaker(self, asset: str, current_price: float):
        """
        Checks for circuit breaker conditions. If triggered, sets a flag and release time.
        """
        if asset not in self.last_prices:
            return # Need previous price to check for breaker

        price_change_pct = ((current_price - self.last_prices[asset]) / self.last_prices[asset]) * 100

        if abs(price_change_pct) >= self.breaker_threshold_pct:
            self.is_circuit_broken[asset] = True
            self.breaker_release_time[asset] = datetime.now() + timedelta(minutes=self.breaker_duration_minutes)
            logger.warning(f"🚨 CIRCUIT BREAKER TRIGGERED for {asset}! Price moved {price_change_pct:.2f}%")
        elif self.is_circuit_broken.get(asset, False) and datetime.now() >= self.breaker_release_time[asset]:
            self.is_circuit_broken[asset] = False
            logger.info(f"✅ CIRCUIT BREAKER RELEASED for {asset}.")

    def is_breaker_active(self, asset: str) -> bool:
        """
        Returns true if a circuit breaker is currently active for the asset.
        """
        if self.is_circuit_broken.get(asset, False):
            if datetime.now() < self.breaker_release_time[asset]:
                return True
            else:
                self.is_circuit_broken[asset] = False # Auto-release if time passed
                logger.info(f"✅ CIRCUIT BREAKER AUTO-RELEASED for {asset}.")
                return False
        return False

# Example usage (for testing)
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    
    config = {
        "atr_period": 14,
        "kelly_risk_factor": 0.7,
        "breaker_threshold_pct": 3.0,
        "breaker_duration_minutes": 5
    }
    sentinel = SentinelAdvancedRiskModule(config)

    print("\n--- ATR Test ---")
    # Simulate price updates over time (simplified)
    sentinel.update_price_data("BTC", close_price=30000, high_price=30500, low_price=29800)
    sentinel.update_price_data("BTC", close_price=30200, high_price=30300, low_price=30000)
    sentinel.update_price_data("BTC", close_price=30150, high_price=30250, low_price=30050)
    
    stop_loss = sentinel.calculate_atr_stop_loss("BTC")
    if stop_loss:
        print(f"Calculated ATR Stop Loss for BTC: {stop_loss:.2f}")

    print("\n--- Kelly Criterion Test ---")
    capital = 10000.0
    win_prob = 0.55
    payout_ratio = 1.5 # For every $1 risked, you win $1.5
    bet_size = sentinel.calculate_kelly_bet_size(win_prob, payout_ratio, capital)
    print(f"Optimal Kelly Bet Size: ${bet_size:.2f}")

    win_prob_bad = 0.45
    bet_size_bad = sentinel.calculate_kelly_bet_size(win_prob_bad, payout_ratio, capital)
    print(f"Optimal Kelly Bet Size (bad prob): ${bet_size_bad:.2f}")

    print("\n--- Circuit Breaker Test ---")
    sentinel.update_price_data("ETH", close_price=2000, high_price=2050, low_price=1980)
    print(f"Is ETH breaker active? {sentinel.is_breaker_active('ETH')}")
    
    # Trigger breaker with a large move
    sentinel.update_price_data("ETH", close_price=2100, high_price=2150, low_price=2080) # +5% move
    print(f"Is ETH breaker active after trigger? {sentinel.is_breaker_active('ETH')}")
    
    # Simulate time passing (manual for demo)
    import time
    print("Waiting 6 minutes to simulate breaker release...")
    # time.sleep(360) # In a real test, this would simulate passage of time
    # For now, manually set release time to past for demo
    sentinel.breaker_release_time["ETH"] = datetime.now() - timedelta(minutes=1)
    
    print(f"Is ETH breaker active after simulated time pass? {sentinel.is_breaker_active('ETH')}")
