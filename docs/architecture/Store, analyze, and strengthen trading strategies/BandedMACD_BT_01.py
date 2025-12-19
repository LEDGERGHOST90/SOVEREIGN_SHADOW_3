# -*- coding: utf-8 -*-
import pandas as pd
from backtesting import Backtest, Strategy
import talib

# 🌙 Moon Dev Data Preparation
def prepare_data(filepath):
    # Load and clean data
    data = pd.read_csv(filepath)
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
    
    # Proper column mapping
    data.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    }, inplace=True)
    
    data['datetime'] = pd.to_datetime(data['datetime'])
    data.set_index('datetime', inplace=True)
    return data

# 🌙✨ BandedMACD Strategy Implementation
class BandedMACD(Strategy):
    risk_pct = 0.01  # 1% risk per trade
    
    def init(self):
        # 🌀 TA-Lib Indicators with self.I()
        # MACD Calculation
        def get_macd(close):
            macd, signal, _ = talib.MACD(close, 12, 26, 9)
            return macd, signal
            
        self.macd_line = self.I(lambda: get_macd(self.data.Close)[0], name='MACD')
        self.macd_signal = self.I(lambda: get_macd(self.data.Close)[1], name='Signal')
        
        # Bollinger Bands
        self.upper_band = self.I(talib.BBANDS, self.data.Close, 20, 2, 2, 0,
                                name='Upper BB', output='upperband')
        
        # Swing Levels
        self.swing_high = self.I(talib.MAX, self.data.High, 20, name='Swing High')
        self.swing_low = self.I(talib.MIN, self.data.Low, 20, name='Swing Low')

    def next(self):
        # 🌙 Current Market Conditions
        price = self.data.Close[-1]
        macd = self.macd_line[-1]
        signal = self.macd_signal[-1]
        upper_band = self.upper_band[-1]
        
        # 🚀 Entry Logic (Simulated existing position)
        if not self.position:
            # Check MACD crossover and band touch
            if (macd > signal and 
                self.data.High[-1] >= upper_band and 
                len(self.data.Close) > 26):
                
                # 🌙 Risk Management Calculation
                entry_price = self.data.Close[-1]
                stop_loss = self.swing_low[-1]
                risk_per_share = entry_price - stop_loss
                
                if risk_per_share > 0:
                    risk_amount = self.equity() * self.risk_pct
                    position_size = int(round(risk_amount / risk_per_share))
                    
                    print(f"🌙 Moon Dev Entry: Buying {position_size} units at {entry_price:.2f} 🚀")
                    self.buy(size=position_size)
        
        # 💎 Exit Logic
        else:
            # Trailing Stop Check
            current_low = self.data.Low[-1]
            trailing_stop = self.swing_low[-1]
            
            # Pullback Check
            swing_high = self.swing_high[-1]
            close_below_swing_high = self.data.Close[-1] < swing_high
            
            # Execute Exit
            if close_below_swing_high or current_low < trailing_stop:
                print(f"🌙 Moon Dev Exit: Closing {self.position.size} units at {price:.2f} ✨")
                self.position.close()

# 🌙🚀 Backtest Execution
if __name__ == '__main__':
    # Load prepared data
    data = prepare_data('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
    
    # Run backtest
    bt = Backtest(data, BandedMACD, cash=1_000_000, commission=.002)
    stats = bt.run()
    
    # 🌕 Print Full Stats
    print("\n" + "="*50)
    print("🌙✨ Moon Dev Backtest Results 🚀💎")
    print("="*50)
    print(stats)
    print(stats._strategy)