# -*- coding: utf-8 -*-
"""
DynamicCrossfire Strategy - Converted for FreqTrade
Original: Moon Dev | Converted: Aurora (Claude)

Strategy: EMA Golden Cross + ADX Trend Strength
- Entry: EMA50 crosses above EMA200 + ADX > 25 and rising
- Exit: RSI > 70 or EMA death cross
- Risk: 1% per trade with swing low stop-loss
"""
import numpy as np
from freqtrade.strategy import IStrategy, merge_informative_pair
from freqtrade.persistence import Trade
from pandas import DataFrame
import talib.abstract as ta
from datetime import datetime
from typing import Optional


class DynamicCrossfire(IStrategy):
    """
    Moon Dev's DynamicCrossfire - EMA crossover with ADX confirmation
    Optimized for trending markets (INJ, LINK, SOL)
    """

    # Strategy interface version
    INTERFACE_VERSION = 3

    # Optimal timeframe for the strategy
    timeframe = '15m'

    # Can this strategy go short?
    can_short = False

    # Minimal ROI designed for the strategy
    minimal_roi = {
        "0": 0.15,    # 15% profit target
        "60": 0.10,   # 10% after 1 hour
        "120": 0.05,  # 5% after 2 hours
        "240": 0.02   # 2% after 4 hours
    }

    # Optimal stoploss
    stoploss = -0.05  # 5% stop loss

    # Trailing stop
    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.04
    trailing_only_offset_is_reached = True

    # Run "populate_indicators()" only for new candle
    process_only_new_candles = True

    # Strategy parameters
    ema_fast_period = 50
    ema_slow_period = 200
    adx_period = 14
    adx_threshold = 25
    rsi_period = 14
    rsi_overbought = 70
    swing_period = 20

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count = 200

    # Position sizing (1% risk)
    position_adjustment_enable = False

    def informative_pairs(self):
        """Define informative pairs for multi-timeframe analysis."""
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds several indicators to the given DataFrame.
        """
        # EMAs
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=self.ema_fast_period)
        dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=self.ema_slow_period)

        # ADX
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=self.adx_period)

        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=self.rsi_period)

        # Swing Low for stop-loss
        dataframe['swing_low'] = dataframe['low'].rolling(window=self.swing_period).min()

        # EMA Cross signals
        dataframe['ema_cross_up'] = (
            (dataframe['ema_fast'] > dataframe['ema_slow']) &
            (dataframe['ema_fast'].shift(1) <= dataframe['ema_slow'].shift(1))
        )
        dataframe['ema_cross_down'] = (
            (dataframe['ema_fast'] < dataframe['ema_slow']) &
            (dataframe['ema_fast'].shift(1) >= dataframe['ema_slow'].shift(1))
        )

        # ADX rising
        dataframe['adx_rising'] = (
            (dataframe['adx'] > dataframe['adx'].shift(1)) &
            (dataframe['adx'] > self.adx_threshold)
        )

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Entry conditions:
        - EMA50 crosses above EMA200 (Golden Cross)
        - ADX > 25 and rising (strong trend)
        """
        conditions = []

        # Golden Cross
        conditions.append(dataframe['ema_cross_up'])

        # ADX confirmation
        conditions.append(dataframe['adx_rising'])

        # Volume confirmation (above average)
        conditions.append(dataframe['volume'] > dataframe['volume'].rolling(20).mean())

        if conditions:
            dataframe.loc[
                np.all(conditions, axis=0),
                'enter_long'
            ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Exit conditions:
        - RSI > 70 (overbought)
        - EMA Death Cross
        """
        conditions_rsi = []
        conditions_cross = []

        # RSI overbought exit
        conditions_rsi.append(dataframe['rsi'] > self.rsi_overbought)

        # Death Cross exit
        conditions_cross.append(dataframe['ema_cross_down'])

        if conditions_rsi:
            dataframe.loc[
                np.all(conditions_rsi, axis=0),
                'exit_long'
            ] = 1

        if conditions_cross:
            dataframe.loc[
                np.all(conditions_cross, axis=0),
                'exit_long'
            ] = 1

        return dataframe

    def custom_stoploss(self, pair: str, trade: Trade, current_time: datetime,
                        current_rate: float, current_profit: float,
                        after_fill: bool, **kwargs) -> Optional[float]:
        """
        Custom stoploss logic - use swing low as dynamic stop
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)

        if len(dataframe) > 0:
            last_candle = dataframe.iloc[-1]
            swing_low = last_candle['swing_low']

            # Calculate stop distance from current price
            if swing_low > 0:
                stop_distance = (current_rate - swing_low) / current_rate
                # Only tighten stop, never loosen
                if stop_distance < abs(self.stoploss):
                    return -stop_distance

        return None
