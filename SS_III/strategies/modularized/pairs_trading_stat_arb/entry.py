import pandas as pd
import numpy as np

class PairsTradingStatArbEntry:
    def __init__(self):
        self.name = "pairs_entry"
    
    def generate_signal(self, df):
        # Requires multi-asset data
        return {'signal': 'NEUTRAL', 'confidence': 0}
