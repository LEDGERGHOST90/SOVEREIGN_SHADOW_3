class VwapMeanReversionEntry:
    def __init__(self):
        self.name = "vwap_entry"
    
    def generate_signal(self, df):
        if df.empty or len(df) < 5:
             return {'signal': 'NEUTRAL', 'confidence': 0}

        # Simplified VWAP (normally intraday cumulative, here rolling approx)
        # Volume Weighted Moving Average (VWMA) as proxy if daily reset isn't tracked
        # Sum(Price * Vol) / Sum(Vol)
        
        v = df['volume']
        p = df['close']
        
        vwma = (p * v).rolling(window=20).sum() / v.rolling(window=20).sum()
        
        curr_price = p.iloc[-1]
        curr_vwma = vwma.iloc[-1]
        
        # Mean Reversion: If price is significantly below VWAP (2%)
        if curr_price < curr_vwma * 0.98:
             return {
                'signal': 'BUY',
                'confidence': 75,
                'price': curr_price,
                'reasoning': f'Price 2% below VWAP Proxy ({curr_vwma:.2f})'
            }
            
        return {'signal': 'NEUTRAL', 'confidence': 0}
