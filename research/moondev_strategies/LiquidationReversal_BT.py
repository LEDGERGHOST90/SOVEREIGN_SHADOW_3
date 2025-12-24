```python
# -*- coding: utf-8 -*-
import pandas as pd
import talib
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

class LiquidationReversal(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade
    rsi_period = 14
    liq_sma_period = 2880  # 30 days in 15m intervals (30*24*4=2880)
    
    def init(self):
        # Clean and prepare data
        self.data.df.columns = self.data.df.columns.str.strip().str.lower()
        
        # Calculate indicators using TA-Lib through self.I()
        self.short_liq = self.data.df['short_liquidations']
        self.sma_30d = self.I(talib.SMA, self.short_liq, timeperiod=self.liq_sma_period, name='SMA_30D')
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period, name='RSI_14')
        
        # Track liquidation candle parameters
        self.liquidation_range = 0
        self.entry_price = 0
    
    def next(self):
        # Moon Dev debug prints 🌙
        if len(self.data) % 1000 == 0:
            print(f"🌙 MOON DEV PROGRESS: Processing candle {len(self.data)}/{len(self.data.df)}")
        
        if not self.position:
            # Entry logic
            if len(self.rsi) > 2 and len(self.sma_30d) > 1:
                current_liq = self.short_liq[-1]
                sma_30d_val = self.sma_30d[-1]
                liq_spike = current_liq >= 3 * sma_30d_val
                
                price_lower_low = self.data.Low[-1] < self.data.Low[-2]
                rsi_higher_low = self.rsi[-1] > self.rsi[-2]
                rsi_divergence = price_lower_low and rsi_higher_low
                
                if liq_spike and rsi_divergence:
                    self.entry_price = self.data.Close[-1]
                    self.liquidation_range = self.data.High[-1] - self.data.Low[-1]
                    
                    # Risk management calculations
                    stop_loss = self.entry_price - 0.5 * self.liquidation_range
                    risk_amount = self.risk_per_trade * self.broker.equity
                    risk_per_unit = self.entry_price - stop_loss
                    position_size = int(round(risk_amount / risk_per_unit))
                    
                    # Moon Dev entry signal 🚀
                    print(f"\n🌙✨ MOON DEV STRONG REVERSAL SIGNAL 🚀")
                    print(f"📈 Entry Price: {self.entry_price:.2f}")
                    print(f"🛡️  SL: {stop_loss:.2f} | 🎯 TP: {self.entry_price + 1.5*self.liquidation_range:.2f}")
                    print(f"📦 Position Size: {position_size} units")
                    
                    self.buy(
                        size=position_size,
                        sl=stop_loss,
                        tp=self.entry_price + 1.5 * self.liquidation_range
                    )
        else:
            # Exit logic
            if self.rsi[-1] < 50:
                self.position.close()
                print(f"\n🌙 MOON DEV EXIT SIGNAL 🛑 RSI crossed below 50")
                print(f"💸 Closed at {self.data.Close[-1]:.2f}")

if __name__ == "__main__":
    # Load and prepare data
    data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
    data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
    
    # Clean data columns
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
    
    # Ensure proper column mapping
    data = data.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })
    
    # Run backtest
    bt = Backtest(
        data,
        LiquidationReversal,
        cash=1_000_000,
        commission=.002,
        exclusive