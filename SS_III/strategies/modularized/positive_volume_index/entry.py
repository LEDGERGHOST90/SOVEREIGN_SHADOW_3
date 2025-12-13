import pandas as pd
import numpy as np

class PositiveVolumeIndexEntry:
    def __init__(self):
        self.name = "pvi_entry"
    
    def generate_signal(self, df):
        # PVI logic (Crowd following)
        return {'signal': 'NEUTRAL', 'confidence': 0}
