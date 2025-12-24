#!/usr/bin/env python3
"""
🏦 AAVE Position Monitor
Real-time monitoring of AAVE v3 position on Ethereum Mainnet

YOUR POSITION:
- Address: 0xC08413B63ecA84E2d9693af9414330dA88dcD81C (Ledger)
- Asset: Aave Ethereum wst (wrapped staked ETH)
- Value: $3,904.74 (63.3% of portfolio)
- Protocol: AAVE v3

CRITICAL: This is your largest holding and needs constant monitoring!
"""

import os
import json
from web3 import Web3
from decimal import Decimal
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class AAVEMonitor:
    """Monitor AAVE v3 position for health factor and liquidation risk"""
    
    # AAVE v3 Ethereum Mainnet Contract Addresses
    AAVE_POOL = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"
    AAVE_DATA_PROVIDER = "0x7B4EB56E7CD4b454BA8ff71E4518426369a138a3"
    
    # Token addresses
    WSTETH = "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0"  # Wrapped staked ETH
    
    # Minimal ABI for getUserAccountData
    POOL_ABI = [
        {
            "inputs": [{"internalType": "address", "name": "user", "type": "address"}],
            "name": "getUserAccountData",
            "outputs": [
                {"internalType": "uint256", "name": "totalCollateralBase", "type": "uint256"},
                {"internalType": "uint256", "name": "totalDebtBase", "type": "uint256"},
                {"internalType": "uint256", "name": "availableBorrowsBase", "type": "uint256"},
                {"internalType": "uint256", "name": "currentLiquidationThreshold", "type": "uint256"},
                {"internalType": "uint256", "name": "ltv", "type": "uint256"},
                {"internalType": "uint256", "name": "healthFactor", "type": "uint256"}
            ],
            "stateMutability": "view",
            "type": "function"
        }
    ]
    
    def __init__(self):
        """Initialize AAVE monitor with Web3 connection"""
        infura_url = os.getenv('INFURA_URL')
        if not infura_url:
            raise ValueError("INFURA_URL not found in environment variables")
        
        self.w3 = Web3(Web3.HTTPProvider(infura_url))
        
        # Verify connection
        if not self.w3.is_connected():
            raise ConnectionError("Failed to connect to Ethereum via Infura")
        
        # Your Ledger address
        self.user_address = os.getenv('LEDGER_ETH_ADDRESS', '0xC08413B63ecA84E2d9693af9414330dA88dcD81C')
        
        # Initialize AAVE Pool contract
        self.pool_contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.AAVE_POOL),
            abi=self.POOL_ABI
        )
        
        print(f"✅ Connected to Ethereum Mainnet (Block: {self.w3.eth.block_number})")
        print(f"📍 Monitoring address: {self.user_address}")
    
    def get_account_data(self) -> Dict[str, Any]:
        """
        Get AAVE account data including health factor
        
        Returns:
            {
                'total_collateral_usd': float,
                'total_debt_usd': float,
                'available_borrows_usd': float,
                'liquidation_threshold': float,
                'ltv': float,
                'health_factor': float,
                'timestamp': str
            }
        """
        try:
            # Call getUserAccountData from AAVE Pool
            account_data = self.pool_contract.functions.getUserAccountData(
                Web3.to_checksum_address(self.user_address)
            ).call()
            
            # AAVE returns values in base currency (USD) with 8 decimals
            # Health factor is returned with 18 decimals (1e18 = 1.0)
            
            total_collateral = account_data[0] / 1e8  # USD
            total_debt = account_data[1] / 1e8  # USD
            available_borrows = account_data[2] / 1e8  # USD
            liquidation_threshold = account_data[3] / 1e4  # Percentage (divide by 10000)
            ltv = account_data[4] / 1e4  # Percentage
            health_factor_raw = account_data[5]
            
            # Convert health factor (1e18 scale)
            if health_factor_raw >= 2**256 - 1:  # Max uint256 means no debt
                health_factor = float('inf')
            else:
                health_factor = health_factor_raw / 1e18
            
            return {
                'total_collateral_usd': total_collateral,
                'total_debt_usd': total_debt,
                'available_borrows_usd': available_borrows,
                'liquidation_threshold': liquidation_threshold,
                'ltv': ltv,
                'health_factor': health_factor,
                'net_position_usd': total_collateral - total_debt,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'block_number': self.w3.eth.block_number
            }
            
        except Exception as e:
            print(f"❌ Error fetching AAVE account data: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
    
    def assess_risk(self, health_factor: float) -> Dict[str, Any]:
        """
        Assess liquidation risk based on health factor
        
        Health Factor scale:
        - > 2.0: SAFE
        - 1.5 - 2.0: MODERATE (caution)
        - 1.0 - 1.5: HIGH RISK (warning)
        - < 1.0: LIQUIDATION (critical)
        """
        if health_factor == float('inf'):
            return {
                'risk_level': 'NONE',
                'status': '✅ SAFE',
                'description': 'No debt position',
                'action': 'None required'
            }
        elif health_factor >= 2.0:
            return {
                'risk_level': 'LOW',
                'status': '✅ SAFE',
                'description': 'Healthy position with good buffer',
                'action': 'Continue monitoring'
            }
        elif health_factor >= 1.5:
            return {
                'risk_level': 'MODERATE',
                'status': '⚠️  CAUTION',
                'description': 'Position is safe but monitor closely',
                'action': 'Watch for price movements'
            }
        elif health_factor >= 1.0:
            return {
                'risk_level': 'HIGH',
                'status': '🚨 WARNING',
                'description': 'Risk of liquidation if collateral value drops',
                'action': 'Consider adding collateral or reducing debt'
            }
        else:
            return {
                'risk_level': 'CRITICAL',
                'status': '💀 LIQUIDATION RISK',
                'description': 'Position can be liquidated at any moment!',
                'action': 'URGENT: Add collateral or repay debt immediately'
            }
    
    def get_position_summary(self) -> Dict[str, Any]:
        """
        Get complete position summary with risk assessment
        """
        account_data = self.get_account_data()
        
        if 'error' in account_data:
            return account_data
        
        health_factor = account_data['health_factor']
        risk_assessment = self.assess_risk(health_factor)
        
        return {
            'address': self.user_address,
            'protocol': 'AAVE v3',
            'network': 'Ethereum Mainnet',
            'position': {
                'total_collateral_usd': account_data['total_collateral_usd'],
                'total_debt_usd': account_data['total_debt_usd'],
                'net_value_usd': account_data['net_position_usd'],
                'available_borrows_usd': account_data['available_borrows_usd']
            },
            'metrics': {
                'health_factor': health_factor,
                'liquidation_threshold': account_data['liquidation_threshold'],
                'loan_to_value': account_data['ltv']
            },
            'risk': risk_assessment,
            'timestamp': account_data['timestamp'],
            'block_number': account_data['block_number']
        }
    
    def print_position_report(self):
        """Print formatted position report"""
        print("\n" + "=" * 70)
        print("🏦 AAVE V3 POSITION REPORT")
        print("=" * 70)
        
        summary = self.get_position_summary()
        
        if 'error' in summary:
            print(f"❌ Error: {summary['error']}")
            return
        
        print(f"\n📍 Address: {summary['address']}")
        print(f"🌐 Network: {summary['network']}")
        print(f"⏱️  Timestamp: {summary['timestamp']}")
        print(f"📦 Block: {summary['block_number']}")
        
        print("\n💰 POSITION:")
        print(f"   Collateral: ${summary['position']['total_collateral_usd']:,.2f}")
        print(f"   Debt: ${summary['position']['total_debt_usd']:,.2f}")
        print(f"   Net Value: ${summary['position']['net_value_usd']:,.2f}")
        print(f"   Available to Borrow: ${summary['position']['available_borrows_usd']:,.2f}")
        
        print("\n📊 METRICS:")
        hf = summary['metrics']['health_factor']
        if hf == float('inf'):
            print(f"   Health Factor: ∞ (No debt)")
        else:
            print(f"   Health Factor: {hf:.4f}")
        print(f"   Liquidation Threshold: {summary['metrics']['liquidation_threshold']:.2f}%")
        print(f"   Loan-to-Value: {summary['metrics']['loan_to_value']:.2f}%")
        
        print("\n⚠️  RISK ASSESSMENT:")
        risk = summary['risk']
        print(f"   Status: {risk['status']}")
        print(f"   Level: {risk['risk_level']}")
        print(f"   Description: {risk['description']}")
        print(f"   Action: {risk['action']}")
        
        print("\n" + "=" * 70)


def main():
    """Run AAVE monitor"""
    try:
        monitor = AAVEMonitor()
        monitor.print_position_report()
        
        # Return summary for programmatic access
        return monitor.get_position_summary()
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
