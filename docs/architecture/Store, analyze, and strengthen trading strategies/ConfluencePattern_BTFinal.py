```python
# 🌙 Moon Dev's ConfluencePattern Backtest Implementation
import pandas as pd
import talib
from backtesting import Backtest, Strategy

class ConfluencePattern(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade
    
    def init(self):
        # 🌙 Calculate indicators using TA-Lib with self.I()
        self.ema50 = self.I(talib.EMA, self.data.Close, timeperiod=50)
        self.ema200 = self.I(talib.EMA, self.data.Close, timeperiod=200)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=14)
        self.macd, self.macd_signal, self.macd_hist = self.I(talib.MACD, 
            self.data.Close, fastperiod=12, slowperiod=26, signalperiod=9)
        self.volume_sma = self.I(talib.SMA, self.data.Volume, timeperiod=20)
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=20)
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=20)
        
        print("🌙✨ Moon Dev Indicators Initialized!")
        print("EMA(50, 200), RSI(14), MACD(12,26,9)")
        print("Volume SMA(20), Swing High/Low(20)")

    def next(self):
        current_close = self.data.Close[-1]
        current_high = self.data.High[-1]
        current_low = self.data.Low[-1]
        current_volume = self.data.Volume[-1]

        # 🌙 Get indicator values
        ema50 = self.ema50[-1]
        ema200 = self.ema200[-1]
        rsi = self.rsi[-1]
        macd_hist = self.macd_hist[-1]
        volume_sma = self.volume_sma[-1]
        swing_high = self.swing_high[-1]
        swing_low = self.swing_low[-1]

        # 🌙 Moon Dev Risk Management Parameters
        risk_amount = self.risk_per_trade * self.equity
        position_size = 0

        if not self.position:
            # 🌙✨ Long Entry Conditions
            long_conditions = [
                current_close > ema50,
                current_close > ema200,
                rsi > 50,
                macd_hist > 0,
                current_volume > volume_sma,
                current_close > swing_high
            ]

            # 🌙✨ Short Entry Conditions
            short_conditions = [
                current_close < ema50,
                current_close < ema200,
                rsi < 50,
                macd_hist < 0,
                current_volume > volume_sma,
                current_close < swing_low
            ]

            if all(long_conditions):
                # 🌙 Calculate long position size
                entry_price = self.data.Open[-1]
                stop_loss = swing_low
                risk_per_share = entry_price - stop_loss
                
                if risk_per_share > 0:
                    position_size = int(round(risk_amount / risk_per_share))
                    take_profit = entry_price + 2 * risk_per_share
                    
                    if position_size > 0:
                        self.buy(size=position_size, sl=stop_loss, tp=take_profit)
                        print(f"🌙🚀✨ BULLISH CONFLUENCE! Long {position_size} shares")
                        print(f"Entry: {entry_price:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}")

            elif all(short_conditions):
                # 🌙 Calculate short position size
                entry_price = self.data.Open[-1]
                stop_loss = swing_high
                risk_per_share = stop_loss - entry_price
                
                if risk_per_share > 0:
                    position_size = int(round(risk_amount / risk_per_share))
                    take_profit = entry_price - 2 * risk_per_share
                    
                    if position_size > 0:
                        self.sell(size=position_size, sl=stop_loss, tp=take_profit)
                        print(f"🌙🚀✨ BEARISH CONFLUENCE! Short {position_size} shares")
                        print(f"Entry: {entry_price:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}")

# 🌙✨ Moon Dev Backtest Setup
if __name__ == "__main__":
    # Load your data here
    data = pd.read_csv('your_data.csv