import pandas as pd
import numpy as np

class InstitutionalOrderFlowEntry:
    def __init__(self):
        self.name = "iof_entry"
    
    def generate_signal(self, df):
        # Requires Tape/Level 2
        return {'signal': 'NEUTRAL', 'confidence': 0}
