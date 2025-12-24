Here's the implementation of the LiquidationSqueeze strategy for backtesting.py:

```python
# -*- coding: utf-8 -*-
import pandas as pd
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover, crossunder

# Load and preprocess data
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Rename required columns to proper case
column_mapping = {
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}
data.rename(columns=column_mapping, inplace=True)

class LiquidationSqueeze(Strategy):
    timeperiod = 20
    bb_dev = 2
    swing_period = 20
    volume_lookback = 50
    funding_threshold = -0.0001  # -0.01%
    risk_pct = 0.02  # 2% per trade
    rrr = 2  # Risk:Reward
    
    def init(self):
        # Bollinger Bands with squeeze detection
        self.bb_upper = self.I(talib.BBANDS, self.data.Close, 
                              timeperiod=self.timeperiod, 
                              nbdevup=self.bb_dev, nbdevdn=self.bb_dev,
                              name='BB_UPPER', which=0)
        self.bb_lower = self.I(talib.BBANDS, self.data.Close, 
                              timeperiod=self.timeperiod, 
                              nbdevup=self.bb_dev, nbdevdn=self.bb_dev,
                              name='BB_LOWER', which=2)
        
        # Swing high/low indicators
        self.swing_high = self.I(talib.MAX, self.data.High, 
                                timeperiod=self.swing_period,
                                name='SWING_HIGH')
        self.swing_low = self.I(talib.MIN, self.data.Low,
                               timeperiod=self.swing_period,
                               name='SWING_LOW')
        
        # Volume analysis
        self.vol_max = self.I(talib.MAX, self.data.Volume,
                             timeperiod=self.volume_lookback,
                             name='VOL_MAX')
        
        # Funding rate series
        self.funding = self.data['funding_rate']
        
    def next(self):
        if self.position:
            return  # Only one active position at a time
            
        # Get current indicator values
        price = self.data.Close[-1]
        upper = self.bb_upper[-1]
        lower = self.bb_lower[-1]
        swing_high = self.swing_high[-1]
        funding_rate = self.funding[-1]
        vol_max = self.vol_max[-1]
        
        # Calculate Bollinger Band squeeze
        bandwidth = (upper - lower) / ((upper + lower)/2)
        squeeze_active = bandwidth < 0.1  # Tight volatility threshold
        
        # Entry conditions
        breakdown = crossunder(self.data.Close, lower)
        funding_ok = funding_rate < self.funding_threshold
        volume_ok = self.data.Volume[-1] > vol_max * 0.8
        
        if all([squeeze_active, breakdown, funding_ok, volume_ok]):
            # Calculate risk parameters
            sl_price = max(swing_high, upper)
            risk_per_unit = sl_price - price
            if risk_per_unit <= 0:
                return  # Invalid SL
            
            # Position sizing calculation
            equity = self.equity
            risk_amount = equity * self.risk_pct
            position_size = risk_amount / risk_per_unit
            position_size = int(round(position_size))
            
            # Execute short with Moon Dev flair 🌙
            self.sell(size=position_size, 
                     sl=sl_price,
                     tp=price - (sl_price - price)*self.rrr)
            print(f"🌙 MOON DEV SHORT ACTIVATED 🌙")
            print(f"Entry: {price:.2f} | Size: {position_size}")
            print(f"SL: {sl_price:.2f} | TP: {price - (sl_price - price)*self.rrr:.2f}")
            
    def notify_trade(self, trade):
        if trade.is_closed:
            emoji = "🚀 PROFIT" if trade.pl > 0 else "💣 LOSS"
            print(f"{emoji} | PnL: ${trade.pl:.2f} | Return: {