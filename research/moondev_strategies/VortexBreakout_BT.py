```python
import pandas as pd
import talib
from backtesting import Strategy, Backtest
from backtesting.lib import crossover

# Data preparation and cleaning
data_path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
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

class VortexBreakout(Strategy):
    risk_pct = 0.01  # 1% risk per trade 🌙
    kc_ema_period = 20
    kc_atr_period = 10
    kc_multiplier = 2.5
    vortex_period = 14
    exit_x_factor = 0.3  # 30% channel width trailing stop ✨

    def init(self):
        # Vortex Indicator calculations 🌀
        vi_plus, vi_minus = talib.VORTEX(self.data.High, self.data.Low, self.data.Close, self.vortex_period)
        self.vi_plus = self.I(lambda: vi_plus, name='VI+')
        self.vi_minus = self.I(lambda: vi_minus, name='VI-')

        # Keltner Channel calculations 🌈
        ema = talib.EMA(self.data.Close, self.kc_ema_period)
        atr = talib.ATR(self.data.High, self.data.Low, self.data.Close, self.kc_atr_period)
        self.upper_kc = self.I(lambda: ema + self.kc_multiplier * atr, name='Upper KC')
        self.lower_kc = self.I(lambda: ema - self.kc_multiplier * atr, name='Lower KC')

    def next(self):
        if len(self.data.Close) < 2:  # Ensure enough data points
            return

        # Current indicator values 📊
        vi_plus = self.vi_plus[-1]
        vi_minus = self.vi_minus[-1]
        prev_vi_plus = self.vi_plus[-2]
        prev_vi_minus = self.vi_minus[-2]
        close = self.data.Close[-1]
        upper = self.upper_kc[-1]
        lower = self.lower_kc[-1]

        # Entry logic 🚪
        if not self.position:
            # Long entry: VI+ crosses above VI- and close > upper KC 🌙🚀
            if crossover(vi_plus, vi_minus) and close > upper:
                risk_amount = self.equity * self.risk_pct
                channel_width = upper - lower
                stop_price = upper - (self.exit_x_factor * channel_width)
                position_size = int(round(risk_amount / (close - stop_price)))
                if position_size > 0:
                    self.buy(size=position_size)
                    print(f"🌙✨🚀 LUNAR LIFT-OFF! Long {position_size} units at {close:.2f}")

            # Short entry: VI- crosses above VI+ and close < lower KC 🌙🎯
            elif crossover(vi_minus, vi_plus) and close < lower:
                risk_amount = self.equity * self.risk_pct
                channel_width = upper - lower
                stop_price = lower + (self.exit_x_factor * channel_width)
                position_size = int(round(risk_amount / (stop_price - close)))
                if position_size > 0:
                    self.sell(size=position_size)
                    print(f"🌙✨🎯 GRAVITY ENGAGE! Short {position_size} units at {close:.2f}")

        # Exit logic 🛑
        else:
            current_upper = self.upper_kc[-1]
            current_lower = self.lower_kc[-1]
            channel_width = current_upper - current_lower

            if self.position.is_long:
                # Trail stop: Upper KC - X% of channel width 🌙📉
                stop_level = current_upper - (self.exit_x_factor * channel_width)
                if close < stop_level:
                    self.position.close()
                    print(f"🌙🌕 MOON LANDING! Closing long at {close:.2f}")

            elif self.position.is_short:
                # Trail stop: Lower KC +