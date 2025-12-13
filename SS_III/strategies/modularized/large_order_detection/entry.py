import pandas as pd
import numpy as np

class LargeOrderDetectionEntry:
    def __init__(self):
        self.name = "large_order_entry"
    
    def generate_signal(self, df):
        # Requires Level 2 / DOM
        return {'signal': 'NEUTRAL', 'confidence': 0}
