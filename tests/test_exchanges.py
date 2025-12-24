#!/usr/bin/env python3
"""
🏴 Sovereign Shadow II - Exchange Connector Tests
Test exchange integrations with mocking
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from core.exchanges.base_connector import BaseExchangeConnector, OrderSide, OrderType
from core.exchanges.coinbase_connector import CoinbaseConnector
from core.exchanges.okx_connector import OKXConnector
from core.exchanges.kraken_connector import KrakenConnector
from core.exchanges.binance_us_connector import BinanceUSConnector
from core.exchanges.ledger_connector import LedgerConnector
from core.exchanges.aave_connector import AAVEConnector


class TestBaseConnector:
    """Test BaseExchangeConnector abstract class"""

    def test_order_validation_positive_amount(self, mock_exchange):
        """Test that order validation requires positive amount"""
        valid, error = mock_exchange.validate_order(
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            amount=0.1,
            price=45000.0
        )

        # Should be valid (mock has balance)
        assert valid is True

    def test_order_validation_negative_amount(self, mock_exchange):
        """Test that negative amounts are rejected"""
        valid, error = mock_exchange.validate_order(
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            amount=-0.1,  # Negative
            price=45000.0
        )

        assert valid is False
        assert "Amount must be positive" in error

    def test_order_validation_zero_amount(self, mock_exchange):
        """Test that zero amounts are rejected"""
        valid, error = mock_exchange.validate_order(
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            amount=0.0,  # Zero
            price=45000.0
        )

        assert valid is False
        assert "Amount must be positive" in error


@patch('ccxt.coinbase')
class TestCoinbaseConnector:
    """Test Coinbase Advanced Trade connector"""

    def test_connection_success(self, mock_ccxt):
        """Test successful connection to Coinbase"""
        mock_exchange = Mock()
        mock_exchange.fetch_balance.return_value = {"total": {"USDT": 10000.0}}
        mock_ccxt.return_value = mock_exchange

        connector = CoinbaseConnector(
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_passphrase"
        )

        result = connector.connect()

        assert result is True
        assert connector.connected is True
        mock_exchange.fetch_balance.assert_called_once()

    def test_connection_failure(self, mock_ccxt):
        """Test connection failure"""
        mock_exchange = Mock()
        mock_exchange.fetch_balance.side_effect = Exception("API error")
        mock_ccxt.return_value = mock_exchange

        connector = CoinbaseConnector(
            api_key="invalid_key",
            api_secret="invalid_secret",
            passphrase="invalid_passphrase"
        )

        result = connector.connect()

        assert result is False
        assert connector.connected is False

    def test_fetch_balance(self, mock_ccxt):
        """Test fetching balance from Coinbase"""
        mock_exchange = Mock()
        mock_exchange.fetch_balance.return_value = {
            "total": {
                "USDT": 10000.0,
                "BTC": 0.5,
                "ETH": 2.0
            }
        }
        mock_ccxt.return_value = mock_exchange

        connector = CoinbaseConnector("key", "secret", "passphrase")
        connector.connected = True

        balance = connector.fetch_balance()

        assert balance["USDT"] == 10000.0
        assert balance["BTC"] == 0.5
        assert balance["ETH"] == 2.0

    def test_create_order_success(self, mock_ccxt):
        """Test creating order on Coinbase"""
        mock_exchange = Mock()
        mock_exchange.create_order.return_value = {
            "id": "ORDER-123",
            "symbol": "BTC/USDT",
            "side": "buy",
            "type": "limit",
            "amount": 0.1,
            "price": 45000.0,
            "status": "open"
        }
        mock_exchange.fetch_balance.return_value = {"total": {"USDT": 10000.0}}
        mock_ccxt.return_value = mock_exchange

        connector = CoinbaseConnector("key", "secret", "passphrase")
        connector.connected = True

        order = connector.create_order(
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            amount=0.1,
            price=45000.0
        )

        assert order["success"] is True
        assert order["order_id"] == "ORDER-123"
        mock_exchange.create_order.assert_called_once()


@patch('ccxt.okx')
class TestOKXConnector:
    """Test OKX v5 API connector"""

    def test_testnet_mode_enabled(self, mock_ccxt):
        """Test that testnet mode is properly enabled"""
        mock_exchange = Mock()
        mock_ccxt.return_value = mock_exchange

        connector = OKXConnector(
            api_key="test_key",
            api_secret="test_secret",
            passphrase="test_passphrase",
            testnet=True
        )

        assert connector.testnet is True
        mock_exchange.set_sandbox_mode.assert_called_once_with(True)

    def test_fetch_ticker(self, mock_ccxt):
        """Test fetching ticker from OKX"""
        mock_exchange = Mock()
        mock_exchange.fetch_ticker.return_value = {
            "bid": 44990.0,
            "ask": 45010.0,
            "last": 45000.0
        }
        mock_ccxt.return_value = mock_exchange

        connector = OKXConnector("key", "secret", "passphrase")
        connector.connected = True

        ticker = connector.fetch_ticker("BTC/USDT")

        assert ticker["bid"] == 44990.0
        assert ticker["ask"] == 45010.0
        assert ticker["last"] == 45000.0


@patch('ccxt.kraken')
class TestKrakenConnector:
    """Test Kraken REST API connector"""

    def test_cancel_order(self, mock_ccxt):
        """Test cancelling order on Kraken"""
        mock_exchange = Mock()
        mock_exchange.cancel_order.return_value = {"status": "canceled"}
        mock_ccxt.return_value = mock_exchange

        connector = KrakenConnector("key", "secret")
        connector.connected = True

        result = connector.cancel_order("ORDER-123", "BTC/USDT")

        assert result is True
        mock_exchange.cancel_order.assert_called_once_with("ORDER-123", "BTC/USDT")


@patch('ccxt.binanceus')
class TestBinanceUSConnector:
    """Test Binance US API connector"""

    def test_fetch_order(self, mock_ccxt):
        """Test fetching order details from Binance US"""
        mock_exchange = Mock()
        mock_exchange.fetch_order.return_value = {
            "id": "ORDER-123",
            "symbol": "BTC/USDT",
            "status": "closed",
            "filled": 0.1
        }
        mock_ccxt.return_value = mock_exchange

        connector = BinanceUSConnector("key", "secret")
        connector.connected = True

        order = connector.fetch_order("ORDER-123", "BTC/USDT")

        assert order["order_id"] == "ORDER-123"
        assert order["symbol"] == "BTC/USDT"
        mock_exchange.fetch_order.assert_called_once()


class TestLedgerConnector:
    """Test Ledger cold storage connector (read-only)"""

    def test_read_only_mode(self):
        """Test that Ledger connector is read-only"""
        connector = LedgerConnector(
            etherscan_api_key="test_key",
            addresses={"ETH": "0x123", "BTC": "1A2B3C"}
        )

        # Should reject order creation
        result = connector.create_order(
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            amount=0.1,
            price=45000.0
        )

        assert result["success"] is False
        assert "read-only" in result["error"].lower()

    def test_connection_with_addresses(self):
        """Test connection with configured addresses"""
        connector = LedgerConnector(
            addresses={"ETH": "0x123", "BTC": "1A2B3C"}
        )

        result = connector.connect()

        assert result is True
        assert connector.connected is True

    def test_connection_without_addresses(self):
        """Test connection fails without addresses"""
        connector = LedgerConnector(addresses={})

        result = connector.connect()

        assert result is False

    @patch('requests.get')
    def test_fetch_eth_balance(self, mock_get):
        """Test fetching ETH balance from Etherscan"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "1",
            "result": "2000000000000000000"  # 2 ETH in wei
        }
        mock_get.return_value = mock_response

        connector = LedgerConnector(
            etherscan_api_key="test_key",
            addresses={"ETH": "0x123"}
        )
        connector.connected = True

        balance = connector._fetch_eth_balance("0x123")

        assert balance == 2.0  # 2 ETH

    @patch('requests.get')
    def test_fetch_btc_balance(self, mock_get):
        """Test fetching BTC balance from blockchain explorer"""
        mock_response = Mock()
        mock_response.text = "50000000"  # 0.5 BTC in satoshis
        mock_get.return_value = mock_response

        connector = LedgerConnector(addresses={"BTC": "1A2B3C"})
        connector.connected = True

        balance = connector._fetch_btc_balance("1A2B3C")

        assert balance == 0.5  # 0.5 BTC


class TestAAVEConnector:
    """Test AAVE v3 DeFi protocol connector"""

    def test_read_only_mode(self):
        """Test that AAVE connector is read-only"""
        with patch('exchanges.aave_connector.Web3'):
            connector = AAVEConnector(
                web3_provider_url="https://eth-mainnet.example.com",
                wallet_address="0x123"
            )

            # Should reject order creation
            result = connector.create_order(
                symbol="ETH/USDT",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                amount=1.0,
                price=2500.0
            )

            assert result["success"] is False
            assert "Web3" in result["error"]

    def test_health_factor_safe(self):
        """Test safe health factor (>= 1.5)"""
        with patch('exchanges.aave_connector.Web3'):
            connector = AAVEConnector(
                web3_provider_url="https://eth-mainnet.example.com",
                wallet_address="0x123"
            )

            # Mock get_position_summary to return safe health factor
            connector.get_position_summary = Mock(return_value={
                "health_factor": 2.5
            })

            is_safe, message = connector.is_position_safe(min_health_factor=1.5)

            assert is_safe is True
            assert "SAFE" in message
            assert "2.5" in message

    def test_health_factor_warning(self):
        """Test warning health factor (1.0 - 1.5)"""
        with patch('exchanges.aave_connector.Web3'):
            connector = AAVEConnector(
                web3_provider_url="https://eth-mainnet.example.com",
                wallet_address="0x123"
            )

            # Mock get_position_summary to return warning health factor
            connector.get_position_summary = Mock(return_value={
                "health_factor": 1.2
            })

            is_safe, message = connector.is_position_safe(min_health_factor=1.5)

            assert is_safe is False
            assert "WARNING" in message
            assert "1.2" in message

    def test_health_factor_critical(self):
        """Test critical health factor (< 1.0)"""
        with patch('exchanges.aave_connector.Web3'):
            connector = AAVEConnector(
                web3_provider_url="https://eth-mainnet.example.com",
                wallet_address="0x123"
            )

            # Mock get_position_summary to return critical health factor
            connector.get_position_summary = Mock(return_value={
                "health_factor": 0.8
            })

            is_safe, message = connector.is_position_safe()

            assert is_safe is False
            assert "CRITICAL" in message
            assert "Liquidation risk" in message


@pytest.mark.integration
@pytest.mark.requires_api
class TestExchangeIntegration:
    """Integration tests requiring real API keys (skip in CI)"""

    @pytest.mark.skip(reason="Requires real API credentials")
    def test_real_coinbase_connection(self):
        """Test real connection to Coinbase (manual testing only)"""
        import os
        connector = CoinbaseConnector(
            api_key=os.getenv("COINBASE_API_KEY"),
            api_secret=os.getenv("COINBASE_API_SECRET"),
            passphrase=os.getenv("COINBASE_PASSPHRASE")
        )

        result = connector.connect()
        assert result is True

    @pytest.mark.skip(reason="Requires real API credentials")
    def test_real_binance_us_connection(self):
        """Test real connection to Binance US (manual testing only)"""
        import os
        connector = BinanceUSConnector(
            api_key=os.getenv("BINANCE_US_API_KEY"),
            api_secret=os.getenv("BINANCE_US_API_SECRET")
        )

        result = connector.connect()
        assert result is True
