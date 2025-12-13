from abc import ABC, abstractmethod
import os

class BaseExchangeConnector(ABC):
    def __init__(self, use_sandbox=True):
        self.use_sandbox = use_sandbox
        self.exchange = self._init_exchange()

    @abstractmethod
    def _init_exchange(self):
        """Initialize the exchange connection using ccxt or native API."""
        pass

    @abstractmethod
    def test_connection(self):
        """Test the connection to the exchange and return status."""
        pass

    @abstractmethod
    def fetch_balance(self):
        """Fetch current account balance."""
        pass

    @abstractmethod
    def fetch_ticker(self, symbol):
        """Fetch current ticker data for a symbol."""
        pass

    @abstractmethod
    def create_order(self, symbol, type, side, amount, price=None):
        """Create a new order."""
        pass
