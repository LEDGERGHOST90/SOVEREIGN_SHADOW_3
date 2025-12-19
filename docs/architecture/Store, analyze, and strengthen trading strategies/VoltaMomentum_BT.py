Here's the complete backtesting implementation for the VoltaMomentum strategy:

```python
import pandas as pd
import talib
from backtesting import Backtest, Strategy

class VoltaMomentumStrategy(Strategy):
    def init(self):
        # Calculate indicators using TA-Lib with self.I()
        self.roc = self.I(talib.ROC, self.data.Close, 3, name='ROC_3')
        
        # Bollinger Bands components
        self.bb_upper = self.I(talib.BBANDS, self.data.Close, 20, 2, 2, 0, 
                              which=0, name='BB_Upper')
        self.bb_middle = self.I(talib.BBANDS, self.data.Close, 20, 2, 2, 0,
                               which=1, name='BB_Middle')
        self.bb_lower = self.I(talib.BBANDS, self.data.Close, 20, 2, 2, 0,
                              which=2, name='BB_Lower')
        
        # Bandwidth calculation
        self.bandwidth = self.I(lambda u, l, m: (u - l)/m, 
                               self.bb_upper, self.bb_lower, self.bb_middle,
                               name='Bandwidth')
        self.bandwidth_sma = self.I(talib.SMA, self.bandwidth, 10, 
                                   name='Bandwidth_SMA')
        
        # Volatility measurements
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, 
                         self.data.Close, 14, name='ATR_14')

    def next(self):
        # Wait until all indicators are calculated
        if len(self.data) < 33:
            return

        # Get current values
        roc = self.roc[-1]
        bw = self.bandwidth[-1]
        bw_sma = self.bandwidth_sma[-1]
        price = self.data.Close[-1]
        atr = self.atr[-1]

        # Moon Dev themed risk management 🌙
        risk_pct = 0.01  # 1% equity risk per trade
        equity = self.equity

        # Entry logic
        if not self.position:
            # Long entry conditions
            if roc > 0.02 and bw > bw_sma:
                sl = price - 1.5 * atr
                risk_amount = equity * risk_pct
                position_size = int(round(risk_amount / (price - sl)))
                
                if position_size > 0:
                    self.buy(size=position_size, sl=sl,
                            tag={'entry_bar': len(self.data)})
                    print(f"🌙✨ BULLISH ALIGNMENT! 🚀 Long {position_size} @ {price:.2f}")
            
            # Short entry conditions
            elif roc < -0.02 and bw > bw_sma:
                sl = price + 1.5 * atr
                risk_amount = equity * risk_pct
                position_size = int(round(risk_amount / (sl - price)))
                
                if position_size > 0:
                    self.sell(size=position_size, sl=sl,
                             tag={'entry_bar': len(self.data)})
                    print(f"🌙✨ BEARISH DIVERGENCE! 💥 Short {position_size} @ {price:.2f}")

        # Exit logic
        for trade in self.trades:
            # Volatility contraction exit
            if bw < bw_sma:
                trade.close()
                moon_emoji = '🌑' if trade.pl_pct < 0 else '🌕'
                print(f"{moon_emoji} VOLATILITY COLLAPSE! 🛑 Closing {trade.type}")

            # Time-based exit (5 days = 480 15m bars)
            elif len(self.data) - trade.entry_bar >= 480:
                trade.close()
                print(f"⏳ MOON CYCLE EXPIRED! Closing {trade.type} after 5 days")

# Data preprocessing
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)
data['datetime'] = pd.to_datetime(data['datetime'])
data = data.set