import pandas as pd
import numpy as np

class FundingRateArbitrageEntry:
    def __init__(self):
        self.name = "funding_arb_entry"
    
    def generate_signal(self, df):
        # Requires Funding Rate data
        return {'signal': 'NEUTRAL', 'confidence': 0}
