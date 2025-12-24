#!/usr/bin/env python3
"""
🏴 Sovereign Shadow II - CLI Tests
Test command-line interface
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from bin.trading_cli import TradingCLI
from argparse import Namespace


class TestTradingCLI:
    """Test TradingCLI interface"""

    @pytest.fixture
    def cli(self, mock_exchange):
        """Create CLI instance with mock exchange"""
        with patch('cli.trading_cli.master_trading_system') as mock_system:
            mock_system.return_value = Mock()
            cli = TradingCLI()
            cli.system.exchange = mock_exchange
            return cli

    def test_validate_trade_valid_json(self, cli, sample_trade_request):
        """Test validate-trade command with valid JSON"""
        args = Namespace(
            symbol=sample_trade_request["symbol"],
            trade_type=sample_trade_request["trade_type"],
            entry_price=sample_trade_request["entry_price"],
            stop_loss=sample_trade_request["stop_loss"],
            take_profit=sample_trade_request["take_profit"],
            account_size=sample_trade_request["account_size"],
            emotion_state=sample_trade_request["emotion_state"],
            emotion_intensity=sample_trade_request["emotion_intensity"],
            market_context=json.dumps(sample_trade_request["market_context"]),
            notes=sample_trade_request.get("notes")
        )

        # Mock pre_trade_check to return success
        cli.system.pre_trade_check = Mock(return_value={
            "approved": True,
            "validation_id": "VAL-123",
            "message": "Trade approved"
        })

        result = cli.validate_trade(args)

        assert result["success"] is True
        assert "validation_id" in result
        cli.system.pre_trade_check.assert_called_once()

    def test_validate_trade_invalid_json(self, cli):
        """Test validate-trade with invalid market_context JSON"""
        args = Namespace(
            symbol="BTC/USDT",
            trade_type="long",
            entry_price=45000.0,
            stop_loss=44000.0,
            take_profit=48000.0,
            account_size=10000.0,
            emotion_state="calm",
            emotion_intensity=3,
            market_context="{invalid json}",  # Malformed JSON
            notes=None
        )

        result = cli.validate_trade(args)

        assert result["success"] is False
        assert "Invalid market_context JSON" in result["error"]

    def test_execute_trade_success(self, cli, mock_exchange):
        """Test execute-trade command success"""
        args = Namespace(
            validation_id="VAL-123",
            exchange="coinbase"
        )

        # Mock execute_trade to return success
        cli.system.execute_trade = Mock(return_value={
            "success": True,
            "trade_id": "TRADE-001",
            "order_id": "ORDER-123",
            "message": "Trade executed successfully"
        })

        result = cli.execute_trade(args)

        assert result["success"] is True
        assert result["trade_id"] == "TRADE-001"
        cli.system.execute_trade.assert_called_once_with("VAL-123", "coinbase")

    def test_execute_trade_failure(self, cli):
        """Test execute-trade command failure"""
        args = Namespace(
            validation_id="VAL-INVALID",
            exchange="coinbase"
        )

        # Mock execute_trade to return failure
        cli.system.execute_trade = Mock(return_value={
            "success": False,
            "error": "Validation ID not found"
        })

        result = cli.execute_trade(args)

        assert result["success"] is False
        assert "Validation ID not found" in result["error"]

    def test_close_trade_success(self, cli):
        """Test close-trade command success"""
        args = Namespace(
            trade_id="TRADE-001",
            exit_price=48000.0,
            close_reason="take_profit",
            notes="Hit TP"
        )

        # Mock close_trade to return success
        cli.system.close_trade = Mock(return_value={
            "success": True,
            "pnl": 300.0,
            "pnl_percent": 3.0,
            "outcome": "winner"
        })

        result = cli.close_trade(args)

        assert result["success"] is True
        assert result["pnl"] == 300.0
        assert result["outcome"] == "winner"

    def test_dashboard_display(self, cli, capsys):
        """Test dashboard command displays system status"""
        args = Namespace()

        # Mock get_system_status
        cli.system.get_system_status = Mock(return_value={
            "account_size": 10000.0,
            "total_trades": 10,
            "win_rate": 60.0,
            "total_pnl": 500.0,
            "psychology_state": {
                "emotion": "calm",
                "consecutive_losses": 0,
                "locked_out": False
            },
            "active_trades": []
        })

        cli.dashboard(args)

        # Check that dashboard was displayed (output contains key info)
        captured = capsys.readouterr()
        assert "SOVEREIGN SHADOW II" in captured.out or "Dashboard" in captured.out

    def test_status_json_output(self, cli):
        """Test status command returns JSON"""
        args = Namespace()

        # Mock get_system_status
        cli.system.get_system_status = Mock(return_value={
            "account_size": 10000.0,
            "total_trades": 10,
            "win_rate": 60.0
        })

        result = cli.status(args)

        assert isinstance(result, dict)
        assert result["account_size"] == 10000.0
        assert result["total_trades"] == 10


class TestCLIArguments:
    """Test CLI argument parsing"""

    def test_validate_trade_required_args(self):
        """Test that validate-trade requires all necessary arguments"""
        # This would test argparse configuration
        # Implementation depends on how TradingCLI.main() is structured
        pass

    def test_execute_trade_required_args(self):
        """Test that execute-trade requires validation_id and exchange"""
        pass

    def test_close_trade_required_args(self):
        """Test that close-trade requires trade_id, exit_price, and reason"""
        pass


class TestCLIErrorHandling:
    """Test CLI error handling"""

    def test_missing_validation_id(self, cli):
        """Test error when validation_id is missing"""
        args = Namespace(
            validation_id=None,
            exchange="coinbase"
        )

        result = cli.execute_trade(args)

        assert result["success"] is False
        assert "validation_id" in result.get("error", "").lower()

    def test_invalid_exchange(self, cli):
        """Test error when invalid exchange is specified"""
        args = Namespace(
            validation_id="VAL-123",
            exchange="invalid_exchange"
        )

        cli.system.execute_trade = Mock(return_value={
            "success": False,
            "error": "Invalid exchange: invalid_exchange"
        })

        result = cli.execute_trade(args)

        assert result["success"] is False
        assert "Invalid exchange" in result["error"]

    def test_negative_position_size(self, cli, sample_trade_request):
        """Test error when position size is negative"""
        args = Namespace(
            validation_id="VAL-123",
            symbol="BTC/USDT",
            trade_type="long",
            entry_price=45000.0,
            stop_loss=44000.0,
            take_profit=48000.0,
            position_size=-0.1,  # Negative
            exchange="coinbase"
        )

        # This should be caught by validation
        result = cli.validate_trade(args)

        # Expect validation error
        assert result["success"] is False or "error" in result


@pytest.mark.unit
class TestCLIIntegration:
    """Integration tests for CLI commands"""

    def test_full_trade_workflow(self, cli):
        """Test complete trade workflow: validate → execute → close"""
        # Step 1: Validate trade
        validate_args = Namespace(
            symbol="BTC/USDT",
            trade_type="long",
            entry_price=45000.0,
            stop_loss=44000.0,
            take_profit=48000.0,
            account_size=10000.0,
            emotion_state="calm",
            emotion_intensity=3,
            market_context=json.dumps({
                "trend_4h": "bullish",
                "trend_15m": "bullish"
            }),
            notes="Test trade"
        )

        cli.system.pre_trade_check = Mock(return_value={
            "approved": True,
            "validation_id": "VAL-123",
            "message": "Trade approved"
        })

        validate_result = cli.validate_trade(validate_args)
        assert validate_result["success"] is True
        validation_id = validate_result["validation_id"]

        # Step 2: Execute trade
        execute_args = Namespace(
            validation_id=validation_id,
            exchange="coinbase"
        )

        cli.system.execute_trade = Mock(return_value={
            "success": True,
            "trade_id": "TRADE-001",
            "order_id": "ORDER-123"
        })

        execute_result = cli.execute_trade(execute_args)
        assert execute_result["success"] is True
        trade_id = execute_result["trade_id"]

        # Step 3: Close trade
        close_args = Namespace(
            trade_id=trade_id,
            exit_price=48000.0,
            close_reason="take_profit",
            notes="Reached TP"
        )

        cli.system.close_trade = Mock(return_value={
            "success": True,
            "pnl": 300.0,
            "pnl_percent": 3.0,
            "outcome": "winner"
        })

        close_result = cli.close_trade(close_args)
        assert close_result["success"] is True
        assert close_result["outcome"] == "winner"
