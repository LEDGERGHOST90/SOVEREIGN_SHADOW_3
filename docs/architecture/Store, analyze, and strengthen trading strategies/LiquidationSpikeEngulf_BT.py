```python
# -*- coding: utf-8 -*-
import pandas as pd
from backtesting import Backtest, Strategy
import talib

# 🌙 Moon Dev Data Preparation
def load_data(path):
    data = pd.read_csv(path)
    # Clean column names
    data.columns = data.columns.str.strip().str.lower()
    # Drop unnamed columns
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
    # Map to backtesting.py columns
    data.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    }, inplace=True)
    # Ensure datetime index
    data['datetime'] = pd.to_datetime(data['datetime'])
    data.set_index('datetime', inplace=True)
    return data

# 🚀 Moon Dev Strategy Implementation
class LiquidationSpikeEngulf(Strategy):
    liquidation_threshold = 2.0  # Spike = 2x 24h average
    risk_percent = 1             # 1% risk per trade
    atr_period = 14
    liq_window = 96              # 24h in 15m intervals (24*4)

    def init(self):
        # 🌙 Indicators using TA-Lib
        self.liq_sma = self.I(talib.SMA, self.data.short_liquidations, self.liq_window)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, self.atr_period)

    def next(self):
        # ✨ Skip early candles
        if len(self.data) < self.liq_window + 2:
            return

        # 🌙 Liquidation Spike Detection
        current_liq = self.data.short_liquidations[-1]
        liq_sma = self.liq_sma[-1]
        spike_detected = current_liq > liq_sma * self.liquidation_threshold

        # 🕯️ Bullish Engulfing Pattern
        prev_bearish = self.data.Close[-2] < self.data.Open[-2]
        curr_bullish = self.data.Close[-1] > self.data.Open[-1]
        body_engulf = (self.data.Close[-1] - self.data.Open[-1]) > (self.data.Open[-2] - self.data.Close[-2])
        engulf_confirmed = prev_bearish and curr_bullish and body_engulf

        if not self.position and spike_detected and engulf_confirmed:
            # 🎯 Calculate Position Size
            entry_price = self.data.Close[-1]
            atr_value = self.atr[-1]
            sl_price = entry_price - 0.5 * atr_value
            risk_amount = self.equity * self.risk_percent / 100
            risk_per_unit = entry_price - sl_price
            
            if risk_per_unit <= 0:
                print("⚠️ Moon Dev Warning: Invalid risk calculation")
                return

            position_size = int(round(risk_amount / risk_per_unit))
            if position_size <= 0:
                return

            # 🚀 Execute Trade
            tp_price = entry_price + 1.5 * atr_value
            self.buy(size=position_size, 
                    sl=sl_price,
                    tp=tp_price,
                    tag="MoonDevLiquidationSpike")
            
            print(f"""
            🌕🌖🌗🌘🌑🌒🌓🌔🌕
            🚀 MOON DEV TRADE TRIGGERED 🚀
            Entry Price: {entry_price:.2f}
            Position Size: {position_size} units
            TP: {tp_price:.2f} (1.5xATR)
            SL: {sl_price:.2f} (0.5xATR)
            Equity: {self.equity:.2f}
            🌙✨🌙✨🌙✨🌙✨🌙
            """)

# 📊 Backtest Execution
if __name__ == "__main__":
    # Load and prepare data
    data = load_data("/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv")
    
    # 🌙 Run backtest with 1M USD capital
    bt = Backtest(data, LiquidationSpikeEngulf, cash=1_000_000)
    stats = bt.run()
    
    # 📈 Print Full Statistics
    print("\n🌙✨🌙✨🌙 MOON DEV BACKTEST RESULTS 🌙✨🌙✨🌙")
    print(st