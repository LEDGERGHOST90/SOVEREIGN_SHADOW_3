I've analyzed the code and found a few technical issues that need fixing. Here's the corrected version with Moon Dev themed debug prints:

```python
import pandas as pd
import talib
from backtesting import Backtest, Strategy
import numpy as np

class MomentumBreakout(Strategy):
    ema_period_fast = 50
    ema_period_slow = 200
    adx_period = 14
    atr_period = 14
    rsi_period = 5
    risk_pct = 0.01  # 1% risk per trade

    def init(self):
        # Calculate indicators using TA-Lib through self.I()
        self.ema50 = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_period_fast, name='EMA50')
        self.ema200 = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_period_slow, name='EMA200')
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, timeperiod=self.adx_period, name='ADX')
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period, name='ATR')
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period, name='RSI')

    def next(self):
        # Moon Dev's Galactic Checkpoint 🌌
        if len(self.data) < 3:
            return

        # Entry Logic Constellation 🌠
        if not self.position:
            # Check previous bar conditions
            ema50_prev = self.ema50[-2]
            ema200_prev = self.ema200[-2]
            adx_prev = self.adx[-2]
            adx_prev_prev = self.adx[-3] if len(self.adx) >= 3 else np.nan

            # Null Check Force Field 🛡️
            if any(np.isnan([ema50_prev, ema200_prev, adx_prev, adx_prev_prev])):
                return

            # Bullish Alignment Check 🌟
            ema_crossover = (ema50_prev > ema200_prev) and (self.ema50[-3] <= self.ema200[-3])
            adx_strength = (adx_prev > 25) and (adx_prev > adx_prev_prev)

            if ema_crossover and adx_strength:
                # Risk Management Supernova 💫
                atr_value = self.atr[-2]
                entry_price = self.data.Open[-1]
                stop_loss = entry_price - 2 * atr_value
                
                risk_amount = self.equity * self.risk_pct
                risk_per_share = entry_price - stop_loss
                
                if risk_per_share <= 0:
                    return  # Black Hole Defense 🕳️

                position_size = int(round(risk_amount / risk_per_share))
                
                if position_size > 0:
                    self.buy(size=position_size, sl=stop_loss, 
                            tag="🌕 Lunar Launch Detected!")
                    print(f"🚀🌙 MOON DEV ALERT: ENTERING ORBIT @ {entry_price:.2f}"
                          f" | Size: {position_size} | Cosmic Stop: {stop_loss:.2f}")

        # Exit Protocol: RSI Event Horizon 🌗
        else:
            current_rsi = self.rsi[-1]
            previous_rsi = self.rsi[-2]
            
            if not np.isnan([current_rsi, previous_rsi]).any():
                rsi_overbought = (previous_rsi < 70) and (current_rsi >= 70)
                rsi_oversold = (previous_rsi > 30) and (current_rsi <= 30)
                
                if rsi_overbought or rsi_oversold:
                    self.position.close()
                    print(f"🌑✨ MOON DEV EXIT: RSI {current_rsi:.1f} - "
                          f"Returning to Space Station 🛸")

# Data Wormhole Configuration 🌐
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')

# Cosmic Data Cleansing 🌌
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col], errors='ignore')

# Stellar Column Mapping 🌠