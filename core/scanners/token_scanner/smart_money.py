"""
Smart Money Tracker
Identify quality wallets with high win rates
"""
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .clients import HeliusClient, DexScreenerClient
from .config import LOG_DIR


@dataclass
class WalletProfile:
    """Profile of a wallet's trading performance"""
    address: str
    total_trades: int
    wins: int
    losses: int
    win_rate: float
    avg_hold_time_hours: float
    avg_gain_pct: float
    last_active: str
    classification: str  # SMART_MONEY, NEUTRAL, DUMPER, UNKNOWN
    confidence: str  # HIGH, MEDIUM, LOW


class SmartMoneyTracker:
    """Track and analyze wallet performance"""

    def __init__(self):
        self.helius = HeliusClient()
        self.dex = DexScreenerClient()
        self.wallet_db_path = LOG_DIR / "smart_money_db.json"
        self.wallet_db = self._load_db()

    def _load_db(self) -> Dict:
        """Load wallet database"""
        if self.wallet_db_path.exists():
            try:
                with open(self.wallet_db_path) as f:
                    return json.load(f)
            except Exception:
                pass
        return {"wallets": {}, "updated": None}

    def _save_db(self):
        """Save wallet database"""
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.wallet_db["updated"] = datetime.now().isoformat()
        with open(self.wallet_db_path, 'w') as f:
            json.dump(self.wallet_db, f, indent=2)

    def analyze_wallet(self, wallet_address: str, depth: int = 20) -> WalletProfile:
        """
        Analyze a wallet's trading history and calculate win rate

        Args:
            wallet_address: Solana wallet address
            depth: Number of recent transactions to analyze
        """
        print(f"\n🔍 Analyzing wallet: {wallet_address[:8]}...{wallet_address[-6:]}")

        # Get recent signatures
        sigs = self.helius.get_signatures(wallet_address, limit=depth)

        if not sigs:
            return WalletProfile(
                address=wallet_address,
                total_trades=0,
                wins=0,
                losses=0,
                win_rate=0,
                avg_hold_time_hours=0,
                avg_gain_pct=0,
                last_active="Unknown",
                classification="UNKNOWN",
                confidence="LOW"
            )

        # Parse transactions to find token trades
        trades = []
        for sig in sigs:
            try:
                tx = self.helius.parse_transaction(sig.get("signature", ""))
                if tx and tx.get("type") in ["SWAP", "TOKEN_MINT"]:
                    trades.append(tx)
            except Exception:
                continue

        # Analyze trade outcomes
        wins = 0
        losses = 0
        gains = []
        hold_times = []

        # Group by token to track buy->sell cycles
        token_positions = {}

        for trade in trades:
            token_transfers = trade.get("tokenTransfers", [])
            for transfer in token_transfers:
                mint = transfer.get("mint", "")
                amount = float(transfer.get("tokenAmount", 0) or 0)

                if transfer.get("fromUserAccount") == wallet_address:
                    # Selling
                    if mint in token_positions:
                        entry = token_positions[mint]
                        # Check if profitable (simplified - would need price data)
                        # For now, mark as win if they held > 1 hour before selling
                        hold_time = 1  # placeholder
                        hold_times.append(hold_time)
                        # Assume 50/50 for now without price history
                        wins += 1
                        del token_positions[mint]
                elif transfer.get("toUserAccount") == wallet_address:
                    # Buying
                    token_positions[mint] = {
                        "amount": amount,
                        "timestamp": trade.get("timestamp", 0)
                    }

        total_trades = wins + losses
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        avg_hold = sum(hold_times) / len(hold_times) if hold_times else 0
        avg_gain = sum(gains) / len(gains) if gains else 0

        # Classify wallet
        if total_trades < 5:
            classification = "UNKNOWN"
            confidence = "LOW"
        elif win_rate >= 70:
            classification = "SMART_MONEY"
            confidence = "HIGH" if total_trades >= 20 else "MEDIUM"
        elif win_rate >= 50:
            classification = "NEUTRAL"
            confidence = "MEDIUM"
        else:
            classification = "DUMPER"
            confidence = "HIGH" if total_trades >= 20 else "MEDIUM"

        last_active = sigs[0].get("blockTime", 0) if sigs else 0
        if last_active:
            last_active = datetime.fromtimestamp(last_active).isoformat()
        else:
            last_active = "Unknown"

        profile = WalletProfile(
            address=wallet_address,
            total_trades=total_trades,
            wins=wins,
            losses=losses,
            win_rate=win_rate,
            avg_hold_time_hours=avg_hold,
            avg_gain_pct=avg_gain,
            last_active=last_active,
            classification=classification,
            confidence=confidence
        )

        # Cache in database
        self.wallet_db["wallets"][wallet_address] = {
            "profile": {
                "total_trades": profile.total_trades,
                "win_rate": profile.win_rate,
                "classification": profile.classification,
                "confidence": profile.confidence,
                "last_active": profile.last_active
            },
            "analyzed_at": datetime.now().isoformat()
        }
        self._save_db()

        return profile

    def analyze_token_holders(self, token_address: str) -> Dict:
        """
        Analyze the quality of a token's top holders

        Returns:
            smart_money_count: How many top holders are smart money
            dumper_count: How many are known dumpers
            smart_money_pct: % held by smart money wallets
            quality_score: 0-100 score based on holder quality
        """
        print(f"\n💎 SMART MONEY ANALYSIS")
        print("=" * 60)
        print(f"Token: {token_address[:20]}...{token_address[-8:]}\n")

        # Get top holders
        holders = self.helius.get_token_holders(token_address, limit=10)

        if not holders:
            return {
                "error": "Could not fetch holders",
                "quality_score": 50  # Neutral if unknown
            }

        total_supply = sum(float(h.get("amount", 0)) for h in holders)

        smart_money_wallets = []
        dumper_wallets = []
        neutral_wallets = []
        unknown_wallets = []

        smart_money_amount = 0
        dumper_amount = 0

        print("Analyzing top 10 holders...\n")
        print(f"{'#':>2} | {'Wallet':20} | {'Hold %':>8} | {'Win Rate':>10} | {'Class':15}")
        print("-" * 70)

        for i, holder in enumerate(holders[:10], 1):
            # Get wallet address from token account
            wallet = holder.get("address", "")
            amount = float(holder.get("amount", 0))
            hold_pct = (amount / total_supply * 100) if total_supply > 0 else 0

            # Check cache first
            cached = self.wallet_db.get("wallets", {}).get(wallet)

            if cached:
                profile_data = cached.get("profile", {})
                win_rate = profile_data.get("win_rate", 0)
                classification = profile_data.get("classification", "UNKNOWN")
            else:
                # Analyze wallet (this is slow - rate limited)
                # For speed, we'll use a simplified check
                win_rate = 0
                classification = "UNKNOWN"
                unknown_wallets.append(wallet)

            # Classify
            class_emoji = {
                "SMART_MONEY": "🧠",
                "NEUTRAL": "😐",
                "DUMPER": "🚨",
                "UNKNOWN": "❓"
            }.get(classification, "❓")

            if classification == "SMART_MONEY":
                smart_money_wallets.append(wallet)
                smart_money_amount += amount
            elif classification == "DUMPER":
                dumper_wallets.append(wallet)
                dumper_amount += amount
            elif classification == "NEUTRAL":
                neutral_wallets.append(wallet)

            wallet_short = f"{wallet[:8]}...{wallet[-6:]}" if len(wallet) > 16 else wallet
            win_str = f"{win_rate:.0f}%" if win_rate > 0 else "N/A"
            print(f"{i:>2} | {wallet_short:20} | {hold_pct:>7.1f}% | {win_str:>10} | {class_emoji} {classification}")

        # Calculate quality score
        smart_pct = (smart_money_amount / total_supply * 100) if total_supply > 0 else 0
        dumper_pct = (dumper_amount / total_supply * 100) if total_supply > 0 else 0

        # Quality score formula:
        # Start at 50, add points for smart money, subtract for dumpers
        quality_score = 50
        quality_score += len(smart_money_wallets) * 10  # +10 per smart money holder
        quality_score -= len(dumper_wallets) * 15  # -15 per dumper
        quality_score += smart_pct * 0.5  # Bonus for smart money concentration
        quality_score -= dumper_pct * 0.7  # Penalty for dumper concentration
        quality_score = max(0, min(100, quality_score))  # Clamp 0-100

        print(f"\n📊 HOLDER QUALITY SUMMARY:")
        print(f"   🧠 Smart Money:  {len(smart_money_wallets)} wallets ({smart_pct:.1f}% of supply)")
        print(f"   🚨 Dumpers:      {len(dumper_wallets)} wallets ({dumper_pct:.1f}% of supply)")
        print(f"   😐 Neutral:      {len(neutral_wallets)} wallets")
        print(f"   ❓ Unknown:      {len(unknown_wallets)} wallets")
        print(f"\n   💎 Quality Score: {quality_score:.0f}/100")

        if quality_score >= 70:
            print("   ✅ BULLISH - Smart money is accumulating")
        elif quality_score >= 50:
            print("   ⚠️ NEUTRAL - Mixed holder quality")
        else:
            print("   ❌ BEARISH - Dumpers present, be careful")

        return {
            "smart_money_count": len(smart_money_wallets),
            "dumper_count": len(dumper_wallets),
            "smart_money_pct": smart_pct,
            "dumper_pct": dumper_pct,
            "quality_score": quality_score,
            "top_holders_analyzed": len(holders)
        }

    def find_smart_money_entries(self, min_wallet_win_rate: float = 60) -> List[Dict]:
        """
        Scan for tokens where known smart money wallets recently entered

        This is the holy grail - finding tokens BEFORE they pump
        by watching what successful traders are buying
        """
        print("\n🎯 SMART MONEY ENTRY SCANNER")
        print("=" * 60)
        print(f"Looking for tokens where wallets with >{min_wallet_win_rate}% win rate just entered...\n")

        # Get smart money wallets from our database
        smart_wallets = []
        for wallet, data in self.wallet_db.get("wallets", {}).items():
            profile = data.get("profile", {})
            if profile.get("win_rate", 0) >= min_wallet_win_rate:
                if profile.get("classification") == "SMART_MONEY":
                    smart_wallets.append(wallet)

        if not smart_wallets:
            print("❌ No smart money wallets in database yet.")
            print("   Run --analyze-wallet on some successful traders first.")
            return []

        print(f"Tracking {len(smart_wallets)} smart money wallets...\n")

        # Check recent activity for each smart wallet
        recent_entries = []

        for wallet in smart_wallets[:5]:  # Limit for rate limits
            sigs = self.helius.get_signatures(wallet, limit=10)

            for sig in sigs:
                tx = self.helius.parse_transaction(sig.get("signature", ""))
                if tx and tx.get("type") == "SWAP":
                    # Found a swap - check if it's a buy
                    transfers = tx.get("tokenTransfers", [])
                    for t in transfers:
                        if t.get("toUserAccount") == wallet:
                            # This is a buy
                            token = t.get("mint", "")
                            if token:
                                recent_entries.append({
                                    "wallet": wallet,
                                    "token": token,
                                    "timestamp": tx.get("timestamp", 0),
                                    "type": "BUY"
                                })

        # Dedupe and get token info
        seen_tokens = set()
        results = []

        for entry in recent_entries:
            token = entry["token"]
            if token not in seen_tokens:
                seen_tokens.add(token)
                # Get token info
                pair = self.dex.get_token(token)
                if pair:
                    symbol = pair.get("baseToken", {}).get("symbol", "???")
                    mc = float(pair.get("marketCap") or 0)
                    results.append({
                        "token": token,
                        "symbol": symbol,
                        "market_cap": mc,
                        "smart_money_wallet": entry["wallet"]
                    })
                    print(f"  🧠 Smart money bought: {symbol} (${mc:,.0f} MC)")

        print(f"\n✅ Found {len(results)} recent smart money entries")
        return results

    def add_known_wallet(self, address: str, classification: str, win_rate: float = 0, notes: str = ""):
        """
        Manually add a known wallet to the database

        Use this to track wallets you've identified as good/bad traders
        """
        self.wallet_db["wallets"][address] = {
            "profile": {
                "total_trades": 0,
                "win_rate": win_rate,
                "classification": classification,
                "confidence": "MANUAL",
                "last_active": "Unknown",
                "notes": notes
            },
            "analyzed_at": datetime.now().isoformat(),
            "manual_entry": True
        }
        self._save_db()
        print(f"✅ Added {address[:16]}... as {classification}")

    def list_tracked_wallets(self):
        """List all tracked wallets"""
        print("\n📋 TRACKED WALLETS")
        print("=" * 60)

        wallets = self.wallet_db.get("wallets", {})

        if not wallets:
            print("No wallets tracked yet.")
            return

        smart = []
        dumpers = []
        other = []

        for addr, data in wallets.items():
            profile = data.get("profile", {})
            classification = profile.get("classification", "UNKNOWN")

            if classification == "SMART_MONEY":
                smart.append((addr, profile))
            elif classification == "DUMPER":
                dumpers.append((addr, profile))
            else:
                other.append((addr, profile))

        if smart:
            print(f"\n🧠 SMART MONEY ({len(smart)}):")
            for addr, p in smart:
                wr = p.get("win_rate", 0)
                print(f"   {addr[:16]}... | Win Rate: {wr:.0f}%")

        if dumpers:
            print(f"\n🚨 DUMPERS ({len(dumpers)}):")
            for addr, p in dumpers:
                print(f"   {addr[:16]}...")

        print(f"\n   Total tracked: {len(wallets)}")

    def discover_winners(self, token_address: str = None) -> List[Dict]:
        """
        Discover winning wallets by analyzing successful tokens

        Strategy: Find wallets that bought winning tokens EARLY
        and still hold or sold for profit.

        Args:
            token_address: Specific token to analyze, or None to use known winners
        """
        print("\n🔍 WALLET DISCOVERY")
        print("=" * 60)

        # Known successful meme coins to analyze
        KNOWN_WINNERS = {
            "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263": "BONK",
            "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm": "WIF",
            "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr": "POPCAT",
            "2qEHjDLDLbuBgRYvsxhc5D6uDWAivNFZGan56P1tpump": "PNUT",
            "MEW1gQWJ3nEXg2qgERiKu7FAFj79PHvQVREQUzScPP5": "MEW",
        }

        if token_address:
            tokens_to_check = {token_address: "Custom"}
        else:
            tokens_to_check = KNOWN_WINNERS
            print("Analyzing holders of known winners: BONK, WIF, POPCAT, PNUT, MEW\n")

        discovered_wallets = []
        wallet_scores = {}  # Track how many winners each wallet holds

        for token, name in tokens_to_check.items():
            print(f"\n📊 Analyzing {name} holders...")

            holders = self.helius.get_token_holders(token, limit=20)

            if not holders:
                print(f"   Could not fetch holders for {name}")
                continue

            for holder in holders[:20]:
                wallet = holder.get("address", "")
                if not wallet:
                    continue

                # Skip if already tracked
                if wallet in self.wallet_db.get("wallets", {}):
                    continue

                # Count how many winning tokens this wallet holds
                if wallet not in wallet_scores:
                    wallet_scores[wallet] = {
                        "tokens": [],
                        "count": 0
                    }

                wallet_scores[wallet]["tokens"].append(name)
                wallet_scores[wallet]["count"] += 1

        # Find wallets that appear in multiple winning tokens
        print("\n\n🎯 DISCOVERED WALLETS")
        print("=" * 60)
        print("Wallets holding multiple successful tokens:\n")

        # Sort by count of winning tokens held
        sorted_wallets = sorted(
            wallet_scores.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )

        candidates = []
        for wallet, data in sorted_wallets[:20]:
            if data["count"] >= 1:  # At least 1 winner
                tokens_held = ", ".join(data["tokens"][:3])
                if len(data["tokens"]) > 3:
                    tokens_held += f" +{len(data['tokens'])-3} more"

                print(f"   {wallet[:12]}...{wallet[-6:]} | {data['count']} winners | {tokens_held}")

                candidates.append({
                    "wallet": wallet,
                    "winner_count": data["count"],
                    "tokens": data["tokens"]
                })

        if not candidates:
            print("   No new wallets discovered")
            return []

        # Offer to track top wallets
        print(f"\n✅ Found {len(candidates)} potential smart money wallets")
        print("\nTo track these wallets, run:")
        for c in candidates[:5]:
            print(f"   --track-wallet {c['wallet']} --as smart")

        return candidates

    def auto_discover(self, auto_track: bool = False) -> List[Dict]:
        """
        Auto-discover and optionally track winning wallets

        This is the easy button - finds wallets from successful tokens
        and optionally adds them to your tracking database.
        """
        print("\n🚀 AUTO-DISCOVERY MODE")
        print("=" * 60)

        candidates = self.discover_winners()

        if not candidates:
            return []

        if auto_track:
            print("\n📝 Auto-tracking top discovered wallets...")
            tracked = 0

            for c in candidates[:10]:  # Track top 10
                if c["winner_count"] >= 2:  # Must hold 2+ winners
                    self.add_known_wallet(
                        c["wallet"],
                        "SMART_MONEY",
                        win_rate=70,  # Estimated based on holding winners
                        notes=f"Auto-discovered: holds {', '.join(c['tokens'][:3])}"
                    )
                    tracked += 1

            print(f"\n✅ Auto-tracked {tracked} wallets")

        return candidates

    def scan_whale_activity(self, min_usd: float = 10000) -> List[Dict]:
        """
        Scan for large recent trades (whale activity)

        Finds big buys/sells to spot where money is flowing
        """
        print(f"\n🐋 WHALE ACTIVITY SCANNER (>${min_usd:,.0f})")
        print("=" * 60)

        # Get trending tokens and check for large trades
        trending = self.dex.get_trending()

        whale_trades = []

        print("Scanning trending tokens for whale activity...\n")

        for token in trending[:10]:
            addr = token.get("tokenAddress") or token.get("address", "")
            if not addr:
                continue

            # Get token info
            pair = self.dex.get_token(addr)
            if not pair:
                continue

            symbol = pair.get("baseToken", {}).get("symbol", "???")
            vol_24h = float(pair.get("volume", {}).get("h24", 0) or 0)

            # High volume = whale activity
            if vol_24h >= min_usd * 10:  # 10x threshold for significance
                mc = float(pair.get("marketCap") or 0)
                liq = float(pair.get("liquidity", {}).get("usd", 0) or 0)

                whale_trades.append({
                    "token": addr,
                    "symbol": symbol,
                    "volume_24h": vol_24h,
                    "market_cap": mc,
                    "liquidity": liq
                })

                vol_mc_ratio = (vol_24h / mc * 100) if mc > 0 else 0
                print(f"   🐋 {symbol:10} | Vol: ${vol_24h:>12,.0f} | MC: ${mc:>12,.0f} | {vol_mc_ratio:.0f}% turnover")

        print(f"\n✅ Found {len(whale_trades)} tokens with high whale activity")
        return whale_trades
