import pandas as pd
import numpy as np

class PerpetualBasisTradeEntry:
    def __init__(self):
        self.name = "basis_trade_entry"
    
    def generate_signal(self, df):
        # Requires Spot and Perp data
        return {'signal': 'NEUTRAL', 'confidence': 0}
