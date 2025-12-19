I'll fix the backtesting.lib imports and ensure all indicators use proper packages. Here's the corrected code with Moon Dev themed debug prints:

```python
import pandas as pd
import talib
from backtesting import Backtest, Strategy
import numpy as np  # Added for array operations

class VolSpikeReversal(Strategy):
    # Strategy parameters
    funding_lookback = 90 * 96  # 90 days in 15m intervals
    risk_percent = 0.01
    stop_loss_pct = 0.05
    sma_period = 20
    exit_vol_multiplier = 3
    volatility_window = 16  # 4 hours in 15m intervals

    def init(self):
        # Clean data columns
        self.data.df.columns = self.data.df.columns.str.strip().str.lower()
        self.data.df = self.data.df.drop(columns=[col for col in self.data.df.columns if 'unnamed' in col])
        
        # Calculate indicators
        # Funding Rate 95th percentile
        self.funding_rate = self.data.df['funding_rate']
        self.funding_rate_95th = self.I(
            lambda x: x.rolling(self.funding_lookback).quantile(0.95),
            self.funding_rate,
            name='FUNDING_95TH'
        )

        # Trend confirmation SMA
        self.sma20 = self.I(talib.SMA, self.data.Close, timeperiod=self.sma_period, name='SMA20')

        # Exit volatility calculations
        returns = self.I(talib.ROC, self.data.Close, timeperiod=1, name='RETURNS')
        std_dev = self.I(talib.STDDEV, returns, timeperiod=self.volatility_window, name='STDDEV')
        volume_avg = self.I(talib.SMA, self.data.Volume, timeperiod=self.volatility_window, name='VOL_AVG')
        normalized_vol = self.I(lambda v, avg: v/avg, self.data.Volume, volume_avg, name='NORM_VOL')
        self.vol_weighted_vol = self.I(lambda std, vol: std*vol, std_dev, normalized_vol, name='VOL_W_VOL')
        self.vol_weighted_vol_avg = self.I(talib.SMA, self.vol_weighted_vol, timeperiod=self.volatility_window, name='VOL_W_VOL_AVG')

        # Track entry bar for time exit
        self.entry_bar = 0

    def next(self):
        current_bar = len(self.data)
        
        if self.position:
            # Check volatility exit condition
            current_vol = self.vol_weighted_vol[-1]
            current_vol_avg = self.vol_weighted_vol_avg[-1]
            if current_vol >= self.exit_vol_multiplier * current_vol_avg:
                self.position.close()
                print(f"🌪️ MOON DEV VOL EXIT | Bar {current_bar} | Price: {self.data.Close[-1]:.2f}")
                return

            # Time-based exit after 24 hours (96 periods)
            if current_bar - self.entry_bar >= 96:
                self.position.close()
                print(f"⏳ MOON DEV TIME EXIT | Bar {current_bar} | Held {current_bar-self.entry_bar} bars")
                return
        else:
            # Entry condition checks
            if len(self.data) < max(self.funding_lookback, self.sma_period+1):
                return

            current_funding = self.funding_rate[-1]
            current_95th = self.funding_rate_95th[-1]
            price_below_sma = self.data.Close[-1] < self.sma20[-1]
            sma_descending = self.sma20[-1] < self.sma20[-2]  # Manual crossover detection

            if current_funding > current_95th and price_below_sma and sma_descending:
                # Calculate position size
                equity = self.equity
                entry_price = self.data.Close[-1]
                stop_loss = entry_price * (1 + self.stop_loss_pct)
                risk_per_share = stop_loss - entry_price
                
                if risk_per_share <= 0:
                    print("⚠️ MOON DEV RISK ERROR: Invalid stop loss")
                    return

                position_size = int(round((equity * self.risk_percent) / risk_per_share))
                
                if position_size > 0:
                    self.sell(size=position_size, sl=stop_loss)
                    self.entry_bar = current_bar
                    print(f"🚀 MOON DEV SHORT EN