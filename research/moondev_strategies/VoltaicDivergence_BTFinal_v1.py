from backtesting import Strategy
import talib
import pandas as pd

class VoltaicDivergence(Strategy):
    bb_period = 20
    bb_dev = 2
    atr_period = 14
    rsi_period = 14
    risk_per_trade = 0.01  # 1% risk per trade
    rr_ratio = 2  # 1:2 risk-reward ratio

    def init(self):
        # Moon Dev Debug: Preparing cosmic data streams 🌌
        print("🌙 MOON DEV INITIALIZING STRATEGY... PREPARING DATA ORBIT")
        
        # Calculate indicators
        self.upper_bb, self.middle_bb, self.lower_bb = self.I(talib.BBANDS, self.data.Close, timeperiod=self.bb_period, nbdevup=self.bb_dev, nbdevdn=self.bb_dev)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        self.atr_avg = self.I(talib.SMA, self.atr, timeperiod=50)
        
        # Track swing highs/lows
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=5)
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=5)
        
        # Track previous values for divergence detection
        self.prev_price_high = None
        self.prev_price_low = None
        self.prev_atr_high = None
        self.prev_atr_low = None

    def next(self):
        if len(self.data.Close) < 50:  # Wait for enough data
            return
            
        current_atr = self.atr[-1]
        atr_avg = self.atr_avg[-1]
        
        # Skip trades during low volatility
        if current_atr < atr_avg:
            return
            
        current_close = self.data.Close[-1]
        current_rsi = self.rsi[-1]
        upper_bb = self.upper_bb[-1]
        lower_bb = self.lower_bb[-1]
        
        # Detect divergences
        price_high = self.swing_high[-1]
        price_low = self.swing_low[-1]
        
        # Long setup: bullish divergence (higher price high but lower volatility)
        if (self.prev_price_high is not None and price_high > self.prev_price_high and 
            current_atr < self.prev_atr_high):
            if (current_close > upper_bb and current_rsi > 50 and 
                not self.position.is_long):
                
                # Calculate position size
                stop_loss = self.swing_low[-1]
                risk_amount = self.equity * self.risk_per_trade
                risk_per_unit = current_close - stop_loss
                position_size = int(round(risk_amount / risk_per_unit))
                
                if position_size > 0:
                    self.buy(size=position_size, sl=stop_loss, 
                            tp=current_close + (self.rr_ratio * (current_close - stop_loss)))
                    print(f"🌙 MOON DEV LONG SIGNAL! 🚀 Price: {current_close}, RSI: {current_rsi}, Size: {position_size}")
        
        # Short setup: bearish divergence (lower price low but higher volatility)
        elif (self.prev_price_low is not None and price_low < self.prev_price_low and 
              current_atr > self.prev_atr_low):
            if (current_close < lower_bb and current_rsi < 50 and 
                not self.position.is_short):
                
                # Calculate position size
                stop_loss = self.swing_high[-1]
                risk_amount = self.equity * self.risk_per_trade
                risk_per_unit = stop_loss - current_close
                position_size = int(round(risk_amount / risk_per_unit))
                
                if position_size > 0:
                    self.sell(size=position_size, sl=stop_loss, 
                             tp=current_close - (self.rr_ratio * (stop_loss - current_close)))
                    print(f"🌙 MOON DEV SHORT SIGNAL! 🌑 Price: {current_close}, RSI: {current_rsi}, Size: {position_size}")
        
        # Update previous values
        self.prev_price_high = price_high
        self.prev_price_low = price_low
        self.prev_atr_high = current_atr if price_high == self.data.High[-1] else self.prev_atr_high
        self.prev_atr_low = current_atr if price_low == self.data.Low[-1] else self.prev_atr_low

if __name__ == '__main__':
    from backtesting import Backtest
    
    # Load and prepare data
    print("🌙 MOON DEV LOADING COSMIC MARKET DATA...")
    data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    data = data.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })
    data['Datetime'] = pd.to_datetime(data['datetime'])
    data = data.set_index('Datetime')
    
    # Moon Dev Debug: Adjusting for cosmic price scales 🌕
    print("🌙 MOON DEV INITIALIZING BACKTEST WITH 100,000 UNITS OF COSMIC CASH")
    bt = Backtest(data, VoltaicDivergence, commission=.002, margin=1.0, trade_on_close=True, cash=100000)
    stats = bt.run()
    
    # Moon Dev Debug: Displaying celestial performance metrics 🌠
    print("\n🌙 MOON DEV BACKTEST RESULTS:")
    print("✨" * 40)
    print(stats)
    print("✨" * 40)
    print(stats._strategy)