```python
# -*- coding: utf-8 -*-
import pandas as pd
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover, crossunder

class ClusterBandwidth(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade
    max_daily_trades = 3
    bandwidth_threshold = 0.5
    bandwidth_expansion = 0.3
    
    def init(self):
        # Clean and prepare data
        self.data.columns = [col.capitalize() for col in self.data.columns]
        
        # Calculate indicators using TA-Lib with self.I()
        # Bollinger Bands and Bandwidth
        def calc_bbands_and_bandwidth(close):
            upper, middle, lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
            bandwidth = (upper - lower) / middle
            bandwidth = np.nan_to_num(bandwidth, nan=0, posinf=0, neginf=0)
            return upper, middle, lower, bandwidth
        
        self.bb_upper, self.bb_middle, self.bb_lower, self.bb_bandwidth = self.I(
            calc_bbands_and_bandwidth, self.data.Close, 
            name=['BB_Upper', 'BB_Middle', 'BB_Lower', 'BB_Bandwidth']
        )
        
        # Liquidation clusters (simulated using swing highs/lows)
        self.cluster_high = self.I(talib.MAX, self.data.High, 20, name='Cluster_High')
        self.cluster_low = self.I(talib.MIN, self.data.Low, 20, name='Cluster_Low')
        
        # Volume validation
        self.volume_sma = self.I(talib.SMA, self.data.Volume, 20, name='Volume_SMA')
        
        # Track daily trades
        self.current_day = None
        self.trades_today = 0

    def next(self):
        # Update daily trade counter
        current_day = self.data.index[-1].date()
        if current_day != self.current_day:
            self.current_day = current_day
            self.trades_today = 0
        
        # Get indicator values
        close_price = self.data.Close[-1]
        upper_band = self.bb_upper[-1]
        lower_band = self.bb_lower[-1]
        bandwidth = self.bb_bandwidth[-1]
        cl_high = self.cluster_high[-1]
        cl_low = self.cluster_low[-1]
        
        # Calculate distance to clusters
        dist_to_high = abs(cl_high - close_price)/close_price if cl_high != 0 else 0
        dist_to_low = abs(close_price - cl_low)/close_price if cl_low != 0 else 0
        
        # Entry conditions
        if not self.position and self.trades_today < self.max_daily_trades:
            # Long entry conditions
            if (dist_to_high <= 0.02 and 
                bandwidth < self.bandwidth_threshold and
                self.data.Volume[-1] > self.volume_sma[-1] and
                crossover(self.data.High, cl_high)):
                
                # Risk management calculations
                sl_price = cl_low
                risk_per_share = close_price - sl_price
                if risk_per_share <= 0: return
                
                position_size = (self.equity * self.risk_per_trade) / risk_per_share
                position_size = int(round(position_size))
                if position_size > 0:
                    self.buy(size=position_size, sl=sl_price, tag={'entry_bw': bandwidth})
                    self.trades_today += 1
                    print(f"🌙✨ LONG signal! Size: {position_size} @ {close_price:.2f} | SL: {sl_price:.2f} 🚀")
            
            # Short entry conditions
            elif (dist_to_low <= 0.02 and 
                  bandwidth < self.bandwidth_threshold and
                  self.data.Volume[-1] > self.volume_sma[-1] and
                  crossunder(self.data.Low, cl_low)):
                
                # Risk management calculations
                sl_price = cl_high
                risk_per_share = sl_price - close_price
                if risk_per_share <= 0: return
                
                position_size = (self.equity * self.risk_per_trade) / risk_per_share
                position_size = int(round(position_size))
                if position_size > 0:
                    self.sell