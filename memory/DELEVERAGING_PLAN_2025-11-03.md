# 🏴 AAVE DELEVERAGING & REBALANCING PLAN
**Strategy:** Option A - Full Deleveraging (Lower Risk)
**Date:** November 3, 2025
**Status:** READY TO EXECUTE

---

## 📊 CURRENT POSITION (LIVE DATA)

```
AAVE Position:
├── Collateral: $3,488.62 wstETH
├── Debt: $1,158.53 USDC
├── Net Value: $2,330.09
└── Health Factor: 2.44 (⚠️ CAUTION)

Cold Storage:
├── BTC: $2,231.74
└── Other: ~$31 (ETH gas, USDT, XRP)

TOTAL PORTFOLIO: ~$4,592.83
```

## 🎯 CORRECTED ALLOCATION ANALYSIS

**Current vs Target:**
```
Asset    Current    Target    Delta      Action
─────────────────────────────────────────────────
ETH      50.7%      30.0%    -20.7%     REDUCE by $952
BTC      48.6%      40.0%    -8.6%      REDUCE by $395
SOL       0.0%      20.0%    +20.0%     BUY $918
XRP       0.1%      10.0%    +9.9%      BUY $456
```

**Key Insight:** You're OVER-allocated to both ETH and BTC. Need to diversify into SOL/XRP.

---

## 📋 DELEVERAGING EXECUTION PLAN

### Phase 1: Repay AAVE Debt (Full Deleveraging)

**Step 1.1: Calculate Exact Repayment**
```bash
# Check current debt (updates every block)
python3 modules/safety/aave_monitor_v2.py | grep "Debt:"

# Expected: ~$1,158.53 USDC
```

**Step 1.2: Source USDC for Repayment**

Option 1: Sell BTC (RECOMMENDED)
```bash
# Sell 0.011 BTC → $1,150 USDC
# Keeps BTC allocation closer to target (40%)
# Exchange: Coinbase (lowest fees for BTC→USDC)
```

Option 2: Partial wstETH Withdrawal
```bash
# Withdraw $1,200 wstETH first
# Unwrap wstETH → stETH → ETH
# Swap ETH → USDC
# Repay debt
# More complex, more gas fees
```

**Recommendation: Use Option 1 (Sell BTC)**

**Step 1.3: Execute Repayment via MetaMask + Ledger**
```
1. Connect Ledger to MetaMask
2. Go to: https://app.aave.com
3. Navigate to: Dashboard → Borrow
4. Click: Repay USDC
5. Amount: MAX (full debt)
6. Confirm: Sign with Ledger
7. Gas estimate: ~$15-30 ETH

Expected Result:
├── Debt: $0
├── Health Factor: ∞ (no debt)
└── Full collateral unlocked: $3,488.62 wstETH
```

---

### Phase 2: Withdraw Excess ETH from AAVE

**Step 2.1: Calculate Withdrawal Amount**
```python
# Target ETH allocation: 30% of $4,593 = $1,378
# Current wstETH: $3,489
# Excess to withdraw: $3,489 - $1,378 = $2,111

Withdraw: $2,111 wstETH (60.5% of collateral)
Keep: $1,378 wstETH (39.5% of collateral)
```

**Step 2.2: Execute Withdrawal**
```
1. Go to: https://app.aave.com
2. Navigate to: Dashboard → Supply
3. Click: Withdraw wstETH
4. Amount: 0.603 wstETH (~$2,111)
5. Confirm: Sign with Ledger

Expected Result:
├── wstETH in AAVE: $1,378 (30% allocation) ✅
├── wstETH in wallet: $2,111 (to convert)
└── Debt: $0
```

---

### Phase 3: Convert wstETH → Stablecoins

**Step 3.1: Unwrap wstETH**
```
# Use Lido: https://stake.lido.fi/withdrawals
# Or use DEX aggregator like 1inch

0.603 wstETH → 0.603 stETH → 0.603 ETH
Value: ~$2,111
Gas: ~$10-20
```

**Step 3.2: Swap ETH → USDC**
```
# Use Uniswap or Coinbase
0.603 ETH → $2,111 USDC
Slippage: 0.5%
Gas: ~$15-30

Expected proceeds: ~$2,080 USDC (after gas)
```

---

### Phase 4: Rebalance Portfolio (Buy SOL + XRP)

**Step 4.1: Transfer USDC to Exchanges**
```
Coinbase: $1,500 USDC (for SOL)
Binance US: $580 USDC (for XRP + fees)
```

**Step 4.2: Execute Purchases**
```
Buy Orders:
├── SOL: $918 @ market price (~$220) = 4.17 SOL
├── XRP: $456 @ market price (~$2.26) = 202 XRP
└── Trading fees: ~$20-30

Keep: ~$700 USDC as trading buffer
```

**Step 4.3: Optional - Trim BTC Slightly**
```
Current BTC: $2,232 (48.6%)
Target BTC: $1,837 (40%)
Excess: $395

Decision: Keep excess BTC for now
Reason: Already selling BTC for AAVE repayment ($1,150)
Total BTC sold: $1,150 + $395 = $1,545
New BTC value: $2,232 - $1,150 = $1,082 (too low)

REVISED: Don't trim BTC further
```

---

## 🎯 EXPECTED FINAL ALLOCATION

```
After Full Rebalancing:

Asset        Amount          Value      % of Portfolio   Target
─────────────────────────────────────────────────────────────────
BTC          0.0106 BTC      $1,082     23.6%           40%  ⚠️
ETH (wstETH) 0.394 wstETH    $1,378     30.0%           30%  ✅
SOL          4.17 SOL        $918       20.0%           20%  ✅
XRP          202 XRP         $456       9.9%            10%  ✅
USDC         $700            $700       15.3%           0%
Other        Various         $31        0.7%            -

TOTAL:                       $4,565     99.5%
```

**⚠️ NOTE:** BTC ends up under-allocated (23.6% vs 40% target) because we sold too much for AAVE repayment.

---

## 🔄 REVISED OPTIMAL STRATEGY

To maintain proper BTC allocation (40%), we should:

### REVISED Phase 1: Repay Debt Without Selling BTC
```bash
1. Withdraw $1,200 wstETH from AAVE first (before repaying)
2. Convert wstETH → ETH → USDC ($1,200)
3. Use $1,158 USDC to repay debt
4. Withdraw remaining wstETH ($2,289 - $1,200 = $1,089)
5. Convert remaining wstETH → USDC ($1,089)
6. Total USDC available: $1,131 ($42 leftover + $1,089)

Result:
├── BTC: $2,232 (48.6%) - Still over, but less dramatic
├── ETH: $1,378 (from remaining AAVE collateral)
├── SOL: $918 (buy with USDC)
├── XRP: $456 (buy with USDC)
└── USDC buffer: ~$200
```

### Wait - This Requires HF Check!

**Problem:** Can't withdraw collateral while debt exists if HF drops below 1.0

**Solution: Two-Step Process**
```
Step 1: Repay DEBT first (selling 0.011 BTC → $1,150 USDC)
Step 2: Withdraw ALL wstETH ($3,489)
Step 3: Rebuy BTC with $395 from wstETH proceeds
Step 4: Buy SOL ($918) and XRP ($456)

Final allocation:
├── BTC: $2,232 - $1,150 + $395 = $1,477 (32%) ⚠️ Still low
├── ETH: $1,378 (30%) ✅
├── SOL: $918 (20%) ✅
├── XRP: $456 (10%) ✅
└── USDC: $336 (7%)
```

---

## ✅ FINAL RECOMMENDED APPROACH

### Simplified 3-Step Plan:

**STEP 1: Repay Debt**
- Sell 0.011 BTC → $1,150 USDC on Coinbase
- Repay full AAVE debt ($1,158)
- Health Factor → ∞

**STEP 2: Withdraw & Convert**
- Withdraw ALL wstETH ($3,489) from AAVE
- Convert to USDC (~$3,489)
- Total USDC available: $3,489

**STEP 3: Rebuild Balanced Portfolio**
- Buy BTC: $1,837 (40% target)
- Buy ETH: $1,378 (30% target)
- Buy SOL: $918 (20% target)
- Buy XRP: $459 (10% target)
- Total: $4,592

**Net change in BTC:** -$1,150 (sold) +$1,837 (rebought) = +$687
**Final BTC:** $2,232 + $687 = $2,919 (63.6%) ⚠️ OVER-ALLOCATED!

---

## 🤯 THE MATH PROBLEM

**We have a circular dependency:**
- Need to sell BTC to repay debt → BTC drops
- Need to buy BTC back to reach 40% → BTC rises
- The portfolio total changes during rebalancing

**Root cause:** Starting portfolio is 90%+ BTC+ETH, need to rotate into SOL/XRP

---

## 🎯 CLEANEST SOLUTION (FINAL)

### Use AAVE as ETH Source for Everything:

**STEP 1:** Withdraw $1,158 wstETH (for debt repayment)
- Convert to USDC
- Repay debt immediately
- Remaining collateral: $2,330 wstETH

**STEP 2:** Withdraw additional $952 wstETH (excess ETH)
- Target ETH: $1,378 (30%)
- Remaining in AAVE: $1,378 wstETH ✅
- Withdrawn total: $2,110 wstETH

**STEP 3:** Convert withdrawn wstETH → USDC ($2,110)

**STEP 4:** Use USDC to buy SOL + XRP
- Buy SOL: $918
- Buy XRP: $456
- Total: $1,374
- Leftover: $736 USDC buffer

**STEP 5:** Keep BTC unchanged at $2,232

**Final Portfolio:**
```
BTC:  $2,232 (46.2%) ⚠️ Still over 40% target
ETH:  $1,378 (28.5%) ✅ Close to 30%
SOL:  $918 (19.0%) ✅ Close to 20%
XRP:  $456 (9.4%) ✅ Close to 10%
USDC: $736 (15.2%) - Emergency buffer

Total: $4,830
```

**To fix BTC over-allocation:** Sell $300 BTC → buy more SOL/XRP later

---

## 📱 EXECUTION CHECKLIST

- [ ] **Day 1:** Withdraw $1,158 wstETH from AAVE
- [ ] **Day 1:** Convert wstETH → USDC
- [ ] **Day 1:** Repay AAVE debt (HF → ∞)
- [ ] **Day 2:** Withdraw $952 wstETH from AAVE
- [ ] **Day 2:** Convert wstETH → USDC
- [ ] **Day 3:** Transfer USDC to Coinbase + Binance
- [ ] **Day 3:** Buy 4.17 SOL on Coinbase
- [ ] **Day 3:** Buy 202 XRP on Binance US
- [ ] **Day 7:** Review allocation, trim BTC if still >45%

---

## ⚠️ RISKS & MITIGATION

**Risk 1:** ETH price drops during withdrawal
- Mitigation: Execute all swaps same day, use limit orders

**Risk 2:** Gas fees eat into proceeds
- Mitigation: Wait for low gas (<20 gwei), batch transactions

**Risk 3:** Slippage on wstETH → ETH swaps
- Mitigation: Use 1inch aggregator, 0.5% max slippage

**Risk 4:** Exchange deposit delays
- Mitigation: Use fast networks (Ethereum mainnet for USDC)

---

## 💰 COST ESTIMATE

```
Gas Fees:
├── Repay debt: ~$20
├── Withdraw collateral (2x): ~$40
├── Unwrap wstETH (2x): ~$30
├── Swap to USDC (2x): ~$40
└── Total gas: ~$130

Trading Fees:
├── Coinbase (SOL): $4.59 (0.5%)
├── Binance (XRP): $2.28 (0.5%)
└── Total fees: ~$7

TOTAL COST: ~$137
```

---

## 🎯 NEXT STEP

Reply with **"EXECUTE"** to begin, or ask questions if you need clarification on any step.

**Estimated Time:** 3-4 days
**Risk Level:** LOW (no leverage after completion)
**Complexity:** MEDIUM (requires MetaMask + Ledger + DEX + CEX)
