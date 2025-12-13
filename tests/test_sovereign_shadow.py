#!/usr/bin/env python3
"""
🧪 Sovereign Shadow II - Test Suite
Tests for core components
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Add workspace to path
sys.path.insert(0, '/workspace')

from core.intelligence.regime_detector import RegimeDetector, MarketRegime
from core.intelligence.performance_tracker import PerformanceTracker, TradeRecord
from core.intelligence.strategy_selector import StrategySelector, SelectionMethod
from core.safety.guardrails import SafetyGuardrails, SafetyStatus
from strategies.modularized.base import Signal, SignalType


class TestRegimeDetector:
    """Tests for Market Regime Detector"""
    
    @pytest.fixture
    def detector(self):
        return RegimeDetector()
    
    @pytest.fixture
    def sample_uptrend_data(self):
        """Generate sample uptrend data"""
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=150, freq='1h')
        base_price = 100000
        trend = np.cumsum(np.abs(np.random.randn(150)) * 100 + 50)  # Strong uptrend
        
        df = pd.DataFrame({
            'open': base_price + trend + np.random.randn(150) * 50,
            'high': base_price + trend + abs(np.random.randn(150)) * 150,
            'low': base_price + trend - abs(np.random.randn(150)) * 50,
            'close': base_price + trend + np.random.randn(150) * 50,
            'volume': np.random.randint(100, 1000, 150)
        }, index=dates)
        
        df['high'] = df[['open', 'high', 'close']].max(axis=1)
        df['low'] = df[['open', 'low', 'close']].min(axis=1)
        return df
    
    @pytest.fixture
    def sample_choppy_data(self):
        """Generate sample choppy/ranging data"""
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=150, freq='1h')
        base_price = 100000
        
        # Ranging market - oscillate around base
        noise = np.sin(np.linspace(0, 10, 150)) * 1000 + np.random.randn(150) * 500
        
        df = pd.DataFrame({
            'open': base_price + noise + np.random.randn(150) * 100,
            'high': base_price + noise + abs(np.random.randn(150)) * 200,
            'low': base_price + noise - abs(np.random.randn(150)) * 200,
            'close': base_price + noise + np.random.randn(150) * 100,
            'volume': np.random.randint(100, 1000, 150)
        }, index=dates)
        
        df['high'] = df[['open', 'high', 'close']].max(axis=1)
        df['low'] = df[['open', 'low', 'close']].min(axis=1)
        return df
    
    def test_detector_initialization(self, detector):
        """Test detector initializes correctly"""
        assert detector.lookback_period == 100
        assert detector.ADX_TREND_THRESHOLD == 25
    
    def test_detect_regime_returns_analysis(self, detector, sample_uptrend_data):
        """Test regime detection returns valid analysis"""
        analysis = detector.detect_regime(sample_uptrend_data)
        
        assert analysis is not None
        assert analysis.regime in MarketRegime
        assert 0 <= analysis.confidence <= 100
        assert analysis.adx >= 0
        assert 0 <= analysis.rsi <= 100
    
    def test_regime_has_recommendations(self, detector, sample_uptrend_data):
        """Test regime provides strategy recommendations"""
        analysis = detector.detect_regime(sample_uptrend_data)
        
        # Should have recommended strategies for non-unknown regimes
        if analysis.regime != MarketRegime.UNKNOWN:
            assert len(analysis.recommended_strategies) > 0
    
    def test_insufficient_data_returns_unknown(self, detector):
        """Test insufficient data returns unknown regime"""
        short_df = pd.DataFrame({
            'open': [100, 101],
            'high': [102, 103],
            'low': [99, 100],
            'close': [101, 102],
            'volume': [100, 100]
        })
        
        analysis = detector.detect_regime(short_df)
        assert analysis.regime == MarketRegime.UNKNOWN
        assert analysis.confidence == 0


class TestPerformanceTracker:
    """Tests for Performance Tracker"""
    
    @pytest.fixture
    def tracker(self):
        """Create in-memory tracker for testing"""
        return PerformanceTracker(":memory:")
    
    def test_tracker_initialization(self, tracker):
        """Test tracker initializes database"""
        assert tracker.conn is not None
    
    def test_log_trade(self, tracker):
        """Test logging a trade"""
        trade = TradeRecord(
            trade_id="test-001",
            strategy_name="ElderReversion",
            regime="choppy_volatile",
            asset="BTC/USDT",
            timeframe="1h",
            side="BUY",
            entry_price=100000,
            exit_price=102000,
            quantity=0.01,
            entry_time="2024-01-01T12:00:00",
            exit_time="2024-01-01T14:00:00",
            pnl_usd=20.0,
            pnl_percent=2.0,
            exit_reason="TAKE_PROFIT"
        )
        
        result = tracker.log_trade(trade)
        assert result == True
    
    def test_duplicate_trade_rejected(self, tracker):
        """Test duplicate trade is rejected"""
        trade = TradeRecord(
            trade_id="test-dup",
            strategy_name="TestStrategy",
            regime="trending_bull",
            asset="BTC/USDT",
            timeframe="1h",
            side="BUY",
            entry_price=100000,
            exit_price=101000,
            quantity=0.01,
            entry_time="2024-01-01T12:00:00",
            exit_time="2024-01-01T13:00:00",
            pnl_usd=10.0,
            pnl_percent=1.0,
            exit_reason="TAKE_PROFIT"
        )
        
        result1 = tracker.log_trade(trade)
        result2 = tracker.log_trade(trade)
        
        assert result1 == True
        assert result2 == False
    
    def test_get_summary(self, tracker):
        """Test getting performance summary"""
        # Log some trades
        for i in range(3):
            trade = TradeRecord(
                trade_id=f"sum-{i}",
                strategy_name="TestStrategy",
                regime="trending_bull",
                asset="BTC/USDT",
                timeframe="1h",
                side="BUY",
                entry_price=100000,
                exit_price=101000 if i < 2 else 99000,  # 2 wins, 1 loss
                quantity=0.01,
                entry_time="2024-01-01T12:00:00",
                exit_time="2024-01-01T13:00:00",
                pnl_usd=10.0 if i < 2 else -10.0,
                pnl_percent=1.0 if i < 2 else -1.0,
                exit_reason="TAKE_PROFIT" if i < 2 else "STOP_LOSS"
            )
            tracker.log_trade(trade)
        
        summary = tracker.get_summary()
        
        assert summary['total_trades'] == 3
        assert summary['total_pnl_usd'] == 10.0  # 10 + 10 - 10


class TestSafetyGuardrails:
    """Tests for Safety Guardrails"""
    
    @pytest.fixture
    def guardrails(self):
        return SafetyGuardrails(
            max_position_size=0.10,
            max_daily_loss=0.03,
            cooldown_seconds=60
        )
    
    def test_position_size_validation(self, guardrails):
        """Test position size limits are enforced"""
        # Valid position (5%)
        is_valid, checks = guardrails.validate_trade(
            portfolio_value=10000,
            position_value=500,
            stop_loss_distance=0.01,
            open_positions=0,
            asset="BTC/USDT"
        )
        assert is_valid == True
        
        # Invalid position (15%)
        is_valid, checks = guardrails.validate_trade(
            portfolio_value=10000,
            position_value=1500,
            stop_loss_distance=0.01,
            open_positions=0,
            asset="BTC/USDT"
        )
        assert is_valid == False
        
        failed_checks = [c for c in checks if c.status == SafetyStatus.FAILED]
        assert any("position" in c.name.lower() for c in failed_checks)
    
    def test_stop_loss_enforcement(self, guardrails):
        """Test stop loss minimum is enforced"""
        # Stop loss too tight (0.3%)
        is_valid, checks = guardrails.validate_trade(
            portfolio_value=10000,
            position_value=500,
            stop_loss_distance=0.003,
            open_positions=0,
            asset="BTC/USDT"
        )
        assert is_valid == False
    
    def test_daily_loss_limit(self, guardrails):
        """Test daily loss limit stops trading"""
        # Simulate losses
        guardrails.daily_pnl = -350  # 3.5% loss on $10k
        
        is_valid, checks = guardrails.validate_trade(
            portfolio_value=10000,
            position_value=500,
            stop_loss_distance=0.01,
            open_positions=0,
            asset="BTC/USDT"
        )
        
        assert is_valid == False
        blocked_checks = [c for c in checks if c.status == SafetyStatus.BLOCKED]
        assert any("daily" in c.name.lower() for c in blocked_checks)


class TestModularStrategies:
    """Tests for modular strategy framework"""
    
    @pytest.fixture
    def sample_data(self):
        """Generate sample OHLCV data"""
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=100, freq='1h')
        
        df = pd.DataFrame({
            'open': np.random.randn(100).cumsum() + 100000,
            'high': np.random.randn(100).cumsum() + 100200,
            'low': np.random.randn(100).cumsum() + 99800,
            'close': np.random.randn(100).cumsum() + 100000,
            'volume': np.random.randint(100, 1000, 100)
        }, index=dates)
        
        df['high'] = df[['open', 'high', 'close']].max(axis=1) + abs(np.random.randn(100)) * 100
        df['low'] = df[['open', 'low', 'close']].min(axis=1) - abs(np.random.randn(100)) * 100
        return df
    
    def test_elder_reversion_entry(self, sample_data):
        """Test Elder Reversion entry module"""
        from strategies.modularized.elder_reversion.entry import ElderReversionEntry
        
        entry = ElderReversionEntry()
        signal = entry.generate_signal(sample_data)
        
        assert isinstance(signal, Signal)
        assert signal.signal in SignalType
        assert 0 <= signal.confidence <= 100
    
    def test_trend_follow_ema_entry(self, sample_data):
        """Test Trend Follow EMA entry module"""
        from strategies.modularized.trend_follow_ema.entry import TrendFollowEMAEntry
        
        entry = TrendFollowEMAEntry()
        signal = entry.generate_signal(sample_data)
        
        assert isinstance(signal, Signal)
        assert signal.signal in SignalType


class TestStrategySelector:
    """Tests for Strategy Selector"""
    
    @pytest.fixture
    def components(self):
        """Create selector components"""
        detector = RegimeDetector()
        tracker = PerformanceTracker(":memory:")
        selector = StrategySelector(detector, tracker)
        return detector, tracker, selector
    
    @pytest.fixture
    def sample_data(self):
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=150, freq='1h')
        
        df = pd.DataFrame({
            'open': np.random.randn(150).cumsum() + 100000,
            'high': np.random.randn(150).cumsum() + 100200,
            'low': np.random.randn(150).cumsum() + 99800,
            'close': np.random.randn(150).cumsum() + 100000,
            'volume': np.random.randint(100, 1000, 150)
        }, index=dates)
        
        df['high'] = df[['open', 'high', 'close']].max(axis=1)
        df['low'] = df[['open', 'low', 'close']].min(axis=1)
        return df
    
    def test_register_strategy(self, components):
        """Test strategy registration"""
        detector, tracker, selector = components
        
        selector.register_strategy("TestStrategy")
        assert "TestStrategy" in selector.registered_strategies
    
    def test_select_strategy_returns_selection(self, components, sample_data):
        """Test strategy selection returns valid result"""
        detector, tracker, selector = components
        
        selector.register_strategies([
            "ElderReversion", "TrendFollowEMA", "RSIReversion"
        ])
        
        selection = selector.select_strategy(sample_data)
        
        assert selection is not None
        assert selection.strategy_name in selector.registered_strategies
        assert 0 <= selection.confidence <= 100
        assert selection.suggested_position_size > 0
        assert selection.suggested_stop_loss > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
