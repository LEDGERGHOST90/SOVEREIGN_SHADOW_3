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
        bb = self.I(talib.BBANDS, self.data.Close, timeperiod=self.bb_period, nbdevup=self.bb_std, nbdevdn=self.bb_std)
        self.bb_upper = bb[0]
        self.bb_middle = bb[1]
        self.bb_lower = bb[2]
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
        self.entry_bar = None
        print(f"🌙 Moon Dev: Initialized VolatilityDivergence Strategy with talib indicators ✨")

    def next(self):
        if len(self.data) < self.sma200_period + self.div_lookback + self.prev_lookback:
            return

        between_emas = min(self.ema9[-1], self.ema21[-1]) <= self.data.Close[-1] <= max(self.ema9[-1], self.ema21[-1])
        if self.squeeze[-1] and self.flat_ema[-1] and between_emas:
            self.consol_count += 1
        else:
            self.consol_count = 0

        bull_div = False
        bear_div = False
        if self.consol_count >= self.consol_bars_min:
            total_lookback = self.div_lookback + self.prev_lookback
            if len(self.data) >= total_lookback:
                prev_slice = slice(-total_lookback, -self.div_lookback)
                curr_slice = slice(-self.div_lookback, None)
                prev_min_p = np.min(self.data.Close[prev_slice])
                curr_min_p = np.min(self.data.Close[curr_slice])
                prev_min_r = np.min(self.rsi[prev_slice])
                curr_min_r = np.min(self.rsi[curr_slice])
                bull_div = (curr_min_p < prev_min_p) and (curr_min_r > prev_min_r) and (curr_min_r < 50)

                prev_max_p = np.max(self.data.Close[prev_slice])
                curr_max_p = np.max(self.data.Close[curr_slice])
                prev_max_r = np.max(self.rsi[prev_slice])
                curr_max_r = np.max(self.rsi[curr_slice])
                bear_div = (curr_max_p > prev_max_p) and (curr_max_r < prev_max_r) and (curr_max_r > 50)

        vol_ok = self.data.Volume[-1] > 1.5 * self.avg_vol[-1]
        price = self.data.Close[-1]
        ema_max = max(self.ema9[-1], self.ema21[-1])
        ema_min = min(self.ema9[-1], self.ema21[-1])
        above_sma = price > self.sma200[-1]
        below_sma = price < self.sma200[-1]

        if not self.position and bull_div and vol_ok and above_sma and price > self.bb_upper[-1] and price > ema_max:
            atr_val = self.atr[-1]
            entry_price = price
            sl_price = entry_price - self.sl_atr_mult * atr_val
            tp_price = entry_price + self.tp_atr_mult * atr_val
            risk_amount = self.risk_per_trade * self.equity
            sl_distance = entry_price - sl_price
            if sl_distance > 0:
                size = risk_amount / sl_distance
                size = int(round(size))
                if size > 0:
                    self.buy(size=size, sl=sl_price, tp=tp_price)
                    self.entry_bar = len(self.data) - 1
                    print(f"🌙 Moon Dev: Entering LONG at {entry_price:.2f}, size {size}, SL {sl_price:.2f}, TP {tp_price:.2f} 🚀")

        elif not self.position and bear_div and vol_ok and below_sma and price < self.bb_lower[-1] and price < ema_min:
            atr_val = self.atr[-1]
            entry_price = price
            sl_price = entry_price + self.sl_atr_mult * atr_val
            tp_price = entry_price - self.tp_atr_mult * atr_val
            risk_amount = self.risk_per_trade * self.equity
            sl_distance = sl_price - entry_price
            if sl_distance > 0:
                size = risk_amount / sl_distance
                size = int(round(size))
                if size > 0:
                    self.sell(size=size, sl=sl_price, tp=tp_price)
                    self.entry_bar = len(self.data) - 1
                    print(f"🌙 Moon Dev: Entering SHORT at {entry_price:.2f}, size {size}, SL {sl_price:.2f}, TP {tp_price:.2f} ✨")

        # Time-based exit
        if self.position and self.entry_bar is not None:
            bars_in_trade = len(self.data) - self.entry_bar
            if bars_in_trade > self.max_bars_in_trade:
                self.position.close()
                print(f"🌙 Moon Dev: Time-based exit after {bars_in_trade} bars 📅")

        # EMA cross exit
        if self.position.is_long and self.data.Close[-1] < self.ema9[-1]:
            self.position.close()
            print(f"🌙 Moon Dev: Exit LONG on EMA9 cross below ❌")
        elif self.position.is_short and self.data.Close[-1] > self.ema9[-1]:
            self.position.close()
            print(f"🌙 Moon Dev: Exit SHORT on EMA9 cross above ❌")

    def adjust_trade(self, trade):
        atr_val = self.atr[-1]
        if trade.is_long:
            if self.data.Close[-1] > trade.entry_price + self.trail_profit_atr * atr_val:
                new_sl = max(trade.sl, trade.entry_price + self.trail_be_atr * atr_val)
                trail_sl = self.ema9[-1] - self.trail_buffer_atr * atr_val
                new_sl = max(new_sl, trail_sl)
                print(f"🌙 Moon Dev: Trailing SL for LONG to {new_sl:.2f} 🔄")
                return {'sl': new_sl}
        elif trade.is_short:
            if self.data.Close[-1] < trade.entry_price - self.trail_profit_atr * atr_val:
                new_sl = min(trade.sl, trade.entry_price - self.trail_be_atr * atr_val)
                trail_sl = self.ema9[-1] + self.trail_buffer_atr * atr_val
                new_sl = min(new_sl, trail_sl)
                print(f"🌙 Moon Dev: Trailing SL for SHORT to {new_sl:.2f} 🔄")
                return {'sl': new_sl}
        return None

bt = Backtest(data, VolatilityDivergence, cash=1000000, commission=0.001)
stats = bt.run()
print(stats)
print(f"🌙 Moon Dev: Backtest completed with talib-powered indicators! Final stats: {stats['Return [%]']:.2f}% 📊✨")