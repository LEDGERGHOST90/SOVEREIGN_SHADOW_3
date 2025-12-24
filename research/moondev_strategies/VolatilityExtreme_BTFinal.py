```python
# 🌙 MOON DEV BACKTESTING IMPLEMENTATION FOR VOLATILITYEXTREME STRATEGY

import pandas as pd
import talib
import numpy as np
from backtesting import Backtest, Strategy

class VolatilityExtreme(Strategy):
    lookback_period = 20
    risk_percent = 0.01
    max_hold_bars = 480  # 5 days in 15m intervals (96*5)

    def init(self):
        # 🌙 MOON DEV INDICATORS
        self.sma = self.I(talib.SMA, self.data.Close, timeperiod=self.lookback_period)
        self.std = self.I(talib.STDDEV, self.data.Close, timeperiod=self.lookback_period)
        self.entry_bar = 0  # Track entry bar for time-based exit

    def next(self):
        current_close = self.data.Close[-1]
        current_sma = self.sma[-1] if len(self.sma) > 0 else 0
        current_std = self.std[-1] if len(self.std) > 0 else 0

        if not self.position:
            # 🌙 CALCULATE VOLATILITY BANDS
            upper_2std = current_sma + 2*current_std
            upper_3std = current_sma + 3*current_std
            lower_3std = current_sma - 3*current_std
            lower_4std = current_sma - 4*current_std

            # 🚀 LONG ENTRY: 3-4σ BELOW MEAN
            if lower_4std < current_close < lower_3std:
                risk_amount = self.equity * self.risk_percent
                risk_per_share = 1.5 * current_std
                
                if risk_per_share > 0:
                    position_size = int(round(risk_amount / risk_per_share))
                    stop_loss = current_close - 1.5*current_std
                    
                    if position_size > 0:
                        self.buy(size=position_size, sl=stop_loss)
                        self.entry_bar = len(self.data)-1
                        print(f"🌙🚀 MOON DEV LONG: {current_close:.2f} < 3σ {lower_3std:.2f} | SL: {stop_loss:.2f} | Size: {position_size}")

            # 📉 SHORT ENTRY: 2-3σ ABOVE MEAN
            elif upper_2std < current_close < upper_3std:
                risk_amount = self.equity * self.risk_percent
                risk_per_share = 1.5 * current_std
                
                if risk_per_share > 0:
                    position_size = int(round(risk_amount / risk_per_share))
                    stop_loss = current_close + 1.5*current_std
                    
                    if position_size > 0:
                        self.sell(size=position_size, sl=stop_loss)
                        self.entry_bar = len(self.data)-1
                        print(f"🌙📉 MOON DEV SHORT: {current_close:.2f} > 2σ {upper_2std:.2f} | SL: {stop_loss:.2f} | Size: {position_size}")
        else:
            # ⏰ TIME-BASED EXIT CHECK
            current_bar = len(self.data)-1
            bars_held = current_bar - self.entry_bar
            
            if bars_held >= self.max_hold_bars:
                self.position.close()
                print(f"🌙⏰ MOON DEV TIME EXIT: Held {bars_held} bars")
                return

            # ✨ MEAN REVERSION EXIT
            if self.position.is_long:
                exit_level = current_sma - current_std
                if current_close >= exit_level:
                    self.position.close()
                    print(f"🌙✨ MOON DEV LONG EXIT: {current_close:.2f} >= 1σ {exit_level:.2f}")
            elif self.position.is_short:
                exit_level = current_sma + current_std
                if current_close <= exit_level:
                    self.position.close()
                    print(f"🌙✨ MOON DEV SHORT EXIT: {current_close:.2f} <= 1σ {exit_level:.2f}")

# 🌙 DATA PREPARATION
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = [col.strip() for col in data.columns]  # Ensure column names are clean

# 🌙 BACKTEST EXECUTION