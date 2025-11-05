#!/usr/bin/env python3
"""
⚡ TRANSACTION MONITOR - Real-time BTC/USDC transfer tracking
Emergency tool for monitoring transfers during AAVE deleveraging
"""

import time
import requests
from datetime import datetime
from typing import Optional, Dict

class TransactionMonitor:
    """Monitor BTC and USDC transactions in real-time"""
    
    def __init__(self):
        self.blockchain_api = "https://blockstream.info/api"  # Free, no API key needed
        self.etherscan_api = "https://api.etherscan.io/api"
        
    def check_btc_transaction(self, tx_id: str) -> Dict:
        """Check BTC transaction status"""
        try:
            url = f"{self.blockchain_api}/tx/{tx_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                confirmations = data.get("status", {}).get("block_height", 0)
                if confirmations:
                    latest_block = requests.get(f"{self.blockchain_api}/blocks/tip/height", timeout=5).json()
                    confirmations = latest_block - confirmations + 1
                else:
                    confirmations = 0
                
                return {
                    "tx_id": tx_id,
                    "confirmed": confirmations > 0,
                    "confirmations": confirmations,
                    "needed": 1 if confirmations == 0 else 0,  # Need 1 for Coinbase
                    "status": "✅ CONFIRMED" if confirmations >= 1 else "⏳ PENDING",
                    "amount": data.get("vout", [{}])[0].get("value", 0) / 1e8 if data.get("vout") else 0,
                }
        except Exception as e:
            return {"error": str(e), "status": "❌ ERROR"}
    
    def monitor_btc_until_confirmed(self, tx_id: str, check_interval: int = 30) -> Dict:
        """Continuously monitor BTC transaction until confirmed"""
        print(f"\n🔍 Monitoring BTC Transaction: {tx_id}")
        print("=" * 60)
        
        start_time = time.time()
        while True:
            status = self.check_btc_transaction(tx_id)
            
            elapsed = int(time.time() - start_time)
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Elapsed: {elapsed}s")
            print(f"Status: {status.get('status', 'Checking...')}")
            print(f"Confirmations: {status.get('confirmations', 0)}")
            
            if status.get("confirmed"):
                print("\n✅ BTC TRANSACTION CONFIRMED!")
                print(f"Time to confirm: {elapsed}s ({elapsed//60}m {elapsed%60}s)")
                print("👉 You can now sell BTC on Coinbase!")
                return status
            
            print(f"⏳ Waiting... (checking again in {check_interval}s)")
            time.sleep(check_interval)
    
    def get_coinbase_balance(self, asset: str = "BTC") -> Optional[float]:
        """Check Coinbase balance (requires API key)"""
        # Note: This would need Coinbase API integration
        # For now, return None - user should check manually
        return None
    
    def estimate_gas_cost_usdc_withdrawal(self) -> Dict:
        """Estimate gas costs for USDC withdrawal to Ledger"""
        try:
            # Get current gas price
            url = f"{self.etherscan_api}?module=gastracker&action=gasoracle&apikey=YourApiKeyToken"
            # For now, return estimated costs
            return {
                "current_gas_gwei": 30,  # Estimate
                "estimated_cost_usd": 15-25,
                "note": "Check current gas at etherscan.io/gastracker"
            }
        except:
            return {"estimated_cost_usd": "15-25", "note": "Check manually"}


def quick_btc_check(tx_id: str):
    """Quick one-time BTC transaction check"""
    monitor = TransactionMonitor()
    status = monitor.check_btc_transaction(tx_id)
    print("\n" + "=" * 60)
    print("BTC TRANSACTION STATUS")
    print("=" * 60)
    for key, value in status.items():
        print(f"{key}: {value}")
    print("=" * 60)
    return status


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        tx_id = sys.argv[1]
        if "--monitor" in sys.argv:
            monitor = TransactionMonitor()
            monitor.monitor_btc_until_confirmed(tx_id)
        else:
            quick_btc_check(tx_id)
    else:
        print("Usage: python transaction_monitor.py <TX_ID> [--monitor]")
        print("Example: python transaction_monitor.py abc123... --monitor")



