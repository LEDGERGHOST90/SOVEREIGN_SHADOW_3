#!/usr/bin/env python3
"""
RSI Reversion Strategy - Risk Module
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from base_strategy import BaseRiskModule


class RSIReversionRisk(BaseRiskModule):
    """RSI Reversion risk management"""
    
    def __init__(self):
        super().__init__(
            max_position_size=0.10,
            stop_loss_percent=1.0,
            take_profit_percent=2.0,
            risk_per_trade=0.01
        )
        self.name = "rsi_reversion_risk"
