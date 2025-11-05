#!/usr/bin/env python3
"""
🏴 Sovereign Shadow II - SHADE Agent Tests
Test strategy validation and risk enforcement
"""

import pytest
from unittest.mock import Mock, patch
from modules.shade_agent import ShadeAgent


class TestShadeAgent:
    """Test SHADE//AGENT strategy validation"""

    @pytest.fixture
    def shade_agent(self):
        """Create SHADE agent instance"""
        return ShadeAgent()

    def test_validate_risk_reward_good(self, shade_agent):
        """Test risk-reward validation with good ratio (>= 1:2)"""
        result = shade_agent.validate_risk_reward(
            entry_price=45000.0,
            stop_loss=44000.0,
            take_profit=48000.0,
            trade_type="long"
        )

        # Risk: $1,000, Reward: $3,000, R:R = 1:3
        assert result["valid"] is True
        assert result["ratio"] == 3.0
        assert "1:3" in result["message"]

    def test_validate_risk_reward_minimum(self, shade_agent):
        """Test risk-reward validation at minimum acceptable (1:2)"""
        result = shade_agent.validate_risk_reward(
            entry_price=45000.0,
            stop_loss=44000.0,
            take_profit=47000.0,
            trade_type="long"
        )

        # Risk: $1,000, Reward: $2,000, R:R = 1:2
        assert result["valid"] is True
        assert result["ratio"] == 2.0

    def test_validate_risk_reward_poor(self, shade_agent, poor_risk_reward):
        """Test risk-reward validation with poor ratio (< 1:2)"""
        result = shade_agent.validate_risk_reward(
            entry_price=poor_risk_reward["entry_price"],
            stop_loss=poor_risk_reward["stop_loss"],
            take_profit=poor_risk_reward["take_profit"],
            trade_type=poor_risk_reward["trade_type"]
        )

        # Should reject poor R:R
        assert result["valid"] is False
        assert "below minimum" in result["message"].lower()

    def test_validate_position_size_within_risk(self, shade_agent):
        """Test position sizing within 1-2% risk rule"""
        result = shade_agent.validate_position_size(
            account_size=10000.0,
            risk_amount=100.0,  # 1% of account
            position_size=0.1
        )

        assert result["valid"] is True
        assert result["risk_percent"] == 1.0

    def test_validate_position_size_exceeds_risk(self, shade_agent):
        """Test position sizing exceeding 2% risk rule"""
        result = shade_agent.validate_position_size(
            account_size=10000.0,
            risk_amount=300.0,  # 3% of account - TOO HIGH
            position_size=0.3
        )

        assert result["valid"] is False
        assert "exceeds maximum" in result["message"].lower()

    def test_validate_trend_alignment_bullish(self, shade_agent):
        """Test trend alignment for LONG trade (both timeframes bullish)"""
        market_context = {
            "trend_4h": "bullish",
            "trend_15m": "bullish"
        }

        result = shade_agent.validate_trend_alignment(
            trade_type="long",
            market_context=market_context
        )

        assert result["valid"] is True
        assert "aligned" in result["message"].lower()

    def test_validate_trend_alignment_bearish(self, shade_agent):
        """Test trend alignment for SHORT trade (both timeframes bearish)"""
        market_context = {
            "trend_4h": "bearish",
            "trend_15m": "bearish"
        }

        result = shade_agent.validate_trend_alignment(
            trade_type="short",
            market_context=market_context
        )

        assert result["valid"] is True

    def test_validate_trend_alignment_misaligned(self, shade_agent):
        """Test trend misalignment (4H bullish, 15M bearish)"""
        market_context = {
            "trend_4h": "bullish",
            "trend_15m": "bearish"
        }

        result = shade_agent.validate_trend_alignment(
            trade_type="long",
            market_context=market_context
        )

        assert result["valid"] is False
        assert "not aligned" in result["message"].lower()

    def test_validate_support_resistance_long(self, shade_agent):
        """Test that LONG entry respects support level"""
        result = shade_agent.validate_support_resistance(
            trade_type="long",
            entry_price=45000.0,
            stop_loss=44000.0,
            support_level=43500.0,
            resistance_level=46000.0
        )

        # Stop loss (44000) is above support (43500) - valid
        assert result["valid"] is True

    def test_validate_support_resistance_short(self, shade_agent):
        """Test that SHORT entry respects resistance level"""
        result = shade_agent.validate_support_resistance(
            trade_type="short",
            entry_price=45000.0,
            stop_loss=46000.0,
            support_level=43500.0,
            resistance_level=46500.0
        )

        # Stop loss (46000) is below resistance (46500) - valid
        assert result["valid"] is True

    def test_validate_rsi_oversold(self, shade_agent):
        """Test RSI validation for oversold condition (good for LONG)"""
        indicators = {
            "rsi_4h": 35.0,  # Oversold
            "rsi_15m": 32.0
        }

        result = shade_agent.validate_rsi(
            trade_type="long",
            indicators=indicators
        )

        assert result["valid"] is True
        assert "oversold" in result["message"].lower()

    def test_validate_rsi_overbought(self, shade_agent):
        """Test RSI validation for overbought condition (good for SHORT)"""
        indicators = {
            "rsi_4h": 72.0,  # Overbought
            "rsi_15m": 75.0
        }

        result = shade_agent.validate_rsi(
            trade_type="short",
            indicators=indicators
        )

        assert result["valid"] is True
        assert "overbought" in result["message"].lower()

    def test_validate_rsi_wrong_direction(self, shade_agent):
        """Test RSI validation when going LONG in overbought"""
        indicators = {
            "rsi_4h": 75.0,  # Overbought - bad for LONG
            "rsi_15m": 78.0
        }

        result = shade_agent.validate_rsi(
            trade_type="long",
            indicators=indicators
        )

        assert result["valid"] is False
        assert "overbought" in result["message"].lower()


class TestShadeAgentIntegration:
    """Integration tests for SHADE agent"""

    @pytest.fixture
    def shade_agent(self):
        """Create SHADE agent instance"""
        return ShadeAgent()

    def test_full_validation_approved(self, shade_agent, sample_trade_request):
        """Test full trade validation with all checks passing"""
        result = shade_agent.validate_trade(sample_trade_request)

        assert result["approved"] is True
        assert "validation_id" in result
        assert len(result["checks"]) > 0
        assert all(check["passed"] for check in result["checks"])

    def test_full_validation_rejected_poor_rr(self, shade_agent, poor_risk_reward):
        """Test full validation rejection due to poor R:R"""
        trade_request = {
            **poor_risk_reward,
            "emotion_state": "calm",
            "emotion_intensity": 3,
            "market_context": {
                "trend_4h": "bullish",
                "trend_15m": "bullish"
            }
        }

        result = shade_agent.validate_trade(trade_request)

        assert result["approved"] is False
        assert any("risk:reward" in check.get("message", "").lower()
                   for check in result["checks"] if not check["passed"])

    def test_full_validation_rejected_trend_misalignment(self, shade_agent):
        """Test full validation rejection due to trend misalignment"""
        trade_request = {
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
                "trend_15m": "bearish"  # Misaligned
            }
        }

        result = shade_agent.validate_trade(trade_request)

        assert result["approved"] is False
        assert any("trend" in check.get("message", "").lower()
                   for check in result["checks"] if not check["passed"])


@pytest.mark.unit
class TestNetworkChuckStrategy:
    """Test NetworkChuck 15M/4H strategy enforcement"""

    @pytest.fixture
    def shade_agent(self):
        """Create SHADE agent instance"""
        return ShadeAgent()

    def test_4h_timeframe_validation(self, shade_agent):
        """Test 4H timeframe structure validation"""
        market_context = {
            "trend_4h": "bullish",
            "structure_4h": "higher_highs"
        }

        result = shade_agent.validate_4h_structure(market_context)

        assert result["valid"] is True

    def test_15m_timeframe_validation(self, shade_agent):
        """Test 15M timeframe entry validation"""
        market_context = {
            "trend_15m": "bullish",
            "structure_15m": "consolidating"
        }

        result = shade_agent.validate_15m_entry(market_context)

        assert result["valid"] is True

    def test_multi_timeframe_confirmation(self, shade_agent):
        """Test that both 4H and 15M must confirm"""
        # 4H bullish, 15M bearish - should reject
        market_context = {
            "trend_4h": "bullish",
            "trend_15m": "bearish",
            "structure_4h": "higher_highs",
            "structure_15m": "lower_lows"
        }

        result = shade_agent.validate_trend_alignment(
            trade_type="long",
            market_context=market_context
        )

        assert result["valid"] is False
