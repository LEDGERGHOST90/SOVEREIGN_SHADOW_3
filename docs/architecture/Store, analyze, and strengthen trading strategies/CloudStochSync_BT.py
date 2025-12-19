Here's the implementation of the CloudStochSync strategy:

```python
import pandas as pd
import talib
import pandas_ta as ta
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

class CloudStochSync(Strategy):
    def init(self):
        # Heikin-Ashi on 4H
        self.ha_close_4h = self.I(lambda o,h,l,c: ta.ha(o,h,l,c)['HA_close'],
                                 self.data.Open, self.data.High, self.data.Low, self.data.Close,
                                 resample='4H', name='HA Close 4H')
        self.ha_open_4h = self.I(lambda o,h,l,c: ta.ha(o,h,l,c)['HA_open'],
                                self.data.Open, self.data.High, self.data.Low, self.data.Close,
                                resample='4H', name='HA Open 4H')

        # Ichimoku Cloud on 4H
        self.tenkan = self.I(lambda h,l: (talib.MAX(h,9) + talib.MIN(l,9))/2,
                            self.data.High, self.data.Low, resample='4H', name='Tenkan')
        self.kijun = self.I(lambda h,l: (talib.MAX(h,26) + talib.MIN(l,26))/2,
                           self.data.High, self.data.Low, resample='4H', name='Kijun')
        self.senkou_a = self.I(lambda t,k: (t+k)/2, self.tenkan, self.kijun,
                              resample='4H', shift=26, name='Senkou A')
        self.senkou_b = self.I(lambda h,l: (talib.MAX(h,52) + talib.MIN(l,52))/2,
                             self.data.High, self.data.Low, resample='4H', shift=26, name='Senkou B')

        # Stochastic RSI on 1H
        def stoch_rsi_k(close):
            k,_ = talib.STOCHRSI(close, 14, 3, 3)
            return k
        self.stoch_k = self.I(stoch_rsi_k, self.data.Close, resample='1H', name='Stoch RSI K')

        # MACD Histogram on 15m
        _,_,self.macd_hist = self.I(talib.MACD, self.data.Close, 12, 26, 9,
                                   name='MACD Hist')

        # Risk management indicators
        self.swing_low = self.I(talib.MIN, self.data.Low, 20, name='Swing Low')
        self.volume_ma = self.I(talib.SMA, self.data.Volume, 20, name='Vol MA')

    def next(self):
        price = self.data.Close[-1]
        
        # Exit conditions
        if self.position:
            # Cloud exit
            if (price < max(self.senkou_a[-1], self.senkou_b[-1]) and \
               (price > min(self.senkou_a[-1], self.senkou_b[-1]):
                self.position.close()
                print(f"🌙 Cloud exit at {price:.2f}! Floating in the mist... ☁️")

            # MACD divergence exit
            if len(self.macd_hist) > 3 and \
               self.data.High[-1] > self.data.High[-2] and \
               self.macd_hist[-1] < self.macd_hist[-2]:
                self.position.close()
                print(f"🌌 MACD divergence detected! Returning to stardust... 💫")

            # HA color change exit
            if self.ha_close_4h[-1] < self.ha_open_4h[-1]:
                self.position.close()
                print(f"🌑 HA candle turned bearish! Eclipse activated... 🌘")

        # Entry conditions
        else:
            ha_bullish = self.ha_close_4h[-1] > self.ha_open_4h[-1]
            above_cloud = (price > self.senkou_a[-1]) and (price > self.senkou_b[-1])
            stoch_entry = crossover(self.stoch_k, 20)
            volume_ok = self.data.Volume[-1] > self.volume_ma[-1]

            if ha_bullish and above_cloud and stoch_entry:
                # Position sizing
                sl = self.swing_low[-1]
                risk = price - sl
                if risk <= 0: return

                risk_pct = 0.01
                size = (self.equity * risk_pct) / risk