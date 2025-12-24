Here's the complete backtesting implementation for the BandChannelBreakout strategy:

```python
# 🌙 Moon Dev's BandChannelBreakout Backtest 🌙
import pandas as pd
import talib
import pandas_ta as ta
from backtesting import Backtest, Strategy
from backtesting.lib import crossover, crossunder

# Clean and prepare data
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume',
}, inplace=True)
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

class BandChannelBreakout(Strategy):
    risk_percent = 0.01
    max_duration = 480  # 5 days in 15m intervals
    
    def init(self):
        # 🌙 Indicator Calculations
        # Bollinger Bands
        self.bb_upper, _, self.bb_lower = self.I(
            talib.BBANDS, self.data.Close, 
            timeperiod=20, nbdevup=2, nbdevdn=2, matype=0,
            name=['BB_UPPER', 'BB_MID', 'BB_LOWER']
        )
        
        # Keltner Channels
        def keltner_channels(h, l, c):
            typical_price = (h + l + c) / 3
            ema = talib.EMA(typical_price, 20)
            atr = talib.ATR(h, l, c, 20)
            return (ema + atr * 1.5, ema - atr * 1.5)
        
        self.kc_upper, self.kc_lower = self.I(
            keltner_channels, self.data.High, self.data.Low, self.data.Close,
            name=['KC_UPPER', 'KC_LOWER']
        )
        
        # Volume Percentile
        self.vol_pct = self.I(
            lambda v: pd.Series(v).rolling(90).quantile(0.9),
            self.data.Volume,
            name='VOL_PCT'
        )
        
        # Parabolic SAR
        self.sar = self.I(
            talib.SAR, self.data.High, self.data.Low,
            acceleration=0.02, maximum=0.2,
            name='SAR'
        )
        
        # RSI
        self.rsi = self.I(talib.RSI, self.data.Close, 14, name='RSI')
        
        self.trade_entry_bar = 0

    def next(self):
        # 🌙 Exit Conditions
        if self.position:
            duration = len(self.data) - self.trade_entry_bar
            if self.position.is_long:
                if (crossunder(self.data.Close, self.sar) or \
                   (self.rsi[-1] < 50 and self.rsi[-2] >= 50) or \
                   (self.data.Close[-1] < self.kc_upper[-1]) or \
                   (duration >= self.max_duration):
                    self.position.close()
                    print(f"🌙 Moon Exit | LONG CLOSE | Price: {self.data.Close[-1]:.2f} | RSI: {self.rsi[-1]:.2f} ✨")
            
            else:  # Short position
                if (crossover(self.data.Close, self.sar) or \
                   (self.rsi[-1] > 50 and self.rsi[-2] <= 50) or \
                   (self.data.Close[-1] > self.kc_lower[-1]) or \
                   (duration >= self.max_duration):
                    self.position.close()
                    print(f"🌙 Moon Exit | SHORT CLOSE | Price: {self.data.Close[-1]:.2f} | RSI: {self.rsi[-1]:.2f} ✨")

        # 🌙 Entry Conditions
        if not self.position:
            squeeze = (self.bb_upper[-1] < self.kc_upper[-1]) and \
                     (self.bb_lower[-1] > self.kc_lower[-1])
            
            vol_ok = self.data.Volume[-1] > self.vol_pct[-1]
            
            # RSI Divergence Check
            price_lows = self.data.Low[-3:]
            rsi_lows = self.rsi[-3:]
            bull_div