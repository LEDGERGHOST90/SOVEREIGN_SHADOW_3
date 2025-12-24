Here's the fixed code with Moon Dev themed debug prints and proper technical implementation. I've ensured all position sizing rules are followed and all indicators are properly wrapped:

```python
import pandas as pd
import talib
from backtesting import Backtest, Strategy

# Data preprocessing
data_path = '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv'
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')

# Clean and format columns
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

class BandSqueezeReversal(Strategy):
    def init(self):
        # Heikin-Ashi calculation
        ha_close, ha_open = [], []
        ha_high, ha_low = [], []
        
        for i in range(len(self.data.Close)):
            if i == 0:
                ha_open_val = (self.data.Open[i] + self.data.Close[i]) / 2
                ha_close_val = (self.data.Open[i] + self.data.High[i] + self.data.Low[i] + self.data.Close[i]) / 4
            else:
                ha_open_val = (ha_open[i-1] + ha_close[i-1]) / 2
                ha_close_val = (self.data.Open[i] + self.data.High[i] + self.data.Low[i] + self.data.Close[i]) / 4
            
            ha_high_val = max(self.data.High[i], ha_open_val, ha_close_val)
            ha_low_val = min(self.data.Low[i], ha_open_val, ha_close_val)
            
            ha_open.append(ha_open_val)
            ha_close.append(ha_close_val)
            ha_high.append(ha_high_val)
            ha_low.append(ha_low_val)
        
        # Add indicators
        self.ha_close = self.I(pd.Series, ha_close, name='HA_Close')
        self.ha_open = self.I(pd.Series, ha_open, name='HA_Open')
        self.ha_high = self.I(pd.Series, ha_high, name='HA_High')
        self.ha_low = self.I(pd.Series, ha_low, name='HA_Low')
        
        # Bollinger Bands using talib
        self.bb_upper, self.bb_middle, self.bb_lower = self.I(
            talib.BBANDS, 
            self.data.Close, 
            timeperiod=20,
            nbdevup=2,
            nbdevdn=2,
            matype=0,
            name='BBANDS'
        )
        self.bb_width = self.I(lambda x: self.bb_upper - self.bb_lower, name='BB_Width')
        self.min_bb_width = self.I(talib.MIN, self.bb_width, timeperiod=10, name='MIN_BB_Width')
        
        # ATR using talib
        self.atr = self.I(
            talib.ATR,
            self.data.High,
            self.data.Low,
            self.data.Close,
            timeperiod=14,
            name='ATR'
        )
        
    def next(self):
        # Skip early bars
        if len(self.data) < 20 or len(self.ha_close) < 3:
            return
        
        # Get current values
        current_bb_width = self.bb_width[-1]
        current_min_bb = self.min_bb_width[-1]
        
        # Check squeeze condition
        squeeze = current_bb_width <= current_min_bb
        
        # Check 3 consecutive bullish HA closes
        ha_bullish = all(self.ha_close[-i] > self.ha_open[-i] for i in range(1,4))
        
        # Entry logic
        if not self.position and squeeze and ha_bullish:
            # Risk management
            risk_pct = 0.01
            risk_amount = self.equity * risk_pct
            atr_val = self.atr[-1]
            
            if atr_val == 0:
                return
                
            # Calculate position size in whole units
            position_size = int(round(risk_amount / (2 * atr_val)))
            
            if position_size > 0:
                self.buy(size=position_size)
                print(f"🌕 MOON DEV ENTRY: LONG {position_size} units at {self.data.Close[-