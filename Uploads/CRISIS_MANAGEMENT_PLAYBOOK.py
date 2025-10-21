#!/usr/bin/env python3
"""
🛡️ CRISIS MANAGEMENT PLAYBOOK - Battle-Tested Crash Strategies
Based on lessons learned from October 2025 BTC crashes

CORE PHILOSOPHY:
- HODL cold storage through chaos (NEVER borrow against Ledger)
- Stop losses cause you to sell bottoms
- -10% to -20% crashes are NORMAL and recoverable
- Only liquidate on STRUCTURAL breaks, not volatility

LESSONS LEARNED:
✅ October Crash #1: HODL'd Ledger → Recovered
✅ October Crash #2: HODL'd Ledger → Recovered  
❌ System suggested liquidation → Ignored (CORRECT)
❌ System suggested borrowing → Ignored (CORRECT)
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/ai_enhanced/crisis_management.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CrisisManagement")

@dataclass
class CrashLevel:
    """Define crash severity levels"""
    name: str
    threshold_percent: float  # Negative percentage from recent high
    action: str
    reasoning: str
    emotion_check: str

class CrisisManagementPlaybook:
    """Battle-tested strategies for surviving market crashes"""
    
    def __init__(self):
        self.crash_levels = {
            "NOISE": CrashLevel(
                name="Market Noise",
                threshold_percent=-5.0,
                action="IGNORE - Normal volatility",
                reasoning="Markets move 5% constantly. This is not a crash.",
                emotion_check="😴 Go touch grass. This isn't even a dip."
            ),
            "HEALTHY_DIP": CrashLevel(
                name="Healthy Dip",
                threshold_percent=-10.0,
                action="ACCUMULATE - Buy opportunity",
                reasoning="10% dips happen 3-5 times per year. Smart money accumulates.",
                emotion_check="😎 This is why you keep stablecoins ready."
            ),
            "CORRECTION": CrashLevel(
                name="Correction",
                threshold_percent=-20.0,
                action="HODL & DCA - Major opportunity",
                reasoning="20% corrections are textbook healthy. BTC has recovered from 50+ of these.",
                emotion_check="💪 Your Ledger holdings are SAFE. This is temporary."
            ),
            "BEAR_MARKET": CrashLevel(
                name="Bear Market",
                threshold_percent=-50.0,
                action="HODL LEDGER, ACCUMULATE HOT WALLET - Generational opportunity",
                reasoning="50% crashes happen once per cycle. Previous holders who sold regret it.",
                emotion_check="🧘 2013: -87%, recovered. 2017: -84%, recovered. 2022: -77%, recovered. You'll be fine."
            ),
            "STRUCTURAL_BREAK": CrashLevel(
                name="Structural Break",
                threshold_percent=-80.0,
                action="EVALUATE FUNDAMENTALS - Rare",
                reasoning="Only happens if Bitcoin fundamentals break (never has in 15 years).",
                emotion_check="🔍 Check: Is Bitcoin itself broken? No? Then HODL."
            )
        }
        
        # CRITICAL RULES - These override all logic
        self.iron_laws = {
            "ledger_protection": {
                "rule": "NEVER borrow against Ledger",
                "reasoning": "Leverage = liquidation risk. October crashes proved this.",
                "status": "IMMUTABLE"
            },
            "no_steth_borrowing": {
                "rule": "NEVER use stETH as collateral for borrowing",
                "reasoning": "ETH drops >40% in crashes. AAVE liquidation = permanent loss.",
                "status": "IMMUTABLE"
            },
            "no_panic_selling": {
                "rule": "NEVER sell cold storage during crashes",
                "reasoning": "You don't have a crystal ball. Every crash has recovered.",
                "status": "IMMUTABLE"
            },
            "hot_wallet_flexibility": {
                "rule": "Hot wallet ($1,663) is for active trading only",
                "reasoning": "This is 'risk capital'. Can trade aggressively here.",
                "status": "FLEXIBLE"
            },
            "stop_losses_disabled_crashes": {
                "rule": "DISABLE stop losses during -10%+ crashes",
                "reasoning": "Stop losses in crashes = selling the bottom to whales.",
                "status": "CONDITIONAL"
            }
        }
        
        # Crash history tracking
        self.crash_history = []
        self.recent_high = None
        self.recent_high_date = None
        
    def assess_crash_severity(self, current_price: float, asset: str = "BTC") -> Tuple[CrashLevel, float]:
        """
        Assess crash severity and return appropriate action
        
        Returns:
            (CrashLevel, drawdown_percent)
        """
        # Update recent high
        if self.recent_high is None or current_price > self.recent_high:
            self.recent_high = current_price
            self.recent_high_date = datetime.now()
            logger.info(f"📈 New high for {asset}: ${current_price:,.2f}")
            
            # Not a crash
            return self.crash_levels["NOISE"], 0.0
        
        # Calculate drawdown
        drawdown_percent = ((current_price - self.recent_high) / self.recent_high) * 100
        
        logger.info(f"📊 {asset} Drawdown: {drawdown_percent:.2f}% from ${self.recent_high:,.2f}")
        
        # Determine crash level
        if drawdown_percent > -5:
            level = self.crash_levels["NOISE"]
        elif drawdown_percent > -10:
            level = self.crash_levels["HEALTHY_DIP"]
        elif drawdown_percent > -20:
            level = self.crash_levels["CORRECTION"]
        elif drawdown_percent > -50:
            level = self.crash_levels["BEAR_MARKET"]
        else:
            level = self.crash_levels["STRUCTURAL_BREAK"]
        
        return level, drawdown_percent
    
    def get_crisis_action(self, current_price: float, asset: str = "BTC") -> Dict:
        """Get recommended action during market crisis"""
        level, drawdown = self.assess_crash_severity(current_price, asset)
        
        # Log crash event
        crash_event = {
            "timestamp": datetime.now().isoformat(),
            "asset": asset,
            "current_price": current_price,
            "recent_high": self.recent_high,
            "drawdown_percent": drawdown,
            "severity_level": level.name,
            "action": level.action
        }
        self.crash_history.append(crash_event)
        
        return {
            "severity": level.name,
            "drawdown_percent": drawdown,
            "action": level.action,
            "reasoning": level.reasoning,
            "emotion_check": level.emotion_check,
            "iron_laws_active": self.iron_laws,
            "timestamp": datetime.now().isoformat()
        }
    
    def check_iron_law_violation(self, proposed_action: str) -> Tuple[bool, str]:
        """
        Check if a proposed action violates iron laws
        
        Returns:
            (is_violation, violation_message)
        """
        action_lower = proposed_action.lower()
        
        # Check for Ledger borrowing
        if any(word in action_lower for word in ["borrow", "leverage", "collateral", "loan"]):
            if "ledger" in action_lower or "steth" in action_lower or "seth" in action_lower:
                return True, "🚨 VIOLATION: Attempting to borrow against Ledger/stETH. This is FORBIDDEN after October crashes."
        
        # Check for panic selling cold storage
        if any(word in action_lower for word in ["sell", "liquidate", "exit"]):
            if "ledger" in action_lower or "cold storage" in action_lower or "vault" in action_lower:
                return True, "🚨 VIOLATION: Attempting to sell cold storage during crash. This is FORBIDDEN."
        
        # Check for stop loss during major crash
        if "stop loss" in action_lower or "stop-loss" in action_lower:
            if self.recent_high and self.recent_high > 0:
                # If we're in a crash, stop losses are disabled
                current_drawdown = ((0 - self.recent_high) / self.recent_high) * 100
                if current_drawdown < -10:
                    return True, f"🚨 VIOLATION: Stop losses DISABLED during {current_drawdown:.1f}% crash. You'll sell the bottom."
        
        return False, "✅ Action does not violate iron laws"
    
    def get_crash_playbook_summary(self) -> str:
        """Generate comprehensive crash playbook summary"""
        summary = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                     🛡️ CRISIS MANAGEMENT PLAYBOOK                            ║
║                  Battle-Tested Strategies from October 2025                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

📜 IRON LAWS (IMMUTABLE):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣  NEVER BORROW AGAINST LEDGER
    Reason: Leverage = liquidation risk in crashes
    October Lesson: You were RIGHT to ignore borrowing suggestions

2️⃣  NEVER USE stETH AS COLLATERAL
    Reason: ETH crashes >40% regularly, AAVE liquidates you
    October Lesson: "Good thing I didn't listen" - You

3️⃣  NEVER SELL COLD STORAGE IN CRASHES
    Reason: All previous crashes recovered 100%
    October Lesson: HODL'd through two crashes → Still whole

4️⃣  HOT WALLET = RISK CAPITAL ONLY
    Reason: Your $1,663 Coinbase is for aggressive trading
    Can be traded, can lose it, separate from vault

5️⃣  DISABLE STOP LOSSES IN CRASHES
    Reason: Stop losses in -10%+ crashes = selling bottom to whales
    October Lesson: Market makers hunt stop losses

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 CRASH SEVERITY MATRIX:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  DRAWDOWN    │ SEVERITY       │ ACTION                    │ EMOTION CHECK
─────────────┼────────────────┼───────────────────────────┼─────────────────────
  0% to -5%  │ 😴 Noise       │ IGNORE                    │ Go touch grass
  -5% to -10%│ 😎 Healthy Dip │ ACCUMULATE                │ Buy opportunity
 -10% to -20%│ 💪 Correction  │ HODL & DCA                │ This is normal
 -20% to -50%│ 🧘 Bear Market │ HODL LEDGER, DCA hot      │ Generational buy
 -50% to -80%│ 🔍 Structural  │ EVALUATE FUNDAMENTALS     │ Check if BTC broken

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 WHAT TO DO IN OCTOBER-STYLE CRASHES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ DO THIS:
   • HODL your Ledger ($6,600) - It's your fortress
   • Turn OFF market monitoring apps (reduces panic)
   • Use hot wallet ($1,663) for tactical DCA buys
   • Check fundamentals: Is Bitcoin itself broken? (Answer: Never has been)
   • Set price alerts for recovery, not further drops

❌ DON'T DO THIS:
   • Borrow against Ledger (liquidation trap)
   • Use stETH as AAVE collateral (liquidation trap)
   • Sell cold storage (permanent loss)
   • Set tight stop losses (whale hunting ground)
   • Panic trade hot wallet (emotion-driven loss)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 YOUR CAPITAL STRUCTURE (PROTECTED):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔒 LEDGER VAULT: $6,600 (80%)
   • NEVER borrow against
   • NEVER sell in crashes
   • NEVER leverage
   • HODL through ANY crash
   • Status: SACRED & UNTOUCHABLE

⚡ HOT WALLET: $1,663 (20%)  
   • Active trading allowed
   • Can use for crash DCA
   • Can lose without panic
   • Separate from vault mentally
   • Status: RISK CAPITAL

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 HISTORICAL CRASH RECOVERY DATA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2013: BTC -87% crash → Recovered + 10,000% gain
2017: BTC -84% crash → Recovered + 1,500% gain  
2020: BTC -60% crash (COVID) → Recovered + 600% gain
2022: BTC -77% crash → Recovered + 150% gain
2025: BTC -15% crashes (Oct) → You HODL'd (CORRECT)

LESSON: Every crash that didn't kill you, made you richer if you held.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 OCTOBER 2025 LESSONS LEARNED:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Crash #1 (Early October):
   ❌ System said: "Liquidate positions"
   ✅ You did: HODL'd Ledger
   📊 Result: Recovered within days

Crash #2 (Late October):  
   ❌ System said: "Borrow against stETH is safe"
   ✅ You did: Ignored borrowing trap
   📊 Result: Avoided liquidation cascade

KEY INSIGHT: Your instincts > Algorithmic panic logic

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"Fearless. Bold. Smiling through chaos." 
    - Your words. Your truth. Your playbook.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return summary
    
    def override_system_suggestions(self, system_suggestion: str) -> Dict:
        """
        Override dangerous system suggestions with crisis playbook logic
        
        Args:
            system_suggestion: The suggestion from other parts of the system
            
        Returns:
            Dict with override decision and reasoning
        """
        is_violation, message = self.check_iron_law_violation(system_suggestion)
        
        if is_violation:
            return {
                "override": True,
                "original_suggestion": system_suggestion,
                "violation_message": message,
                "corrected_action": "HODL cold storage, use hot wallet for opportunities only",
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "override": False,
            "original_suggestion": system_suggestion,
            "validation": "✅ Suggestion does not violate crisis playbook",
            "timestamp": datetime.now().isoformat()
        }
    
    def save_crash_history(self):
        """Save crash history to file"""
        Path("logs/ai_enhanced").mkdir(parents=True, exist_ok=True)
        
        history_file = Path("logs/ai_enhanced/crash_history.json")
        with open(history_file, 'w') as f:
            json.dump({
                "crash_history": self.crash_history,
                "iron_laws": self.iron_laws,
                "last_updated": datetime.now().isoformat()
            }, f, indent=2)
        
        logger.info(f"📄 Crash history saved to {history_file}")
    
    def display_current_status(self, btc_price: Optional[float] = None):
        """Display current crisis management status"""
        print(self.get_crash_playbook_summary())
        
        if btc_price:
            print("\n🔍 CURRENT MARKET STATUS:")
            print("=" * 80)
            crisis_action = self.get_crisis_action(btc_price, "BTC")
            print(f"BTC Price: ${btc_price:,.2f}")
            print(f"Severity: {crisis_action['severity']}")
            print(f"Drawdown: {crisis_action['drawdown_percent']:.2f}%")
            print(f"Action: {crisis_action['action']}")
            print(f"Reasoning: {crisis_action['reasoning']}")
            print(f"Emotion Check: {crisis_action['emotion_check']}")
            print("=" * 80)

def main():
    """Main execution - Display crisis playbook"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║             🛡️ CRISIS MANAGEMENT PLAYBOOK - INITIALIZATION                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    playbook = CrisisManagementPlaybook()
    
    # Display full playbook
    playbook.display_current_status()
    
    print("\n\n📋 TESTING IRON LAW ENFORCEMENT:")
    print("=" * 80)
    
    # Test dangerous suggestions
    dangerous_suggestions = [
        "Liquidate Ledger positions to prevent further losses",
        "Use stETH as collateral on AAVE to borrow stablecoins",
        "Set 5% stop loss on all cold storage positions",
        "Borrow against Ledger to buy the dip with leverage"
    ]
    
    for suggestion in dangerous_suggestions:
        result = playbook.override_system_suggestions(suggestion)
        if result["override"]:
            print(f"\n❌ BLOCKED: {suggestion}")
            print(f"   Reason: {result['violation_message']}")
            print(f"   Corrected: {result['corrected_action']}")
        else:
            print(f"\n✅ ALLOWED: {suggestion}")
    
    print("\n" + "=" * 80)
    print("✅ Crisis Management Playbook loaded and protecting your capital.")
    print("📄 Run this script anytime you feel panicked during a crash.")
    print("=" * 80)

if __name__ == "__main__":
    main()

