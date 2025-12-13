import pandas as pd
import numpy as np

class SupplyDemandZonesEntry:
    def __init__(self):
        self.name = "supply_demand_entry"
        self.lookback = 50
    
    def generate_signal(self, df):
        if df.empty or len(df) < self.lookback:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # Identify Demand Zone: Strong impulsive move up
        # Simplified: Look for largest green candle body in lookback
        
        opens = df['open']
        closes = df['close']
        body_sizes = closes - opens
        
        # Find strongest green candle (Demand origin)
        max_green_idx = body_sizes.iloc[-self.lookback:].idxmax()
        
        if pd.isna(max_green_idx):
             return {'signal': 'NEUTRAL', 'confidence': 0}

        demand_zone_top = df.loc[max_green_idx, 'open']
        demand_zone_bottom = df.loc[max_green_idx, 'low']
        
        curr_price = df['close'].iloc[-1]
        
        # Retest of demand zone
        in_zone = demand_zone_bottom <= curr_price <= demand_zone_top
        
        if in_zone:
             return {
                'signal': 'BUY',
                'confidence': 80,
                'price': curr_price,
                'reasoning': f'Retest of Demand Zone ({demand_zone_bottom:.2f} - {demand_zone_top:.2f})'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}
