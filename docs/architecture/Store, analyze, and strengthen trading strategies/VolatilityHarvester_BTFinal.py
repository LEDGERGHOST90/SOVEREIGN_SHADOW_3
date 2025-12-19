# -*- coding: utf-8 -*-
import pandas as pd
import talib
from backtesting import Strategy, Backtest
import numpy as np

# 🌙 MOON DEV DATA PREPARATION 🌙
def load_data(path):
    # Load and clean data
    data = pd.read_csv(path, parse_dates=['datetime'], index_col='datetime')
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
    
    # Map columns to Backtesting.py format
    data = data.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })
    return data

class VolatilityHarvester(Strategy):
    risk_per_trade = 0.02  # 2% risk per trade 🌙
    atr_period = 14
    swing_period = 20
    vix_threshold = 20  # Not actual VIX but normalized volatility
    
    def init(self):
        # 🌙 CELESTIAL INDICATORS 🌙
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.swing_high = self.I(talib.MAX, self.data.High, self.swing_period)
        self.swing_low = self.I(talib.MIN, self.data.Low, self.swing_period)
        self.volume_sma = self.I(talib.SMA, self.data.Volume, timeperiod=96)  # 24h SMA
        
        # Track entry details for risk management
        self.entry_price = None
        self.stop_loss = None
        self.take_profit = None
        
    def next(self):
        current_hour = self.data.index[-1].hour
        price = self.data.Close[-1]
        
        # 🌌 COSMIC CONDITIONS CHECK 🌌
        time_condition = 9 <= current_hour < 11
        vol_condition = self.atr[-1] > (price * 0.01)  # 1% volatility threshold
        liquidity_condition = self.data.Volume[-1] < self.volume_sma[-1]
        
        if time_condition and vol_condition and liquidity_condition:
            if not self.position:
                # 🚀 LAUNCH TRADE SEQUENCE 🚀
                risk_amount = self.equity * self.risk_per_trade
                atr_value = self.atr[-1]
                
                # 🌕 LUNAR RISK CALCULATIONS 🌕
                # Fixed stop loss and take profit calculations
                self.stop_loss = price + (1.5 * atr_value)
                self.take_profit = price - (2 * atr_value)
                position_size = risk_amount / (1.5 * atr_value)
                
                # Convert to whole units
                position_size = int(round(position_size))
                
                if position_size > 0:
                    self.sell(size=position_size, 
                             sl=self.stop_loss,
                             tp=self.take_profit)
                    
                    print(f"🌙 MOON DEV ENTRY 🌙 | SHORT {position_size} units | "
                          f"Price: {price:.2f} | SL: {self.stop_loss:.2f} | TP: {self.take_profit:.2f}")
        else:
            # 🌑 CLOSING BELL CONDITIONS 🌑
            if self.position:
                if self.data.Close[-1] >= self.stop_loss or self.data.Close[-1] <= self.take_profit:
                    self.position.close()
                    print(f"🌖 MOON DEV EXIT 🌖 | CLOSING POSITION | "
                          f"Price: {price:.2f} | Equity: {self.equity:.2f}")

# 🌠 STARGAZER BACKTEST EXECUTION 🌠
if __name__ == "__main__":
    data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
    bt_data = load_data(data_path)
    
    bt = Backtest(bt_data, VolatilityHarvester, cash=1_000_000, exclusive_orders=True)
    
    # 🪐 RUN COSMIC SIMULATION 🪐
    stats = bt.run()
    print("🌌 COSMIC BACKTEST COMPLETE 🌌")
    print(stats)