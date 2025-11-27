"""
MemeMachine Analyzer
Breakout detection and automated scoring system
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .clients import DexScreenerClient, HeliusClient
from .config import MIN_LIQUIDITY, MAX_MARKET_CAP, MAX_HOLDER_CONCENTRATION


@dataclass
class TokenScore:
    """Scored token with verdict"""
    address: str
    symbol: str
    name: str

    # Raw metrics
    market_cap: float
    liquidity: float
    volume_24h: float
    price_change_24h: float
    buys_24h: int
    sells_24h: int
    age_hours: float
    top5_holder_pct: float
    risk_level: str

    # Calculated scores (0-100)
    distribution_score: int
    liquidity_score: int
    volume_score: int
    momentum_score: int
    age_score: int

    # Final verdict
    total_score: int
    verdict: str  # SNIPE, WATCH, AVOID
    reasons: List[str]


class BreakoutAnalyzer:
    """Analyze tokens for breakout potential"""

    def __init__(self):
        self.dex = DexScreenerClient()
        self.helius = HeliusClient()

    def score_token(self, address: str) -> Optional[TokenScore]:
        """
        Score a single token and return verdict

        Returns TokenScore with:
        - Individual scores (0-100) for each metric
        - Total score (0-100)
        - Verdict: SNIPE (70+), WATCH (50-69), AVOID (<50)
        - Reasons explaining the score
        """
        # Get DexScreener data
        pair = self.dex.get_token(address)
        if not pair:
            return None

        # Extract metrics
        symbol = pair.get("baseToken", {}).get("symbol", "???")
        name = pair.get("baseToken", {}).get("name", "Unknown")
        mc = float(pair.get("marketCap") or pair.get("fdv") or 0)
        liq = float(pair.get("liquidity", {}).get("usd", 0) or 0)
        vol = float(pair.get("volume", {}).get("h24", 0) or 0)
        change = float(pair.get("priceChange", {}).get("h24", 0) or 0)

        txns = pair.get("txns", {}).get("h24", {})
        buys = int(txns.get("buys", 0) or 0)
        sells = int(txns.get("sells", 0) or 0)

        # Calculate age
        created = pair.get("pairCreatedAt", 0)
        if created:
            age_hours = (datetime.now().timestamp() * 1000 - created) / (1000 * 60 * 60)
        else:
            age_hours = 999  # Unknown age

        # Get holder concentration from Helius
        concentration = self.helius.get_holder_concentration(address)
        if "error" in concentration:
            top5_pct = 100  # Assume worst if we can't check
            risk_level = "UNKNOWN"
        else:
            top5_pct = concentration.get("top5_percent", 100)
            risk_level = concentration.get("risk_level", "UNKNOWN")

        # Calculate individual scores
        reasons = []

        # 1. Distribution Score (0-100)
        if top5_pct <= 30:
            distribution_score = 100
            reasons.append("✅ Excellent distribution (top 5 < 30%)")
        elif top5_pct <= 40:
            distribution_score = 80
            reasons.append("✅ Good distribution (top 5 < 40%)")
        elif top5_pct <= 50:
            distribution_score = 60
            reasons.append("⚠️ Moderate concentration (top 5 < 50%)")
        elif top5_pct <= 70:
            distribution_score = 30
            reasons.append("⚠️ High concentration (top 5 < 70%)")
        else:
            distribution_score = 0
            reasons.append("❌ Extreme concentration (top 5 > 70%)")

        # 2. Liquidity Score (0-100)
        liq_ratio = (liq / mc * 100) if mc > 0 else 0
        if liq >= 100000 and liq_ratio >= 15:
            liquidity_score = 100
            reasons.append(f"✅ Strong liquidity (${liq:,.0f}, {liq_ratio:.1f}% ratio)")
        elif liq >= 50000 and liq_ratio >= 10:
            liquidity_score = 80
            reasons.append(f"✅ Good liquidity (${liq:,.0f}, {liq_ratio:.1f}% ratio)")
        elif liq >= 20000 and liq_ratio >= 5:
            liquidity_score = 60
            reasons.append(f"⚠️ Moderate liquidity (${liq:,.0f})")
        elif liq >= MIN_LIQUIDITY:
            liquidity_score = 40
            reasons.append(f"⚠️ Low liquidity (${liq:,.0f})")
        else:
            liquidity_score = 0
            reasons.append(f"❌ Insufficient liquidity (${liq:,.0f})")

        # 3. Volume Score (0-100)
        vol_ratio = (vol / mc * 100) if mc > 0 else 0
        if vol_ratio >= 100:
            volume_score = 100
            reasons.append(f"🔥 Explosive volume ({vol_ratio:.0f}% of MC)")
        elif vol_ratio >= 50:
            volume_score = 85
            reasons.append(f"✅ High volume ({vol_ratio:.0f}% of MC)")
        elif vol_ratio >= 20:
            volume_score = 70
            reasons.append(f"✅ Good volume ({vol_ratio:.0f}% of MC)")
        elif vol_ratio >= 5:
            volume_score = 50
            reasons.append(f"⚠️ Moderate volume ({vol_ratio:.1f}% of MC)")
        else:
            volume_score = 20
            reasons.append(f"⚠️ Low volume ({vol_ratio:.1f}% of MC)")

        # 4. Momentum Score (0-100) - Buy/sell ratio + price change
        total_txns = buys + sells
        if total_txns > 0:
            buy_ratio = buys / total_txns
        else:
            buy_ratio = 0.5

        # Combine buy pressure with price action
        if buy_ratio >= 0.7 and change > 0:
            momentum_score = 100
            reasons.append(f"🚀 Strong buy pressure ({buys}B/{sells}S, {change:+.1f}%)")
        elif buy_ratio >= 0.6 and change > 0:
            momentum_score = 80
            reasons.append(f"✅ Good momentum ({buys}B/{sells}S, {change:+.1f}%)")
        elif buy_ratio >= 0.5:
            momentum_score = 60
            reasons.append(f"⚠️ Neutral momentum ({buys}B/{sells}S, {change:+.1f}%)")
        elif buy_ratio >= 0.4:
            momentum_score = 40
            reasons.append(f"⚠️ Slight sell pressure ({buys}B/{sells}S, {change:+.1f}%)")
        else:
            momentum_score = 20
            reasons.append(f"❌ Heavy selling ({buys}B/{sells}S, {change:+.1f}%)")

        # 5. Age Score (0-100) - Sweet spot is 24-168 hours (1-7 days)
        if 24 <= age_hours <= 168:
            age_score = 100
            reasons.append(f"✅ Optimal age ({age_hours:.0f}h) - survived initial dump")
        elif 6 <= age_hours < 24:
            age_score = 70
            reasons.append(f"⚠️ Young ({age_hours:.0f}h) - still proving itself")
        elif 168 < age_hours <= 720:  # 1-4 weeks
            age_score = 60
            reasons.append(f"⚠️ Established ({age_hours/24:.0f}d) - may have run already")
        elif age_hours < 6:
            age_score = 30
            reasons.append(f"⚠️ Very new ({age_hours:.1f}h) - high rug risk")
        else:
            age_score = 40
            reasons.append(f"⚠️ Old ({age_hours/24:.0f}d) - check if still active")

        # Calculate total score (weighted)
        total_score = int(
            distribution_score * 0.25 +  # 25% - most important
            liquidity_score * 0.25 +      # 25% - exit ability
            volume_score * 0.20 +          # 20% - activity
            momentum_score * 0.20 +        # 20% - direction
            age_score * 0.10               # 10% - timing
        )

        # Determine verdict
        if total_score >= 70:
            verdict = "SNIPE"
        elif total_score >= 50:
            verdict = "WATCH"
        else:
            verdict = "AVOID"

        # Add market cap context
        if mc < 100000:
            reasons.append(f"💎 Micro cap (${mc:,.0f}) - high risk/reward")
        elif mc < 500000:
            reasons.append(f"💎 Low cap (${mc:,.0f}) - good upside potential")
        elif mc < 2000000:
            reasons.append(f"📊 Mid cap (${mc:,.0f}) - moderate upside")
        else:
            reasons.append(f"📊 Higher cap (${mc:,.0f}) - lower risk, less upside")

        return TokenScore(
            address=address,
            symbol=symbol,
            name=name,
            market_cap=mc,
            liquidity=liq,
            volume_24h=vol,
            price_change_24h=change,
            buys_24h=buys,
            sells_24h=sells,
            age_hours=age_hours,
            top5_holder_pct=top5_pct,
            risk_level=risk_level,
            distribution_score=distribution_score,
            liquidity_score=liquidity_score,
            volume_score=volume_score,
            momentum_score=momentum_score,
            age_score=age_score,
            total_score=total_score,
            verdict=verdict,
            reasons=reasons
        )

    def scan_breakouts(self, min_score: int = 60) -> List[TokenScore]:
        """
        Scan for breakout candidates
        Returns tokens scoring above min_score
        """
        print("\n🎯 BREAKOUT SCANNER")
        print("=" * 60)
        print("Scanning for high-potential tokens...\n")

        candidates = []

        # Get new pairs from DexScreener
        new_pairs = self.dex.get_new_pairs("solana")
        trending = self.dex.get_trending()

        # Combine and dedupe
        all_tokens = []
        seen = set()

        for token in new_pairs + trending:
            addr = token.get("tokenAddress") or token.get("address", "")
            if addr and addr not in seen:
                seen.add(addr)
                all_tokens.append(addr)

        print(f"Analyzing {len(all_tokens)} tokens...\n")

        for i, addr in enumerate(all_tokens[:30]):  # Limit to 30 for speed
            try:
                score = self.score_token(addr)
                if score and score.total_score >= min_score:
                    candidates.append(score)
                    verdict_emoji = {"SNIPE": "🎯", "WATCH": "👀", "AVOID": "❌"}[score.verdict]
                    print(f"  {verdict_emoji} {score.symbol:10} | Score: {score.total_score:3} | ${score.market_cap:>12,.0f} MC | {score.verdict}")
            except Exception:
                continue

        # Sort by score
        candidates.sort(key=lambda x: x.total_score, reverse=True)

        print(f"\n✅ Found {len(candidates)} candidates above {min_score} score")
        return candidates

    def quick_verdict(self, address: str) -> str:
        """
        Get a quick one-line verdict for a token
        Returns formatted string with verdict
        """
        score = self.score_token(address)
        if not score:
            return "❌ Could not analyze token"

        verdict_emoji = {"SNIPE": "🎯", "WATCH": "👀", "AVOID": "❌"}[score.verdict]

        return f"""
{verdict_emoji} {score.verdict}: {score.symbol} ({score.name})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 SCORE: {score.total_score}/100

   Distribution: {'█' * (score.distribution_score // 10)}{'░' * (10 - score.distribution_score // 10)} {score.distribution_score}
   Liquidity:    {'█' * (score.liquidity_score // 10)}{'░' * (10 - score.liquidity_score // 10)} {score.liquidity_score}
   Volume:       {'█' * (score.volume_score // 10)}{'░' * (10 - score.volume_score // 10)} {score.volume_score}
   Momentum:     {'█' * (score.momentum_score // 10)}{'░' * (10 - score.momentum_score // 10)} {score.momentum_score}
   Age:          {'█' * (score.age_score // 10)}{'░' * (10 - score.age_score // 10)} {score.age_score}

💰 METRICS:
   Market Cap:   ${score.market_cap:,.0f}
   Liquidity:    ${score.liquidity:,.0f}
   24h Volume:   ${score.volume_24h:,.0f}
   24h Change:   {score.price_change_24h:+.1f}%
   Buy/Sell:     {score.buys_24h}/{score.sells_24h}
   Top 5 Hold:   {score.top5_holder_pct:.1f}%
   Risk Level:   {score.risk_level}

📝 ANALYSIS:
""" + "\n".join(f"   {r}" for r in score.reasons)

    def snipe_decision(self, address: str) -> Tuple[bool, str]:
        """
        Final automated decision: Should I snipe this?
        Returns (True/False, reason)
        """
        score = self.score_token(address)
        if not score:
            return False, "Could not analyze token"

        # Hard stops - never snipe these
        if score.top5_holder_pct > 60:
            return False, f"❌ NO - Top 5 wallets hold {score.top5_holder_pct:.1f}% (rug risk)"

        if score.liquidity < 15000:
            return False, f"❌ NO - Liquidity only ${score.liquidity:,.0f} (can't exit)"

        if score.age_hours < 2:
            return False, f"❌ NO - Only {score.age_hours:.1f}h old (too early)"

        if score.market_cap > 5000000:
            return False, f"❌ NO - MC ${score.market_cap:,.0f} (limited upside)"

        # Score-based decision
        if score.total_score >= 75:
            return True, f"✅ YES - Strong score {score.total_score}/100, {score.verdict}"
        elif score.total_score >= 65:
            return True, f"⚠️ MAYBE - Decent score {score.total_score}/100, proceed with caution"
        else:
            return False, f"❌ NO - Score {score.total_score}/100 too low"
