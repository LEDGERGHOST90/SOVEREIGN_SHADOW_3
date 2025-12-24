#!/usr/bin/env python3
"""
🏦 AAVE v3 Monitor - Production Grade (Based on Security Audit)
Fixes from audit:
- Provider failover with chain guard
- No hardcoded addresses
- Decimal precision for repay calculations
- USD-base values (no price guessing)
- Alerting thresholds
"""

import os
import sys
from decimal import Decimal, getcontext
from web3 import Web3
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional
import json
from datetime import datetime

# Load environment
load_dotenv()

# Decimal precision for financial calculations
getcontext().prec = 28

# AAVE v3 Pool contract (Ethereum mainnet)
AAVE_POOL_ADDRESS = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"

# ABI for getUserAccountData
AAVE_POOL_ABI = [{
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
}]


@dataclass
class AavePosition:
    """Typed model for AAVE position data"""
    collateral_base: int  # USD in 1e8
    debt_base: int  # USD in 1e8
    available_borrows_base: int  # USD in 1e8
    liquidation_threshold: int  # 1e4 (e.g., 8100 = 81%)
    ltv: int  # 1e4
    health_factor_wei: int  # 1e18 (or max uint256 for infinity)

    @property
    def collateral_usd(self) -> Decimal:
        return Decimal(self.collateral_base) / Decimal(1e8)

    @property
    def debt_usd(self) -> Decimal:
        return Decimal(self.debt_base) / Decimal(1e8)

    @property
    def available_borrows_usd(self) -> Decimal:
        return Decimal(self.available_borrows_base) / Decimal(1e8)

    @property
    def health_factor(self) -> Decimal:
        if self.health_factor_wei >= 2**256 - 1 or self.debt_base == 0:
            return Decimal('Infinity')
        return Decimal(self.health_factor_wei) / Decimal(1e18)

    @property
    def liquidation_threshold_pct(self) -> Decimal:
        return Decimal(self.liquidation_threshold) / Decimal(100)

    @property
    def ltv_pct(self) -> Decimal:
        return Decimal(self.ltv) / Decimal(100)


class AaveMonitor:
    """Production-grade AAVE v3 monitor with failover and alerts"""

    def __init__(self):
        self.w3 = self._get_provider()
        self.pool = self.w3.eth.contract(
            address=Web3.to_checksum_address(AAVE_POOL_ADDRESS),
            abi=AAVE_POOL_ABI
        )

        # Load user address from env (REQUIRED - no defaults)
        self.user_address = os.getenv('LEDGER_ETH_ADDRESS')
        if not self.user_address:
            raise SystemExit("❌ Missing LEDGER_ETH_ADDRESS in .env")

        self.user_address = Web3.to_checksum_address(self.user_address)

        # Alert thresholds
        self.CRITICAL_HF = Decimal('1.6')
        self.WARNING_HF = Decimal('2.0')
        self.SAFE_HF = Decimal('3.0')

        print(f"✅ AAVE Monitor initialized")
        print(f"   Address: {self.user_address}")
        print(f"   Chain: Ethereum Mainnet (ID: {self.w3.eth.chain_id})")
        print(f"   Block: {self.w3.eth.block_number:,}")

    def _get_provider(self) -> Web3:
        """Provider failover with mainnet chain guard"""
        providers = [
            ('Infura', os.getenv('INFURA_URL')),
            ('Alchemy', os.getenv('ALCHEMY_URL')),
            ('Ankr Public', 'https://rpc.ankr.com/eth'),
            ('Llama RPC', 'https://eth.llamarpc.com'),
            ('Cloudflare', 'https://cloudflare-eth.com'),
        ]

        last_error = None

        for name, url in providers:
            if not url:
                continue

            try:
                w3 = Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 15}))

                if w3.is_connected():
                    chain_id = w3.eth.chain_id

                    # CRITICAL: Enforce mainnet only
                    if chain_id != 1:
                        print(f"⚠️ {name}: Wrong chain (ID: {chain_id}, expected 1)")
                        continue

                    print(f"✅ Provider: {name}")
                    return w3

            except Exception as e:
                last_error = e
                print(f"❌ {name}: {e}")

        raise RuntimeError(f"❌ No working mainnet provider. Last error: {last_error}")

    def get_position(self) -> AavePosition:
        """Fetch current AAVE position data"""
        try:
            data = self.pool.functions.getUserAccountData(self.user_address).call()

            return AavePosition(
                collateral_base=data[0],
                debt_base=data[1],
                available_borrows_base=data[2],
                liquidation_threshold=data[3],
                ltv=data[4],
                health_factor_wei=data[5]
            )

        except Exception as e:
            raise RuntimeError(f"Failed to fetch AAVE data: {e}")

    def calculate_repay_to_target(self, position: AavePosition, target_hf: Decimal) -> Decimal:
        """Calculate USD to repay to reach target Health Factor"""
        current_hf = position.health_factor
        debt_usd = position.debt_usd

        if current_hf == Decimal('Infinity') or debt_usd == 0:
            return Decimal(0)

        if target_hf <= current_hf:
            return Decimal(0)

        # Formula: repay = debt * (1 - HF_now / HF_target)
        repay = debt_usd * (Decimal(1) - (current_hf / target_hf))

        return repay.quantize(Decimal('0.01'))  # Round to cents

    def calculate_collateral_drop_to_hf(self, position: AavePosition, target_hf: Decimal) -> Decimal:
        """Calculate collateral % drop needed to reach target HF (debt constant)"""
        current_hf = position.health_factor

        if current_hf == Decimal('Infinity'):
            return Decimal(100)

        # HF scales linearly with collateral: HF_new / HF_old = Coll_new / Coll_old
        # Drop% = (1 - HF_new / HF_old) * 100
        drop_pct = (Decimal(1) - (target_hf / current_hf)) * Decimal(100)

        return drop_pct.quantize(Decimal('0.1'))

    def assess_risk(self, position: AavePosition) -> dict:
        """Comprehensive risk assessment"""
        hf = position.health_factor

        if hf == Decimal('Infinity'):
            return {
                'level': 'NONE',
                'emoji': '✅',
                'message': 'No debt - no liquidation risk',
                'action': 'N/A'
            }

        if hf < self.CRITICAL_HF:
            return {
                'level': 'CRITICAL',
                'emoji': '🚨',
                'message': f'Health Factor critically low: {hf:.2f}',
                'action': f'URGENT: Repay ${self.calculate_repay_to_target(position, Decimal("2.5")):.2f} USDC NOW or add collateral'
            }
        elif hf < self.WARNING_HF:
            return {
                'level': 'WARNING',
                'emoji': '🔴',
                'message': f'Health Factor below safe threshold: {hf:.2f}',
                'action': f'Repay ${self.calculate_repay_to_target(position, self.SAFE_HF):.2f} USDC to reach HF 3.0'
            }
        elif hf < self.SAFE_HF:
            return {
                'level': 'CAUTION',
                'emoji': '🟠',
                'message': f'Health Factor moderate: {hf:.2f}',
                'action': f'Consider repaying ${self.calculate_repay_to_target(position, Decimal("3.5")):.2f} to reach HF 3.5'
            }
        else:
            return {
                'level': 'SAFE',
                'emoji': '✅',
                'message': f'Health Factor healthy: {hf:.2f}',
                'action': 'Monitor regularly, no immediate action needed'
            }

    def generate_repay_table(self, position: AavePosition) -> list:
        """Generate repay amounts for common target HFs"""
        targets = [Decimal(x) for x in ['2.8', '3.0', '3.2', '3.5', '4.0']]

        table = []
        for target in targets:
            repay_amount = self.calculate_repay_to_target(position, target)

            if repay_amount > 0:
                table.append({
                    'target_hf': float(target),
                    'repay_usd': float(repay_amount),
                    'new_debt': float(position.debt_usd - repay_amount)
                })

        return table

    def generate_report(self) -> dict:
        """Complete monitoring report"""
        print(f"\n{'='*70}")
        print(f"🏦 AAVE V3 POSITION MONITOR - PRODUCTION GRADE")
        print(f"{'='*70}\n")

        # Fetch position
        position = self.get_position()
        risk = self.assess_risk(position)

        # Display position
        print(f"💰 POSITION:")
        print(f"   Collateral: ${position.collateral_usd:,.2f}")
        print(f"   Debt: ${position.debt_usd:,.2f}")
        print(f"   Available to Borrow: ${position.available_borrows_usd:,.2f}")

        print(f"\n📊 METRICS:")
        print(f"   Health Factor: {position.health_factor if position.health_factor != Decimal('Infinity') else '∞'}")
        print(f"   Liquidation Threshold: {position.liquidation_threshold_pct:.1f}%")
        print(f"   LTV: {position.ltv_pct:.1f}%")

        print(f"\n⚠️  RISK ASSESSMENT:")
        print(f"   Status: {risk['emoji']} {risk['level']}")
        print(f"   {risk['message']}")
        print(f"   Action: {risk['action']}")

        # Repay table (only if debt exists)
        if position.debt_usd > 0:
            print(f"\n💊 REPAY GUIDE (to reach target HF):")
            repay_table = self.generate_repay_table(position)

            for row in repay_table:
                print(f"   HF {row['target_hf']:.1f} → Repay ${row['repay_usd']:,.2f} → New Debt: ${row['new_debt']:,.2f}")

            # Liquidation cushion
            print(f"\n🛡️  LIQUIDATION CUSHION (how far to danger):")
            for target_hf in [Decimal('2.0'), Decimal('1.8'), Decimal('1.5'), Decimal('1.2')]:
                drop = self.calculate_collateral_drop_to_hf(position, target_hf)
                print(f"   HF {target_hf:.1f} → Collateral must drop {drop:.1f}%")

        print(f"\n{'='*70}\n")

        # Return structured data
        return {
            'position': {
                'collateral_usd': float(position.collateral_usd),
                'debt_usd': float(position.debt_usd),
                'available_borrows_usd': float(position.available_borrows_usd),
                'health_factor': float(position.health_factor) if position.health_factor != Decimal('Infinity') else None,
                'liquidation_threshold_pct': float(position.liquidation_threshold_pct),
                'ltv_pct': float(position.ltv_pct)
            },
            'risk': risk,
            'repay_table': self.generate_repay_table(position) if position.debt_usd > 0 else [],
            'timestamp': datetime.now().isoformat(),
            'block_number': self.w3.eth.block_number
        }


if __name__ == '__main__':
    try:
        monitor = AaveMonitor()
        report = monitor.generate_report()

        # Save to file
        from pathlib import Path
        output_file = Path(__file__).parent.parent.parent / 'logs' / 'aave_monitor_report.json'
        output_file.parent.mkdir(exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"📄 Report saved to: {output_file}")

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        sys.exit(1)
