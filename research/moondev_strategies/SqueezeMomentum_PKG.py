Here's the fixed code with all backtesting.lib imports removed and replaced with proper implementations:

```python
import pandas as pd
import talib
from backtesting import Backtest, Strategy

class SqueezeMomentum(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade
    
    def init(self):
        # Clean data and ensure proper column mapping
        self.data.columns = [col.strip().lower() for col in self.data.columns]
        
        # Calculate Bollinger Bands using TA-Lib
        close = self.data.close
        self.upper_band, self.middle_band, self.lower_band = self.I(
            lambda: talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0),
            name='BBANDS'
        )
        
        # Calculate ADX and DIs
        self.adx = self.I(talib.ADX, self.data.high, self.data.low, self.data.close, 14, name='ADX')
        self.plus_di = self.I(talib.PLUS_DI, self.data.high, self.data.low, self.data.close, 14, name='+DI')
        self.minus_di = self.I(talib.MINUS_DI, self.data.high, self.data.low, self.data.close, 14, name='-DI')
        
        # Band width calculation
        self.band_width = self.I(lambda: (self.upper_band - self.lower_band)/self.middle_band, name='BandWidth')
        self.band_squeeze = self.I(talib.MIN, self.band_width, 20, name='Squeeze')

    def next(self):
        # Skip early bars where indicators aren't calculated
        if len(self.data) < 50:
            return
        
        # Moon Dev Trade Logic 🌙✨
        entry_price = self.data.close[-1]
        
        if not self.position:
            # Long Entry Constellation 🌟
            if (entry_price > self.upper_band[-1] and
                self.adx[-1] > 25 and
                self.plus_di[-1] > self.minus_di[-1] and
                self.band_width[-1] > self.band_squeeze[-1]):
                
                sl_price = self.lower_band[-1]
                risk_distance = entry_price - sl_price
                position_size = self._calculate_size(risk_distance)
                
                if position_size > 0:
                    self.buy(size=position_size, sl=sl_price)
                    print(f"🚀🌕 MOON SHOT! LONG {position_size} @ {entry_price:.2f} | SL {sl_price:.2f}")
            
            # Short Entry Eclipse 🌑 
            elif (entry_price < self.lower_band[-1] and
                  self.adx[-1] > 25 and
                  self.minus_di[-1] > self.plus_di[-1] and
                  self.band_width[-1] > self.band_squeeze[-1]):
                  
                sl_price = self.upper_band[-1]
                risk_distance = sl_price - entry_price
                position_size = self._calculate_size(risk_distance)
                
                if position_size > 0:
                    self.sell(size=position_size, sl=sl_price)
                    print(f"🌑💫 BLACK HOLE! SHORT {position_size} @ {entry_price:.2f} | SL {sl_price:.2f}")
        
        else:
            # Exit Conditions 🌙
            if self.position.is_long:
                if (entry_price < self.upper_band[-1]) or (self.adx[-1] < 20):
                    self.position.close()
                    print(f"🌕💸 MOON LANDING! LONG CLOSED @ {entry_price:.2f}")
            
            if self.position.is_short:
                if (entry_price > self.lower_band[-1]) or (self.adx[-1] < 20):
                    self.position.close()
                    print(f"🌑💥 SUPERNOVA! SHORT CLOSED @ {entry_price:.2f}")

    def _calculate_size(self, risk_distance):
        """Moon Dev Risk Management Rocket 🚀"""
        if risk_distance <= 0:
            return 0
        risk_amount = self.risk_per_trade * self.equity
        position_size = risk_amount / risk_distance
        return int(round(position_size))

# Data Loading and Preparation 🌙
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data