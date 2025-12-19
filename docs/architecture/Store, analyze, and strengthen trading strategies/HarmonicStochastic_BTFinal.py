```python
# 🌙 MOON DEV BACKTESTING IMPLEMENTATION FOR HARMONICSTOCHASTIC STRATEGY 🚀

import pandas as pd
import talib
from backtesting import Backtest, Strategy

class HarmonicStochastic(Strategy):
    def init(self):
        # 🌟 INDICATOR INITIALIZATION
        # Harmonic Oscillator (RSI)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=14, name='RSI')
        
        # Stochastic Convergence
        h, l, c = self.data.High, self.data.Low, self.data.Close
        slowk, slowd = talib.STOCH(h, l, c,
                                   fastk_period=14,
                                   slowk_period=3,
                                   slowk_matype=0,
                                   slowd_period=3,
                                   slowd_matype=0)
        self.stoch_k = self.I(lambda: slowk, name='Stoch_%K')
        self.stoch_d = self.I(lambda: slowd, name='Stoch_%D')
        
        # Volatility Measurement
        self.atr = self.I(talib.ATR, h, l, c, timeperiod=14, name='ATR')
        
        print("🌙 INITIALIZED MOON DEV TRADING BOT WITH COSMIC INDICATORS ✨")

    def next(self):
        # 🌌 CURRENT MARKET CONDITIONS
        current_close = self.data.Close[-1]
        atr_value = self.atr[-1]
        
        # 🚨 ENTRY LOGIC
        if not self.position:
            # LONG SIGNAL: RSI crosses above 70 AND Stoch crossover
            if (self.rsi[-2] < 70 and self.rsi[-1] > 70) and (self.stoch_k[-2] < self.stoch_d[-2] and self.stoch_k[-1] > self.stoch_d[-1]):
                sl = current_close - 0.5 * atr_value
                tp = current_close + 1.5 * atr_value
                risk_amount = self.equity * 0.01
                risk_per_share = current_close - sl
                
                if risk_per_share > 0:
                    position_size = int(round(risk_amount / risk_per_share))
                    if position_size > 0:
                        self.buy(size=position_size, sl=sl, tp=tp)
                        print(f"🌙✨ BULLISH BREAKOUT! LONG {position_size} @ {current_close:.2f}")
                        print(f"   🛡️ SL: {sl:.2f} | 🎯 TP: {tp:.2f} | 📏 ATR: {atr_value:.2f}")

            # SHORT SIGNAL: RSI crosses below 30 AND Stoch crossunder
            elif (self.rsi[-2] > 30 and self.rsi[-1] < 30) and (self.stoch_k[-2] > self.stoch_d[-2] and self.stoch_k[-1] < self.stoch_d[-1]):
                sl = current_close + 0.5 * atr_value
                tp = current_close - 1.5 * atr_value
                risk_amount = self.equity * 0.01
                risk_per_share = sl - current_close
                
                if risk_per_share > 0:
                    position_size = int(round(risk_amount / risk_per_share))
                    if position_size > 0:
                        self.sell(size=position_size, sl=sl, tp=tp)
                        print(f"🌙✨ BEARISH BREAKDOWN! SHORT {position_size} @ {current_close:.2f}")
                        print(f"   🛡️ SL: {sl:.2f} | 🎯 TP: {tp:.2f} | 📏 ATR: {atr_value:.2f}")

        # 💫 EXIT LOGIC
        else:
            if self.position.is_long and (self.rsi[-2] > 70 and self.rsi[-1] < 70):
                self.position.close()
                print(f"🌙💎 CLOSING LONG POSITION | RSI REVERSAL @ {current_close:.2f}")
                
            elif self.position.is_short and (self.rsi[-2] < 30 and self.rsi[-1] > 30):
                self.position.close()
                print(f"🌙💎 CLOSING SHORT POSITION | RSI REVERSAL @ {current_close:.2f}")

# 🌙 MOON DEV BACKTESTING SETUP 🚀
if __name__ == "__main__":
    # Load your