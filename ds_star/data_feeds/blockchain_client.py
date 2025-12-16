"""
Blockchain Data Client
Fetches on-chain data from public APIs (Etherscan, Blockchain.com, etc.)
"""

import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import os


class BlockchainClient:
    """Client for fetching on-chain blockchain data."""
    
    ETHERSCAN_BASE = "https://api.etherscan.io/api"
    BLOCKCHAIR_BASE = "https://api.blockchair.com"
    BLOCKCHAIN_INFO_BASE = "https://blockchain.info"
    
    @classmethod
    def _get_etherscan_key(cls) -> Optional[str]:
        """Get Etherscan API key from environment (optional for basic calls)."""
        return os.environ.get("ETHERSCAN_API_KEY", "")
    
    @classmethod
    def get_eth_gas_prices(cls) -> Dict[str, Any]:
        """Get current Ethereum gas prices."""
        try:
            response = requests.get(
                cls.ETHERSCAN_BASE,
                params={
                    "module": "gastracker",
                    "action": "gasoracle",
                    "apikey": cls._get_etherscan_key()
                },
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1" and "result" in data:
                    result = data["result"]
                    return {
                        "success": True,
                        "safe_gas": float(result.get("SafeGasPrice", 0)),
                        "propose_gas": float(result.get("ProposeGasPrice", 0)),
                        "fast_gas": float(result.get("FastGasPrice", 0)),
                        "base_fee": float(result.get("suggestBaseFee", 0)),
                        "timestamp": datetime.utcnow().isoformat()
                    }
        except Exception as e:
            print(f"Gas price fetch error: {e}")
        
        return {
            "success": False,
            "safe_gas": 0,
            "propose_gas": 0,
            "fast_gas": 0,
            "base_fee": 0,
            "timestamp": datetime.utcnow().isoformat(),
            "error": "Unable to fetch gas prices"
        }
    
    @classmethod
    def get_eth_price(cls) -> Dict[str, Any]:
        """Get current ETH price from Etherscan."""
        try:
            response = requests.get(
                cls.ETHERSCAN_BASE,
                params={
                    "module": "stats",
                    "action": "ethprice",
                    "apikey": cls._get_etherscan_key()
                },
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1" and "result" in data:
                    result = data["result"]
                    return {
                        "success": True,
                        "eth_usd": float(result.get("ethusd", 0)),
                        "eth_btc": float(result.get("ethbtc", 0)),
                        "eth_usd_timestamp": result.get("ethusd_timestamp"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
        except Exception as e:
            print(f"ETH price fetch error: {e}")
        
        return {"success": False, "error": "Unable to fetch ETH price"}
    
    @classmethod
    def get_eth_supply(cls) -> Dict[str, Any]:
        """Get current ETH total supply."""
        try:
            response = requests.get(
                cls.ETHERSCAN_BASE,
                params={
                    "module": "stats",
                    "action": "ethsupply",
                    "apikey": cls._get_etherscan_key()
                },
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1" and "result" in data:
                    supply_wei = int(data["result"])
                    supply_eth = supply_wei / 1e18
                    return {
                        "success": True,
                        "total_supply_eth": supply_eth,
                        "total_supply_formatted": f"{supply_eth:,.2f} ETH",
                        "timestamp": datetime.utcnow().isoformat()
                    }
        except Exception as e:
            print(f"ETH supply fetch error: {e}")
        
        return {"success": False, "error": "Unable to fetch ETH supply"}
    
    @classmethod
    def get_address_balance(cls, address: str, chain: str = "ethereum") -> Dict[str, Any]:
        """Get address balance for a given blockchain."""
        if chain == "ethereum":
            return cls._get_eth_address_balance(address)
        elif chain == "bitcoin":
            return cls._get_btc_address_balance(address)
        else:
            return {"success": False, "error": f"Unsupported chain: {chain}"}
    
    @classmethod
    def _get_eth_address_balance(cls, address: str) -> Dict[str, Any]:
        """Get ETH balance for an address."""
        try:
            response = requests.get(
                cls.ETHERSCAN_BASE,
                params={
                    "module": "account",
                    "action": "balance",
                    "address": address,
                    "tag": "latest",
                    "apikey": cls._get_etherscan_key()
                },
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1":
                    balance_wei = int(data["result"])
                    balance_eth = balance_wei / 1e18
                    return {
                        "success": True,
                        "chain": "ethereum",
                        "address": address,
                        "balance": balance_eth,
                        "balance_formatted": f"{balance_eth:.6f} ETH",
                        "timestamp": datetime.utcnow().isoformat()
                    }
        except Exception as e:
            print(f"ETH balance fetch error: {e}")
        
        return {"success": False, "error": "Unable to fetch ETH balance"}
    
    @classmethod
    def _get_btc_address_balance(cls, address: str) -> Dict[str, Any]:
        """Get BTC balance for an address."""
        try:
            response = requests.get(
                f"{cls.BLOCKCHAIN_INFO_BASE}/balance",
                params={"active": address},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if address in data:
                    balance_satoshi = data[address].get("final_balance", 0)
                    balance_btc = balance_satoshi / 1e8
                    return {
                        "success": True,
                        "chain": "bitcoin",
                        "address": address,
                        "balance": balance_btc,
                        "balance_formatted": f"{balance_btc:.8f} BTC",
                        "total_received": data[address].get("total_received", 0) / 1e8,
                        "n_tx": data[address].get("n_tx", 0),
                        "timestamp": datetime.utcnow().isoformat()
                    }
        except Exception as e:
            print(f"BTC balance fetch error: {e}")
        
        return {"success": False, "error": "Unable to fetch BTC balance"}
    
    @classmethod
    def get_recent_eth_blocks(cls, count: int = 5) -> List[Dict[str, Any]]:
        """Get recent Ethereum blocks using Etherscan."""
        try:
            response = requests.get(
                cls.ETHERSCAN_BASE,
                params={
                    "module": "proxy",
                    "action": "eth_blockNumber",
                    "apikey": cls._get_etherscan_key()
                },
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                latest_block = int(data.get("result", "0"), 16)
                
                blocks = []
                for i in range(count):
                    block_num = latest_block - i
                    block_info = cls._get_block_info(block_num)
                    if block_info:
                        blocks.append(block_info)
                
                return blocks
        except Exception as e:
            print(f"Recent blocks fetch error: {e}")
        
        return []
    
    @classmethod
    def _get_block_info(cls, block_number: int) -> Optional[Dict[str, Any]]:
        """Get info for a specific Ethereum block."""
        try:
            response = requests.get(
                cls.ETHERSCAN_BASE,
                params={
                    "module": "proxy",
                    "action": "eth_getBlockByNumber",
                    "tag": hex(block_number),
                    "boolean": "false",
                    "apikey": cls._get_etherscan_key()
                },
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                result = data.get("result", {})
                if result:
                    timestamp = int(result.get("timestamp", "0"), 16)
                    gas_used = int(result.get("gasUsed", "0"), 16)
                    gas_limit = int(result.get("gasLimit", "0"), 16)
                    base_fee = int(result.get("baseFeePerGas", "0"), 16) / 1e9 if result.get("baseFeePerGas") else None
                    
                    return {
                        "block_number": block_number,
                        "hash": result.get("hash", ""),
                        "miner": result.get("miner", ""),
                        "timestamp": datetime.utcfromtimestamp(timestamp).isoformat() if timestamp else None,
                        "tx_count": len(result.get("transactions", [])),
                        "gas_used": gas_used,
                        "gas_limit": gas_limit,
                        "gas_utilization": round((gas_used / gas_limit) * 100, 2) if gas_limit else 0,
                        "base_fee_gwei": round(base_fee, 2) if base_fee else None
                    }
        except Exception as e:
            print(f"Block info fetch error for {block_number}: {e}")
        
        return None
    
    @classmethod
    def get_btc_network_stats(cls) -> Dict[str, Any]:
        """Get Bitcoin network statistics."""
        try:
            stats_response = requests.get(
                f"{cls.BLOCKCHAIN_INFO_BASE}/stats",
                params={"format": "json"},
                timeout=10
            )
            if stats_response.status_code == 200:
                stats = stats_response.json()
                return {
                    "success": True,
                    "chain": "bitcoin",
                    "market_price_usd": stats.get("market_price_usd", 0),
                    "hash_rate": stats.get("hash_rate", 0),
                    "hash_rate_formatted": f"{stats.get('hash_rate', 0) / 1e12:.2f} TH/s",
                    "difficulty": stats.get("difficulty", 0),
                    "n_blocks_total": stats.get("n_blocks_total", 0),
                    "n_tx_24h": stats.get("n_tx", 0),
                    "total_btc_sent_24h": stats.get("total_btc_sent", 0) / 1e8,
                    "estimated_btc_sent": stats.get("estimated_btc_sent", 0) / 1e8,
                    "miners_revenue_btc": stats.get("miners_revenue_btc", 0) / 1e8,
                    "miners_revenue_usd": stats.get("miners_revenue_usd", 0),
                    "n_btc_mined": stats.get("n_btc_mined", 0) / 1e8,
                    "trade_volume_btc": stats.get("trade_volume_btc", 0),
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            print(f"BTC network stats fetch error: {e}")
        
        return {"success": False, "error": "Unable to fetch BTC network stats"}
    
    @classmethod
    def get_defi_tvl_overview(cls) -> Dict[str, Any]:
        """Get DeFi Total Value Locked overview from DefiLlama."""
        try:
            response = requests.get(
                "https://api.llama.fi/protocols",
                timeout=15
            )
            if response.status_code == 200:
                protocols = response.json()
                
                top_10 = sorted(protocols, key=lambda x: x.get("tvl", 0), reverse=True)[:10]
                
                total_tvl = sum(p.get("tvl", 0) for p in protocols)
                
                result = {
                    "success": True,
                    "total_tvl": total_tvl,
                    "total_tvl_formatted": f"${total_tvl / 1e9:.2f}B",
                    "protocol_count": len(protocols),
                    "top_protocols": [
                        {
                            "name": p.get("name", "Unknown"),
                            "symbol": p.get("symbol", ""),
                            "tvl": p.get("tvl", 0),
                            "tvl_formatted": f"${p.get('tvl', 0) / 1e9:.2f}B" if p.get('tvl', 0) >= 1e9 else f"${p.get('tvl', 0) / 1e6:.2f}M",
                            "chain": p.get("chain", "Multi"),
                            "category": p.get("category", ""),
                            "change_1d": p.get("change_1d"),
                            "change_7d": p.get("change_7d")
                        }
                        for p in top_10
                    ],
                    "timestamp": datetime.utcnow().isoformat()
                }
                return result
        except Exception as e:
            print(f"DeFi TVL fetch error: {e}")
        
        return {"success": False, "error": "Unable to fetch DeFi TVL data"}
    
    @classmethod
    def get_chain_overview(cls) -> Dict[str, Any]:
        """Get overview of multiple blockchain networks."""
        eth_price = cls.get_eth_price()
        eth_gas = cls.get_eth_gas_prices()
        btc_stats = cls.get_btc_network_stats()
        
        return {
            "ethereum": {
                "price_usd": eth_price.get("eth_usd", 0) if eth_price.get("success") else None,
                "gas_price_gwei": eth_gas.get("propose_gas", 0) if eth_gas.get("success") else None,
                "gas_safe": eth_gas.get("safe_gas", 0),
                "gas_fast": eth_gas.get("fast_gas", 0),
                "status": "online" if eth_price.get("success") else "error"
            },
            "bitcoin": {
                "price_usd": btc_stats.get("market_price_usd", 0) if btc_stats.get("success") else None,
                "hash_rate": btc_stats.get("hash_rate_formatted", "N/A"),
                "difficulty": btc_stats.get("difficulty", 0),
                "blocks_total": btc_stats.get("n_blocks_total", 0),
                "tx_24h": btc_stats.get("n_tx_24h", 0),
                "status": "online" if btc_stats.get("success") else "error"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
