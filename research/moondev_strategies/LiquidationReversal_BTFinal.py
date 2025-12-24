Here's the debugged backtest code with Moon Dev themed fixes 🌙✨:

```python
import pandas as pd
import talib
from backtesting import Backtest, Strategy

# Load and preprocess data
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
try:
    data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
except FileNotFoundError:
    print("🌑 COSMIC DATA NOT FOUND! Please check your data path.")
    raise

# Clean and format columns 🌙
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col], errors='ignore')
data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)

# Check for required columns
required_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'fundingrate', 'liquidationcluster']
missing_cols = [col for col in required_cols if col.lower() not in data.columns]
if missing_cols:
    print(f"🌘 WARNING: Missing cosmic data columns - {missing_cols}")

class LiquidationReversal(Strategy):
    def init(self):
        # Volatility and momentum indicators 🌊
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=14)
        
        # Price pattern detection 🕯️
        self.bullish_engulf = self.I(talib.CDLENGULFING, self.data.Open, self.data.High, self.data.Low, self.data.Close)
        self.hammer = self.I(talib.CDLHAMMER, self.data.Open, self.data.High, self.data.Low, self.data.Close)
        
        # Swing detection 🌗
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=20)
        
        print("🌙 Lunar indicators activated! Tracking cosmic patterns... 🌌")

    def next(self):
        if self.position:
            return  # Maintain existing position

        # Check if we have enough data for indicators
        if len(self.data.Close) < 20:
            return

        # Extract current market conditions 🧮
        entry_price = self.data.Close[-1]
        funding_negative = self.data.fundingrate[-1] < 0 if 'fundingrate' in self.data.df.columns else False
        in_liquidation_zone = self.data.liquidationcluster[-1] == 1 if 'liquidationcluster' in self.data.df.columns else False
        rsi_oversold = self.rsi[-1] < 30 if len(self.rsi) > 0 else False
        bullish_signal = (self.bullish_engulf[-1] == 100 or self.hammer[-1] == 100) if len(self.bullish_engulf) > 0 else False

        # Cosmic entry alignment conditions 🌠
        if all([funding_negative, in_liquidation_zone, rsi_oversold, bullish_signal]):
            # Risk management calculations ⚖️
            sl_price = self.swing_low[-1] if len(self.swing_low) > 0 else entry_price * 0.98  # 2% stop if no swing low
            risk_per_share = entry_price - sl_price
            
            if risk_per_share <= 0:
                print("🚨 Cosmic anomaly! SL >= entry price. Aborting launch. 🚨")
                return
                
            # Position sizing calculation 🌕
            risk_capital = self.equity * 0.01  # 1% risk
            position_size = int(round(risk_capital / risk_per_share))
            
            if position_size <= 0:
                print(f"🌙 Stardust shortage: {position_size} units available. Needs more cosmic dust! 🌌")
                return

            # Execute trade with celestial stops 🌌
            tp_price = entry_price + 1.5 * (self.atr[-1] if len(self.atr) > 0 else entry_price * 0.03)  # 3% target if no ATR
            self.buy(size=position_size, 
                     sl=sl_price,
                     tp=tp_price,
                     tag="LunarReversal")
            
            print(f