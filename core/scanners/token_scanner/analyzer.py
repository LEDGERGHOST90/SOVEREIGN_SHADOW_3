"""
MemeMachine Analyzer
Breakout detection with Smart Money scoring
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .clients import DexScreenerClient, HeliusClient
from .smart_money import SmartMoneyTracker
from .config import MIN_LIQUIDITY, MAX_MARKET_CAP


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

    # Smart money metrics (replaces old top5 concentration)
    smart_money_count: int
    dumper_count: int
    holder_quality_score: int  # 0-100 based on WHO holds, not just how much

    # Calculated scores (0-100)
    liquidity_score: int
    volume_score: int
    momentum_score: int
    age_score: int

    # Final verdict
    total_score: int
    verdict: str  # SNIPE, WATCH, AVOID
    reasons: List[str]


class BreakoutAnalyzer:
    """Analyze tokens for breakout potential using Smart Money signals"""

    def __init__(self):
        self.dex = DexScreenerClient()
        self.helius = HeliusClient()
        self.smart_money = SmartMoneyTracker()

    def score_token(self, address: str) -> Optional[TokenScore]:
        """
        Score a single token using Smart Money analysis

        Scoring factors:
        - Holder Quality (25%): Smart money vs dumpers holding
        - Liquidity (25%): Can you exit?
        - Volume (20%): Is it active?
        - Momentum (20%): Buy pressure + price action
        - Age (10%): Sweet spot timing
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
            age_hours = 999

        reasons = []

        # =================================================================
        # 1. HOLDER QUALITY SCORE (Smart Money Analysis) - 25%
        # =================================================================
        # This replaces the old "top 5 concentration" metric
        # Now we check WHO holds, not just how much they hold

        holders = self.helius.get_token_holders(address, limit=10)
        smart_count = 0
        dumper_count = 0

        if holders:
            for holder in holders:
                wallet = holder.get("address", "")
                # Check if wallet is in our database
                cached = self.smart_money.wallet_db.get("wallets", {}).get(wallet)
                if cached:
                    classification = cached.get("profile", {}).get("classification", "")
                    if classification == "SMART_MONEY":
                        smart_count += 1
                    elif classification == "DUMPER":
                        dumper_count += 1

        # Calculate holder quality score
        # Base score of 50, modified by smart money presence
        holder_quality_score = 50
        holder_quality_score += smart_count * 15  # +15 per smart money holder
        holder_quality_score -= dumper_count * 20  # -20 per dumper (harsher penalty)
        holder_quality_score = max(0, min(100, holder_quality_score))

        if smart_count >= 3:
            reasons.append(f"🧠 Strong smart money ({smart_count} tracked wallets holding)")
        elif smart_count >= 1:
            reasons.append(f"🧠 Smart money present ({smart_count} tracked wallet)")
        elif dumper_count >= 2:
            reasons.append(f"🚨 Multiple dumpers detected ({dumper_count} wallets)")
        elif dumper_count == 1:
            reasons.append(f"⚠️ Known dumper holding (1 wallet)")
        else:
            reasons.append("❓ No tracked wallets in top holders")

        # =================================================================
        # 2. LIQUIDITY SCORE - 25%
        # =================================================================
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

        # =================================================================
        # 3. VOLUME SCORE - 20%
        # =================================================================
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

        # =================================================================
        # 4. MOMENTUM SCORE - 20%
        # =================================================================
        total_txns = buys + sells
        buy_ratio = buys / total_txns if total_txns > 0 else 0.5

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

        # =================================================================
        # 5. AGE SCORE - 10%
        # =================================================================
        if 24 <= age_hours <= 168:
            age_score = 100
            reasons.append(f"✅ Optimal age ({age_hours:.0f}h) - survived initial dump")
        elif 6 <= age_hours < 24:
            age_score = 70
            reasons.append(f"⚠️ Young ({age_hours:.0f}h) - still proving itself")
        elif 168 < age_hours <= 720:
            age_score = 60
            reasons.append(f"⚠️ Established ({age_hours/24:.0f}d) - may have run already")
        elif age_hours < 6:
            age_score = 30
            reasons.append(f"⚠️ Very new ({age_hours:.1f}h) - high risk")
        else:
            age_score = 40
            reasons.append(f"⚠️ Old ({age_hours/24:.0f}d) - check if still active")

        # =================================================================
        # TOTAL SCORE (weighted)
        # =================================================================
        total_score = int(
            holder_quality_score * 0.25 +  # 25% - WHO holds matters most
            liquidity_score * 0.25 +        # 25% - exit ability
            volume_score * 0.20 +            # 20% - activity
            momentum_score * 0.20 +          # 20% - direction
            age_score * 0.10                 # 10% - timing
        )

        # Determine verdict
        if total_score >= 70:
            verdict = "SNIPE"
        elif total_score >= 50:
            verdict = "WATCH"
        else:
            verdict = "AVOID"

        # Market cap context
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
            smart_money_count=smart_count,
            dumper_count=dumper_count,
            holder_quality_score=holder_quality_score,
            liquidity_score=liquidity_score,
            volume_score=volume_score,
            momentum_score=momentum_score,
            age_score=age_score,
            total_score=total_score,
            verdict=verdict,
            reasons=reasons
        )

    def scan_breakouts(self, min_score: int = 60) -> List[TokenScore]:
        """Scan for breakout candidates"""
        print("\n🎯 BREAKOUT SCANNER (Smart Money Edition)")
        print("=" * 60)
        print("Scanning for tokens with quality holders...\n")

        candidates = []

        new_pairs = self.dex.get_new_pairs("solana")
        trending = self.dex.get_trending()

        all_tokens = []
        seen = set()

        for token in new_pairs + trending:
            addr = token.get("tokenAddress") or token.get("address", "")
            if addr and addr not in seen:
                seen.add(addr)
                all_tokens.append(addr)

        print(f"Analyzing {len(all_tokens)} tokens...\n")

        for addr in all_tokens[:30]:
            try:
                score = self.score_token(addr)
                if score and score.total_score >= min_score:
                    candidates.append(score)
                    verdict_emoji = {"SNIPE": "🎯", "WATCH": "👀", "AVOID": "❌"}[score.verdict]
                    sm_indicator = f"🧠{score.smart_money_count}" if score.smart_money_count else ""
                    print(f"  {verdict_emoji} {score.symbol:10} | Score: {score.total_score:3} | ${score.market_cap:>12,.0f} MC | {sm_indicator} {score.verdict}")
            except Exception:
                continue

        candidates.sort(key=lambda x: x.total_score, reverse=True)
        print(f"\n✅ Found {len(candidates)} candidates above {min_score} score")
        return candidates

    def quick_verdict(self, address: str) -> str:
        """Get formatted verdict for a token"""
        score = self.score_token(address)
        if not score:
            return "❌ Could not analyze token"

        verdict_emoji = {"SNIPE": "🎯", "WATCH": "👀", "AVOID": "❌"}[score.verdict]

        return f"""
{verdict_emoji} {score.verdict}: {score.symbol} ({score.name})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 SCORE: {score.total_score}/100

   Holder Quality: {'█' * (score.holder_quality_score // 10)}{'░' * (10 - score.holder_quality_score // 10)} {score.holder_quality_score}
   Liquidity:      {'█' * (score.liquidity_score // 10)}{'░' * (10 - score.liquidity_score // 10)} {score.liquidity_score}
   Volume:         {'█' * (score.volume_score // 10)}{'░' * (10 - score.volume_score // 10)} {score.volume_score}
   Momentum:       {'█' * (score.momentum_score // 10)}{'░' * (10 - score.momentum_score // 10)} {score.momentum_score}
   Age:            {'█' * (score.age_score // 10)}{'░' * (10 - score.age_score // 10)} {score.age_score}

💰 METRICS:
   Market Cap:     ${score.market_cap:,.0f}
   Liquidity:      ${score.liquidity:,.0f}
   24h Volume:     ${score.volume_24h:,.0f}
   24h Change:     {score.price_change_24h:+.1f}%
   Buy/Sell:       {score.buys_24h}/{score.sells_24h}

🧠 SMART MONEY:
   Tracked Holders: {score.smart_money_count} smart, {score.dumper_count} dumpers
   Quality Score:   {score.holder_quality_score}/100

📝 ANALYSIS:
""" + "\n".join(f"   {r}" for r in score.reasons)

    def snipe_decision(self, address: str) -> Tuple[bool, str]:
        """
        Final automated decision: Should I snipe this?

        Hard stops (auto-reject):
        - Known dumpers holding
        - Liquidity < $15K
        - Age < 2 hours
        - MC > $5M
        """
        score = self.score_token(address)
        if not score:
            return False, "Could not analyze token"

        # Hard stops
        if score.dumper_count >= 2:
            return False, f"❌ NO - {score.dumper_count} known dumpers in top holders"

        if score.liquidity < 15000:
            return False, f"❌ NO - Liquidity only ${score.liquidity:,.0f} (can't exit)"

        if score.age_hours < 2:
            return False, f"❌ NO - Only {score.age_hours:.1f}h old (too early)"

        if score.market_cap > 5000000:
            return False, f"❌ NO - MC ${score.market_cap:,.0f} (limited upside)"

        # Smart money bonus - if smart money is in, lower the threshold
        score_threshold = 65
        if score.smart_money_count >= 2:
            score_threshold = 55  # Lower bar if smart money is accumulating
            if score.total_score >= score_threshold:
                return True, f"✅ YES - Smart money accumulating ({score.smart_money_count} wallets), score {score.total_score}/100"

        # Standard score-based decision
        if score.total_score >= 75:
            return True, f"✅ YES - Strong score {score.total_score}/100"
        elif score.total_score >= 65:
            return True, f"⚠️ MAYBE - Decent score {score.total_score}/100, proceed with caution"
        else:
            return False, f"❌ NO - Score {score.total_score}/100 too low"
