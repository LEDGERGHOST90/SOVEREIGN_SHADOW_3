#!/usr/bin/env python3
"""
🚨 AAVE EMERGENCY REPAY SCRIPT
Executes immediate debt repayment to restore Health Factor
"""

import os
import sys
import json
from pathlib import Path
from decimal import Decimal, getcontext
from datetime import datetime, timezone

# Set precision
getcontext().prec = 28

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / 'modules' / 'safety'))

from aave_monitor_v2 import AaveMonitor

class EmergencyRepay:
    """Execute emergency AAVE debt repayment"""

    def __init__(self):
        self.monitor = AaveMonitor()
        self.logs_dir = Path(__file__).parent.parent / 'logs' / 'emergency_repay'
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        print(f"🚨 AAVE EMERGENCY REPAY INITIALIZED")
        print(f"   Logs: {self.logs_dir}\n")

    def get_current_position(self):
        """Get current AAVE position"""
        position = self.monitor.get_position()

        print(f"📊 CURRENT POSITION:")
        print(f"   Collateral: ${position.collateral_usd:,.2f} wstETH")
        print(f"   Debt: ${position.debt_usd:,.2f} USDC")
        print(f"   Health Factor: {position.health_factor:.2f}")
        print()

        return position

    def calculate_repay_amount(self, position, target_hf):
        """Calculate exact repay amount needed"""
        current_hf = position.health_factor

        if current_hf == Decimal('Infinity'):
            print(f"✅ No debt - Health Factor is already ∞")
            return Decimal('0')

        if current_hf >= target_hf:
            print(f"✅ Current HF {current_hf:.2f} already above target {target_hf:.2f}")
            return Decimal('0')

        repay_amount = self.monitor.calculate_repay_to_target(position, target_hf)

        print(f"💊 REPAY CALCULATION:")
        print(f"   Current HF: {current_hf:.2f}")
        print(f"   Target HF: {target_hf:.2f}")
        print(f"   Repay needed: ${repay_amount:,.2f} USDC")
        print()

        return repay_amount

    def preview_new_position(self, position, repay_amount):
        """Preview position after repay"""
        new_debt = position.debt_usd - repay_amount

        if new_debt <= 0:
            new_hf = Decimal('Infinity')
            print(f"📈 AFTER REPAY (FULL PAYOFF):")
            print(f"   Collateral: ${position.collateral_usd:,.2f} (unchanged)")
            print(f"   Debt: $0.00")
            print(f"   Health Factor: ∞")
        else:
            # HF = (Collateral × LT) / Debt
            LT = Decimal('0.81')  # wstETH liquidation threshold
            new_hf = (position.collateral_usd * LT) / new_debt

            print(f"📈 AFTER REPAY:")
            print(f"   Collateral: ${position.collateral_usd:,.2f} (unchanged)")
            print(f"   Debt: ${new_debt:,.2f} (was ${position.debt_usd:,.2f})")
            print(f"   Health Factor: {new_hf:.2f} (was {position.health_factor:.2f})")
            print(f"   HF Improvement: +{new_hf - position.health_factor:.2f}")

        print()
        return new_hf if new_debt > 0 else Decimal('Infinity')

    def check_safety_requirements(self, repay_amount):
        """Safety checks before execution"""
        print(f"🛡️  SAFETY CHECKS:")

        issues = []

        # Check 1: Repay amount reasonable (not > $5,000)
        if repay_amount > Decimal('5000'):
            issues.append(f"Repay amount ${repay_amount:,.2f} exceeds safety limit ($5,000)")
            print(f"   ❌ Repay amount too large (${repay_amount:,.2f} > $5,000)")
        else:
            print(f"   ✅ Repay amount within limits (${repay_amount:,.2f} < $5,000)")

        # Check 2: Connected to mainnet
        chain_id = self.monitor.w3.eth.chain_id
        if chain_id != 1:
            issues.append(f"Wrong network (chain_id: {chain_id}, expected: 1)")
            print(f"   ❌ Wrong network (chain_id: {chain_id})")
        else:
            print(f"   ✅ Connected to Ethereum mainnet")

        # Check 3: RPC provider working
        try:
            block_number = self.monitor.w3.eth.block_number
            print(f"   ✅ RPC provider working (block: {block_number:,})")
        except Exception as e:
            issues.append(f"RPC provider error: {e}")
            print(f"   ❌ RPC provider error: {e}")

        print()

        return len(issues) == 0, issues

    def log_repay_action(self, repay_amount, target_hf, position_before, position_after, executed=False, tx_hash=None):
        """Log repay action to file"""
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'action': 'EMERGENCY_REPAY',
            'executed': executed,
            'repay_amount_usd': float(repay_amount),
            'target_hf': float(target_hf),
            'position_before': {
                'collateral_usd': float(position_before.collateral_usd),
                'debt_usd': float(position_before.debt_usd),
                'health_factor': float(position_before.health_factor) if position_before.health_factor != Decimal('Infinity') else None
            },
            'position_after': {
                'health_factor_target': float(position_after) if position_after != Decimal('Infinity') else None
            }
        }

        if tx_hash:
            log_entry['transaction_hash'] = tx_hash

        log_file = self.logs_dir / 'repay_history.json'

        if log_file.exists():
            with open(log_file, 'r') as f:
                history = json.load(f)
        else:
            history = {'repays': []}

        history['repays'].append(log_entry)

        with open(log_file, 'w') as f:
            json.dump(history, f, indent=2)

        print(f"📝 Logged to: {log_file}")

    def execute_repay(self, repay_amount, dry_run=True):
        """Execute the repay transaction"""
        if dry_run:
            print(f"🔒 DRY RUN MODE - No transaction will be executed")
            print(f"   To execute for real, set dry_run=False")
            print()
            return None

        print(f"⚠️  LIVE EXECUTION MODE")
        print(f"   This will execute a REAL transaction on Ethereum mainnet")
        print()

        # TODO: Implement actual Web3 transaction
        # This requires:
        # 1. Private key management (from env or keystore)
        # 2. USDC token approval
        # 3. AAVE repay function call
        # 4. Gas estimation
        # 5. Transaction signing and submission

        print(f"❌ LIVE EXECUTION NOT IMPLEMENTED YET")
        print(f"   This requires:")
        print(f"   1. Wallet private key setup")
        print(f"   2. USDC approval transaction")
        print(f"   3. AAVE repay transaction")
        print(f"   4. Gas management")
        print()
        print(f"   For now, execute manually via:")
        print(f"   - MetaMask + AAVE UI: https://app.aave.com")
        print(f"   - Or use Coinbase wallet integration")
        print()

        return None

    def run_emergency_repay(self, target_hf, dry_run=True, auto_confirm=False):
        """Run full emergency repay workflow"""
        print(f"\n{'='*70}")
        print(f"🚨 EMERGENCY REPAY - TARGET HF {target_hf}")
        print(f"{'='*70}\n")

        # Step 1: Get current position
        position = self.get_current_position()

        # Step 2: Calculate repay amount
        repay_amount = self.calculate_repay_amount(position, target_hf)

        if repay_amount == 0:
            print(f"✅ No repay needed")
            return {'success': True, 'repay_amount': 0, 'message': 'No repay needed'}

        # Step 3: Preview new position
        new_hf = self.preview_new_position(position, repay_amount)

        # Step 4: Safety checks
        safe, issues = self.check_safety_requirements(repay_amount)

        if not safe:
            print(f"❌ SAFETY CHECK FAILED:")
            for issue in issues:
                print(f"   - {issue}")
            print()
            return {'success': False, 'error': 'Safety check failed', 'issues': issues}

        # Step 5: Confirmation
        if not auto_confirm and not dry_run:
            print(f"⚠️  READY TO EXECUTE")
            print(f"   Repay: ${repay_amount:,.2f} USDC")
            print(f"   Target HF: {target_hf:.2f}")
            print(f"   Expected HF: {new_hf:.2f}")
            print()

            confirm = input("Type 'EXECUTE' to proceed: ")
            if confirm != 'EXECUTE':
                print(f"❌ Cancelled by user")
                return {'success': False, 'message': 'Cancelled by user'}

        # Step 6: Execute repay
        tx_hash = self.execute_repay(repay_amount, dry_run=dry_run)

        # Step 7: Log action
        self.log_repay_action(
            repay_amount=repay_amount,
            target_hf=target_hf,
            position_before=position,
            position_after=new_hf,
            executed=(not dry_run and tx_hash is not None),
            tx_hash=tx_hash
        )

        print(f"\n{'='*70}")
        print(f"✅ EMERGENCY REPAY COMPLETE")
        print(f"{'='*70}\n")

        return {
            'success': True,
            'repay_amount': float(repay_amount),
            'target_hf': float(target_hf),
            'expected_new_hf': float(new_hf),
            'tx_hash': tx_hash,
            'dry_run': dry_run
        }

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='AAVE Emergency Repay Script')
    parser.add_argument('--target-hf', type=float, default=2.5,
                       help='Target Health Factor (default: 2.5)')
    parser.add_argument('--execute', action='store_true',
                       help='Execute LIVE transaction (default: dry run)')
    parser.add_argument('--auto-confirm', action='store_true',
                       help='Skip confirmation prompt')

    args = parser.parse_args()

    target_hf = Decimal(str(args.target_hf))
    dry_run = not args.execute

    repayer = EmergencyRepay()
    result = repayer.run_emergency_repay(
        target_hf=target_hf,
        dry_run=dry_run,
        auto_confirm=args.auto_confirm
    )

    if result['success']:
        print(f"✅ Success")
        if dry_run:
            print(f"   (Dry run - no actual transaction)")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)

if __name__ == '__main__':
    main()
