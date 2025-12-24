```python
# 🌙 Moon Dev's ChannelMomentumBreakout Strategy Backtest 🌙
import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover, crossunder

class ChannelMomentumBreakout(Strategy):
    # Strategy parameters
    risk_per_trade = 0.01  # 1% of equity
    keltner_period = 20
    atr_multiplier = 2
    cmo_period = 14
    cmo_signal_period = 9
    bb_period = 20
    bb_dev = 2
    
    def init(self):
        # 🌙 Clean and prepare data
        self.data.df.columns = self.data.df.columns.str.strip().str.lower()
        self.data.df = self.data.df.drop(columns=[col for col in self.data.df.columns if 'unnamed' in col])
        
        # ✨ Calculate indicators using TA-Lib through self.I()
        # Keltner Channel Components
        typical_price = self.I(lambda h, l, c: (h + l + c) / 3,
                               self.data.High, self.data.Low, self.data.Close,
                               name='Typical_Price')
        
        self.keltner_middle = self.I(talib.EMA, typical_price, timeperiod=self.keltner_period,
                                    name='Keltner_Middle')
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close,
                         timeperiod=self.keltner_period, name='ATR')
        
        self.keltner_upper = self.I(lambda m, a: m + self.atr_multiplier * a,
                                   self.keltner_middle, self.atr,
                                   name='Keltner_Upper')
        self.keltner_lower = self.I(lambda m, a: m - self.atr_multiplier * a,
                                   self.keltner_middle, self.atr,
                                   name='Keltner_Lower')
        
        # Chande Momentum Oscillator
        self.cmo = self.I(talib.CMO, self.data.Close, timeperiod=self.cmo_period,
                         name='CMO')
        self.cmo_signal = self.I(talib.EMA, self.cmo, timeperiod=self.cmo_signal_period,
                                name='CMO_Signal')
        
        # Bollinger Bands
        self.bb_upper, self.bb_middle, self.bb_lower = [
            self.I(fn, self.data.Close, timeperiod=self.bb_period, nbdevup=self.bb_dev, 
                  nbdevdn=self.bb_dev, name=name)
            for fn, name in zip(
                [lambda c: talib.BBANDS(c, timeperiod=self.bb_period, nbdevup=self.bb_dev, nbdevdn=self.bb_dev)[0],
                 lambda c: talib.BBANDS(c, timeperiod=self.bb_period, nbdevup=self.bb_dev, nbdevdn=self.bb_dev)[1],
                 lambda c: talib.BBANDS(c, timeperiod=self.bb_period, nbdevup=self.bb_dev, nbdevdn=self.bb_dev)[2]],
                ['BB_Upper', 'BB_Middle', 'BB_Lower']
            )
        ]
        
        # %B Calculation
        self.bb_pctb = self.I(lambda c, l, u: (c - l) / (u - l) if (u - l) != 0 else 0,
                             self.data.Close, self.bb_lower, self.bb_upper,
                             name='%B')
        
        # 🌕 Track equity for risk management
        self.equity = self._broker.starting_cash

    def next(self):
        # ✨ Update current equity
        self.equity = self._broker.equity
        
        # 🌙 Check entry/exit conditions
        price = self.data.Close[-1]
        
        # Exit conditions
        if self.position:
            if self.position.is_long:
                if self.bb_pctb[-1] >= 1.0:
                    self.position.close()
                    print(f"✨🌕 Moon Take Profit! Closing long at {price}")
                elif self.bb_pctb[-1] <= 0.0:
                    self.position.close()
                    print(f"🌧️🌕 Moon Stop Loss! Closing long at {price}")
            elif self.position.is_short:
                if self.bb_pctb[-1] <= 0.0:
                    self.position.close()
                    print(f"✨🌑 Moon Take Profit! Closing short at {price