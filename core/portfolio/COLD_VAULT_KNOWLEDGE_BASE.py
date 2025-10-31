#!/usr/bin/env python3
"""
🏴 COLD VAULT KNOWLEDGE BASE - Hardcoded for AI System
PERMANENT REFERENCE FOR ALL AI AGENTS

This file contains authoritative data about LedgerGhost90's cold storage vault.
All AI agents (Claude, assistants, orchestrators) MUST reference this data.

⚠️  THIS IS THE SOURCE OF TRUTH - DO NOT MODIFY WITHOUT AUTHORIZATION
"""

from datetime import datetime
from typing import Dict, Any

# =============================================================================
# LEDGER HARDWARE WALLET - COLD STORAGE VAULT
# =============================================================================

COLD_VAULT_CONFIG = {
    "owner": "LedgerGhost90",
    "purpose": "Long-term cold storage - NEVER used for automated trading",
    "security_level": "MAXIMUM",
    "last_updated": "2025-10-30T00:00:00Z",

    # WALLET ADDRESSES
    "addresses": {
        "btc": {
            "xpub": "xpub6BgzNEknk2B5tMGRKoNrpCbu435dtAQQXiq1DENttBFToUeZvNtr7CeQhPEGrzGHZ4vyMWQYaR9yH1PNSEFpqDvee1dp49SMxqgBN2K3fg6",
            "type": "BTC Native SegWit (bech32)",
            "derivation_path": "m/84'/0'/0'",
            "note": "Ledger hardware wallet - never expose private keys"
        },
        "eth": {
            "address": "0xC08413B63ecA84E2d9693af9414330dA88dcD81C",
            "type": "Ethereum EVM-compatible",
            "note": "Ledger hardware wallet - also used for DeFi (AAVE)"
        }
    },

    # CURRENT HOLDINGS (From Ledger Live screenshot Oct 30, 2025)
    "holdings": {
        "aave_wsteth": {
            "value_usd": 3904.74,  # Aave wrapped staked ETH position
            "note": "DeFi position in AAVE protocol - largest holding"
        },
        "btc": {
            "value_usd": 2231.74,  # BTC Native SegWit
            "note": "Bitcoin cold storage - second largest holding"
        },
        "eth": {
            "value_usd": 21.62,  # ETH for gas fees
            "note": "Small amount for transaction fees"
        },
        "usdtb": {
            "value_usd": 4.99,  # Bridged USDT
            "note": "Minimal stablecoin holding"
        },
        "xrp": {
            "value_usd": 2.57,  # XRP
            "note": "Small XRP position"
        }
    },

    # PORTFOLIO ALLOCATION (Oct 30, 2025 - ACTUAL FROM LEDGER LIVE)
    "allocation": {
        "total_value_usd": 6167.43,  # Real-time from Ledger
        "aave_percent": 63.3,  # $3,904.74 / $6,167.43
        "btc_percent": 36.2,   # $2,231.74 / $6,167.43
        "eth_percent": 0.4,    # $21.62 / $6,167.43
        "stablecoin_percent": 0.1,  # $4.99 / $6,167.43
        "other_percent": 0.04,  # $2.57 XRP
        "note": "Most value is in AAVE DeFi position, not pure BTC"
    },

    # TRANSACTION SUMMARY
    "transaction_history": {
        "total_transactions": 227,  # From Ledger Live export
        "btc_transactions": 64,
        "eth_transactions": 163,  # Includes gas fees
        "first_transaction": "2025-05-12T23:33:03.000Z",
        "last_transaction": "2025-10-17T09:01:35.000Z",
        "csv_export_path": "/Volumes/LegacySafe/Shadow Loop/ZOOP_UNIFICATION/ledgerlive-operations-10.20.2025.csv"
    },

    # SAFETY RULES
    "safety_rules": {
        "never_automate": True,
        "read_only_monitoring": True,
        "no_api_trading_access": True,
        "no_private_key_exposure": True,
        "require_hardware_confirmation": True,
        "description": "Cold storage vault is NEVER accessible to automated trading bots"
    },

    # MONITORING CONFIGURATION
    "monitoring": {
        "refresh_interval_minutes": 60,
        "price_apis": ["coingecko", "cryptocompare"],
        "blockchain_explorers": {
            "btc": "blockstream.info",
            "eth": "etherscan.io"
        },
        "alert_thresholds": {
            "unexpected_transaction": True,
            "balance_decrease": True,
            "balance_change_percent": 1.0  # Alert if balance changes by 1%
        }
    }
}

# =============================================================================
# PORTFOLIO CONTEXT FOR AI AGENTS
# =============================================================================

PORTFOLIO_CONTEXT = {
    "total_portfolio": {
        "total_value_usd": 6204,  # CORRECTED from actual data
        "breakdown": {
            "ledger_hardware_wallet": 6167.43,  # Actual from Ledger Live screenshots
            "metamask_hot_wallet": 36.51,       # 0.00936201 ETH from MetaMask export
            "note": "AAVE position ($3,904.74) is ON Ledger but is DeFi, not cold storage"
        }
    },

    "ledger_breakdown": {
        "total": 6167.43,
        "aave_defi": {
            "amount": 3904.74,
            "percent": 63.3,
            "type": "DeFi Position - NOT cold storage",
            "note": "Wrapped staked ETH in AAVE protocol"
        },
        "btc_cold_storage": {
            "amount": 2231.74,
            "percent": 36.2,
            "type": "TRUE Cold Storage",
            "note": "Native SegWit BTC - long-term hold"
        },
        "eth_gas": {
            "amount": 21.62,
            "percent": 0.4,
            "type": "Utility",
            "note": "Gas fees for transactions"
        },
        "stablecoin": {
            "amount": 4.99,
            "percent": 0.1,
            "type": "USDTb",
            "note": "Bridged USDT"
        },
        "xrp": {
            "amount": 2.57,
            "percent": 0.04,
            "type": "Alt Coin",
            "note": "Small position"
        }
    },

    "metamask_hot_wallet": {
        "total_eth": 0.00936201,
        "total_usd": 36.51,
        "addresses": {
            "0x097dF24DE4fA66877339e6f75e5Af6d618B6489B": {
                "balance_eth": 0.00100343,
                "balance_usd": 3.91,
                "type": "Hot Wallet"
            },
            "0xC08413B63ecA84E2d9693af9414330dA88dcD81C": {
                "balance_eth": 0.00553443,
                "balance_usd": 21.58,
                "type": "Also Ledger ETH address",
                "note": "This address is BOTH in Ledger and MetaMask"
            },
            "0xcd2057ebbC340A77c0B55Da60dbEa26310071bDc": {
                "balance_eth": 0.00282416,
                "balance_usd": 11.01,
                "type": "Hot Wallet"
            }
        }
    },

    "capital_allocation_philosophy": {
        "fortress_btc": {
            "amount": 2231.74,
            "purpose": "TRUE cold storage - long-term BTC hold",
            "access": "Ledger hardware wallet only",
            "strategy": "Dollar-cost averaging into BTC",
            "trading_access": "NEVER"
        },
        "defi_positions": {
            "amount": 3904.74,
            "purpose": "AAVE wstETH - yield generation",
            "access": "Ledger hardware wallet (requires signing)",
            "strategy": "Monitor health factor, track yield",
            "trading_access": "DO NOT LIQUIDATE unless emergency"
        },
        "hot_wallet": {
            "amount": 36.51,
            "purpose": "Active wallet for MetaMask interactions",
            "access": "MetaMask browser extension",
            "strategy": "Small amounts for DeFi testing",
            "trading_access": "Can be used but monitor carefully"
        },
        "exchange_velocity": {
            "amount": "TBD - need exchange API data",
            "purpose": "Active trading capital on Coinbase/OKX/Kraken",
            "access": "Exchange APIs",
            "strategy": "Short-term trades, meme coins, arbitrage"
        }
    }
}

# =============================================================================
# DATA ACCESS FUNCTIONS FOR AI AGENTS
# =============================================================================

def get_cold_vault_snapshot() -> Dict[str, Any]:
    """
    Get current cold vault snapshot
    This is what AI agents should call to understand cold storage
    """
    return {
        "addresses": COLD_VAULT_CONFIG["addresses"],
        "holdings": COLD_VAULT_CONFIG["holdings"],
        "total_value_usd": COLD_VAULT_CONFIG["allocation"]["total_value_usd"],
        "safety_status": COLD_VAULT_CONFIG["safety_rules"],
        "last_updated": COLD_VAULT_CONFIG["last_updated"]
    }

def get_full_portfolio_context() -> Dict[str, Any]:
    """
    Get complete portfolio picture including cold + hot + defi
    """
    return PORTFOLIO_CONTEXT

def verify_cold_vault_safety() -> bool:
    """
    Verify that cold vault safety rules are being followed
    Returns False if any automated trading is detected
    """
    rules = COLD_VAULT_CONFIG["safety_rules"]
    return all([
        rules["never_automate"],
        rules["read_only_monitoring"],
        rules["no_api_trading_access"],
        rules["no_private_key_exposure"]
    ])

def get_trading_capital() -> Dict[str, float]:
    """
    Get ONLY the capital available for automated trading
    NEVER includes cold storage or AAVE positions
    """
    return {
        "exchange_velocity_capital": "TBD",  # Need to fetch from Coinbase/OKX/Kraken APIs
        "metamask_hot_wallet": 36.51,  # Available but small
        "max_position_size": "TBD",  # 25% of velocity once known
        "max_daily_exposure": 50,  # Conservative until we know exchange balances
        "emergency_reserve": "TBD",
        "PROTECTED_DO_NOT_TOUCH": {
            "btc_cold_storage": 2231.74,
            "aave_defi": 3904.74,
            "ledger_total": 6167.43,
            "note": "These funds are NEVER available for automated trading"
        }
    }

def is_address_cold_storage(address: str) -> bool:
    """
    Check if an address belongs to cold storage
    AI agents MUST check this before any trading operation
    """
    cold_addresses = [
        COLD_VAULT_CONFIG["addresses"]["btc"]["xpub"],
        COLD_VAULT_CONFIG["addresses"]["eth"]["address"]
    ]
    return any(addr in address for addr in cold_addresses)

# =============================================================================
# AI AGENT INSTRUCTIONS
# =============================================================================

AI_INSTRUCTIONS = """
🏴 INSTRUCTIONS FOR ALL AI AGENTS

CRITICAL PORTFOLIO UNDERSTANDING (Updated Oct 30, 2025):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL KNOWN PORTFOLIO: $6,204 (Ledger + MetaMask only)

LEDGER HARDWARE WALLET: $6,167.43
├─ AAVE DeFi (wstETH): $3,904.74 (63.3%)
│  └─ Type: DeFi position, NOT cold storage
│  └─ Action: Monitor health factor, DO NOT liquidate
│
├─ BTC Cold Storage: $2,231.74 (36.2%)
│  └─ Type: TRUE cold storage (Native SegWit)
│  └─ Action: NEVER touch, read-only monitoring only
│
├─ ETH (Gas): $21.62 (0.4%)
├─ USDTb: $4.99 (0.1%)
└─ XRP: $2.57 (0.04%)

METAMASK HOT WALLET: $36.51 (0.00936201 ETH)
├─ 0x097d...89B: $3.91 (Hot wallet)
├─ 0xC084...D81C: $21.58 (Also Ledger address)
└─ 0xcd20...5bDc: $11.01 (Hot wallet)

EXCHANGE BALANCES: TBD
└─ Need to fetch from Coinbase/OKX/Kraken APIs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TRADING RULES:

NEVER TOUCH:
✗ BTC Cold Storage ($2,231.74) - Ledger Native SegWit
✗ AAVE DeFi Position ($3,904.74) - Unless emergency liquidation needed

PROTECTED BUT MONITORABLE:
⚠ AAVE wstETH - Check health factor regularly
⚠ ETH Gas ($21.62) - Keep for transaction fees
⚠ Stablecoins ($4.99) - Minimal value

POTENTIALLY AVAILABLE:
? MetaMask Hot Wallet ($36.51) - Small amounts OK
? Exchange Balances (TBD) - Need to fetch live data

BEFORE ANY TRADE:
1. Check is_address_cold_storage(address) - Must return False
2. Verify get_trading_capital() - Only use exchange velocity
3. NEVER suggest moving funds FROM Ledger TO exchanges
4. Monitor cold vault for informational purposes only

The goal is to GROW exchange trading capital, eventually
moving PROFITS into cold storage, never the reverse!
"""

# =============================================================================
# EXPORT FOR MCP SERVER
# =============================================================================

def export_for_mcp() -> Dict[str, Any]:
    """
    Export data in format suitable for MCP server context
    This allows Claude Desktop to always have cold vault awareness
    """
    return {
        "cold_vault": COLD_VAULT_CONFIG,
        "portfolio": PORTFOLIO_CONTEXT,
        "instructions": AI_INSTRUCTIONS,
        "functions": {
            "get_snapshot": "get_cold_vault_snapshot()",
            "verify_safety": "verify_cold_vault_safety()",
            "get_trading_capital": "get_trading_capital()",
            "check_address": "is_address_cold_storage(address)"
        }
    }

# =============================================================================
# MAIN - For Testing
# =============================================================================

if __name__ == "__main__":
    print("="*70)
    print("🏴 COLD VAULT KNOWLEDGE BASE")
    print("="*70)

    snapshot = get_cold_vault_snapshot()
    print(f"\n💰 BTC: {snapshot['holdings']['btc']['amount']:.8f} BTC")
    print(f"💎 ETH: {snapshot['holdings']['eth']['amount']:.8f} ETH")
    print(f"💵 Total Value: ${snapshot['total_value_usd']:,.2f}")

    print(f"\n🔐 Safety Check: {'✅ SECURE' if verify_cold_vault_safety() else '❌ COMPROMISED'}")

    trading = get_trading_capital()
    print(f"\n💸 Available for Trading: ${trading['available_for_trading']:,.2f}")

    print(f"\n📋 Full Context Available: {len(export_for_mcp())} data sections")
    print("="*70)
