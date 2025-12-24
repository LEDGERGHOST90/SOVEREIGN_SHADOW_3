Here's the fixed code with all backtesting.lib imports removed and proper Moon Dev themed implementation:

```python
# 🌙 MOON DEV BACKTESTING IMPLEMENTATION 🚀

# 1. NECESSARY IMPORTS (CLEANED FOR MOON DEV STANDARDS)
import pandas as pd
import talib
import pandas_ta as pta
from backtesting import Backtest, Strategy

# 2. STRATEGY CLASS WITH INDICATORS (MOON DEV APPROVED)
class VolBandBreakout(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade 🌙
    
    def init(self):
        # Clean data columns handled externally
        
        # BOLLINGER BANDS INDICATORS 🌈 (TALIB IMPLEMENTATION)
        self.bb_upper = self.I(lambda close: talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)[0],
                              self.data.Close, name='BB_UPPER')
        self.bb_lower = self.I(lambda close: talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)[2],
                              self.data.Close, name='BB_LOWER')
        
        # BOLLINGER BAND WIDTH CALCULATION 📏 (PURE PYTHON)
        self.bb_width = self.I(lambda u, l: u - l, self.bb_upper, self.bb_lower, name='BB_WIDTH')
        
        # VOLUME INDICATORS 🔊 (TALIB + PANDAS-TA)
        self.vol_ma20 = self.I(talib.SMA, self.data.Volume, timeperiod=20, name='VOL_MA20')
        self.vwma20 = self.I(pta.vwma, self.data.Close, self.data.Volume, length=20, name='VWMA20')
        
        print("🌙 MOON DEV INDICATORS INITIALIZED! READY FOR LIFTOFF! 🚀")

    def next(self):
        # 3. ENTRY/EXIT LOGIC (NO BACKTESTING.LIB USAGE)
        price = self.data.Close[-1]
        upper = self.bb_upper[-1]
        lower = self.bb_lower[-1]
        
        # RISK MANAGEMENT CALCULATIONS 🛡️ (MOON DEV APPROVED)
        def calculate_position_size(entry_price, stop_price):
            risk_amount = self.equity * self.risk_per_trade
            risk_per_share = abs(entry_price - stop_price)
            return int(round(risk_amount / risk_per_share)) if risk_per_share > 0 else 0

        # 4. VOLBAND BREAKOUT CONDITIONS 🌌 (PURE PYTHON IMPLEMENTATION)
        # Check Bollinger contraction
        width_history = self.bb_width[-50:]
        if len(width_history) >= 50:
            current_width = width_history[-1]
            min_width = talib.MIN(width_history, timeperiod=50)[-1]
            max_width = talib.MAX(width_history, timeperiod=50)[-1]
            
            if max_width != min_width:
                width_ratio = (current_width - min_width) / (max_width - min_width)
                contraction = width_ratio <= 0.2
                
                # Volume confirmation 🌊 (ARRAY INDEXING METHOD)
                vol_increasing = (self.data.Volume[-3] < self.data.Volume[-2] and 
                                self.data.Volume[-2] < self.data.Volume[-1])
                vol_spike = self.data.Volume[-1] > self.vol_ma20[-1]
                
                if contraction and vol_increasing and vol_spike:
                    # LONG ENTRY 🚀 (NO CROSSOVER USAGE)
                    if (self.bb_upper[-2] > self.data.Close[-2] and 
                        self.bb_upper[-1] < self.data.Close[-1] and 
                        not self.position.is_long):
                        size = calculate_position_size(price, lower)
                        if size > 0 and len(self.positions) < 5:
                            self.buy(size=size, sl=lower)
                            print(f"🌕 MOON ENTRY! LONG {size} @ {price:.2f} | SL {lower:.2f} 🌙")
                    
                    # SHORT ENTRY 🌑 (NO CROSSOVER USAGE)
                    elif (self.bb_lower[-2] < self.data.Close[-2] and 
                          self.bb_lower[-1] > self.data.Close[-1] and 
                          not self.position.is_