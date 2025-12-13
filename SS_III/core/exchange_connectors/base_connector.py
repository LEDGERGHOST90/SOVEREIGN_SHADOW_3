from abc import ABC, abstractmethod
import os
import ccxt

class BaseExchangeConnector(ABC):
    @abstractmethod
    def test_connection(self):
        pass

    @abstractmethod
    def fetch_balance(self):
        pass

    @abstractmethod
    def place_order(self, symbol, side, amount, price=None, params={}):
        pass
