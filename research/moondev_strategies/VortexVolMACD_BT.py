```python
import pandas as pd
import talib
import pandas_ta as ta
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

# Load and preprocess data
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd.read_csv(data_path, parse_dates=['datetime'])
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Rename columns to match backtesting.py requirements
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)
data.set_index('datetime', inplace=True)

class VortexVolMACD(Strategy):
    risk_pct = 0.01  # 1% risk per trade
    
    def init(self):
        # Calculate indicators using TA-Lib/pandas_ta with self.I()
        self.vi_plus, self.vi_minus = self.I(ta.vortex, 
                                           high=self.data.High, 
                                           low=self.data.Low, 
                                           length=14, 
                                           name=['VI+', 'VI-'])
        
        # Volume-weighted MACD
        close_volume = self.data.Close * self.data.Volume
        macd, signal, _ = talib.MACD(close_volume, 
                                    fastperiod=12, 
                                    slowperiod=26, 
                                    signalperiod=9)
        self.macd_line = self.I(lambda x: macd, name='MACD')
        self.signal_line = self.I(lambda x: signal, name='Signal')
        
        # Keltner Channels
        ema20 = self.I(talib.EMA, self.data.Close, 20)
        atr20 = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 20)
        self.upper_kc = self.I(lambda x: ema20 + 1.5*atr20, name='Upper KC')
        self.lower_kc = self.I(lambda x: ema20 - 1.5*atr20, name='Lower KC')
        
        # Volatility filter
        kc_width = self.upper_kc - self.lower_kc
        self.kc_width_avg = self.I(talib.SMA, kc_width, 20)
        
    def next(self):
        # Moon Dev safety check ✨
        if len(self.data.Close) < 20:
            return

        # Get current values
        vi_plus, vi_minus = self.vi_plus[-1], self.vi_minus[-1]
        macd, signal = self.macd_line[-1], self.signal_line[-1]
        close = self.data.Close[-1]
        upper_kc, lower_kc = self.upper_kc[-1], self.lower_kc[-1]
        kc_width = upper_kc - lower_kc
        kc_width_avg = self.kc_width_avg[-1]

        # Moon Dev crossover detection 🌙
        vi_bullish = crossover(vi_plus, vi_minus)
        vi_bearish = crossover(vi_minus, vi_plus)
        macd_bullish = crossover(self.macd_line, self.signal_line)
        macd_bearish = crossover(-self.macd_line, -self.signal_line)
        price_in_kc = lower_kc < close < upper_kc
        low_volatility = kc_width < kc_width_avg

        # Moon Dev Risk Management 🌙
        equity = self.equity
        risk_amount = equity * self.risk_pct

        # Long entry constellation 🌌
        if not self.position and vi_bullish and macd_bullish and price_in_kc and low_volatility:
            sl = lower_kc - (0.01 * close)  # 1% buffer below KC
            risk_per_unit = close - sl
            if risk_per_unit > 0:
                size = int(round(risk_amount / risk_per_unit))
                self.buy(size=size, sl=sl, tp=close + 2*(close - sl))
                print(f"🌙✨🚀 MOON DEV LONG ENTRY! Size: {size} | Entry: {close:.2f} | SL: {sl:.2f} | TP: {close + 2*(close - sl):.2f}")

        # Short entry constellation 🌌
        elif not self