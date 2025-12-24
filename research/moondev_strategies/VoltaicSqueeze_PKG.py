I'll help fix the code by removing all `backtesting.lib` imports and replacing any usage of `crossover` and `crossunder` with proper implementations. Here's the corrected version:

```python
import pandas as pd
import talib
from backtesting import Backtest, Strategy

# Load and preprocess data
data_path = '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv'
data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)

class VoltaicSqueeze(Strategy):
    risk_pct = 0.01
    atr_multiplier = 2
    max_daily_loss = 0.03
    max_weekly_loss = 0.07
    
    def init(self):
        # Bollinger Bands components
        def bb_upper(close):
            upper, _, _ = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
            return upper
        self.upper_band = self.I(bb_upper, self.data.Close)
        
        def bb_lower(close):
            _, _, lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
            return lower
        self.lower_band = self.I(bb_lower, self.data.Close)
        
        # Volatility metrics
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 14)
        self.bandwidth = self.I(lambda: self.upper_band - self.lower_band)
        self.min_bandwidth = self.I(talib.MIN, self.bandwidth, 30)
        
        # Tracking variables
        self.max_high = None
        self.min_low = None
        self.current_day = None
        self.daily_equity_start = None
        self.weekly_equity_start = None

    def next(self):
        # Moon-themed risk management 🌙
        current_date = self.data.index[-1].date()
        if current_date != self.current_day:
            self.current_day = current_date
            self.daily_equity_start = self.equity
            if self.data.index[-1].weekday() == 0:
                self.weekly_equity_start = self.equity
            self.daily_loss_hit = False
            self.weekly_loss_hit = False
        
        if self.daily_equity_start:
            daily_pnl = (self.equity - self.daily_equity_start)/self.daily_equity_start
            if daily_pnl <= -self.max_daily_loss:
                self.daily_loss_hit = True
                print(f"🌙 DAILY LOSS LIMIT ({daily_pnl*100:.1f}%)! Trading halted 🚫")
        
        if self.weekly_equity_start:
            weekly_pnl = (self.equity - self.weekly_equity_start)/self.weekly_equity_start
            if weekly_pnl <= -self.max_weekly_loss:
                self.weekly_loss_hit = True
                print(f"🌙 WEEKLY LOSS LIMIT ({weekly_pnl*100:.1f}%)! Trading halted 🚫")

        if not self.position:
            if self.daily_loss_hit or self.weekly_loss_hit:
                return

            # Volatility squeeze detection ✨
            squeeze_condition = (self.bandwidth[-1] <= self.min_bandwidth[-1])
            
            if squeeze_condition and len(self.data.Close) > 1:
                # Long entry logic 🚀
                if self.data.Close[-2] < self.upper_band[-2] and self.data.Close[-1] > self.upper_band[-1]:  # Replaced crossover
                    risk_amount = self.equity * self.risk_pct
                    atr_value = self.atr[-1]
                    size = int(round(risk_amount/(self.atr_multiplier * atr_value)))
                    if size > 0:
                        self.buy(size=size)
                        self.max_high = self.data.High[-1]
                        print(f"🌙🚀 LONG ENTRY