# 🌙 Moon Dev's CoTrendalNeutral Backtest - AI5 Implementation 🌙
from backtesting import Backtest, Strategy
import pandas as pd
import pandas_ta as ta

# Data Preparation
print("🌙 Loading BTC-USD 15m data for CoTrendalNeutral strategy...")
data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

print(f"🚀 Data loaded: {len(data)} bars from {data.index[0]} to {data.index[-1]}")

def sma(series, period):
    return series.rolling(period).mean()

def atr_func(high, low, close, period=14):
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return true_range.rolling(period).mean()

def rolling_max(series, period):
    return series.rolling(period).max()

def rolling_min(series, period):
    return series.rolling(period).min()

class CoTrendalNeutral(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade
    
    def init(self):
        # Trend Indicators
        self.sma50 = self.I(sma, self.data.Close, 50)
        self.sma200 = self.I(sma, self.data.Close, 200)
        
        # Volatility Indicators
        self.atr = self.I(atr_func, self.data.High, self.data.Low, self.data.Close, 14)
        self.atr_ma = self.I(sma, self.atr, 14)
        
        # Swing Levels
        self.swing_high = self.I(rolling_max, self.data.High, 20)
        self.swing_low = self.I(rolling_min, self.data.Low, 20)
        
        print("✨ Moon Dev CoTrendalNeutral Indicators Initialized! Ready for Launch 🚀")

    def next(self):
        price = self.data.Close[-1]
        
        # Ensure we have enough data
        if len(self.sma200) < 200:
            return
            
        # Trend Conditions
        uptrend = price > self.sma50[-1] and self.sma50[-1] > self.sma200[-1]
        downtrend = price < self.sma50[-1] and self.sma50[-1] < self.sma200[-1]
        
        # Volatility Conditions
        vol_decreasing = self.atr[-1] < self.atr_ma[-1]
        vol_increasing = self.atr[-1] > self.atr_ma[-1]
        
        if not self.position:
            # Long Entry Logic - Uptrend with decreasing volatility (neutral trending)
            if uptrend and vol_decreasing:
                sl = self.swing_low[-1]
                risk_per_share = price - sl
                if risk_per_share > 0:
                    tp = price + 3 * risk_per_share
                    risk_amount = self.risk_per_trade * self.equity
                    position_size = int(round(risk_amount / risk_per_share))
                    
                    if position_size > 0:
                        self.buy(size=position_size, sl=sl, tp=tp)
                        print(f"🌙🚀 MOON SHOT LONG! Entry: {price:.2f}, Size: {position_size}, SL: {sl:.2f}, TP: {tp:.2f}")

            # Short Entry Logic - Downtrend with increasing volatility        
            elif downtrend and vol_increasing:
                sl = self.swing_high[-1]
                risk_per_share = sl - price
                if risk_per_share > 0:
                    tp = price - 3 * risk_per_share
                    risk_amount = self.risk_per_trade * self.equity
                    position_size = int(round(risk_amount / risk_per_share))
                    
                    if position_size > 0:
                        self.sell(size=position_size, sl=sl, tp=tp)
                        print(f"🌙📉 BLACK HOLE SHORT! Entry: {price:.2f}, Size: {position_size}, SL: {sl:.2f}, TP: {tp:.2f}")

        else:
            # Moon Gravity Exit Check 🌕
            if self.position.is_long and vol_increasing:
                self.position.close()
                print(f"🌕🌌 LONG GRAVITY EXIT at {price:.2f} - Volatility increasing")
            elif self.position.is_short and vol_decreasing:
                self.position.close()
                print(f"🌕🌠 SHORT GRAVITY EXIT at {price:.2f} - Volatility decreasing")

# Launch Backtest 🚀
print("🚀 Launching CoTrendalNeutral backtest with $1,000,000 portfolio...")
bt = Backtest(data, CoTrendalNeutral, cash=1_000_000, commission=0.002)
stats = bt.run()

print("\n" + "="*60)
print("🌙 MOON DEV COTRENDALNEUTRAL STRATEGY RESULTS 🌙")
print("="*60)
print(stats)
print("\n🔍 Strategy Details:")
print(stats._strategy)
print("="*60)