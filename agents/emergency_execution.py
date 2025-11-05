#!/usr/bin/env python3
"""
🚨 EMERGENCY EXECUTION HELPER
Quick commands for BTC → USDC → AAVE repayment flow
"""

import sys
from agents.transaction_monitor import TransactionMonitor, quick_btc_check

def main():
    print("🚨 EMERGENCY EXECUTION HELPER")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python emergency_execution.py check <BTC_TX_ID>")
        print("  python emergency_execution.py monitor <BTC_TX_ID>")
        print("\nExample:")
        print("  python emergency_execution.py check abc123...")
        print("  python emergency_execution.py monitor abc123...")
        return
    
    command = sys.argv[1].lower()
    
    if command == "check" and len(sys.argv) > 2:
        tx_id = sys.argv[2]
        quick_btc_check(tx_id)
    
    elif command == "monitor" and len(sys.argv) > 2:
        tx_id = sys.argv[2]
        monitor = TransactionMonitor()
        monitor.monitor_btc_until_confirmed(tx_id)
    
    else:
        print("❌ Invalid command. Use 'check' or 'monitor'")

if __name__ == "__main__":
    main()



