#!/usr/bin/env python3
"""
🏴 Sovereign Shadow II - Pytest Configuration
Shared fixtures and test configuration
"""

import pytest
import os
from datetime import datetime
from typing import Dict, Any
from unittest.mock import Mock, MagicMock


@pytest.fixture
def sample_trade_request():
    """Sample trade validation request for testing"""
    return {
        "symbol": "BTC/USDT",
        "trade_type": "long",
        "entry_price": 45000.0,
        "stop_loss": 44000.0,
        "take_profit": 48000.0,
        "account_size": 10000.0,
        "emotion_state": "calm",
        "emotion_intensity": 3,
        "market_context": {
            "trend_4h": "bullish",
            "trend_15m": "bullish",
            "structure_4h": "higher_highs",
            "structure_15m": "consolidating",
            "support_level": 43500.0,
            "resistance_level": 46000.0,
            "indicators": {
                "rsi_4h": 55.0,
                "rsi_15m": 52.0,
                "ema_9": 44800.0,
                "ema_21": 44500.0,
                "volume_increasing": True
            }
        },
        "notes": "Testing NetworkChuck 4H/15M strategy"
    }


@pytest.fixture
def sample_long_trade():
    """Sample LONG trade setup"""
    return {
        "symbol": "ETH/USDT",
        "trade_type": "long",
        "entry_price": 2500.0,
        "stop_loss": 2450.0,
        "take_profit": 2600.0,
        "account_size": 5000.0
    }


@pytest.fixture
def sample_short_trade():
    """Sample SHORT trade setup"""
    return {
        "symbol": "SOL/USDT",
        "trade_type": "short",
        "entry_price": 100.0,
        "stop_loss": 102.0,
        "take_profit": 95.0,
        "account_size": 5000.0
    }


@pytest.fixture
def invalid_stop_loss_long():
    """Invalid LONG trade - stop loss above entry"""
    return {
        "symbol": "BTC/USDT",
        "trade_type": "long",
        "entry_price": 45000.0,
        "stop_loss": 46000.0,  # WRONG: Should be below entry
        "take_profit": 48000.0,
        "account_size": 10000.0
    }


@pytest.fixture
def invalid_stop_loss_short():
    """Invalid SHORT trade - stop loss below entry"""
    return {
        "symbol": "BTC/USDT",
        "trade_type": "short",
        "entry_price": 45000.0,
        "stop_loss": 44000.0,  # WRONG: Should be above entry
        "take_profit": 42000.0,
        "account_size": 10000.0
    }


@pytest.fixture
def poor_risk_reward():
    """Trade with poor risk-reward ratio (< 1:2)"""
    return {
        "symbol": "BTC/USDT",
        "trade_type": "long",
        "entry_price": 45000.0,
        "stop_loss": 44000.0,  # Risk: $1000
        "take_profit": 45500.0,  # Reward: $500 (R:R = 1:0.5)
        "account_size": 10000.0
    }


@pytest.fixture
def mock_exchange():
    """Mock exchange connector for testing"""
    exchange = Mock()
    exchange.connected = True
    exchange.fetch_balance.return_value = {
        "USDT": 10000.0,
        "BTC": 0.5,
        "ETH": 2.0
    }
    exchange.create_order.return_value = {
        "success": True,
        "order_id": "TEST-ORDER-123",
        "symbol": "BTC/USDT",
        "side": "buy",
        "type": "limit",
        "amount": 0.1,
        "price": 45000.0,
        "status": "open"
    }
    exchange.fetch_ticker.return_value = {
        "bid": 44990.0,
        "ask": 45010.0,
        "last": 45000.0
    }
    return exchange


@pytest.fixture
def psychology_state_calm():
    """Calm psychology state"""
    return {
        "emotion": "calm",
        "intensity": 3,
        "consecutive_losses": 0,
        "last_loss_time": None,
        "daily_loss_count": 0
    }


@pytest.fixture
def psychology_state_tilted():
    """Tilted psychology state (3 consecutive losses)"""
    return {
        "emotion": "revenge",
        "intensity": 8,
        "consecutive_losses": 3,
        "last_loss_time": datetime.now().isoformat(),
        "daily_loss_count": 3
    }


@pytest.fixture
def sample_market_context():
    """Sample market analysis context"""
    return {
        "trend_4h": "bullish",
        "trend_15m": "bullish",
        "structure_4h": "higher_highs",
        "structure_15m": "consolidating",
        "support_level": 43500.0,
        "resistance_level": 46000.0,
        "indicators": {
            "rsi_4h": 55.0,
            "rsi_15m": 52.0,
            "ema_9": 44800.0,
            "ema_21": 44500.0,
            "volume_increasing": True
        }
    }


@pytest.fixture
def completed_trade_winner():
    """Completed winning trade"""
    return {
        "trade_id": "TRADE-001",
        "symbol": "BTC/USDT",
        "side": "long",
        "entry_price": 45000.0,
        "exit_price": 48000.0,
        "stop_loss": 44000.0,
        "take_profit": 48000.0,
        "position_size": 0.1,
        "pnl": 300.0,
        "pnl_percent": 3.0,
        "outcome": "winner",
        "entry_time": "2025-01-01T10:00:00",
        "exit_time": "2025-01-01T14:00:00"
    }


@pytest.fixture
def completed_trade_loser():
    """Completed losing trade"""
    return {
        "trade_id": "TRADE-002",
        "symbol": "ETH/USDT",
        "side": "long",
        "entry_price": 2500.0,
        "exit_price": 2450.0,
        "stop_loss": 2450.0,
        "take_profit": 2600.0,
        "position_size": 2.0,
        "pnl": -100.0,
        "pnl_percent": -2.0,
        "outcome": "loser",
        "entry_time": "2025-01-01T15:00:00",
        "exit_time": "2025-01-01T16:00:00"
    }


@pytest.fixture
def temp_journal_file(tmp_path):
    """Create temporary journal file for testing"""
    journal_file = tmp_path / "test_journal.json"
    return str(journal_file)


# Test configuration
def pytest_configure(config):
    """Pytest configuration hook"""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for system components"
    )
    config.addinivalue_line(
        "markers", "slow: Slow-running tests"
    )
    config.addinivalue_line(
        "markers", "requires_api: Tests that require API keys"
    )
