import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy

path = "/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv"
data = pd.read_csv(path)
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
data = data.set_index(pd.to_datetime(data['datetime']))

class VolatilityDivergence(Strategy):
    ema9_period = 9
    ema21_period = 21
    bb_period = 20
    bb_std = 2
    rsi_period = 14
    atr_period = 14
    sma200_period = 200
    vol_period = 10
    consol_bars_min = 10
    div_lookback = 10
    prev_lookback = 10
    risk_per_trade = 0.01
    sl_atr_mult = 1.5
    tp_atr_mult = 2.0
    trail_profit_atr = 1.0
    trail_be_atr = 0.5
    trail_buffer_atr = 0.5
    max_bars_in_trade = 20

    def init(self):
        self.ema9 = self.I(talib.EMA, self.data.Close, timeperiod=self.ema9_period)
        self.ema21 = self.I(talib.EMA, self.data.Close, timeperiod=self.ema21_period)
        self.bb_upper, self.bb_middle, self.bb_lower = self.I(talib.BBANDS, self.data.Close, timeperiod=self.bb_period, nbdevup=self.bb_std, nbdevdn=self.bb_std)
        self.bb_width = self.I(lambda u, l: u - l, self.bb_upper, self.bb_lower)
        self.avg_bb_width = self.I(talib.SMA, self.bb_width, timeperiod=self.bb_period)
        self.squeeze = self.I(lambda w, aw: w < 0.5 * aw, self.bb_width, self.avg_bb_width)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        self.sma200 = self.I(talib.SMA, self.data.Close, timeperiod=self.sma200_period)
        self.avg_vol = self.I(talib.SMA, self.data.Volume, timeperiod=self.vol_period)
        self.ema_diff = self.I(lambda e1, e2: np.abs(e1 - e2), self.ema9, self.ema21)
        self.flat_ema = self.I(lambda d, a: d < 0.5 * a, self.ema_diff, self.atr)
        self.consol_count = 0
        self.bars_in_trade = 0
        print(f"🌙 Moon Dev: Initialized VolatilityDivergence Strategy with talib indicators ✨")

    def next(self):
        if len(self.data) < self.sma200_period:
            return

        if self.position:
            self.bars_in_trade += 1
            if self.bars_in_trade > self.max_bars_in_trade:
                self.position.close()
                print(f"🌙 Moon Dev: Time-based exit after {self.bars_in_trade} bars 📅")

        bull_div = False
        bear_div = False
        total_lookback = self.div_lookback + self.prev_lookback
        if self.consol_count >= self.consol_bars_min and len(self.data) > total_lookback:
            print(f"🌙 Moon Dev: Checking divergence after {self.consol_count} consolidation bars 🔍")
            prev_slice = slice(-total_lookback - 1, -self.div_lookback - 1)
            curr_slice = slice(-self.div_lookback - 1, -1)
            prev_min_p = np.min(self.data.Close.iloc[prev_slice])
            curr_min_p = np.min(self.data.Close.iloc[curr_slice])
            prev_min_r = np.min(self.rsi[prev_slice])
            curr_min_r = np.min(self.rsi[curr_slice])
            bull_div = (curr_min_p < prev_min_p) and (curr_min_r > prev_min_r) and (curr_min_r < 50)

            prev_max_p = np.max(self.data.Close.iloc[prev_slice])
            curr_max_p = np.max(self.data.Close.iloc[curr_slice])
            prev_max_r = np.max(self.rsi[prev_slice])
            curr_max_r = np.max(self.rsi[curr_slice])
            bear_div = (curr_max_p > prev_max_p) and (curr_max_r < prev_max_r) and (curr_max_r > 50)

            if bull_div:
                print(f"🌙 Moon Dev: Bullish divergence detected! curr_min_p={curr_min_p:.2f} < prev_min_p={prev_min_p:.2f}, curr_min_r={curr_min_r:.2f} > prev_min_r={prev_min_r:.2f} 📈")
            if bear_div:
                print(f"🌙 Moon Dev: Bearish divergence detected! curr_max_p={curr_max_p:.2f} > prev_max_p={prev_max_p:.2f}, curr_max_r={curr_max_r:.2f} < prev_max_r={prev_max_r:.2f} 📉")

        between_emas = min(self.ema9[-1], self.ema21[-1]) <= self.data.Close[-1] <= max(self.ema9[-1], self.ema21[-1])
        squeeze_ok = not np.isnan(self.squeeze[-1]) and self.squeeze[-1]
        flat_ok = not np.isnan(self.flat_ema[-1]) and self.flat_ema[-1]
        if squeeze_ok and flat_ok and between_emas:
            self.consol_count += 1
            if self.consol_count == self.consol_bars_min:
                print(f"🌙 Moon Dev: Consolidation threshold reached: {self.consol_count} bars! Ready for breakout 🎯")
        else:
            if self.consol_count >= self.consol_bars_min:
                print(f"🌙 Moon Dev: Consolidation broken after {self.consol_count} bars 💥")
            self.consol_count = 0

        vol_ok = self.data.Volume[-1] > 1.5 * self.avg_vol[-1]
        price = self.data.Close[-1]
        ema_max = max(self.ema9[-1], self.ema21[-1])
        ema_min = min(self.ema9[-1], self.ema21[-1])
        above_sma = price > self.sma200[-1]
        below_sma = price < self.sma200[-1]

        if not self.position and bull_div and vol_ok and above_sma and price > self.bb_upper[-1] and price > ema_max:
            print(f"🌙 Moon Dev: All LONG entry conditions met! Vol OK, Above SMA200, Breakout above BB & EMAs ✅")
            atr_val = self.atr[-1]
            entry_price = price
            sl_price = entry_price - self.sl_atr_mult * atr_val
            tp_price = entry_price + self.tp_atr_mult * atr_val
            sl_distance = entry_price - sl_price
            if sl_distance > 0:
                size = self.risk_per_trade * entry_price / sl_distance
                size = min(size, 1.0)
                self.buy(size=size, sl=sl_price, tp=tp_price)
                self.bars_in_trade = 0
                print(f"🌙 Moon Dev: Entering LONG at {entry_price:.2f}, size {size:.4f}, SL {sl_price:.2f}, TP {tp_price:.2f} 🚀")
            else:
                print(f"🌙 Moon Dev: Invalid SL distance {sl_distance} <=0 for LONG, no trade ⚠️")

        elif not self.position and bear_div and vol_ok and below_sma and price < self.bb_lower[-1] and price < ema_min:
            print(f"🌙 Moon Dev: All SHORT entry conditions met! Vol OK, Below SMA200, Breakdown below BB & EMAs ✅")
            atr_val = self.atr[-1]
            entry_price = price
            sl_price = entry_price + self.sl_atr_mult * atr_val
            tp_price = entry_price - self.tp_atr_mult * atr_val
            sl_distance = sl_price - entry_price
            if sl_distance > 0:
                size = self.risk_per_trade * entry_price / sl_distance
                size = min(size, 1.0)
                self.sell(size=size, sl=sl_price, tp=tp_price)
                self.bars_in_trade = 0
                print(f"🌙 Moon Dev: Entering SHORT at {entry_price:.2f}, size {size:.4f}, SL {sl_price:.2f}, TP {tp_price:.2f} ✨")
            else:
                print(f"🌙 Moon Dev: Invalid SL distance {sl_distance} <=0 for SHORT, no trade ⚠️")

        # EMA cross exit
        if self.position.is_long and self.data.Close[-1] < self.ema9[-1]:
            self.position.close()
            print(f"🌙 Moon Dev: Exit LONG on EMA9 cross below ❌")
        elif self.position.is_short and self.data.Close[-1] > self.ema9[-1]:
            self.position.close()
            print(f"🌙 Moon Dev: Exit SHORT on EMA9 cross above ❌")

bt = Backtest(data, VolatilityDivergence, cash=1000000, commission=0.001)
stats = bt.run()
print(stats)
print(f"🌙 Moon Dev: Backtest completed with talib-powered indicators! Final stats: {stats['Return [%]']:.2f}% 📊✨")