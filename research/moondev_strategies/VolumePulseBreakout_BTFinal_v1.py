from backtesting import Strategy, Backtest
import talib
import pandas as pd
import numpy as np

class VolumePulseBreakout(Strategy):
    def init(self):
        # Calculate indicators
        close = self.data.Close
        volume = self.data.Volume
        high = self.data.High
        low = self.data.Low
        
        # VWMA (Volume Weighted Moving Average)
        self.vwma = self.I(talib.SMA, close * volume, timeperiod=20) / self.I(talib.SMA, volume, timeperiod=20)
        
        # RSI
        self.rsi = self.I(talib.RSI, close, timeperiod=14)
        
        # Bollinger Bands
        self.bb_upper, self.bb_middle, self.bb_lower = self.I(talib.BBANDS, close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        
        # ATR for risk management
        self.atr = self.I(talib.ATR, high, low, close, timeperiod=14)
        
        # Trackers
        self.consecutive_losses = 0
        self.open_positions = 0
        self.max_positions = 5
        self.risk_per_trade = 0.02
        self.equity = 1000000
        
        print("🌙 Moon Dev Strategy Initialized! VolumePulse Breakout is ready to launch! 🚀")

    def next(self):
        current_close = self.data.Close[-1]
        current_open = self.data.Open[-1]
        previous_close = self.data.Close[-2]
        current_volume = self.data.Volume[-1]
        current_low = self.data.Low[-1]
        
        # Check if we can take new trades
        if self.consecutive_losses >= 3:
            print("🌙 Moon Dev Alert: 3 consecutive losses - cooling down period activated! ❄️")
            return
            
        if self.open_positions >= self.max_positions:
            print("🌙 Moon Dev Alert: Max positions reached! No new trades. 🛑")
            return
            
        # Check trading hours (first 2 hours of session)
        current_hour = self.data.index[-1].hour
        if current_hour > 2:
            return
            
        # Entry conditions
        entry_conditions = (
            current_close < self.bb_lower[-2] and  # Price was below lower BB
            self.rsi[-2] < 30 and  # RSI was oversold
            current_volume > 1.5 * self.vwma[-2] and  # Volume spike
            current_close > self.bb_lower[-1] and  # Price closed back inside BB
            current_open > previous_close  # Confirmation candle
        )
        
        if entry_conditions:
            # Calculate position size with 2% risk
            stop_loss = min(current_low, current_close * 0.98)
            risk_amount = self.equity * self.risk_per_trade
            risk_per_share = current_close - stop_loss
            position_size = int(round(risk_amount / risk_per_share))
            
            # Take profit levels
            tp1 = current_close + 1.5 * self.atr[-1]
            tp2 = self.bb_upper[-1]
            
            # Execute trade
            if position_size > 0:
                self.buy(size=position_size, sl=stop_loss)
                self.open_positions += 1
                
                print(f"🌙 Moon Dev Signal: BUY! 🚀 Price: {current_close:.2f}")
                print(f"✨ Position Size: {position_size} shares | SL: {stop_loss:.2f}")
                print(f"🎯 TP1: {tp1:.2f} | TP2: {tp2:.2f}")
            
        # Manage open positions
        for trade in self.trades:
            if trade.is_long:
                current_price = self.data.Close[-1]
                
                # Check for TP1 (partial exit)
                if current_price >= trade.entry_price + 1.5 * self.atr[-1]:
                    if trade.size > 1:  # Only partial close if we have more than 1 share
                        self.position.close(0.5)
                        print("🌙 Moon Dev Action: Partial profit taken! 🎯 Half position closed.")
                
                # Check for TP2 (full exit)
                if current_price >= self.bb_upper[-1]:
                    self.position.close()
                    self.open_positions -= 1
                    print("🌙 Moon Dev Action: Full profit taken! 💰 Position closed at upper BB.")
    
    def on_trade_end(self, trade):
        if trade.pnl < 0:
            self.consecutive_losses += 1
            print(f"🌙 Moon Dev Warning: Trade ended in loss. Consecutive losses: {self.consecutive_losses} 😢")
        else:
            self.consecutive_losses = 0
            print("🌙 Moon Dev Celebration: Winning trade! 🎊 Resetting loss counter.")
            
        self.open_positions -= 1
        self.equity = self.equity + trade.pnl

# Load and prepare data
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})
data['Datetime'] = pd.to_datetime(data['datetime'])
data = data.set_index('Datetime')

# Run backtest with increased initial cash
bt = Backtest(data, VolumePulseBreakout, cash=1000000, commission=.002, exclusive_orders=True)
stats = bt.run()
print(stats)
print(stats._strategy)