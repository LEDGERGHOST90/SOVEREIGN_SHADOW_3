import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import asyncio

from src.utils.config_manager import config_manager

logger = logging.getLogger(__name__)

@dataclass
class VaultTransaction:
    """Vault transaction record"""
    transaction_id: str
    timestamp: datetime
    source_signal_id: str
    source_symbol: str
    profit_amount: float
    siphon_percentage: float
    siphon_amount: float
    target_asset: str
    vault_tier: str
    restake_mode: str  # auto, manual
    status: str  # pending, completed, failed
    exchange: Optional[str] = None
    order_id: Optional[str] = None
    error_message: Optional[str] = None

@dataclass
class SleepAsset:
    """SLEEP tier asset configuration"""
    symbol: str
    name: str
    primary_role: str
    apy_range: str
    staking_method: str
    exchange_support: List[str]
    auto_restake: bool = True
    allocation_weight: float = 1.0

class VaultRouter:
    """
    Vault siphon routing system for SLEEP asset integration
    Routes profits from successful trades to long-term passive income assets
    """
    
    def __init__(self):
        self.vault_log_file = "vault_log.json"
        self.vault_transactions: List[VaultTransaction] = []
        
        # SLEEP tier asset definitions
        self.sleep_assets = {
            'ADA': SleepAsset(
                symbol='ADA',
                name='Cardano',
                primary_role='Passive Staking Anchor',
                apy_range='4-5%',
                staking_method='Yoroi/Daedalus',
                exchange_support=['binance_us', 'kucoin', 'bybit'],
                auto_restake=True,
                allocation_weight=1.2
            ),
            'KAVA': SleepAsset(
                symbol='KAVA',
                name='Kava',
                primary_role='Vault-grade Passive Income',
                apy_range='7-9%',
                staking_method='Kava Platform',
                exchange_support=['kucoin', 'bybit'],
                auto_restake=True,
                allocation_weight=1.5
            ),
            'INJ': SleepAsset(
                symbol='INJ',
                name='Injective',
                primary_role='Smart Swing + Weekly Passive Yield',
                apy_range='10-14%',
                staking_method='Keplr native',
                exchange_support=['binance_us', 'kucoin', 'bybit'],
                auto_restake=True,
                allocation_weight=1.8
            ),
            'COTI': SleepAsset(
                symbol='COTI',
                name='COTI',
                primary_role='Lightweight Rest-State Exposure',
                apy_range='5-8%',
                staking_method='Treasury node',
                exchange_support=['kucoin', 'bybit'],
                auto_restake=False,
                allocation_weight=0.8
            ),
            'ALGO': SleepAsset(
                symbol='ALGO',
                name='Algorand',
                primary_role='Frictionless Yield on Auto',
                apy_range='4%',
                staking_method='Wallet staking',
                exchange_support=['binance_us', 'kucoin'],
                auto_restake=True,
                allocation_weight=1.0
            ),
            'XTZ': SleepAsset(
                symbol='XTZ',
                name='Tezos',
                primary_role='Set-and-Forget Governance Sleeper',
                apy_range='3-6%',
                staking_method='Self-delegated/pooled',
                exchange_support=['binance_us', 'kucoin'],
                auto_restake=True,
                allocation_weight=0.9
            ),
            'ATOM': SleepAsset(
                symbol='ATOM',
                name='Cosmos',
                primary_role='Backbone Layer-0 with Reliable Cycles',
                apy_range='8-10%',
                staking_method='PoS delegation',
                exchange_support=['binance_us', 'kucoin', 'bybit'],
                auto_restake=True,
                allocation_weight=1.3
            ),
            'FLOW': SleepAsset(
                symbol='FLOW',
                name='Flow',
                primary_role='NFT Ecosystem Base + Passive APY',
                apy_range='5-7%',
                staking_method='Kraken-eligible',
                exchange_support=['kucoin'],
                auto_restake=False,
                allocation_weight=0.7
            ),
            'NEAR': SleepAsset(
                symbol='NEAR',
                name='Near Protocol',
                primary_role='Asia-Market Passive Catcher',
                apy_range='10%+',
                staking_method='PoS staking',
                exchange_support=['binance_us', 'kucoin', 'bybit'],
                auto_restake=True,
                allocation_weight=1.4
            )
        }
        
        # Load existing vault log
        self._load_vault_log()
        
        # Vault routing preferences
        self.default_siphon_percentage = 30.0
        self.min_profit_threshold = 100.0  # Minimum $100 profit to trigger siphon
        self.preferred_assets = ['INJ', 'KAVA', 'NEAR', 'ATOM', 'ADA']  # Ordered by preference
        
    def _load_vault_log(self):
        """Load existing vault transaction log"""
        try:
            if Path(self.vault_log_file).exists():
                with open(self.vault_log_file, 'r') as f:
                    data = json.load(f)
                    
                for tx_data in data.get('transactions', []):
                    # Convert timestamp string back to datetime
                    tx_data['timestamp'] = datetime.fromisoformat(tx_data['timestamp'])
                    self.vault_transactions.append(VaultTransaction(**tx_data))
                    
                logger.info(f"Loaded {len(self.vault_transactions)} vault transactions")
        except Exception as e:
            logger.error(f"Failed to load vault log: {e}")
            self.vault_transactions = []
    
    def _save_vault_log(self):
        """Save vault transaction log to file"""
        try:
            data = {
                'last_updated': datetime.utcnow().isoformat(),
                'total_transactions': len(self.vault_transactions),
                'transactions': []
            }
            
            for tx in self.vault_transactions:
                tx_dict = asdict(tx)
                tx_dict['timestamp'] = tx.timestamp.isoformat()
                data['transactions'].append(tx_dict)
            
            with open(self.vault_log_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
            logger.info(f"Saved vault log with {len(self.vault_transactions)} transactions")
            
        except Exception as e:
            logger.error(f"Failed to save vault log: {e}")
    
    def select_target_asset(self, exchange: str, profit_amount: float) -> Optional[str]:
        """
        Select optimal SLEEP asset for vault routing
        
        Args:
            exchange: Source exchange for the trade
            profit_amount: Profit amount to route
            
        Returns:
            Selected asset symbol or None
        """
        try:
            # Filter assets by exchange support
            available_assets = [
                asset for symbol, asset in self.sleep_assets.items()
                if exchange in asset.exchange_support
            ]
            
            if not available_assets:
                logger.warning(f"No SLEEP assets available on {exchange}")
                return None
            
            # Sort by allocation weight (preference)
            available_assets.sort(key=lambda x: x.allocation_weight, reverse=True)
            
            # Select based on profit amount and current allocation
            for asset in available_assets:
                # Check if this asset is in preferred list
                if asset.symbol in self.preferred_assets:
                    return asset.symbol
            
            # Fallback to highest weighted available asset
            return available_assets[0].symbol
            
        except Exception as e:
            logger.error(f"Asset selection failed: {e}")
            return None
    
    async def route_to_vault(self, signal_id: str, symbol: str, profit_amount: float,
                           siphon_percentage: float = None, exchange: str = 'binance_us',
                           target_asset: str = None) -> Dict[str, Any]:
        """
        Route profits to SLEEP vault
        
        Args:
            signal_id: Source signal ID
            symbol: Source trading symbol
            profit_amount: Total profit amount
            siphon_percentage: Percentage to siphon (default from config)
            exchange: Source exchange
            target_asset: Specific target asset (auto-select if None)
            
        Returns:
            Routing result
        """
        try:
            # Use default siphon percentage if not specified
            if siphon_percentage is None:
                siphon_percentage = self.default_siphon_percentage
            
            # Calculate siphon amount
            siphon_amount = profit_amount * (siphon_percentage / 100.0)
            
            # Check minimum threshold
            if siphon_amount < self.min_profit_threshold:
                return {
                    'success': False,
                    'reason': f'Siphon amount ${siphon_amount:.2f} below threshold ${self.min_profit_threshold}',
                    'siphon_amount': siphon_amount
                }
            
            # Select target asset if not specified
            if not target_asset:
                target_asset = self.select_target_asset(exchange, siphon_amount)
                
            if not target_asset:
                return {
                    'success': False,
                    'reason': f'No suitable SLEEP asset found for {exchange}',
                    'siphon_amount': siphon_amount
                }
            
            # Create vault transaction
            transaction = VaultTransaction(
                transaction_id=f"vault_{int(datetime.utcnow().timestamp())}_{signal_id}",
                timestamp=datetime.utcnow(),
                source_signal_id=signal_id,
                source_symbol=symbol,
                profit_amount=profit_amount,
                siphon_percentage=siphon_percentage,
                siphon_amount=siphon_amount,
                target_asset=target_asset,
                vault_tier='SLEEP',
                restake_mode='auto' if self.sleep_assets[target_asset].auto_restake else 'manual',
                status='pending',
                exchange=exchange
            )
            
            # Execute vault routing
            routing_result = await self._execute_vault_routing(transaction)
            
            # Update transaction status
            transaction.status = 'completed' if routing_result['success'] else 'failed'
            if not routing_result['success']:
                transaction.error_message = routing_result.get('error')
            
            # Store transaction
            self.vault_transactions.append(transaction)
            self._save_vault_log()
            
            # Log vault siphon
            logger.info(f"Vault siphon: ${siphon_amount:.2f} → {target_asset} from signal {signal_id}")
            
            return {
                'success': routing_result['success'],
                'transaction_id': transaction.transaction_id,
                'target_asset': target_asset,
                'siphon_amount': siphon_amount,
                'restake_mode': transaction.restake_mode,
                'vault_tier': 'SLEEP',
                'message': f'Routed ${siphon_amount:.2f} to {target_asset}',
                'error': routing_result.get('error')
            }
            
        except Exception as e:
            logger.error(f"Vault routing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'siphon_amount': 0.0
            }
    
    async def _execute_vault_routing(self, transaction: VaultTransaction) -> Dict[str, Any]:
        """
        Execute the actual vault routing (simulation for now)
        In production, this would place actual buy orders
        """
        try:
            # Simulate vault routing execution
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # In paper trading mode, just log the transaction
            if config_manager.get_config('system.paper_trading', True):
                logger.info(f"PAPER: Vault routing ${transaction.siphon_amount:.2f} to {transaction.target_asset}")
                return {'success': True, 'mode': 'paper'}
            
            # TODO: Implement actual exchange integration for vault routing
            # This would involve:
            # 1. Converting profit to USDT if needed
            # 2. Placing buy order for target asset
            # 3. Setting up staking if auto_restake is enabled
            # 4. Tracking order execution
            
            # For now, simulate successful execution
            return {
                'success': True,
                'mode': 'simulated',
                'order_id': f"vault_order_{int(datetime.utcnow().timestamp())}"
            }
            
        except Exception as e:
            logger.error(f"Vault routing execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_vault_summary(self) -> Dict[str, Any]:
        """Get vault routing summary and statistics"""
        try:
            total_routed = sum(tx.siphon_amount for tx in self.vault_transactions if tx.status == 'completed')
            total_transactions = len(self.vault_transactions)
            successful_transactions = len([tx for tx in self.vault_transactions if tx.status == 'completed'])
            
            # Asset breakdown
            asset_breakdown = {}
            for tx in self.vault_transactions:
                if tx.status == 'completed':
                    if tx.target_asset not in asset_breakdown:
                        asset_breakdown[tx.target_asset] = {
                            'total_amount': 0.0,
                            'transaction_count': 0,
                            'asset_info': self.sleep_assets.get(tx.target_asset)
                        }
                    asset_breakdown[tx.target_asset]['total_amount'] += tx.siphon_amount
                    asset_breakdown[tx.target_asset]['transaction_count'] += 1
            
            # Recent transactions (last 10)
            recent_transactions = sorted(
                self.vault_transactions,
                key=lambda x: x.timestamp,
                reverse=True
            )[:10]
            
            return {
                'total_routed': round(total_routed, 2),
                'total_transactions': total_transactions,
                'successful_transactions': successful_transactions,
                'success_rate': round((successful_transactions / total_transactions * 100), 2) if total_transactions > 0 else 0,
                'asset_breakdown': asset_breakdown,
                'recent_transactions': [
                    {
                        'transaction_id': tx.transaction_id,
                        'timestamp': tx.timestamp.isoformat(),
                        'source_symbol': tx.source_symbol,
                        'target_asset': tx.target_asset,
                        'siphon_amount': tx.siphon_amount,
                        'status': tx.status
                    }
                    for tx in recent_transactions
                ],
                'sleep_assets': {symbol: asdict(asset) for symbol, asset in self.sleep_assets.items()}
            }
            
        except Exception as e:
            logger.error(f"Failed to generate vault summary: {e}")
            return {'error': str(e)}
    
    def get_asset_allocation_recommendation(self, total_vault_value: float) -> Dict[str, float]:
        """
        Get recommended asset allocation for SLEEP vault
        
        Args:
            total_vault_value: Total value in vault
            
        Returns:
            Recommended allocation by asset
        """
        try:
            # Calculate total weight
            total_weight = sum(asset.allocation_weight for asset in self.sleep_assets.values())
            
            # Calculate recommended allocation
            allocation = {}
            for symbol, asset in self.sleep_assets.items():
                percentage = (asset.allocation_weight / total_weight) * 100
                recommended_value = total_vault_value * (percentage / 100)
                
                allocation[symbol] = {
                    'percentage': round(percentage, 1),
                    'recommended_value': round(recommended_value, 2),
                    'asset_info': {
                        'name': asset.name,
                        'apy_range': asset.apy_range,
                        'primary_role': asset.primary_role
                    }
                }
            
            return allocation
            
        except Exception as e:
            logger.error(f"Allocation recommendation failed: {e}")
            return {}
    
    def check_restake_status(self, asset: str) -> Dict[str, Any]:
        """Check restaking status for a SLEEP asset"""
        if asset not in self.sleep_assets:
            return {'error': f'Asset {asset} not found in SLEEP tier'}
        
        sleep_asset = self.sleep_assets[asset]
        
        return {
            'asset': asset,
            'auto_restake': sleep_asset.auto_restake,
            'staking_method': sleep_asset.staking_method,
            'apy_range': sleep_asset.apy_range,
            'status': 'auto' if sleep_asset.auto_restake else 'manual'
        }

# Global vault router instance
vault_router = VaultRouter()

# Convenience function for external use
async def route_profit_to_vault(signal_id: str, symbol: str, profit_amount: float,
                               siphon_percentage: float = 30.0, exchange: str = 'binance_us') -> Dict[str, Any]:
    """
    Convenience function to route profits to SLEEP vault
    
    Args:
        signal_id: Source signal ID
        symbol: Source trading symbol
        profit_amount: Total profit amount
        siphon_percentage: Percentage to siphon (default 30%)
        exchange: Source exchange
        
    Returns:
        Routing result
    """
    return await vault_router.route_to_vault(
        signal_id=signal_id,
        symbol=symbol,
        profit_amount=profit_amount,
        siphon_percentage=siphon_percentage,
        exchange=exchange
    )

