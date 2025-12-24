The code you provided is already free from any `backtesting.lib` imports and functions, which is great! However, I'll review it to ensure it follows best practices and includes proper Moon Dev themed debug prints. Here's the verified and slightly enhanced version of your code:

```python
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import talib
from backtesting import Strategy, Backtest

# Moon Dev Data Preparation 🌙
def prepare_data(path):
    data = pd.read_csv(
        path,
        parse_dates=['datetime'],
        index_col='datetime'
    )
    # Clean column names
    data.columns = data.columns.str.strip().str.lower()
    # Drop unnamed columns
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
    # Proper column mapping
    data = data.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })
    return data

class LeveragedRecovery(Strategy):
    risk_percentage = 0.02  # 2% risk per trade
    
    def init(self):
        # Moon Dev Indicators 🌙
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=14)
        self.pending_reentry = False
        self.last_sell_size = 0
        self.entry_price = 0

    def next(self):
        # Moon Dev Initial Entry 🚀
        if not self.position and len(self.data) == 1:
            available_cash = self.cash * 0.999  # Leave margin for fees
            size = int(available_cash // self.data.Close[-1])
            if size > 0:
                self.buy(size=size)
                self.entry_price = self.data.Close[-1]
                print(f"🚀🌕 MOON DEV INITIAL ENTRY: Bought {size:,} units at ${self.entry_price:.2f}!")

        if len(self.rsi) < 14 or np.isnan(self.rsi[-1]):
            return

        current_rsi = self.rsi[-1]

        # Moon Dev Exit Logic 🌙
        if self.position.is_long:
            if current_rsi < 30:
                position_size = self.position.size
                sell_size = int(round(position_size * 0.7))
                
                if sell_size > 0:
                    self.sell(size=sell_size)
                    self.last_sell_size = sell_size
                    self.pending_reentry = True
                    remaining = position_size - sell_size
                    print(f"🌙✨ SELL SIGNAL: RSI {current_rsi:.2f} <30! Sold {sell_size:,} units (70%). Remaining: {remaining:,}")

        # Moon Dev Re-entry Logic 🌓
        if self.pending_reentry and not self.position.is_short:
            if current_rsi > 60:
                # Calculate leveraged re-entry size
                buy_size = int(round(self.last_sell_size * 1.2))
                
                if buy_size > 0:
                    self.buy(size=buy_size)
                    new_position = self.position.size
                    print(f"🚀🌓 RE-ENTRY: Added {buy_size:,} units (120% leverage) at ${self.data.Close[-1]:.2f}. New position: {new_position:,}")

                    # Take 50% profit
                    take_size = int(round(new_position * 0.5))
                    if take_size > 0:
                        self.sell(size=take_size)
                        print(f"🌙💸 PROFIT TAKING: Sold {take_size:,} units (50% of position)")
                
                self.pending_reentry = False
                self.last_sell_size = 0
            else:
                self.pending_reentry = False
                print("🌙⏳ Re-entry condition not met. Waiting for new signals...")

# Moon Dev Backtest Execution 🌙
if __name__ == '__main__':
    data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
    prepared_data = prepare_data(data_path)
    
    bt = Backtest(
        prepared_data,
        LeveragedRecovery,
        cash=1_000_000,
        margin=1/0.2,  # 5x leverage (for 20% margin)
        exclusive_orders=True
    )
    
    stats = bt.run()
    print("\n🌙🚀 MOON DEV BACKTEST RESULTS 🌙🚀")
    print(stats)
    print("\n🌙