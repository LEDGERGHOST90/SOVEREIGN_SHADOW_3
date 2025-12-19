```python
# 🌙 Moon Dev's VolCompress Surge Backtest 🌙
import pandas as pd
import talib
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

class VolCompressSurge(Strategy):
    # Strategy parameters
    bb_period = 20
    bb_dev = 2
    rsi_period = 14
    atr_period = 14
    bbw_lookback = 252
    risk_pct = 0.01
    max_position_pct = 0.05

    def init(self):
        # 🌟 Indicator calculation using TA-Lib
        self.bbw = self.I(self.calculate_bbw, self.data.Close)
        self.bbw_min = self.I(talib.MIN, self.bbw, self.bbw_lookback)
        self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_period)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, 
                         self.data.Close, self.atr_period)
        
        # 🌕 Tracking variables
        self.max_equity = self._broker.equity
        self.allow_trading = True
        self.trade_count = 0

    def calculate_bbw(self, close):
        """✨ Calculate Bollinger Band Width with TA-Lib"""
        upper, middle, lower = talib.BBANDS(
            close, 
            timeperiod=self.bb_period,
            nbdevup=self.bb_dev,
            nbdevdn=self.bb_dev
        )
        return (upper - lower) / middle

    def next(self):
        # 🌙 Update risk management metrics
        current_equity = self._broker.equity
        self.max_equity = max(self.max_equity, current_equity)
        drawdown = (self.max_equity - current_equity)/self.max_equity
        
        if drawdown > 0.10:
            self.allow_trading = False
            print(f"🌑🔥 PORTFOLIO DRAWDOWN 10%! Trading halted. Current DD: {drawdown*100:.1f}%")

        # Entry Logic 🌠
        if not self.position and self.allow_trading:
            bbw_condition = np.isclose(self.bbw[-1], self.bbw_min[-1], atol=1e-5)
            rsi_condition = self.rsi[-1] < 30
            
            if bbw_condition and rsi_condition:
                # 🚀 Calculate position size with risk management
                atr_value = self.atr[-1]
                risk_amount = self.risk_pct * current_equity
                position_size = risk_amount / atr_value
                
                # Enforce 5% maximum position size
                max_size = (self.max_position_pct * current_equity) / self.data.Close[-1]
                position_size = min(position_size, max_size)
                position_size = int(round(position_size))
                
                if position_size > 0:
                    self.buy(size=position_size)
                    self.trade_count += 1
                    self.entry_price = self.data.Close[-1]
                    self.stop_loss = self.entry_price - atr_value
                    self.trailing_level = self.entry_price + 2*atr_value
                    print(f"🌕🚀 ENTRY #{self.trade_count} @ {self.entry_price:.2f}")
                    print(f"    Size: {position_size} BTC | SL: {self.stop_loss:.2f} | Trail: {self.trailing_level:.2f}")

        # Exit Logic 🌈
        if self.position:
            # Trailing stop update
            self.trailing_level = max(self.trailing_level, self.data.High[-1] - 2*self.atr[-1])
            
            # Exit conditions
            if (self.data.Low[-1] < self.trailing_level or
                self.data.Low[-1] < self.stop_loss or
                crossover(self.rsi, 70)):
                
                self.position.close()
                pnl_pct = (self.data.Close[-1]/self.entry_price - 1)*100
                print(f"🌑📉 EXIT #{self.trade_count} @ {self.data.Close[-1]:.2f} ({pnl_pct:+.1f}%)")

# Data Preparation 🌍
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd