#!/usr/bin/env python3
"""
🏴 Sovereign Shadow II - Psychology Tests
Test MIND//LOCK emotion tracking and 3-strike rule
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from core.modules.psychology_tracker import PsychologyTracker
from core.schemas.trade_schemas import EmotionType


class TestPsychologyTracker:
    """Test PsychologyTracker emotion gating"""

    @pytest.fixture
    def tracker(self, tmp_path):
        """Create psychology tracker with temp file"""
        state_file = tmp_path / "psychology_state.json"
        return PsychologyTracker(state_file=str(state_file))

    def test_initial_state_calm(self, tracker):
        """Test that initial state is calm"""
        state = tracker.get_current_state()

        assert state["emotion"] == "calm"
        assert state["intensity"] == 0
        assert state["consecutive_losses"] == 0
        assert state["locked_out"] is False

    def test_emotion_validation_calm(self, tracker):
        """Test validation with calm emotion (should pass)"""
        result = tracker.validate_emotion(
            emotion="calm",
            intensity=3
        )

        assert result["valid"] is True
        assert result["allowed_to_trade"] is True

    def test_emotion_validation_fearful(self, tracker):
        """Test validation with fearful emotion (should warn)"""
        result = tracker.validate_emotion(
            emotion="fearful",
            intensity=7
        )

        assert result["valid"] is False
        assert "fearful" in result["message"].lower()

    def test_emotion_validation_revenge(self, tracker):
        """Test validation with revenge emotion (should reject)"""
        result = tracker.validate_emotion(
            emotion="revenge",
            intensity=9
        )

        assert result["valid"] is False
        assert result["allowed_to_trade"] is False
        assert "revenge" in result["message"].lower()

    def test_emotion_validation_greedy(self, tracker):
        """Test validation with greedy emotion (should reject)"""
        result = tracker.validate_emotion(
            emotion="greedy",
            intensity=8
        )

        assert result["valid"] is False
        assert "greedy" in result["message"].lower()

    def test_high_intensity_rejection(self, tracker):
        """Test that high intensity (>= 7) rejects trade"""
        result = tracker.validate_emotion(
            emotion="confident",
            intensity=8  # Too intense
        )

        assert result["valid"] is False
        assert "intensity too high" in result["message"].lower()

    def test_record_loss_first_time(self, tracker):
        """Test recording first loss"""
        tracker.record_loss()

        state = tracker.get_current_state()
        assert state["consecutive_losses"] == 1
        assert state["daily_loss_count"] == 1
        assert state["locked_out"] is False

    def test_record_loss_second_time(self, tracker):
        """Test recording second loss"""
        tracker.record_loss()
        tracker.record_loss()

        state = tracker.get_current_state()
        assert state["consecutive_losses"] == 2
        assert state["daily_loss_count"] == 2
        assert state["locked_out"] is False

    def test_three_strike_lockout(self, tracker):
        """Test 3-strike rule triggers lockout"""
        # Record 3 losses
        tracker.record_loss()
        tracker.record_loss()
        tracker.record_loss()

        state = tracker.get_current_state()
        assert state["consecutive_losses"] == 3
        assert state["daily_loss_count"] == 3
        assert state["locked_out"] is True

    def test_lockout_prevents_trading(self, tracker):
        """Test that lockout prevents trading"""
        # Trigger lockout
        tracker.record_loss()
        tracker.record_loss()
        tracker.record_loss()

        # Try to validate emotion
        result = tracker.validate_emotion(
            emotion="calm",
            intensity=3
        )

        assert result["valid"] is False
        assert result["allowed_to_trade"] is False
        assert "locked out" in result["message"].lower()

    def test_record_win_resets_consecutive(self, tracker):
        """Test that win resets consecutive losses"""
        # Record 2 losses
        tracker.record_loss()
        tracker.record_loss()

        state = tracker.get_current_state()
        assert state["consecutive_losses"] == 2

        # Record win
        tracker.record_win()

        state = tracker.get_current_state()
        assert state["consecutive_losses"] == 0  # Reset
        assert state["daily_loss_count"] == 2  # Not reset

    def test_daily_reset(self, tracker):
        """Test that losses reset at midnight"""
        # Record losses yesterday
        yesterday = datetime.now() - timedelta(days=1)
        tracker.state["last_loss_time"] = yesterday.isoformat()
        tracker.state["daily_loss_count"] = 3
        tracker.state["locked_out"] = True

        # Check if should reset
        if tracker.should_reset_daily():
            tracker.reset_daily()

        state = tracker.get_current_state()
        assert state["daily_loss_count"] == 0
        assert state["locked_out"] is False

    def test_manual_unlock(self, tracker):
        """Test manual unlock after cooldown"""
        # Trigger lockout
        tracker.record_loss()
        tracker.record_loss()
        tracker.record_loss()

        assert tracker.state["locked_out"] is True

        # Manually unlock
        tracker.unlock()

        state = tracker.get_current_state()
        assert state["locked_out"] is False
        assert state["consecutive_losses"] == 0


class TestEmotionIntensity:
    """Test emotion intensity tracking"""

    @pytest.fixture
    def tracker(self, tmp_path):
        """Create psychology tracker"""
        state_file = tmp_path / "psychology_state.json"
        return PsychologyTracker(state_file=str(state_file))

    def test_intensity_1_allowed(self, tracker):
        """Test intensity 1 (very low) is allowed"""
        result = tracker.validate_emotion("calm", intensity=1)
        assert result["valid"] is True

    def test_intensity_3_allowed(self, tracker):
        """Test intensity 3 (low) is allowed"""
        result = tracker.validate_emotion("calm", intensity=3)
        assert result["valid"] is True

    def test_intensity_5_allowed(self, tracker):
        """Test intensity 5 (medium) is allowed"""
        result = tracker.validate_emotion("calm", intensity=5)
        assert result["valid"] is True

    def test_intensity_7_rejected(self, tracker):
        """Test intensity 7 (high) is rejected"""
        result = tracker.validate_emotion("calm", intensity=7)
        assert result["valid"] is False

    def test_intensity_10_rejected(self, tracker):
        """Test intensity 10 (maximum) is rejected"""
        result = tracker.validate_emotion("calm", intensity=10)
        assert result["valid"] is False


class TestEmotionTypes:
    """Test different emotion type validations"""

    @pytest.fixture
    def tracker(self, tmp_path):
        """Create psychology tracker"""
        state_file = tmp_path / "psychology_state.json"
        return PsychologyTracker(state_file=str(state_file))

    def test_calm_allowed(self, tracker):
        """Test CALM emotion is allowed"""
        result = tracker.validate_emotion("calm", intensity=3)
        assert result["valid"] is True
        assert result["allowed_to_trade"] is True

    def test_confident_allowed_low_intensity(self, tracker):
        """Test CONFIDENT emotion allowed at low intensity"""
        result = tracker.validate_emotion("confident", intensity=4)
        assert result["valid"] is True

    def test_confident_rejected_high_intensity(self, tracker):
        """Test CONFIDENT emotion rejected at high intensity"""
        result = tracker.validate_emotion("confident", intensity=8)
        assert result["valid"] is False

    def test_fearful_rejected(self, tracker):
        """Test FEARFUL emotion is rejected"""
        result = tracker.validate_emotion("fearful", intensity=5)
        assert result["valid"] is False

    def test_greedy_rejected(self, tracker):
        """Test GREEDY emotion is rejected"""
        result = tracker.validate_emotion("greedy", intensity=5)
        assert result["valid"] is False

    def test_revenge_rejected(self, tracker):
        """Test REVENGE emotion is rejected"""
        result = tracker.validate_emotion("revenge", intensity=5)
        assert result["valid"] is False

    def test_confused_rejected(self, tracker):
        """Test CONFUSED emotion is rejected"""
        result = tracker.validate_emotion("confused", intensity=5)
        assert result["valid"] is False


@pytest.mark.unit
class TestPsychologyIntegration:
    """Integration tests for psychology system"""

    @pytest.fixture
    def tracker(self, tmp_path):
        """Create psychology tracker"""
        state_file = tmp_path / "psychology_state.json"
        return PsychologyTracker(state_file=str(state_file))

    def test_losing_streak_workflow(self, tracker):
        """Test complete losing streak workflow"""
        # Start: Can trade
        result = tracker.validate_emotion("calm", intensity=3)
        assert result["allowed_to_trade"] is True

        # Loss 1: Still can trade
        tracker.record_loss()
        result = tracker.validate_emotion("calm", intensity=3)
        assert result["allowed_to_trade"] is True

        # Loss 2: Still can trade
        tracker.record_loss()
        result = tracker.validate_emotion("calm", intensity=3)
        assert result["allowed_to_trade"] is True

        # Loss 3: LOCKED OUT
        tracker.record_loss()
        result = tracker.validate_emotion("calm", intensity=3)
        assert result["allowed_to_trade"] is False
        assert "locked out" in result["message"].lower()

    def test_recovery_workflow(self, tracker):
        """Test recovery from lockout"""
        # Trigger lockout
        tracker.record_loss()
        tracker.record_loss()
        tracker.record_loss()

        assert tracker.state["locked_out"] is True

        # Wait for daily reset (simulate next day)
        tracker.reset_daily()

        # Can trade again
        result = tracker.validate_emotion("calm", intensity=3)
        assert result["allowed_to_trade"] is True

    def test_win_streak_recovery(self, tracker):
        """Test that wins don't trigger lockout"""
        # Record 10 wins
        for _ in range(10):
            tracker.record_win()

        state = tracker.get_current_state()
        assert state["consecutive_losses"] == 0
        assert state["locked_out"] is False

        # Can still trade
        result = tracker.validate_emotion("calm", intensity=3)
        assert result["allowed_to_trade"] is True

    def test_state_persistence(self, tmp_path):
        """Test that psychology state persists across restarts"""
        state_file = tmp_path / "psychology_state.json"

        # Session 1: Record losses
        tracker1 = PsychologyTracker(state_file=str(state_file))
        tracker1.record_loss()
        tracker1.record_loss()

        # Session 2: Load state
        tracker2 = PsychologyTracker(state_file=str(state_file))
        state = tracker2.get_current_state()

        # Should remember 2 losses
        assert state["consecutive_losses"] == 2
        assert state["daily_loss_count"] == 2
