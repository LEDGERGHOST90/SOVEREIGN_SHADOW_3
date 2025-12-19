I'll fix the code while maintaining the original strategy logic and adding Moon Dev themed debug prints. Here's the corrected version:

```python
from backtesting import Backtest, Strategy
import pandas as pd
import talib
import numpy as np

# Load and preprocess data
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Column mapping and formatting
column_mapping = {
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}
data.rename(columns=column_mapping, inplace=True)
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

class LiquidationVolatility(Strategy):
    risk_pct = 0.01
    bb_period = 20
    bb_dev = 2
    atr_period = 14
    funding_extreme = 0.001
    liquidation_thresh = 1000000
    bbw_lookback = 20

    def init(self):
        # Bollinger Bands components
        self.mid_band = self.I(talib.SMA, self.data.Close, timeperiod=self.bb_period)
        self.upper_band = self.I(self._bb_upper, self.data.Close)
        self.lower_band = self.I(self._bb_lower, self.data.Close)
        
        # Bollinger Band Width
        self.bbw = self.I(self._calc_bbw, self.upper_band, self.lower_band, self.mid_band)
        
        # ATR for volatility measurement
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        
        # Funding rate and liquidation data
        self.funding = self.data['fundingrate']
        self.liquidations = self.data['liquidations']
        
        self.entry_atr = None
        self.entry_price = None

    def _bb_upper(self, close):
        upper, _, _ = talib.BBANDS(close, timeperiod=self.bb_period, nbdevup=self.bb_dev, nbdevdn=self.bb_dev)
        return upper

    def _bb_lower(self, close):
        _, _, lower = talib.BBANDS(close, timeperiod=self.bb_period, nbdevup=self.bb_dev, nbdevdn=self.bb_dev)
        return lower

    def _calc_bbw(self, upper, lower, mid):
        return (upper - lower) / mid

    def _enter_long(self):
        self.entry_atr = self.atr[-1]
        self.entry_price = self.data.Close[-1]
        size = round(self.risk_pct * self.equity / (1.5 * self.entry_atr))
        self.buy(size=min(size, 1))  # Ensure size doesn't exceed 100% of equity
        print(f"🌕🚀 Moon Launch! Long entry at {self.entry_price:.2f} with ATR shield {self.entry_atr:.2f}")

    def _enter_short(self):
        self.entry_atr = self.atr[-1]
        self.entry_price = self.data.Close[-1]
        size = round(self.risk_pct * self.equity / (1.5 * self.entry_atr))
        self.sell(size=min(size, 1))  # Ensure size doesn't exceed 100% of equity
        print(f"🌑🚀 Dark Moon! Short entry at {self.entry_price:.2f} with ATR shield {self.entry_atr:.2f}")

    def next(self):
        # Moon Dev position management system 🌙
        if self.position:
            current_atr = self.atr[-1]
            
            if self.position.is_long:
                sl_price = min(self.lower_band[-1], self.entry_price - 1.5*self.entry_atr)
                if self.data.Low[-1] < sl_price:
                    self.position.close()
                    print(f"🌙✨ Long stopped out at {self.data.Close[-1]:.2f}! Moon shields engaged!")
                elif current_atr >= 2*self.entry_atr:
                    self.position.close()
                    print(f"🚀🌕 ATR doubled! Long profit taken at {self.data.Close[-1]: