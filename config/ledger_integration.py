#!/usr/bin/env python3
"""
LEDGER HARDWARE WALLET INTEGRATION
Advanced Ledger integration for SovereignShadow.AI
"""
import os
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

class LedgerWalletManager:
    """Advanced Ledger Hardware Wallet Manager"""
    
    def __init__(self):
        self.ledger_live_path = "/Applications/Ledger Live.app"
        self.connected = False
        self.device_info = {}
        self.balances = {}
        
    def check_hardware_connection(self):
        """Check if Ledger hardware wallet is connected"""
        try:
            result = subprocess.run(['system_profiler', 'SPUSBDataType'], 
                                  capture_output=True, text=True, timeout=10)
            
            if 'Ledger' in result.stdout:
                print("✅ Ledger hardware wallet detected")
                self.connected = True
                
                # Extract device info
                lines = result.stdout.split('\n')
                for i, line in enumerate(lines):
                    if 'Ledger' in line:
                        # Get device details from surrounding lines
                        device_section = lines[max(0, i-5):i+10]
                        self.device_info = self._parse_device_info(device_section)
                        break
                        
                return True
            else:
                print("❌ No Ledger hardware wallet found")
                print("💡 Please connect your Ledger device and unlock it")
                self.connected = False
                return False
                
        except subprocess.TimeoutExpired:
            print("⏱️ Hardware check timed out")
            return False
        except Exception as e:
            print(f"❌ Error checking hardware: {e}")
            return False
    
    def _parse_device_info(self, device_section):
        """Parse device information from system profiler output"""
        info = {}
        for line in device_section:
            if 'Product ID' in line:
                info['product_id'] = line.split(':')[-1].strip()
            elif 'Vendor ID' in line:
                info['vendor_id'] = line.split(':')[-1].strip()
            elif 'Serial Number' in line:
                info['serial'] = line.split(':')[-1].strip()
        return info
    
    def get_ledger_live_accounts(self):
        """Get account information from Ledger Live"""
        try:
            # Ledger Live stores data in ~/Library/Application Support/Ledger Live
            ledger_data_path = Path.home() / "Library/Application Support/Ledger Live"
            
            if not ledger_data_path.exists():
                print("❌ Ledger Live data directory not found")
                return {}
            
            # Look for account data files
            accounts_file = ledger_data_path / "accounts.json"
            if accounts_file.exists():
                with open(accounts_file, 'r') as f:
                    accounts_data = json.load(f)
                    return accounts_data
            else:
                print("❌ Ledger Live accounts file not found")
                return {}
                
        except Exception as e:
            print(f"❌ Error reading Ledger Live data: {e}")
            return {}
    
    def get_crypto_balances(self):
        """Get cryptocurrency balances from Ledger"""
        if not self.connected:
            print("❌ Ledger not connected. Please connect your device.")
            return {}
        
        try:
            # Try to get balances via Ledger Live CLI if available
            ledger_cli_path = "/usr/local/bin/ledger-live"
            
            if os.path.exists(ledger_cli_path):
                result = subprocess.run([ledger_cli_path, 'account', 'list'], 
                                      capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    # Parse CLI output for balances
                    self.balances = self._parse_cli_balances(result.stdout)
                    return self.balances
            
            # Fallback: Read from Ledger Live data files
            accounts = self.get_ledger_live_accounts()
            if accounts:
                self.balances = self._extract_balances_from_accounts(accounts)
                return self.balances
            
            print("⚠️ Could not retrieve balances. Please ensure Ledger Live is set up.")
            return {}
            
        except subprocess.TimeoutExpired:
            print("⏱️ Ledger balance check timed out")
            return {}
        except Exception as e:
            print(f"❌ Error getting balances: {e}")
            return {}
    
    def _parse_cli_balances(self, cli_output):
        """Parse balances from Ledger Live CLI output"""
        balances = {}
        lines = cli_output.split('\n')
        
        for line in lines:
            if 'balance:' in line.lower():
                # Extract currency and amount
                parts = line.split()
                for i, part in enumerate(parts):
                    if 'balance:' in part.lower() and i + 1 < len(parts):
                        amount_str = parts[i + 1]
                        # Extract numeric value
                        try:
                            amount = float(amount_str.replace(',', ''))
                            # Try to determine currency from context
                            currency = self._extract_currency_from_line(line)
                            if currency:
                                balances[currency] = amount
                        except ValueError:
                            continue
        return balances
    
    def _extract_currency_from_line(self, line):
        """Extract currency symbol from CLI output line"""
        # Common currency patterns
        currencies = ['BTC', 'ETH', 'USDT', 'USDC', 'SOL', 'ADA', 'DOT', 'MATIC', 'AVAX']
        for currency in currencies:
            if currency in line.upper():
                return currency
        return None
    
    def _extract_balances_from_accounts(self, accounts_data):
        """Extract balances from Ledger Live accounts data"""
        balances = {}
        
        if isinstance(accounts_data, list):
            for account in accounts_data:
                if 'balance' in account and 'currency' in account:
                    currency = account['currency']['ticker']
                    balance = account['balance']
                    balances[currency] = balance
        
        return balances
    
    def generate_ledger_report(self):
        """Generate comprehensive Ledger report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'ledger_live_installed': os.path.exists(self.ledger_live_path),
            'hardware_connected': self.connected,
            'device_info': self.device_info,
            'balances': self.balances,
            'total_currencies': len(self.balances),
            'total_balance_value': sum(self.balances.values()) if self.balances else 0
        }
        
        return report
    
    def save_report(self, report):
        """Save Ledger report to file"""
        os.makedirs('logs/ai_enhanced', exist_ok=True)
        
        with open('logs/ai_enhanced/ledger_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📄 Ledger report saved to: logs/ai_enhanced/ledger_report.json")

def main():
    """Main execution function"""
    print("🔐 LEDGER HARDWARE WALLET INTEGRATION")
    print("=" * 50)
    
    manager = LedgerWalletManager()
    
    # Check hardware connection
    connected = manager.check_hardware_connection()
    
    if connected:
        # Get balances
        balances = manager.get_crypto_balances()
        
        if balances:
            print(f"\n💰 LEDGER WALLET BALANCES:")
            for currency, amount in balances.items():
                print(f"   {currency}: {amount}")
        else:
            print("\n⚠️ No balances found. Please check your Ledger Live setup.")
    else:
        print("\n💡 Please connect your Ledger device to check balances.")
        # Simulate balances for demonstration
        manager.balances = {
            'BTC': 0.5,
            'ETH': 2.5,
            'USDT': 1000.0,
            'SOL': 50.0
        }
        print("\n📊 SIMULATED BALANCES (for demonstration):")
        for currency, amount in manager.balances.items():
            print(f"   {currency}: {amount}")
    
    # Generate and save report
    report = manager.generate_ledger_report()
    manager.save_report(report)
    
    print(f"\n📊 LEDGER STATUS SUMMARY:")
    print(f"   Ledger Live Installed: {'✅' if report['ledger_live_installed'] else '❌'}")
    print(f"   Hardware Connected: {'✅' if report['hardware_connected'] else '❌'}")
    print(f"   Currencies Tracked: {report['total_currencies']}")
    print(f"   Total Value: {report['total_balance_value']}")

if __name__ == "__main__":
    main()