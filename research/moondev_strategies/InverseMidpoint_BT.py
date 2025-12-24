# -*- coding: utf-8 -*-
import pandas as pd
import talib as ta
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import numpy as np

# Load and prepare data
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')

# Clean and process data
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])

# Resample to daily timeframe 🌙
daily_data = data.resample('D').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
})
daily_data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
daily_data = daily_data.dropna()

class InverseMidpoint(Strategy):
    risk_pct = 0.02  # 2% risk per trade 🌕
    
    def init(self):
        # Calculate indicators using TA-Lib wrapped with self.I()
        self.prev_open = self.I(ta.SMA, self.data.Open, timeperiod=1, name='PrevOpen')  # Shifted open
        self.prev_high = self.I(ta.SMA, self.data.High, timeperiod=1, name='PrevHigh')  # Shifted high
        
        # Midpoint calculation (previous day's (Open+High)/2)
        self.midpoint = self.I(lambda: (self.prev_open + self.prev_high) / 2, name='Midpoint')
        
        # Volume indicators 📊
        self.avg_volume = self.I(ta.SMA, self.data.Volume, timeperiod=20, name='AvgVolume')
        
    def next(self):
        # Wait for enough data to compute indicators
        if len(self.data) < 20:
            return
            
        current_close = self.data.Close[-1]
        current_volume = self.data.Volume[-1]
        midpoint = self.midpoint[-1]
        avg_vol = self.avg_volume[-1]

        # Moon Dev Risk Management 🌙
        equity = self.equity
        risk_amount = equity * self.risk_pct
        
        # Entry logic: Bearish setup with volume confirmation 📉
        if not self.position:
            if current_close < midpoint and current_volume > 0.1 * avg_vol:
                # Calculate position size with stop loss
                entry_price = current_close
                stop_loss = entry_price * 1.05  # 5% stop loss
                risk_per_share = stop_loss - entry_price
                
                if risk_per_share > 0:
                    position_size = risk_amount / risk_per_share
                    position_size = int(round(position_size))
                    
                    if position_size > 0:
                        self.sell(size=position_size, sl=stop_loss, tag='ShortEntry')
                        print(f"🚀🌙 Moon Dev SHORT Signal! Entry: {entry_price:.2f}, Size: {position_size} ✨")

        # Exit logic: Price above midpoint or volume drops 📈
        elif self.position.is_short:
            if current_close > midpoint or current_volume < 0.1 * avg_vol:
                self.position.close()
                print(f"🌙💫 Closing SHORT at {current_close:.2f} - Moon Profit Activated! 🎯")

# Run backtest with $1M capital 🌕
bt = Backtest(daily_data, InverseMidpoint, cash=1_000_000, commission=.002)
stats = bt.run()

# Print full Moon Dev performance report 🌙
print("\n" + "="*50)
print("🌕🌖🌗 MOON DEV BACKTEST REPORT 🌘🌑🌒")
print("="*50)
print(stats)
print("\n✨ Strategy Details:")
print(stats._strategy)