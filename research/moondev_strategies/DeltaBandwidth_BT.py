```python
import pandas as pd
import talib
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

class DeltaBandwidth(Strategy):
    risk_pct = 0.01  # 1% risk per trade
    atr_period = 14
    cvd_window = 20
    sma_period = 3 * 24 * 4  # 3-day SMA for 15m data
    bb_period = 20
    bandwidth_lookback = 6 * 30 * 24 * 4  # 6-month lookback

    def init(self):
        # Bollinger Bands components
        self.middle = self.I(talib.SMA, self.data.Close, self.bb_period, name='BB_MID')
        self.std = self.I(talib.STDDEV, self.data.Close, self.bb_period, name='BB_STD')
        self.upper = self.I(lambda: self.middle + 2*self.std, name='BB_UPPER')
        self.lower = self.I(lambda: self.middle - 2*self.std, name='BB_LOWER')
        
        # Bollinger Bandwidth
        self.bandwidth = self.I(lambda: (self.upper - self.lower)/self.middle, name='BB_WIDTH')
        self.bandwidth_low = self.I(talib.MIN, self.bandwidth, self.bandwidth_lookback, name='BBW_LOW')
        
        # Cumulative Volume Delta
        self.cvd = self.I(self._calculate_cvd, name='CVD')
        
        # ATR for risk management
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, self.atr_period, name='ATR')
        
        # SMA for exit
        self.exit_sma = self.I(talib.SMA, self.data.Close, self.sma_period, name='EXIT_SMA')

    def _calculate_cvd(self):
        delta = np.where(self.data.Close > self.data.Open, self.data.Volume, -self.data.Volume)
        return delta.cumsum()

    def next(self):
        if len(self.data) < max(self.bandwidth_lookback, self.sma_period, self.cvd_window):
            return

        # Check bandwidth contraction
        if self.bandwidth[-1] != self.bandwidth_low[-1]:
            return

        # Find liquidity clusters
        cvd_window = self.cvd[-self.cvd_window:]
        max_idx = np.argmax(cvd_window)
        min_idx = np.argmin(cvd_window)
        liquidity_high = self.data.High[-self.cvd_window + max_idx]
        liquidity_low = self.data.Low[-self.cvd_window + min_idx]

        # Entry logic
        current_close = self.data.Close[-1]
        atr_value = self.atr[-1]
        
        if not self.position:
            # Long entry
            if current_close > liquidity_high:
                stop_price = current_close - 2 * atr_value
                risk_amount = self.risk_pct * self.equity
                position_size = int(round(risk_amount / (current_close - stop_price)))
                if position_size > 0:
                    self.buy(size=position_size, sl=stop_price)
                    print(f"🚀 MOON DEV LONG! 🌙 Size: {position_size} | Entry: {current_close:.2f} | SL: {stop_price:.2f} ✨")

            # Short entry
            elif current_close < liquidity_low:
                stop_price = current_close + 2 * atr_value
                risk_amount = self.risk_pct * self.equity
                position_size = int(round(risk_amount / (stop_price - current_close)))
                if position_size > 0:
                    self.sell(size=position_size, sl=stop_price)
                    print(f"🌑 MOON DEV SHORT! 🌙 Size: {position_size} | Entry: {current_close:.2f} | SL: {stop_price:.2f} ✨")

        # Exit logic
        elif self.position.is_long and current_close < self.exit_sma[-1]:
            self.position.close()
            print(f"🌕 MOON DEV EXIT LONG! 🌙 Price {current_close:.2f} < SMA {self.exit_sma[-1]:.2f}")

        elif self.position.is_short and current_close > self.exit_sma[-1]:
            self.position.close()
            print(f"🌓 MOON DEV EXIT SHORT! 🌙 Price {current_close:.2f} > SMA {self.exit_sma[-