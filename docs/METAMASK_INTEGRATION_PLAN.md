# 🦊 MetaMask Integration Plan

**Date:** October 30, 2025
**Purpose:** Complete MetaMask + blockchain infrastructure setup

---

## 🎯 WHAT WE HAVE vs WHAT WE NEED

### ✅ Currently Implemented:

**1. Etherscan API (Free Tier)**
- **Purpose:** Read ETH balances from public blockchain
- **Usage:** `metamask_balance_tracker.py` fetches balances for 3 addresses
- **Limitation:** Rate limited, basic balance queries only
- **Status:** ✅ Working (falls back to cache on rate limit)

**2. MetaMask Addresses Tracked:**
```
0x097dF24DE4fA66877339e6f75e5Af6d618B6489B - MetaMask Hot #1
0xC08413B63ecA84E2d9693af9414330dA88dcD81C - Ledger + MetaMask
0xcd2057ebbC340A77c0B55Da60dbEa26310071bDc - MetaMask Hot #2
```

### ❌ What We're Missing:

**1. Infura/Alchemy API Key**
- **Purpose:** Reliable blockchain RPC node access
- **Needed for:**
  - AAVE smart contract queries (health factor, position details)
  - Token balance queries (ERC20, stablecoins)
  - Transaction history
  - Contract state reading
  - Higher rate limits than Etherscan free tier
- **Status:** ❌ Not configured

**2. MetaMask SDK**
- **Purpose:** Connect dapp to MetaMask wallet for user actions
- **Needed for:**
  - Request account access
  - Sign transactions
  - Send transactions (if needed)
  - Interact with AAVE contracts (emergency actions)
  - Mobile wallet connections
- **Status:** ❌ Not integrated

**3. AAVE API Integration**
- **Purpose:** Monitor your $3,904.74 wstETH position
- **Needed for:**
  - Real-time health factor
  - Liquidation risk alerts
  - Yield tracking
  - Position details
- **Status:** ❌ Not implemented

---

## 🔧 INTEGRATION STRATEGY

### Phase 1: Infrastructure (Immediate)

#### 1.1 Get Infura API Key
**Priority:** HIGH (needed for AAVE monitoring)

**Steps:**
1. Go to https://infura.io
2. Sign up for free account
3. Create new project "SovereignShadow"
4. Get API key for Ethereum Mainnet
5. Add to `.env`:
   ```bash
   INFURA_PROJECT_ID="your_project_id"
   INFURA_API_KEY="your_api_key"
   INFURA_URL="https://mainnet.infura.io/v3/YOUR_PROJECT_ID"
   ```

**Alternative:** Alchemy (also free tier)
- Go to https://www.alchemy.com
- Better dashboard and analytics
- Same purpose as Infura
- Add to `.env`:
   ```bash
   ALCHEMY_API_KEY="your_api_key"
   ALCHEMY_URL="https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
   ```

#### 1.2 Get Etherscan API Key (Optional but Recommended)
**Priority:** MEDIUM (improves rate limits)

**Steps:**
1. Go to https://etherscan.io/apis
2. Sign up for free account
3. Create API key
4. Add to `.env`:
   ```bash
   ETHERSCAN_API_KEY="your_api_key"
   ```

**Benefit:**
- Increases rate limit from 1 call/5sec to 5 calls/sec
- Allows more frequent MetaMask balance checks

---

### Phase 2: AAVE Position Monitoring (High Priority)

#### 2.1 Implement AAVE Smart Contract Reader
**File to create:** `core/portfolio/aave_monitor.py`

**Purpose:** Read AAVE v3 position details using Web3.py + Infura

**What it needs to fetch:**
- **Health Factor:** Critical metric (currently unknown)
- **Collateral:** wstETH amount and value
- **Debt:** Any borrowed amounts
- **Liquidation Price:** When position becomes at risk
- **Yield/APY:** Current earning rate

**AAVE Contracts (Ethereum Mainnet):**
```python
AAVE_POOL = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"
AAVE_DATA_PROVIDER = "0x7B4EB56E7CD4b454BA8ff71E4518426369a138a3"
WSTETH_TOKEN = "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0"

YOUR_ADDRESS = "0xC08413B63ecA84E2d9693af9414330dA88dcD81C"
```

**Implementation:**
```python
from web3 import Web3
import os

class AAVEMonitor:
    def __init__(self):
        infura_url = os.getenv('INFURA_URL')
        self.w3 = Web3(Web3.HTTPProvider(infura_url))
        self.address = "0xC08413B63ecA84E2d9693af9414330dA88dcD81C"

    def get_health_factor(self) -> float:
        """Query AAVE contract for health factor"""
        # Use AAVE Data Provider contract
        # Returns health factor (e18 scaled)

    def get_position_details(self) -> dict:
        """Get complete AAVE position"""
        return {
            'health_factor': self.get_health_factor(),
            'collateral_usd': self.get_collateral_value(),
            'debt_usd': self.get_debt_value(),
            'liquidation_threshold': self.get_liquidation_threshold()
        }
```

#### 2.2 Update unified_portfolio_api.py
**Change:**
```python
def get_defi_positions(self) -> Dict[str, Any]:
    # OLD: Returns hardcoded placeholder
    # NEW: Query AAVE monitor for live data

    aave_monitor = AAVEMonitor()
    position = aave_monitor.get_position_details()

    return {
        'health_factor': position['health_factor'],  # REAL data
        'liquidation_risk': 'LOW' if position['health_factor'] > 2.0 else 'HIGH',
        ...
    }
```

---

### Phase 3: MetaMask SDK Integration (Lower Priority)

**When needed:** Only if you want to perform transactions from the system

**Use cases:**
- Emergency AAVE position adjustment
- Moving funds between wallets
- Interacting with DeFi protocols
- NFT transfers

**Implementation note:**
Since your Ledger is already connected to MetaMask, and all transactions require hardware confirmation, you may NOT need SDK integration unless building a web interface.

**Current setup works for:**
- ✅ Read-only monitoring (Etherscan API)
- ✅ Balance tracking (blockchain queries)
- ✅ Position viewing (once AAVE monitor implemented)

**MetaMask SDK only needed for:**
- ❌ Initiating transactions from code
- ❌ Automated trading with MetaMask addresses
- ❌ Web dapp interface

**Recommendation:** Skip SDK integration for now, focus on monitoring.

---

## 📋 IMMEDIATE ACTION ITEMS

### Step 1: Get Infura/Alchemy Key (5 minutes)
```bash
# Add to .env file:
INFURA_PROJECT_ID="get_from_infura_dashboard"
INFURA_API_KEY="get_from_infura_dashboard"
INFURA_URL="https://mainnet.infura.io/v3/YOUR_PROJECT_ID"
```

### Step 2: Implement AAVE Monitor (30 minutes)
**File:** `core/portfolio/aave_monitor.py`

**Requirements:**
```bash
pip install web3
```

**Test:**
```bash
python3 core/portfolio/aave_monitor.py
# Should output:
# Health Factor: X.XX
# Collateral: $X,XXX.XX
# Debt: $X,XXX.XX
# Status: SAFE/WARNING/DANGER
```

### Step 3: Integrate with Portfolio API (10 minutes)
**Update:** `unified_portfolio_api.py`
- Import AAVEMonitor
- Replace hardcoded AAVE data with live queries

### Step 4: Set Up Alerts (15 minutes)
**Create:** Alert system for health factor < 1.5

---

## 🎯 WHY THIS MATTERS

### Your Current Risk Exposure:

```
AAVE Position: $3,904.74 (63.3% of portfolio)
├── Current Status: UNKNOWN (no health factor data)
├── Risk: Protocol risk + liquidation risk
└── Action: Need real-time monitoring!

BTC Cold Storage: $2,231.74 (36.2% of portfolio)
├── Current Status: SAFE (hardware wallet)
├── Risk: Minimal
└── Action: Read-only monitoring (already implemented)
```

### Why AAVE Monitoring is Critical:

**Scenario 1: Health Factor Drops**
- Without monitoring: You don't know until liquidation
- With monitoring: Alert triggers at 1.5, time to act

**Scenario 2: Market Volatility**
- ETH price crash → wstETH collateral value drops
- If health factor < 1.0 → Position liquidated
- You lose: $3,904.74 (63% of portfolio!)

**Scenario 3: Yield Tracking**
- Currently earning yield on wstETH
- Without monitoring: Don't know APY or earnings
- With monitoring: Track performance over time

---

## 💡 RECOMMENDED SETUP

### Option A: Minimal (Just monitoring)
**What you need:**
- ✅ Etherscan API key (optional, improves rate limits)
- ✅ Infura API key (required for AAVE monitoring)
- ✅ AAVE monitor implementation
- ❌ MetaMask SDK (not needed for read-only)

**Cost:** FREE (all free tiers)
**Time:** ~1 hour setup
**Result:** Complete portfolio monitoring

### Option B: Full Integration (With transaction capability)
**What you need:**
- ✅ Everything from Option A
- ✅ MetaMask SDK integration
- ✅ Web interface for wallet connection
- ✅ Transaction signing workflow

**Cost:** FREE (SDKs are free)
**Time:** ~8-10 hours development
**Result:** Can execute transactions from system

**Recommendation:** Start with Option A (monitoring only)

---

## 🚨 CRITICAL: AAVE Position Needs Attention

### Your $3,904.74 AAVE Position:
```
Asset: Wrapped staked ETH (wstETH)
Protocol: AAVE v3 on Ethereum Mainnet
Address: 0xC08413B63ecA84E2d9693af9414330dA88dcD81C (Ledger)
Current Value: $3,904.74 (63.3% of portfolio)

Health Factor: ??? (UNKNOWN - NEED TO IMPLEMENT MONITORING!)
Liquidation Risk: ??? (UNKNOWN)
Yield APY: ??? (UNKNOWN)
```

### Without Monitoring:
- ❌ Don't know if position is safe
- ❌ Don't know yield earnings
- ❌ Can't detect liquidation risk
- ❌ No alerts if health factor drops

### With Monitoring:
- ✅ Real-time health factor tracking
- ✅ Liquidation risk alerts
- ✅ Yield performance tracking
- ✅ Peace of mind

---

## 📝 NEXT STEPS SUMMARY

1. **Get Infura API key** (5 min) - https://infura.io
2. **Add to .env file** (1 min)
3. **Implement AAVE monitor** (30 min) - I can do this
4. **Test AAVE monitoring** (5 min)
5. **Integrate with portfolio API** (10 min)
6. **Set up health factor alerts** (15 min)

**Total time:** ~1 hour
**Cost:** $0 (all free tiers)
**Benefit:** Complete visibility into 63% of your portfolio

---

## ❓ DO YOU WANT ME TO:

1. ✅ **Create AAVE monitor implementation** (after you get Infura key)
2. ✅ **Set up health factor alerts**
3. ✅ **Integrate with portfolio API**
4. ❌ **Skip MetaMask SDK** (not needed for monitoring)

**Your call:** Get Infura API key, then I'll build the AAVE monitoring system.

---

**Current Status:**
- Read-only blockchain queries: ✅ Working
- MetaMask balance tracking: ✅ Working (rate limited)
- AAVE position monitoring: ❌ NOT IMPLEMENTED (HIGH PRIORITY)
- Transaction capability: ❌ Not needed (Ledger handles this)

**Recommendation:** Focus on AAVE monitoring ASAP to protect your largest holding.
