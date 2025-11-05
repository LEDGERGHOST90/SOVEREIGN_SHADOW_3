#!/usr/bin/env python3
"""
🏴 Sovereign Shadow II - Journal Tests
Test LEDGER//ECHO trade journaling and P&L tracking
"""

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch
from modules.trade_journal import TradeJournal


class TestTradeJournal:
    """Test TradeJournal logging and analytics"""

    @pytest.fixture
    def journal(self, temp_journal_file):
        """Create trade journal with temp file"""
        return TradeJournal(journal_file=temp_journal_file)

    def test_log_trade_entry(self, journal):
        """Test logging a new trade entry"""
        trade_id = journal.log_entry(
            symbol="BTC/USDT",
            side="long",
            entry_price=45000.0,
            stop_loss=44000.0,
            take_profit=48000.0,
            position_size=0.1,
            notes="NetworkChuck 4H/15M setup"
        )

        assert trade_id is not None
        assert trade_id.startswith("TRADE-")

        # Verify trade was logged
        trade = journal.get_trade(trade_id)
        assert trade["symbol"] == "BTC/USDT"
        assert trade["entry_price"] == 45000.0
        assert trade["status"] == "open"

    def test_log_trade_exit_winner(self, journal):
        """Test logging a winning trade exit"""
        # Enter trade
        trade_id = journal.log_entry(
            symbol="BTC/USDT",
            side="long",
            entry_price=45000.0,
            stop_loss=44000.0,
            take_profit=48000.0,
            position_size=0.1
        )

        # Exit at profit
        result = journal.log_exit(
            trade_id=trade_id,
            exit_price=48000.0,
            close_reason="take_profit",
            notes="Hit TP target"
        )

        assert result["success"] is True
        assert result["pnl"] > 0
        assert result["outcome"] == "winner"

        # Verify trade was updated
        trade = journal.get_trade(trade_id)
        assert trade["status"] == "closed"
        assert trade["exit_price"] == 48000.0
        assert trade["pnl"] > 0

    def test_log_trade_exit_loser(self, journal):
        """Test logging a losing trade exit"""
        # Enter trade
        trade_id = journal.log_entry(
            symbol="BTC/USDT",
            side="long",
            entry_price=45000.0,
            stop_loss=44000.0,
            take_profit=48000.0,
            position_size=0.1
        )

        # Exit at loss
        result = journal.log_exit(
            trade_id=trade_id,
            exit_price=44000.0,
            close_reason="stop_loss",
            notes="Hit SL"
        )

        assert result["success"] is True
        assert result["pnl"] < 0
        assert result["outcome"] == "loser"

    def test_calculate_pnl_long(self, journal):
        """Test P&L calculation for LONG trade"""
        pnl = journal.calculate_pnl(
            side="long",
            entry_price=45000.0,
            exit_price=48000.0,
            position_size=0.1
        )

        # P&L = (48000 - 45000) × 0.1 = $300
        assert pnl == 300.0

    def test_calculate_pnl_short(self, journal):
        """Test P&L calculation for SHORT trade"""
        pnl = journal.calculate_pnl(
            side="short",
            entry_price=45000.0,
            exit_price=42000.0,
            position_size=0.1
        )

        # P&L = (45000 - 42000) × 0.1 = $300
        assert pnl == 300.0

    def test_calculate_pnl_percent(self, journal):
        """Test P&L percentage calculation"""
        pnl_percent = journal.calculate_pnl_percent(
            pnl=300.0,
            entry_price=45000.0,
            position_size=0.1
        )

        # % = (300 / (45000 × 0.1)) × 100 = 6.67%
        assert abs(pnl_percent - 6.67) < 0.1

    def test_get_all_trades(self, journal):
        """Test retrieving all trades"""
        # Log 3 trades
        trade_ids = []
        for i in range(3):
            trade_id = journal.log_entry(
                symbol=f"BTC/USDT",
                side="long",
                entry_price=45000.0 + (i * 100),
                stop_loss=44000.0,
                take_profit=48000.0,
                position_size=0.1
            )
            trade_ids.append(trade_id)

        # Get all trades
        all_trades = journal.get_all_trades()

        assert len(all_trades) == 3
        assert all(t["trade_id"] in trade_ids for t in all_trades)

    def test_get_open_trades(self, journal):
        """Test retrieving only open trades"""
        # Log 2 trades
        trade_id_1 = journal.log_entry(
            symbol="BTC/USDT", side="long", entry_price=45000.0,
            stop_loss=44000.0, take_profit=48000.0, position_size=0.1
        )
        trade_id_2 = journal.log_entry(
            symbol="ETH/USDT", side="long", entry_price=2500.0,
            stop_loss=2450.0, take_profit=2600.0, position_size=2.0
        )

        # Close first trade
        journal.log_exit(trade_id_1, 48000.0, "take_profit")

        # Get open trades
        open_trades = journal.get_open_trades()

        assert len(open_trades) == 1
        assert open_trades[0]["trade_id"] == trade_id_2


class TestTradeAnalytics:
    """Test trade analytics and statistics"""

    @pytest.fixture
    def journal(self, temp_journal_file):
        """Create trade journal"""
        return TradeJournal(journal_file=temp_journal_file)

    def test_calculate_win_rate(self, journal):
        """Test win rate calculation"""
        # Log 10 trades: 6 winners, 4 losers
        for i in range(6):
            trade_id = journal.log_entry(
                symbol="BTC/USDT", side="long", entry_price=45000.0,
                stop_loss=44000.0, take_profit=48000.0, position_size=0.1
            )
            journal.log_exit(trade_id, 48000.0, "take_profit")  # Winner

        for i in range(4):
            trade_id = journal.log_entry(
                symbol="BTC/USDT", side="long", entry_price=45000.0,
                stop_loss=44000.0, take_profit=48000.0, position_size=0.1
            )
            journal.log_exit(trade_id, 44000.0, "stop_loss")  # Loser

        stats = journal.get_statistics()

        assert stats["total_trades"] == 10
        assert stats["win_rate"] == 60.0  # 6/10 = 60%

    def test_calculate_total_pnl(self, journal):
        """Test total P&L calculation"""
        # Log 3 trades
        for i, exit_price in enumerate([48000.0, 47000.0, 44000.0]):
            trade_id = journal.log_entry(
                symbol="BTC/USDT", side="long", entry_price=45000.0,
                stop_loss=44000.0, take_profit=48000.0, position_size=0.1
            )
            journal.log_exit(trade_id, exit_price, "manual")

        stats = journal.get_statistics()

        # Trade 1: +$300, Trade 2: +$200, Trade 3: -$100 = +$400 total
        assert stats["total_pnl"] == 400.0

    def test_calculate_average_win(self, journal):
        """Test average win calculation"""
        # Log 3 winning trades
        for exit_price in [48000.0, 47000.0, 46000.0]:
            trade_id = journal.log_entry(
                symbol="BTC/USDT", side="long", entry_price=45000.0,
                stop_loss=44000.0, take_profit=48000.0, position_size=0.1
            )
            journal.log_exit(trade_id, exit_price, "take_profit")

        stats = journal.get_statistics()

        # Wins: $300, $200, $100 = Average $200
        assert stats["average_win"] == 200.0

    def test_calculate_average_loss(self, journal):
        """Test average loss calculation"""
        # Log 3 losing trades
        for exit_price in [44000.0, 43500.0, 43000.0]:
            trade_id = journal.log_entry(
                symbol="BTC/USDT", side="long", entry_price=45000.0,
                stop_loss=44000.0, take_profit=48000.0, position_size=0.1
            )
            journal.log_exit(trade_id, exit_price, "stop_loss")

        stats = journal.get_statistics()

        # Losses: -$100, -$150, -$200 = Average -$150
        assert stats["average_loss"] == -150.0

    def test_calculate_profit_factor(self, journal):
        """Test profit factor calculation"""
        # Log 2 winners and 2 losers
        for exit_price in [48000.0, 47000.0]:  # Winners: +$300, +$200
            trade_id = journal.log_entry(
                symbol="BTC/USDT", side="long", entry_price=45000.0,
                stop_loss=44000.0, take_profit=48000.0, position_size=0.1
            )
            journal.log_exit(trade_id, exit_price, "take_profit")

        for exit_price in [44000.0, 43000.0]:  # Losers: -$100, -$200
            trade_id = journal.log_entry(
                symbol="BTC/USDT", side="long", entry_price=45000.0,
                stop_loss=44000.0, take_profit=48000.0, position_size=0.1
            )
            journal.log_exit(trade_id, exit_price, "stop_loss")

        stats = journal.get_statistics()

        # Profit factor = Total wins / Total losses = $500 / $300 = 1.67
        assert abs(stats["profit_factor"] - 1.67) < 0.1

    def test_get_statistics_empty_journal(self, journal):
        """Test statistics with no trades"""
        stats = journal.get_statistics()

        assert stats["total_trades"] == 0
        assert stats["win_rate"] == 0.0
        assert stats["total_pnl"] == 0.0


class TestTradeFiltering:
    """Test trade filtering and queries"""

    @pytest.fixture
    def journal(self, temp_journal_file):
        """Create trade journal"""
        return TradeJournal(journal_file=temp_journal_file)

    def test_filter_by_symbol(self, journal):
        """Test filtering trades by symbol"""
        # Log trades for different symbols
        journal.log_entry("BTC/USDT", "long", 45000.0, 44000.0, 48000.0, 0.1)
        journal.log_entry("ETH/USDT", "long", 2500.0, 2450.0, 2600.0, 2.0)
        journal.log_entry("BTC/USDT", "long", 46000.0, 45000.0, 49000.0, 0.1)

        btc_trades = journal.filter_trades(symbol="BTC/USDT")

        assert len(btc_trades) == 2
        assert all(t["symbol"] == "BTC/USDT" for t in btc_trades)

    def test_filter_by_outcome(self, journal):
        """Test filtering trades by outcome"""
        # Log winners and losers
        trade_id_1 = journal.log_entry("BTC/USDT", "long", 45000.0, 44000.0, 48000.0, 0.1)
        journal.log_exit(trade_id_1, 48000.0, "take_profit")  # Winner

        trade_id_2 = journal.log_entry("BTC/USDT", "long", 45000.0, 44000.0, 48000.0, 0.1)
        journal.log_exit(trade_id_2, 44000.0, "stop_loss")  # Loser

        winners = journal.filter_trades(outcome="winner")
        losers = journal.filter_trades(outcome="loser")

        assert len(winners) == 1
        assert len(losers) == 1

    def test_filter_by_date_range(self, journal):
        """Test filtering trades by date range"""
        # This would require mocking datetime
        pass


@pytest.mark.unit
class TestJournalPersistence:
    """Test journal persistence and data integrity"""

    def test_journal_saves_to_file(self, temp_journal_file):
        """Test that journal saves to file"""
        journal = TradeJournal(journal_file=temp_journal_file)

        trade_id = journal.log_entry(
            symbol="BTC/USDT", side="long", entry_price=45000.0,
            stop_loss=44000.0, take_profit=48000.0, position_size=0.1
        )

        # Verify file exists and contains data
        with open(temp_journal_file, 'r') as f:
            data = json.load(f)

        assert len(data) == 1
        assert data[0]["trade_id"] == trade_id

    def test_journal_loads_from_file(self, temp_journal_file):
        """Test that journal loads from existing file"""
        # Session 1: Log trade
        journal1 = TradeJournal(journal_file=temp_journal_file)
        trade_id = journal1.log_entry(
            symbol="BTC/USDT", side="long", entry_price=45000.0,
            stop_loss=44000.0, take_profit=48000.0, position_size=0.1
        )

        # Session 2: Load journal
        journal2 = TradeJournal(journal_file=temp_journal_file)
        all_trades = journal2.get_all_trades()

        assert len(all_trades) == 1
        assert all_trades[0]["trade_id"] == trade_id
