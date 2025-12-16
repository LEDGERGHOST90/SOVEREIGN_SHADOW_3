"""
AAVE DeFi Position Tracker
Fetches collateral, debt, and health factor from AAVE V3 protocol on Ethereum
Using Etherscan API V2 to call AAVE Pool contract directly
"""

import os
import requests
from typing import Dict, Any, Optional
from datetime import datetime


class AaveClient:
    """Fetches AAVE V3 lending position data on Ethereum mainnet."""
    
    AAVE_V3_POOL = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"
    ETHERSCAN_V2_URL = "https://api.etherscan.io/v2/api"
    
    def __init__(self):
        raw_addr = os.environ.get('AAVE_USER_ADDRESS', '') or os.environ.get('LEDGER_ETH_ADDRESS', '')
        if raw_addr.startswith('n0x'):
            raw_addr = raw_addr[1:]
        self.user_address = raw_addr
        self.etherscan_key = os.environ.get('ETHERSCAN_API_KEY', '')
    
    def is_configured(self) -> bool:
        """Check if AAVE tracking is configured."""
        return bool(self.user_address and self.etherscan_key)
    
    def get_position(self) -> Dict[str, Any]:
        """Get AAVE position using Etherscan API V2."""
        if not self.is_configured():
            return {
                'configured': False,
                'error': 'AAVE_USER_ADDRESS or ETHERSCAN_API_KEY not configured'
            }
        
        position = self._fetch_from_etherscan()
        
        if position and not position.get('error'):
            position['configured'] = True
            position['address'] = self.user_address
            position['last_updated'] = datetime.now().isoformat()
            return position
        
        error_msg = position.get('error', 'Could not fetch AAVE position') if position else 'Could not fetch AAVE position'
        return {
            'configured': True,
            'address': self.user_address,
            'collateral_usd': 0,
            'debt_usd': 0,
            'health_factor': 0,
            'net_worth_usd': 0,
            'positions': [],
            'error': error_msg,
            'last_updated': datetime.now().isoformat()
        }
    
    def _fetch_from_etherscan(self) -> Optional[Dict[str, Any]]:
        """
        Call AAVE Pool getUserAccountData(address) via Etherscan V2 API.
        
        Returns:
        - totalCollateralBase (in base currency, 8 decimals for USD)
        - totalDebtBase (in base currency)
        - availableBorrowsBase
        - currentLiquidationThreshold
        - ltv
        - healthFactor (18 decimals, divide by 1e18)
        """
        try:
            user_addr = self.user_address.lower()
            if user_addr.startswith('0x'):
                user_addr = user_addr[2:]
            
            function_sig = "bf92857c"
            padded_address = user_addr.lower().zfill(64)
            data = "0x" + function_sig + padded_address
            
            params = {
                'chainid': 1,
                'module': 'proxy',
                'action': 'eth_call',
                'to': self.AAVE_V3_POOL,
                'data': data,
                'tag': 'latest',
                'apikey': self.etherscan_key
            }
            
            response = requests.get(self.ETHERSCAN_V2_URL, params=params, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                
                if 'result' in result and result['result'] != '0x':
                    return self._parse_account_data(result['result'])
                else:
                    return {'error': f"No data returned: {result}"}
            else:
                return {'error': f"API error: {response.status_code}"}
                
        except Exception as e:
            print(f"Etherscan API error: {e}")
            return {'error': str(e)}
    
    def _parse_account_data(self, hex_result: str) -> Dict[str, Any]:
        """
        Parse getUserAccountData result.
        
        The result is 6 uint256 values (32 bytes each):
        1. totalCollateralBase - 8 decimals (USD)
        2. totalDebtBase - 8 decimals (USD)
        3. availableBorrowsBase - 8 decimals (USD)
        4. currentLiquidationThreshold - 4 decimals (e.g., 8250 = 82.5%)
        5. ltv - 4 decimals
        6. healthFactor - 18 decimals
        """
        try:
            hex_data = hex_result[2:] if hex_result.startswith('0x') else hex_result
            
            if len(hex_data) < 384:
                return {'error': 'Invalid response length'}
            
            total_collateral_raw = int(hex_data[0:64], 16)
            total_debt_raw = int(hex_data[64:128], 16)
            available_borrows_raw = int(hex_data[128:192], 16)
            liq_threshold_raw = int(hex_data[192:256], 16)
            ltv_raw = int(hex_data[256:320], 16)
            health_factor_raw = int(hex_data[320:384], 16)
            
            collateral_usd = total_collateral_raw / 1e8
            debt_usd = total_debt_raw / 1e8
            available_borrows = available_borrows_raw / 1e8
            liq_threshold = liq_threshold_raw / 10000
            ltv = ltv_raw / 10000
            health_factor = health_factor_raw / 1e18
            
            if health_factor > 1e10:
                health_factor = float('inf')
            
            return {
                'collateral_usd': round(collateral_usd, 2),
                'debt_usd': round(debt_usd, 2),
                'health_factor': round(health_factor, 2) if health_factor < 100 else 999,
                'net_worth_usd': round(collateral_usd - debt_usd, 2),
                'available_borrows_usd': round(available_borrows, 2),
                'liquidation_threshold': round(liq_threshold * 100, 1),
                'ltv': round(ltv * 100, 1),
                'positions': [],
                'source': 'etherscan_v2'
            }
            
        except Exception as e:
            print(f"Parse error: {e}")
            return {'error': f"Parse error: {e}"}
    
    def get_health_status(self) -> str:
        """Get health factor status label."""
        position = self.get_position()
        hf = position.get('health_factor', 0)
        
        if hf == 0 or hf >= 999:
            return 'NO_DEBT'
        elif hf >= 3:
            return 'SAFE'
        elif hf >= 2:
            return 'HEALTHY'
        elif hf >= 1.5:
            return 'MODERATE'
        elif hf >= 1.1:
            return 'AT_RISK'
        else:
            return 'DANGER'
