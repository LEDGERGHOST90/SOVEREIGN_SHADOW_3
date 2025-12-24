import pandas as pd
from backtesting import Backtest, Strategy
import numpy as np

# Data preprocessing
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data.rename(columns={
    'datetime': 'Date',
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)

class BandMACDDivergence(Strategy):
    risk_pct = 0.01
    bb_period = 20
    bb_dev = 2
    macd_fast = 12
    macd_slow = 26
    macd_signal = 9
    atr_period = 14
    slope_period = 5
    atr_multiplier = 0.3
    slope_threshold = 0.02

    def init(self):
        # 🌙 Moon Dev Indicators Setup
        close = pd.Series(self.data.Close)
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        
        # Bollinger Bands
        sma20 = close.rolling(self.bb_period).mean()
        std20 = close.rolling(self.bb_period).std()
        
        self.bb_upper = self.I(lambda: sma20 + self.bb_dev*std20)
        self.bb_mid = self.I(lambda: sma20)
        self.bb_lower = self.I(lambda: sma20 - self.bb_dev*std20)
        
        # MACD
        ema12 = close.ewm(span=self.macd_fast).mean()
        ema26 = close.ewm(span=self.macd_slow).mean()
        macd_line = ema12 - ema26
        macd_signal = macd_line.ewm(span=self.macd_signal).mean()
        
        self.macd_line = self.I(lambda: macd_line)
        self.macd_signal = self.I(lambda: macd_signal)
        
        # ATR for stop loss
        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        self.atr = self.I(lambda: tr.rolling(self.atr_period).mean())
        
        # Bollinger Band Upper slope
        bb_upper_series = sma20 + self.bb_dev*std20
        slopes = []
        for i in range(len(bb_upper_series)):
            if i < self.slope_period:
                slopes.append(0)
            else:
                y_vals = bb_upper_series.iloc[i-self.slope_period+1:i+1].values
                x_vals = np.arange(len(y_vals))
                if len(y_vals) > 1:
                    slope = np.polyfit(x_vals, y_vals, 1)[0]
                    slopes.append(slope)
                else:
                    slopes.append(0)
        
        self.ub_slope = self.I(lambda: pd.Series(slopes, index=bb_upper_series.index))
        
        print("🌙✨ Moon Dev BandMACDDivergence Indicators Activated! 🚀")

    def next(self):
        if len(self.data) < 50:
            return

        # Current cosmic readings
        price = self.data.Close[-1]
        ub_slope = self.ub_slope[-1] if not np.isnan(self.ub_slope[-1]) else 0
        macd_line_val = self.macd_line[-1] if not np.isnan(self.macd_line[-1]) else 0
        macd_signal_val = self.macd_signal[-1] if not np.isnan(self.macd_signal[-1]) else 0
        macd_diff = macd_line_val - macd_signal_val
        atr_value = self.atr[-1] if not np.isnan(self.atr[-1]) else 100

        # Risk management
        risk_amount = self.equity * self.risk_pct

        # Long entry supernova conditions  
        if not self.position and atr_value > 10:
            if (ub_slope > self.slope_threshold and
                macd_diff > 0.5 * atr_value):
                
                # Calculate position size
                stop_loss = price - 2 * atr_value
                risk_per_share = price - stop_loss
                
                if risk_per_share > 0:
                    position_size = int(round(risk_amount / risk_per_share))
                    take_profit = price + 3 * atr_value

                    if position_size > 0:
                        self.buy(size=position_size, sl=stop_loss, tp=take_profit)
                        print(f"🚀🌙 LIFT OFF! Long {position_size} @ {price:.2f} | "
                              f"SL: {stop_loss:.2f} | TP: {take_profit:.2f} | Cosmic Momentum: {ub_slope:.4f}")

        # Exit conditions
        elif self.position and self.position.is_long:
            # Check for bearish divergence signals or profit target
            if (ub_slope < -0.5 or macd_diff < -10):
                self.position.close()
                print(f"🌑🌠 COMET RETREAT! Closing long @ {price:.2f}")

# 🌙🚀 Moon Dev Backtest Execution
print("🌙🚀 Starting BandMACDDivergence Backtest...")
bt = Backtest(data, BandMACDDivergence, cash=1000000, commission=0.002)
stats = bt.run()
print("\n" + "="*60)
print("🌙✨ BAND MACD DIVERGENCE STRATEGY RESULTS ✨🌙")
print("="*60)
print(stats)
print("\n🚀 Strategy Details:")
print(stats._strategy)
print("="*60)