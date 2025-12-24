I'll fix the code by removing all `backtesting.lib` imports and replacing the crossover functionality with manual checks. Here's the corrected version with Moon Dev themed improvements:

```python
import pandas as pd
import talib
import numpy as np
from backtesting import Backtest, Strategy

# Moon Dev Data Preparation Ritual 🌙
def prepare_data(path):
    data = pd.read_csv(path, parse_dates=['datetime'], index_col='datetime')
    # Cleanse cosmic dust from column names
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    
    # Align celestial coordinates (proper column mapping)
    column_map = {
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    }
    data = data.rename(columns=column_map)
    return data

# Cosmic Gateway to the Stars 🌌
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = prepare_data(data_path)

class LiquidationVolBreakout(Strategy):
    risk_pct = 0.01
    max_daily_loss = 0.05
    atr_period = 14
    bb_period = 20
    bb_dev = 2
    cluster_lookback = 20
    consecutive_losses = 0
    
    def init(self):
        # Cosmic Energy Indicators 🌠
        self.liquidation_high = self.I(talib.MAX, self.data.High, self.cluster_lookback, name='Liquidation Cluster')
        
        # Bollinger Band Stargate 🔮
        close = np.array(self.data.Close)
        self.upper, self.middle, self.lower = (
            self.I(talib.BBANDS, close, self.bb_period, self.bb_dev, self.bb_dev, 
                   name='BB_' + band) 
            for band in ['Upper', 'Middle', 'Lower']
        )
        self.bb_width = self.I(lambda: (self.upper - self.lower)/self.middle, name='BB Width')
        self.bbw_ma = self.I(talib.SMA, self.bb_width, 20, name='BB Width MA')
        
        # Volatility Compass 🌪️
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, self.atr_period, name='ATR')
        
        # Volume Vortex 🌊
        self.vol_ma = self.I(talib.SMA, self.data.Volume, 20, name='Volume MA')
        
        print("🌙 Moon Dev Hyperdrive Activated! Indicators locked and loaded")

    def next(self):
        # Skip if in cooldown after 3 losses
        if self.consecutive_losses >= 3:
            if len(self.trades) == 0:
                print("🚨 Cosmic Shield Active: Trading paused after 3 consecutive losses")
            return

        # Current celestial alignments 🌟
        price = self.data.Close[-1]
        liq_high = self.liquidation_high[-1]
        atr = self.atr[-1]
        
        # Entry Protocol Conditions 🔍
        in_proximity = self.data.High[-1] >= 0.99 * liq_high
        bb_contraction = self.bb_width[-1] < self.bbw_ma[-1]
        breakout = price > liq_high
        volume_spike = self.data.Volume[-1] > self.vol_ma[-1]
        
        if not self.position and all([in_proximity, bb_contraction, breakout, volume_spike]):
            # Calculate Moon Rocket Fuel (position size) 🚀
            stop_loss = price - 0.5 * atr
            risk_amount = self.equity * self.risk_pct
            position_size = int(round(risk_amount / (price - stop_loss)))
            
            if position_size > 0:
                self.buy(
                    size=position_size,
                    sl=stop_loss,
                    tp=price + 1.5 * atr,
                    tag="🌕 Lunar Launch"
                )
                print(f"🚀 IGNITION! Long {position_size} @ {price:.2f} | SL: {stop_loss:.2f} | TP: {price + 1.5 * atr:.2f}")

        # Stellar Exit Protocol 🌠
        if self.position:
            if self.position.pl >= at