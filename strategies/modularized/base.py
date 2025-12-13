#!/usr/bin/env python3
"""
🏴 Sovereign Shadow II - Base Strategy Modules
Abstract base classes for modular strategy components

Author: SovereignShadow Trading System
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class SignalType(str, Enum):
    """Signal types"""
    BUY = "BUY"
    SELL = "SELL"
    NEUTRAL = "NEUTRAL"
    HOLD = "HOLD"


class ExitReason(str, Enum):
    """Exit reasons"""
    TAKE_PROFIT = "TAKE_PROFIT"
    STOP_LOSS = "STOP_LOSS"
    SIGNAL_EXIT = "SIGNAL_EXIT"
    TRAILING_STOP = "TRAILING_STOP"
    TIME_EXIT = "TIME_EXIT"
    MANUAL = "MANUAL"


@dataclass
class Signal:
    """Entry signal result"""
    signal: SignalType
    confidence: float  # 0-100
    price: float
    reasoning: str = ""
    indicators: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExitSignal:
    """Exit signal result"""
    signal: SignalType  # SELL or HOLD
    reason: ExitReason
    pnl_percent: float
    price: float
    reasoning: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PositionSizing:
    """Position sizing result"""
    position_value_usd: float
    quantity: float
    stop_loss_price: float
    take_profit_price: float
    risk_reward_ratio: float
    risk_percent: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseEntryModule(ABC):
    """
    Abstract base class for entry signal generation
    
    All entry modules must implement:
    - generate_signal(): Returns Signal object
    - get_required_indicators(): List of indicators needed
    """
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.indicators_required = []
    
    @abstractmethod
    def generate_signal(self, df: pd.DataFrame) -> Signal:
        """
        Generate entry signal from OHLCV data
        
        Args:
            df: DataFrame with columns: open, high, low, close, volume
                Should have enough history for indicator calculation
        
        Returns:
            Signal object with signal type, confidence, and reasoning
        """
        pass
    
    def get_required_indicators(self) -> List[str]:
        """Return list of required indicators"""
        return self.indicators_required
    
    def _calculate_ema(self, series: pd.Series, period: int) -> pd.Series:
        """Calculate EMA"""
        return series.ewm(span=period, adjust=False).mean()
    
    def _calculate_sma(self, series: pd.Series, period: int) -> pd.Series:
        """Calculate SMA"""
        return series.rolling(window=period).mean()
    
    def _calculate_rsi(self, series: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = series.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_bollinger_bands(
        self, series: pd.Series, period: int = 20, std_dev: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands (middle, upper, lower)"""
        middle = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        return middle, upper, lower
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate ATR"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        return tr.rolling(window=period).mean()
    
    def _calculate_stochastic(
        self, df: pd.DataFrame, k_period: int = 14, d_period: int = 3
    ) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic K and D"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        d = k.rolling(window=d_period).mean()
        
        return k, d
    
    def _calculate_macd(
        self, series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD, Signal, and Histogram"""
        fast_ema = series.ewm(span=fast, adjust=False).mean()
        slow_ema = series.ewm(span=slow, adjust=False).mean()
        macd = fast_ema - slow_ema
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        
        return macd, signal_line, histogram


class BaseExitModule(ABC):
    """
    Abstract base class for exit signal generation
    
    All exit modules must implement:
    - generate_signal(): Returns ExitSignal object
    """
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    @abstractmethod
    def generate_signal(
        self,
        df: pd.DataFrame,
        entry_price: float,
        position_side: str = "long"
    ) -> ExitSignal:
        """
        Generate exit signal
        
        Args:
            df: OHLCV DataFrame
            entry_price: Entry price of position
            position_side: "long" or "short"
        
        Returns:
            ExitSignal object
        """
        pass
    
    def _calculate_pnl_percent(
        self,
        entry_price: float,
        current_price: float,
        position_side: str = "long"
    ) -> float:
        """Calculate P&L percentage"""
        if position_side == "long":
            return ((current_price - entry_price) / entry_price) * 100
        else:
            return ((entry_price - current_price) / entry_price) * 100


class BaseRiskModule(ABC):
    """
    Abstract base class for position sizing and risk management
    
    All risk modules must implement:
    - calculate_position_size(): Returns PositionSizing object
    """
    
    def __init__(
        self,
        max_position_size: float = 0.10,  # 10% of portfolio
        risk_per_trade: float = 0.01,  # 1% risk per trade
        stop_loss_percent: float = 1.0,
        take_profit_percent: float = 2.0
    ):
        self.name = self.__class__.__name__
        self.max_position_size = max_position_size
        self.risk_per_trade = risk_per_trade
        self.stop_loss_percent = stop_loss_percent
        self.take_profit_percent = take_profit_percent
    
    @abstractmethod
    def calculate_position_size(
        self,
        portfolio_value: float,
        current_price: float,
        atr: Optional[float] = None
    ) -> PositionSizing:
        """
        Calculate position size
        
        Args:
            portfolio_value: Total portfolio value in USD
            current_price: Current asset price
            atr: Optional ATR for volatility-adjusted sizing
        
        Returns:
            PositionSizing object
        """
        pass


class ModularStrategy:
    """
    Complete modular strategy combining Entry, Exit, and Risk modules
    
    Usage:
        strategy = ModularStrategy(
            name="ElderReversion",
            entry_module=ElderReversionEntry(),
            exit_module=ElderReversionExit(),
            risk_module=ElderReversionRisk()
        )
        
        signal = strategy.generate_entry_signal(df)
        if signal.signal == SignalType.BUY:
            sizing = strategy.calculate_position(portfolio_value, current_price)
    """
    
    def __init__(
        self,
        name: str,
        entry_module: BaseEntryModule,
        exit_module: BaseExitModule,
        risk_module: BaseRiskModule,
        suitable_regimes: List[str] = None,
        timeframes: List[str] = None,
        assets: List[str] = None
    ):
        """
        Initialize modular strategy
        
        Args:
            name: Strategy name
            entry_module: Entry signal module
            exit_module: Exit signal module
            risk_module: Risk/position sizing module
            suitable_regimes: List of suitable market regimes
            timeframes: Suitable timeframes (e.g., ['15m', '1h'])
            assets: Suitable assets (e.g., ['BTC/USDT', 'ETH/USDT'])
        """
        self.name = name
        self.entry = entry_module
        self.exit = exit_module
        self.risk = risk_module
        
        self.suitable_regimes = suitable_regimes or []
        self.timeframes = timeframes or ['15m', '1h', '4h']
        self.assets = assets or ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT']
        
        # Track performance
        self.total_trades = 0
        self.winning_trades = 0
        
        logger.info(f"📊 Strategy initialized: {name}")
    
    def generate_entry_signal(self, df: pd.DataFrame) -> Signal:
        """Generate entry signal"""
        return self.entry.generate_signal(df)
    
    def generate_exit_signal(
        self,
        df: pd.DataFrame,
        entry_price: float,
        position_side: str = "long"
    ) -> ExitSignal:
        """Generate exit signal"""
        return self.exit.generate_signal(df, entry_price, position_side)
    
    def calculate_position(
        self,
        portfolio_value: float,
        current_price: float,
        atr: Optional[float] = None
    ) -> PositionSizing:
        """Calculate position size"""
        return self.risk.calculate_position_size(portfolio_value, current_price, atr)
    
    def is_suitable_for_regime(self, regime: str) -> bool:
        """Check if strategy is suitable for given regime"""
        return regime in self.suitable_regimes
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get strategy metadata"""
        return {
            'strategy_name': self.name,
            'suitable_regimes': self.suitable_regimes,
            'timeframes': self.timeframes,
            'assets': self.assets,
            'entry_indicators': self.entry.get_required_indicators(),
            'risk_per_trade': self.risk.risk_per_trade,
            'max_position_size': self.risk.max_position_size,
            'stop_loss_percent': self.risk.stop_loss_percent,
            'take_profit_percent': self.risk.take_profit_percent,
            'performance': {
                'total_trades': self.total_trades,
                'winning_trades': self.winning_trades,
                'win_rate': self.winning_trades / self.total_trades if self.total_trades > 0 else 0
            }
        }
    
    def record_trade_result(self, is_winner: bool):
        """Record trade result for tracking"""
        self.total_trades += 1
        if is_winner:
            self.winning_trades += 1
    
    def __repr__(self) -> str:
        return f"ModularStrategy(name='{self.name}', regimes={self.suitable_regimes})"
