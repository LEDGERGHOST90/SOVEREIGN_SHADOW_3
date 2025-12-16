"""
Centralized Exchange (CEX) Data Client
Fetches real-time market data from multiple exchanges:
- Coinbase, Kraken, OKX, Binance.US, CoinGecko
"""

import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class CEXClient:
    """Client for fetching real-time data from multiple exchanges."""
    
    COINBASE_BASE_URL = "https://api.coinbase.com/v2"
    COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
    KRAKEN_BASE_URL = "https://api.kraken.com/0/public"
    OKX_BASE_URL = "https://www.okx.com/api/v5"
    BINANCE_US_BASE_URL = "https://api.binance.us/api/v3"
    
    TOP_50_SYMBOLS = [
        'BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'ADA', 'DOGE', 'AVAX', 'DOT', 'MATIC',
        'LINK', 'SHIB', 'LTC', 'TRX', 'ATOM', 'UNI', 'XLM', 'ETC', 'NEAR', 'FIL',
        'APT', 'ARB', 'OP', 'IMX', 'INJ', 'AAVE', 'MKR', 'GRT', 'SAND', 'MANA',
        'AXS', 'FTM', 'ALGO', 'VET', 'HBAR', 'EOS', 'THETA', 'XTZ', 'FLOW', 'NEO',
        'CHZ', 'EGLD', 'KAVA', 'ZEC', 'DASH', 'COMP', 'SNX', 'CRV', 'ENJ', 'BAT'
    ]
    
    SYMBOL_MAPPING = {
        "BTC": {"coinbase": "BTC", "coingecko": "bitcoin", "kraken": "XXBTZUSD", "okx": "BTC-USDT", "binance": "BTCUSDT"},
        "ETH": {"coinbase": "ETH", "coingecko": "ethereum", "kraken": "XETHZUSD", "okx": "ETH-USDT", "binance": "ETHUSDT"},
        "SOL": {"coinbase": "SOL", "coingecko": "solana", "kraken": "SOLUSD", "okx": "SOL-USDT", "binance": "SOLUSDT"},
        "BNB": {"coinbase": "BNB", "coingecko": "binancecoin", "kraken": None, "okx": "BNB-USDT", "binance": "BNBUSDT"},
        "XRP": {"coinbase": "XRP", "coingecko": "ripple", "kraken": "XXRPZUSD", "okx": "XRP-USDT", "binance": "XRPUSDT"},
        "ADA": {"coinbase": "ADA", "coingecko": "cardano", "kraken": "ADAUSD", "okx": "ADA-USDT", "binance": "ADAUSDT"},
        "DOGE": {"coinbase": "DOGE", "coingecko": "dogecoin", "kraken": "XDGUSD", "okx": "DOGE-USDT", "binance": "DOGEUSDT"},
        "AVAX": {"coinbase": "AVAX", "coingecko": "avalanche-2", "kraken": "AVAXUSD", "okx": "AVAX-USDT", "binance": "AVAXUSDT"},
        "DOT": {"coinbase": "DOT", "coingecko": "polkadot", "kraken": "DOTUSD", "okx": "DOT-USDT", "binance": "DOTUSDT"},
        "MATIC": {"coinbase": "MATIC", "coingecko": "matic-network", "kraken": "MATICUSD", "okx": "MATIC-USDT", "binance": "MATICUSDT"},
        "LINK": {"coinbase": "LINK", "coingecko": "chainlink", "kraken": "LINKUSD", "okx": "LINK-USDT", "binance": "LINKUSDT"},
        "SHIB": {"coinbase": "SHIB", "coingecko": "shiba-inu", "kraken": "SHIBUSD", "okx": "SHIB-USDT", "binance": "SHIBUSDT"},
        "LTC": {"coinbase": "LTC", "coingecko": "litecoin", "kraken": "XLTCZUSD", "okx": "LTC-USDT", "binance": "LTCUSDT"},
        "TRX": {"coinbase": "TRX", "coingecko": "tron", "kraken": "TRXUSD", "okx": "TRX-USDT", "binance": "TRXUSDT"},
        "ATOM": {"coinbase": "ATOM", "coingecko": "cosmos", "kraken": "ATOMUSD", "okx": "ATOM-USDT", "binance": "ATOMUSDT"},
        "UNI": {"coinbase": "UNI", "coingecko": "uniswap", "kraken": "UNIUSD", "okx": "UNI-USDT", "binance": "UNIUSDT"},
        "XLM": {"coinbase": "XLM", "coingecko": "stellar", "kraken": "XXLMZUSD", "okx": "XLM-USDT", "binance": "XLMUSDT"},
        "ETC": {"coinbase": "ETC", "coingecko": "ethereum-classic", "kraken": "XETCZUSD", "okx": "ETC-USDT", "binance": "ETCUSDT"},
        "NEAR": {"coinbase": "NEAR", "coingecko": "near", "kraken": "NEARUSD", "okx": "NEAR-USDT", "binance": "NEARUSDT"},
        "FIL": {"coinbase": "FIL", "coingecko": "filecoin", "kraken": "FILUSD", "okx": "FIL-USDT", "binance": "FILUSDT"},
        "APT": {"coinbase": "APT", "coingecko": "aptos", "kraken": "APTUSD", "okx": "APT-USDT", "binance": "APTUSDT"},
        "ARB": {"coinbase": "ARB", "coingecko": "arbitrum", "kraken": "ARBUSD", "okx": "ARB-USDT", "binance": "ARBUSDT"},
        "OP": {"coinbase": "OP", "coingecko": "optimism", "kraken": "OPUSD", "okx": "OP-USDT", "binance": "OPUSDT"},
        "IMX": {"coinbase": "IMX", "coingecko": "immutable-x", "kraken": "IMXUSD", "okx": "IMX-USDT", "binance": "IMXUSDT"},
        "INJ": {"coinbase": "INJ", "coingecko": "injective-protocol", "kraken": "INJUSD", "okx": "INJ-USDT", "binance": "INJUSDT"},
        "AAVE": {"coinbase": "AAVE", "coingecko": "aave", "kraken": "AAVEUSD", "okx": "AAVE-USDT", "binance": "AAVEUSDT"},
        "MKR": {"coinbase": "MKR", "coingecko": "maker", "kraken": "MKRUSD", "okx": "MKR-USDT", "binance": "MKRUSDT"},
        "GRT": {"coinbase": "GRT", "coingecko": "the-graph", "kraken": "GRTUSD", "okx": "GRT-USDT", "binance": "GRTUSDT"},
        "SAND": {"coinbase": "SAND", "coingecko": "the-sandbox", "kraken": "SANDUSD", "okx": "SAND-USDT", "binance": "SANDUSDT"},
        "MANA": {"coinbase": "MANA", "coingecko": "decentraland", "kraken": "MANAUSD", "okx": "MANA-USDT", "binance": "MANAUSDT"},
        "AXS": {"coinbase": "AXS", "coingecko": "axie-infinity", "kraken": "AXSUSD", "okx": "AXS-USDT", "binance": "AXSUSDT"},
        "FTM": {"coinbase": "FTM", "coingecko": "fantom", "kraken": "FTMUSD", "okx": "FTM-USDT", "binance": "FTMUSDT"},
        "ALGO": {"coinbase": "ALGO", "coingecko": "algorand", "kraken": "ALGOUSD", "okx": "ALGO-USDT", "binance": "ALGOUSDT"},
        "VET": {"coinbase": "VET", "coingecko": "vechain", "kraken": "VETUSD", "okx": "VET-USDT", "binance": "VETUSDT"},
        "HBAR": {"coinbase": "HBAR", "coingecko": "hedera-hashgraph", "kraken": "HBARUSD", "okx": "HBAR-USDT", "binance": "HBARUSDT"},
        "EOS": {"coinbase": "EOS", "coingecko": "eos", "kraken": "EOSUSD", "okx": "EOS-USDT", "binance": "EOSUSDT"},
        "THETA": {"coinbase": "THETA", "coingecko": "theta-token", "kraken": "THETAUSD", "okx": "THETA-USDT", "binance": "THETAUSDT"},
        "XTZ": {"coinbase": "XTZ", "coingecko": "tezos", "kraken": "XTZUSD", "okx": "XTZ-USDT", "binance": "XTZUSDT"},
        "FLOW": {"coinbase": "FLOW", "coingecko": "flow", "kraken": "FLOWUSD", "okx": "FLOW-USDT", "binance": "FLOWUSDT"},
        "NEO": {"coinbase": "NEO", "coingecko": "neo", "kraken": "NEOUSD", "okx": "NEO-USDT", "binance": "NEOUSDT"},
        "CHZ": {"coinbase": "CHZ", "coingecko": "chiliz", "kraken": "CHZUSD", "okx": "CHZ-USDT", "binance": "CHZUSDT"},
        "EGLD": {"coinbase": "EGLD", "coingecko": "elrond-erd-2", "kraken": "EGLDUSD", "okx": "EGLD-USDT", "binance": "EGLDUSDT"},
        "KAVA": {"coinbase": "KAVA", "coingecko": "kava", "kraken": "KAVAUSD", "okx": "KAVA-USDT", "binance": "KAVAUSDT"},
        "ZEC": {"coinbase": "ZEC", "coingecko": "zcash", "kraken": "XZECZUSD", "okx": "ZEC-USDT", "binance": "ZECUSDT"},
        "DASH": {"coinbase": "DASH", "coingecko": "dash", "kraken": "DASHUSD", "okx": "DASH-USDT", "binance": "DASHUSDT"},
        "COMP": {"coinbase": "COMP", "coingecko": "compound-governance-token", "kraken": "COMPUSD", "okx": "COMP-USDT", "binance": "COMPUSDT"},
        "SNX": {"coinbase": "SNX", "coingecko": "havven", "kraken": "SNXUSD", "okx": "SNX-USDT", "binance": "SNXUSDT"},
        "CRV": {"coinbase": "CRV", "coingecko": "curve-dao-token", "kraken": "CRVUSD", "okx": "CRV-USDT", "binance": "CRVUSDT"},
        "ENJ": {"coinbase": "ENJ", "coingecko": "enjincoin", "kraken": "ENJUSD", "okx": "ENJ-USDT", "binance": "ENJUSDT"},
        "BAT": {"coinbase": "BAT", "coingecko": "basic-attention-token", "kraken": "BATUSD", "okx": "BAT-USDT", "binance": "BATUSDT"},
    }
    
    @classmethod
    def get_coinbase_price(cls, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current price from Coinbase."""
        mapping = cls.SYMBOL_MAPPING.get(symbol.upper(), {})
        coinbase_symbol = mapping.get("coinbase", symbol.upper())
        
        try:
            response = requests.get(
                f"{cls.COINBASE_BASE_URL}/prices/{coinbase_symbol}-USD/spot",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "symbol": symbol.upper(),
                    "price": float(data["data"]["amount"]),
                    "exchange": "Coinbase",
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            pass
        return None
    
    @classmethod
    def get_kraken_price(cls, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current price from Kraken."""
        mapping = cls.SYMBOL_MAPPING.get(symbol.upper(), {})
        kraken_pair = mapping.get("kraken")
        
        if not kraken_pair:
            return None
        
        try:
            response = requests.get(
                f"{cls.KRAKEN_BASE_URL}/Ticker",
                params={"pair": kraken_pair},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("result"):
                    ticker_data = list(data["result"].values())[0]
                    return {
                        "symbol": symbol.upper(),
                        "price": float(ticker_data["c"][0]),
                        "volume_24h": float(ticker_data["v"][1]),
                        "high_24h": float(ticker_data["h"][1]),
                        "low_24h": float(ticker_data["l"][1]),
                        "exchange": "Kraken",
                        "timestamp": datetime.utcnow().isoformat()
                    }
        except Exception as e:
            pass
        return None
    
    @classmethod
    def get_okx_price(cls, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current price from OKX."""
        mapping = cls.SYMBOL_MAPPING.get(symbol.upper(), {})
        okx_pair = mapping.get("okx")
        
        if not okx_pair:
            return None
        
        try:
            response = requests.get(
                f"{cls.OKX_BASE_URL}/market/ticker",
                params={"instId": okx_pair},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("data") and len(data["data"]) > 0:
                    ticker = data["data"][0]
                    return {
                        "symbol": symbol.upper(),
                        "price": float(ticker["last"]),
                        "volume_24h": float(ticker.get("vol24h", 0)),
                        "high_24h": float(ticker.get("high24h", 0)),
                        "low_24h": float(ticker.get("low24h", 0)),
                        "change_24h": float(ticker.get("sodUtc8", 0)) if ticker.get("sodUtc8") else 0,
                        "exchange": "OKX",
                        "timestamp": datetime.utcnow().isoformat()
                    }
        except Exception as e:
            pass
        return None
    
    @classmethod
    def get_binance_us_price(cls, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current price from Binance.US."""
        mapping = cls.SYMBOL_MAPPING.get(symbol.upper(), {})
        binance_pair = mapping.get("binance")
        
        if not binance_pair:
            return None
        
        try:
            response = requests.get(
                f"{cls.BINANCE_US_BASE_URL}/ticker/24hr",
                params={"symbol": binance_pair},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "symbol": symbol.upper(),
                    "price": float(data["lastPrice"]),
                    "volume_24h": float(data.get("volume", 0)),
                    "high_24h": float(data.get("highPrice", 0)),
                    "low_24h": float(data.get("lowPrice", 0)),
                    "change_24h": float(data.get("priceChangePercent", 0)),
                    "exchange": "Binance.US",
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            pass
        return None
    
    @classmethod
    def get_coingecko_price(cls, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current price from CoinGecko."""
        mapping = cls.SYMBOL_MAPPING.get(symbol.upper(), {})
        coingecko_id = mapping.get("coingecko")
        if not coingecko_id:
            return None
        
        try:
            response = requests.get(
                f"{cls.COINGECKO_BASE_URL}/simple/price",
                params={
                    "ids": coingecko_id,
                    "vs_currencies": "usd",
                    "include_24hr_vol": "true",
                    "include_24hr_change": "true"
                },
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if coingecko_id in data:
                    coin_data = data[coingecko_id]
                    return {
                        "symbol": symbol.upper(),
                        "price": coin_data.get("usd", 0),
                        "change_24h": coin_data.get("usd_24h_change", 0),
                        "volume_24h": coin_data.get("usd_24h_vol", 0),
                        "exchange": "CoinGecko",
                        "timestamp": datetime.utcnow().isoformat()
                    }
        except Exception as e:
            pass
        return None
    
    @classmethod
    def get_all_exchange_prices(cls, symbol: str) -> Dict[str, Any]:
        """Get price from all exchanges for a single symbol."""
        results = {
            "symbol": symbol.upper(),
            "exchanges": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        exchange_methods = [
            ("Coinbase", cls.get_coinbase_price),
            ("Kraken", cls.get_kraken_price),
            ("OKX", cls.get_okx_price),
            ("Binance.US", cls.get_binance_us_price),
            ("CoinGecko", cls.get_coingecko_price),
        ]
        
        for exchange_name, method in exchange_methods:
            try:
                data = method(symbol)
                if data:
                    results["exchanges"][exchange_name] = data
            except:
                pass
        
        prices = [d["price"] for d in results["exchanges"].values() if d and d.get("price")]
        if prices:
            results["avg_price"] = sum(prices) / len(prices)
            results["min_price"] = min(prices)
            results["max_price"] = max(prices)
            results["spread"] = results["max_price"] - results["min_price"]
            results["spread_pct"] = (results["spread"] / results["avg_price"]) * 100 if results["avg_price"] else 0
        
        return results
    
    @classmethod
    def get_top_50_multi_exchange(cls) -> List[Dict[str, Any]]:
        """Get top 50 crypto prices from all exchanges."""
        results = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(cls.get_all_exchange_prices, symbol): symbol for symbol in cls.TOP_50_SYMBOLS}
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result and result.get("exchanges"):
                        results.append(result)
                except:
                    pass
        
        results.sort(key=lambda x: cls.TOP_50_SYMBOLS.index(x["symbol"]) if x["symbol"] in cls.TOP_50_SYMBOLS else 999)
        return results
    
    @classmethod
    def get_exchange_comparison(cls, symbols: List[str] = None) -> Dict[str, Any]:
        """Get price comparison across exchanges for given symbols."""
        if symbols is None:
            symbols = cls.TOP_50_SYMBOLS[:10]
        
        comparison = {
            "symbols": [],
            "exchanges": ["Coinbase", "Kraken", "OKX", "Binance.US", "CoinGecko"],
            "data": [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for symbol in symbols:
            all_prices = cls.get_all_exchange_prices(symbol)
            if all_prices.get("exchanges"):
                comparison["symbols"].append(symbol)
                row = {"symbol": symbol}
                for exchange in comparison["exchanges"]:
                    ex_data = all_prices["exchanges"].get(exchange, {})
                    row[exchange] = ex_data.get("price") if ex_data else None
                row["avg"] = all_prices.get("avg_price")
                row["spread_pct"] = all_prices.get("spread_pct")
                comparison["data"].append(row)
        
        return comparison
    
    @classmethod
    def get_coingecko_market_data(cls, symbols: List[str]) -> List[Dict[str, Any]]:
        """Get market data from CoinGecko for multiple symbols."""
        coingecko_ids = []
        symbol_map = {}
        
        for sym in symbols:
            mapping = cls.SYMBOL_MAPPING.get(sym.upper(), {})
            cg_id = mapping.get("coingecko")
            if cg_id:
                coingecko_ids.append(cg_id)
                symbol_map[cg_id] = sym.upper()
        
        if not coingecko_ids:
            return []
        
        try:
            response = requests.get(
                f"{cls.COINGECKO_BASE_URL}/coins/markets",
                params={
                    "vs_currency": "usd",
                    "ids": ",".join(coingecko_ids),
                    "order": "market_cap_desc",
                    "sparkline": "false"
                },
                timeout=15
            )
            if response.status_code == 200:
                data = response.json()
                results = []
                for coin in data:
                    symbol = symbol_map.get(coin["id"], coin["symbol"].upper())
                    results.append({
                        "symbol": symbol,
                        "price": coin.get("current_price", 0),
                        "change_24h": coin.get("price_change_percentage_24h", 0) or 0,
                        "high_24h": coin.get("high_24h", 0),
                        "low_24h": coin.get("low_24h", 0),
                        "volume_24h": coin.get("total_volume", 0),
                        "market_cap": coin.get("market_cap", 0),
                        "trades_24h": 0
                    })
                return results
        except Exception as e:
            print(f"CoinGecko market data error: {e}")
        return []
    
    @classmethod
    def get_multi_exchange_prices(cls, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get prices from multiple exchanges for comparison."""
        results = {}
        
        for symbol in symbols:
            coinbase_price = cls.get_coinbase_price(symbol)
            coingecko_price = cls.get_coingecko_price(symbol)
            
            results[symbol] = {
                "coinbase": coinbase_price,
                "coingecko": coingecko_price,
                "price_difference": None,
                "price_difference_pct": None
            }
            
            if coinbase_price and coingecko_price:
                diff = coingecko_price["price"] - coinbase_price["price"]
                avg_price = (coinbase_price["price"] + coingecko_price["price"]) / 2
                diff_pct = (diff / avg_price) * 100 if avg_price else 0
                results[symbol]["price_difference"] = round(diff, 2)
                results[symbol]["price_difference_pct"] = round(diff_pct, 4)
        
        return results
    
    @classmethod
    def get_market_overview(cls, symbols: List[str] = None) -> List[Dict[str, Any]]:
        """Get market overview for multiple symbols using CoinGecko."""
        if symbols is None:
            symbols = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA"]
        
        return cls.get_coingecko_market_data(symbols)
    
    @classmethod  
    def get_ticker(cls, symbol: str) -> Optional[Dict[str, Any]]:
        """Get ticker data for a symbol."""
        market_data = cls.get_coingecko_market_data([symbol])
        if market_data:
            ticker = market_data[0]
            return {
                "symbol": ticker["symbol"],
                "exchange": "coingecko",
                "price": ticker["price"],
                "price_change_24h": ticker.get("price", 0) * (ticker.get("change_24h", 0) / 100),
                "price_change_pct_24h": ticker.get("change_24h", 0),
                "high_24h": ticker.get("high_24h", 0),
                "low_24h": ticker.get("low_24h", 0),
                "volume_24h": ticker.get("volume_24h", 0),
                "quote_volume_24h": ticker.get("volume_24h", 0),
                "trades_24h": 0,
                "timestamp": datetime.utcnow().isoformat()
            }
        return None
    
    @classmethod
    def get_simulated_orderbook(cls, symbol: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """Generate simulated orderbook based on current price."""
        price_data = cls.get_coinbase_price(symbol) or cls.get_coingecko_price(symbol)
        if not price_data:
            return None
        
        current_price = price_data["price"]
        spread_pct = 0.0005
        
        bids = []
        asks = []
        
        for i in range(limit):
            bid_price = current_price * (1 - spread_pct * (i + 1))
            ask_price = current_price * (1 + spread_pct * (i + 1))
            qty = round(0.1 + (0.5 * (limit - i) / limit), 4)
            
            bids.append([round(bid_price, 2), qty])
            asks.append([round(ask_price, 2), qty])
        
        best_bid = bids[0][0]
        best_ask = asks[0][0]
        spread = best_ask - best_bid
        
        return {
            "symbol": symbol.upper(),
            "exchange": "simulated",
            "bids": bids,
            "asks": asks,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "spread": round(spread, 2),
            "spread_pct": round((spread / best_bid) * 100, 4),
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Simulated orderbook based on current market price"
        }
    
    @classmethod
    def get_simulated_trades(cls, symbol: str, limit: int = 20) -> Optional[List[Dict[str, Any]]]:
        """Generate simulated recent trades based on current price."""
        price_data = cls.get_coinbase_price(symbol) or cls.get_coingecko_price(symbol)
        if not price_data:
            return None
        
        import random
        current_price = price_data["price"]
        trades = []
        
        for i in range(limit):
            price_variance = random.uniform(-0.002, 0.002)
            trade_price = current_price * (1 + price_variance)
            qty = round(random.uniform(0.01, 2.0), 4)
            side = random.choice(["buy", "sell"])
            
            time_offset = i * random.randint(5, 30)
            trade_time = datetime.utcnow()
            
            trades.append({
                "id": str(int(time.time() * 1000) - i),
                "price": round(trade_price, 2),
                "quantity": qty,
                "value": round(trade_price * qty, 2),
                "is_buyer_maker": side == "sell",
                "side": side,
                "timestamp": trade_time.isoformat()
            })
        
        return trades
    
    @classmethod
    def get_exchange_status(cls) -> Dict[str, Any]:
        """Check exchange connectivity status."""
        status = {
            "Coinbase": {"connected": False, "url": cls.COINBASE_BASE_URL},
            "Kraken": {"connected": False, "url": cls.KRAKEN_BASE_URL},
            "OKX": {"connected": False, "url": cls.OKX_BASE_URL},
            "Binance.US": {"connected": False, "url": cls.BINANCE_US_BASE_URL},
            "CoinGecko": {"connected": False, "url": cls.COINGECKO_BASE_URL},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            response = requests.get(f"{cls.COINBASE_BASE_URL}/time", timeout=3)
            status["Coinbase"]["connected"] = response.status_code == 200
        except:
            pass
        
        try:
            response = requests.get(f"{cls.KRAKEN_BASE_URL}/Time", timeout=3)
            status["Kraken"]["connected"] = response.status_code == 200
        except:
            pass
        
        try:
            response = requests.get(f"{cls.OKX_BASE_URL}/public/time", timeout=3)
            status["OKX"]["connected"] = response.status_code == 200
        except:
            pass
        
        try:
            response = requests.get(f"{cls.BINANCE_US_BASE_URL}/time", timeout=3)
            status["Binance.US"]["connected"] = response.status_code == 200
        except:
            pass
        
        try:
            response = requests.get(f"{cls.COINGECKO_BASE_URL}/ping", timeout=3)
            status["CoinGecko"]["connected"] = response.status_code == 200
        except:
            pass
        
        return status
