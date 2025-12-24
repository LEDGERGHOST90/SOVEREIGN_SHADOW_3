I'll help fix the code while maintaining the strategy logic. Here's the debugged version with Moon Dev themed improvements:

```python
import pandas as pd
import talib
from backtesting import Backtest, Strategy

class VolatilitySqueezeEdge(Strategy):
    risk_percent = 0.01  # 1% risk per trade
    
    def init(self):
        # Clean and prepare data
        self.data.columns = [col.strip().lower() for col in self.data.columns]
        self.data = self.data.drop(columns=[col for col in self.data.columns if 'unnamed' in col])
        
        # Calculate indicators using TA-Lib with self.I()
        # Bollinger Bands components
        def upper_bb(close):
            upper, _, _ = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
            return upper
        
        def lower_bb(close):
            _, _, lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
            return lower
        
        self.upper_band = self.I(upper_bb, self.data.Close, name='Upper BB')
        self.lower_band = self.I(lower_bb, self.data.Close, name='Lower BB')
        self.bb_width = self.I(lambda upper, lower: upper - lower, 
                              self.upper_band, self.lower_band, name='BB Width')
        self.bb_width_min = self.I(lambda x: talib.MIN(x, timeperiod=20), 
                                  self.bb_width, name='BB Width Min')
        
        # RSI indicator
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=14, name='RSI')
        
        # ATR for risk management
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 
                         timeperiod=14, name='ATR')
        
        print("🌙✨ MOON DEV INDICATORS LOADED! Ready to launch profits! 🚀")

    def next(self):
        if len(self.data) < 34:  # Warm-up period for indicators
            return
        
        current_close = self.data.Close[-1]
        upper_value = self.upper_band[-1]
        lower_value = self.lower_band[-1]
        bb_width = self.bb_width[-1]
        bb_width_min = self.bb_width_min[-1]
        rsi_value = self.rsi[-1]
        atr_value = self.atr[-1]

        volatility_squeeze = bb_width <= bb_width_min

        if not self.position:
            # Long entry logic
            if (volatility_squeeze and
                rsi_value > 70 and
                current_close > upper_value):
                
                risk_amount = self.equity * self.risk_percent
                risk_per_unit = atr_value
                if risk_per_unit == 0:
                    return  # Prevent division by zero
                
                position_size = int(round(risk_amount / risk_per_unit))
                if position_size > 0:
                    sl = current_close - atr_value
                    tp = current_close + 2 * atr_value
                    self.buy(size=position_size, sl=sl, tp=tp)
                    print(f"🌕🚀 MOON BLASTOFF! LONG {position_size} units at {current_close:.2f}")
                    print(f"   RSI: {rsi_value:.2f} | ATR Guard: ±{atr_value:.2f} ✨")

            # Short entry logic        
            elif (volatility_squeeze and
                  rsi_value < 30 and
                  current_close < lower_value):
                
                risk_amount = self.equity * self.risk_percent
                risk_per_unit = atr_value
                if risk_per_unit == 0:
                    return
                
                position_size = int(round(risk_amount / risk_per_unit))
                if position_size > 0:
                    sl = current_close + atr_value
                    tp = current_close - 2 * atr_value
                    self.sell(size=position_size, sl=sl, tp=tp)
                    print(f"🌑🌌 BLACK HOLE SHORT! {position_size} units at {current_close:.2f}")
                    print(f"   RSI: {rsi_value:.2f} | ATR Guard: ±{atr_value:.2f} ✨")

    def notify_trade(self, trade):
        if trade.is_closed:
            pl_pct = trade.pl_pct
            if pl_pct > 0:
                print