#!/usr/bin/env python3
"""
🚀 COINBASE CDP INTEGRATION
Advanced Coinbase Developer Platform integration for SovereignShadow.AI
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
import subprocess
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ai_enhanced/coinbase_cdp_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("coinbase_cdp")

class CoinbaseCDPIntegration:
    """Advanced Coinbase CDP integration for SovereignShadow.AI"""
    
    def __init__(self):
        self.project_id = "f5b80ba9-92fd-4d0f-bb26-b9f546edcc1e"
        self.api_key = None
        self.wallets = {}
        self.balances = {}
        self.is_initialized = False
        
        logger.info("🚀 Coinbase CDP Integration initialized")
    
    def install_cdp_sdk(self):
        """Install Coinbase CDP SDK"""
        logger.info("📦 Installing Coinbase CDP SDK...")
        
        try:
            # Install the CDP SDK
            result = subprocess.run([
                'npm', 'install', '@coinbase/cdp-sdk'
            ], capture_output=True, text=True, cwd='/tmp')
            
            if result.returncode == 0:
                logger.info("✅ Coinbase CDP SDK installed successfully")
                return True
            else:
                logger.error(f"❌ Failed to install CDP SDK: {result.stderr}")
                return False
                
        except FileNotFoundError:
            logger.error("❌ npm not found. Please install Node.js first.")
            return False
        except Exception as e:
            logger.error(f"❌ Error installing CDP SDK: {e}")
            return False
    
    def setup_api_key(self, api_key: str):
        """Setup API key for CDP"""
        self.api_key = api_key
        os.environ['COINBASE_CDP_API_KEY'] = api_key
        logger.info("✅ Coinbase CDP API key configured")
    
    def create_wallet(self, wallet_name: str = "SovereignShadow") -> Dict:
        """Create a new wallet using CDP SDK"""
        logger.info(f"🔐 Creating wallet: {wallet_name}")
        
        try:
            # Create a Node.js script to interact with CDP
            script_content = f"""
const {{ CoinbaseSDK }} = require('@coinbase/cdp-sdk');

async function createWallet() {{
    const sdk = new CoinbaseSDK({{
        apiKey: '{self.api_key}',
        projectId: '{self.project_id}'
    }});
    
    try {{
        const wallet = await sdk.createWallet({{
            name: '{wallet_name}',
            description: 'SovereignShadow AI Trading Wallet'
        }});
        
        console.log(JSON.stringify({{
            success: true,
            walletId: wallet.id,
            address: wallet.address,
            name: wallet.name
        }}));
    }} catch (error) {{
        console.log(JSON.stringify({{
            success: false,
            error: error.message
        }}));
    }}
}}

createWallet();
"""
            
            # Write script to temporary file
            script_path = '/tmp/create_wallet.js'
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Execute the script
            result = subprocess.run([
                'node', script_path
            ], capture_output=True, text=True, cwd='/tmp')
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                if response['success']:
                    wallet_info = {
                        'id': response['walletId'],
                        'address': response['address'],
                        'name': response['name'],
                        'created_at': datetime.now().isoformat()
                    }
                    self.wallets[wallet_name] = wallet_info
                    logger.info(f"✅ Wallet created: {wallet_info['address']}")
                    return wallet_info
                else:
                    logger.error(f"❌ Wallet creation failed: {response['error']}")
                    return {}
            else:
                logger.error(f"❌ Script execution failed: {result.stderr}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Error creating wallet: {e}")
            return {}
    
    def get_wallet_balances(self, wallet_id: str) -> Dict:
        """Get balances for a specific wallet"""
        logger.info(f"💰 Fetching balances for wallet: {wallet_id}")
        
        try:
            script_content = f"""
const {{ CoinbaseSDK }} = require('@coinbase/cdp-sdk');

async function getBalances() {{
    const sdk = new CoinbaseSDK({{
        apiKey: '{self.api_key}',
        projectId: '{self.project_id}'
    }});
    
    try {{
        const balances = await sdk.getWalletBalances('{wallet_id}');
        
        console.log(JSON.stringify({{
            success: true,
            balances: balances
        }}));
    }} catch (error) {{
        console.log(JSON.stringify({{
            success: false,
            error: error.message
        }}));
    }}
}}

getBalances();
"""
            
            script_path = '/tmp/get_balances.js'
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            result = subprocess.run([
                'node', script_path
            ], capture_output=True, text=True, cwd='/tmp')
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                if response['success']:
                    self.balances[wallet_id] = response['balances']
                    logger.info(f"✅ Retrieved {len(response['balances'])} balances")
                    return response['balances']
                else:
                    logger.error(f"❌ Balance fetch failed: {response['error']}")
                    return {}
            else:
                logger.error(f"❌ Script execution failed: {result.stderr}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Error fetching balances: {e}")
            return {}
    
    def send_transaction(self, wallet_id: str, to_address: str, amount: float, currency: str) -> Dict:
        """Send a transaction using CDP"""
        logger.info(f"📤 Sending {amount} {currency} from {wallet_id} to {to_address}")
        
        try:
            script_content = f"""
const {{ CoinbaseSDK }} = require('@coinbase/cdp-sdk');

async function sendTransaction() {{
    const sdk = new CoinbaseSDK({{
        apiKey: '{self.api_key}',
        projectId: '{self.project_id}'
    }});
    
    try {{
        const transaction = await sdk.sendTransaction({{
            walletId: '{wallet_id}',
            to: '{to_address}',
            amount: {amount},
            currency: '{currency}'
        }});
        
        console.log(JSON.stringify({{
            success: true,
            transactionId: transaction.id,
            hash: transaction.hash,
            status: transaction.status
        }}));
    }} catch (error) {{
        console.log(JSON.stringify({{
            success: false,
            error: error.message
        }}));
    }}
}}

sendTransaction();
"""
            
            script_path = '/tmp/send_transaction.js'
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            result = subprocess.run([
                'node', script_path
            ], capture_output=True, text=True, cwd='/tmp')
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                if response['success']:
                    logger.info(f"✅ Transaction sent: {response['transactionId']}")
                    return response
                else:
                    logger.error(f"❌ Transaction failed: {response['error']}")
                    return {}
            else:
                logger.error(f"❌ Script execution failed: {result.stderr}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Error sending transaction: {e}")
            return {}
    
    def generate_cdp_report(self) -> Dict:
        """Generate comprehensive CDP integration report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'project_id': self.project_id,
            'api_key_configured': bool(self.api_key),
            'wallets': self.wallets,
            'balances': self.balances,
            'total_wallets': len(self.wallets),
            'total_currencies': sum(len(balances) for balances in self.balances.values()),
            'integration_status': 'active' if self.is_initialized else 'inactive'
        }
        
        return report
    
    def save_report(self, report: Dict):
        """Save CDP report to file"""
        os.makedirs('logs/ai_enhanced', exist_ok=True)
        
        with open('logs/ai_enhanced/coinbase_cdp_report.json', 'w') as f:
            json.dump(report, f, indent=4, default=str)
        
        logger.info("📄 CDP report saved to logs/ai_enhanced/coinbase_cdp_report.json")

def main():
    """Main execution function"""
    print("🚀 COINBASE CDP INTEGRATION")
    print("=" * 50)
    
    cdp = CoinbaseCDPIntegration()
    
    # Check if Node.js is available
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js version: {result.stdout.strip()}")
        else:
            print("❌ Node.js not found. Please install Node.js first.")
            return
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js first.")
        return
    
    # Install CDP SDK
    if cdp.install_cdp_sdk():
        print("✅ Coinbase CDP SDK ready")
    else:
        print("❌ Failed to install CDP SDK")
        return
    
    # Setup API key (you'll need to provide this)
    api_key = input("Enter your Coinbase CDP API key (or press Enter to skip): ").strip()
    if api_key:
        cdp.setup_api_key(api_key)
        cdp.is_initialized = True
        
        # Create a test wallet
        wallet = cdp.create_wallet("SovereignShadow-Test")
        if wallet:
            print(f"✅ Test wallet created: {wallet['address']}")
            
            # Get balances
            balances = cdp.get_wallet_balances(wallet['id'])
            if balances:
                print(f"✅ Retrieved {len(balances)} balances")
    else:
        print("⚠️ Skipping API key setup. CDP features will be limited.")
    
    # Generate report
    report = cdp.generate_cdp_report()
    cdp.save_report(report)
    
    print(f"\n📊 CDP INTEGRATION STATUS:")
    print(f"   Project ID: {report['project_id']}")
    print(f"   API Key: {'✅ Configured' if report['api_key_configured'] else '❌ Not configured'}")
    print(f"   Wallets: {report['total_wallets']}")
    print(f"   Currencies: {report['total_currencies']}")
    print(f"   Status: {report['integration_status']}")
    
    print(f"\n📄 Report saved to: logs/ai_enhanced/coinbase_cdp_report.json")

if __name__ == "__main__":
    main()
