#!/usr/bin/env python3
"""
🏴 Sovereign Shadow II - Schema Tests
Test Pydantic schema validation
"""

import pytest
from pydantic import ValidationError
from core.schemas.trade_schemas import (
    TradeValidationRequest,
    TradeExecutionRequest,
    TradeCloseRequest,
    MarketContext,
    IndicatorData,
    PositionSizing,
    TradeDirection,
    EmotionType,
)


class TestTradeValidationRequest:
    """Test TradeValidationRequest schema validation"""

    def test_valid_long_trade(self, sample_long_trade, sample_market_context):
        """Test valid LONG trade request"""
        request_data = {
            **sample_long_trade,
            "emotion_state": "calm",
            "emotion_intensity": 3,
            "market_context": sample_market_context
        }

        # Should not raise validation error
        request = TradeValidationRequest(**request_data)
        assert request.symbol == "ETH/USDT"
        assert request.trade_type == TradeDirection.LONG
        assert request.entry_price == 2500.0
        assert request.stop_loss == 2450.0
        assert request.take_profit == 2600.0

    def test_valid_short_trade(self, sample_short_trade, sample_market_context):
        """Test valid SHORT trade request"""
        request_data = {
            **sample_short_trade,
            "emotion_state": "calm",
            "emotion_intensity": 3,
            "market_context": sample_market_context
        }

        request = TradeValidationRequest(**request_data)
        assert request.trade_type == TradeDirection.SHORT
        assert request.entry_price == 100.0
        assert request.stop_loss == 102.0  # Above entry for SHORT
        assert request.take_profit == 95.0   # Below entry for SHORT

    def test_invalid_stop_loss_long(self, invalid_stop_loss_long, sample_market_context):
        """Test invalid LONG trade - stop loss above entry"""
        request_data = {
            **invalid_stop_loss_long,
            "emotion_state": "calm",
            "emotion_intensity": 3,
            "market_context": sample_market_context
        }

        with pytest.raises(ValidationError) as exc_info:
            TradeValidationRequest(**request_data)

        assert "stop_loss must be below entry_price" in str(exc_info.value)

    def test_invalid_stop_loss_short(self, invalid_stop_loss_short, sample_market_context):
        """Test invalid SHORT trade - stop loss below entry"""
        request_data = {
            **invalid_stop_loss_short,
            "emotion_state": "calm",
            "emotion_intensity": 3,
            "market_context": sample_market_context
        }

        with pytest.raises(ValidationError) as exc_info:
            TradeValidationRequest(**request_data)

        assert "stop_loss must be above entry_price" in str(exc_info.value)

    def test_negative_prices(self, sample_market_context):
        """Test that negative prices are rejected"""
        with pytest.raises(ValidationError):
            TradeValidationRequest(
                symbol="BTC/USDT",
                trade_type="long",
                entry_price=-45000.0,  # Negative price
                stop_loss=44000.0,
                take_profit=48000.0,
                emotion_state="calm",
                emotion_intensity=3,
                market_context=sample_market_context
            )

    def test_invalid_emotion_intensity(self, sample_long_trade, sample_market_context):
        """Test that emotion intensity must be 1-10"""
        request_data = {
            **sample_long_trade,
            "emotion_state": "calm",
            "emotion_intensity": 15,  # Out of range
            "market_context": sample_market_context
        }

        with pytest.raises(ValidationError) as exc_info:
            TradeValidationRequest(**request_data)

        assert "emotion_intensity" in str(exc_info.value)


class TestMarketContext:
    """Test MarketContext schema validation"""

    def test_valid_bullish_trend(self):
        """Test valid bullish market context"""
        context = MarketContext(
            trend_4h="bullish",
            trend_15m="bullish",
            structure_4h="higher_highs",
            structure_15m="consolidating",
            support_level=43500.0,
            resistance_level=46000.0,
            indicators=IndicatorData(
                rsi_4h=55.0,
                rsi_15m=52.0,
                ema_9=44800.0,
                ema_21=44500.0,
                volume_increasing=True
            )
        )

        assert context.trend_4h == "bullish"
        assert context.indicators.rsi_4h == 55.0

    def test_invalid_rsi_range(self):
        """Test that RSI must be 0-100"""
        with pytest.raises(ValidationError):
            IndicatorData(
                rsi_4h=150.0,  # Out of range
                rsi_15m=52.0,
                ema_9=44800.0,
                ema_21=44500.0,
                volume_increasing=True
            )

    def test_trend_validation(self):
        """Test trend validation (bullish/bearish/neutral)"""
        # Valid trends
        context = MarketContext(
            trend_4h="bullish",
            trend_15m="bearish",
            structure_4h="higher_highs",
            structure_15m="lower_lows"
        )
        assert context.trend_4h == "bullish"
        assert context.trend_15m == "bearish"


class TestPositionSizing:
    """Test PositionSizing calculations"""

    def test_position_sizing_long(self):
        """Test position sizing for LONG trade"""
        sizing = PositionSizing(
            account_size=10000.0,
            risk_percent=1.0,
            entry_price=45000.0,
            stop_loss=44000.0,
            trade_type=TradeDirection.LONG
        )

        # Risk amount = $10,000 × 1% = $100
        # Price risk = $45,000 - $44,000 = $1,000
        # Position size = $100 / $1,000 = 0.1 BTC
        assert sizing.risk_amount == 100.0
        assert sizing.price_risk == 1000.0
        assert abs(sizing.position_size - 0.1) < 0.001

    def test_position_sizing_short(self):
        """Test position sizing for SHORT trade"""
        sizing = PositionSizing(
            account_size=5000.0,
            risk_percent=2.0,
            entry_price=100.0,
            stop_loss=102.0,
            trade_type=TradeDirection.SHORT
        )

        # Risk amount = $5,000 × 2% = $100
        # Price risk = $102 - $100 = $2
        # Position size = $100 / $2 = 50 units
        assert sizing.risk_amount == 100.0
        assert sizing.price_risk == 2.0
        assert abs(sizing.position_size - 50.0) < 0.001

    def test_risk_reward_calculation(self):
        """Test risk-reward ratio calculation"""
        sizing = PositionSizing(
            account_size=10000.0,
            risk_percent=1.0,
            entry_price=45000.0,
            stop_loss=44000.0,
            take_profit=48000.0,
            trade_type=TradeDirection.LONG
        )

        # Risk = $1,000, Reward = $3,000, R:R = 1:3
        assert sizing.risk_reward_ratio == 3.0


class TestTradeExecutionRequest:
    """Test TradeExecutionRequest schema"""

    def test_valid_execution_request(self):
        """Test valid trade execution request"""
        request = TradeExecutionRequest(
            validation_id="VAL-123",
            symbol="BTC/USDT",
            trade_type="long",
            entry_price=45000.0,
            stop_loss=44000.0,
            take_profit=48000.0,
            position_size=0.1,
            exchange="coinbase",
            notes="NetworkChuck 4H/15M setup"
        )

        assert request.validation_id == "VAL-123"
        assert request.position_size == 0.1
        assert request.exchange == "coinbase"

    def test_missing_required_fields(self):
        """Test that required fields are enforced"""
        with pytest.raises(ValidationError):
            TradeExecutionRequest(
                # Missing validation_id
                symbol="BTC/USDT",
                trade_type="long",
                entry_price=45000.0
            )


class TestTradeCloseRequest:
    """Test TradeCloseRequest schema"""

    def test_valid_close_request(self):
        """Test valid trade close request"""
        request = TradeCloseRequest(
            trade_id="TRADE-001",
            exit_price=48000.0,
            close_reason="take_profit",
            notes="Hit TP target"
        )

        assert request.trade_id == "TRADE-001"
        assert request.exit_price == 48000.0
        assert request.close_reason == "take_profit"

    def test_invalid_exit_price(self):
        """Test that exit price must be positive"""
        with pytest.raises(ValidationError):
            TradeCloseRequest(
                trade_id="TRADE-001",
                exit_price=-48000.0,  # Negative price
                close_reason="take_profit"
            )


@pytest.mark.unit
class TestEmotionType:
    """Test EmotionType enum"""

    def test_all_emotion_types(self):
        """Test all valid emotion types"""
        valid_emotions = ["calm", "confident", "fearful", "greedy", "revenge", "confused"]

        for emotion in valid_emotions:
            assert emotion in [e.value for e in EmotionType]

    def test_emotion_validation(self, sample_long_trade, sample_market_context):
        """Test that only valid emotions are accepted"""
        request_data = {
            **sample_long_trade,
            "emotion_state": "excited",  # Not a valid emotion
            "emotion_intensity": 5,
            "market_context": sample_market_context
        }

        with pytest.raises(ValidationError):
            TradeValidationRequest(**request_data)
