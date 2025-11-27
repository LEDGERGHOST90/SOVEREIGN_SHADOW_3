"""
MemeMachine Scanner
Core scanning and analysis logic
"""
import json
from datetime import datetime
from typing import Dict, List

from .config import (
    LOG_DIR, MIN_LIQUIDITY, MAX_MARKET_CAP,
    MIN_VOLUME_24H, MAX_HOLDER_CONCENTRATION
)
from .clients import BirdeyeClient, DexScreenerClient, HeliusClient, PumpFunClient


class MemeMachine:
    """Meme coin sniper and analyzer"""

    def __init__(self):
        self.birdeye = BirdeyeClient()
        self.dex = DexScreenerClient()
        self.helius = HeliusClient()
        self.pumpfun = PumpFunClient()
        self.log_file = LOG_DIR / 'scans.json'

        # Ensure log directory exists
        LOG_DIR.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # DEXSCREENER SCANNING (No Rate Limits)
    # =========================================================================

    def dex_scan(self) -> List[Dict]:
        """Scan using DexScreener - FREE, NO LIMITS"""
        print("\n🔍 DEXSCREENER SCAN (No Rate Limits)")
        print("=" * 50)

        candidates = []

        print("📊 Fetching new Solana pairs...")
        new_pairs = self.dex.get_new_pairs("solana")

        if not new_pairs:
            print("  Trying trending tokens...")
            new_pairs = self.dex.get_trending()

        print(f"  Found {len(new_pairs)} tokens to analyze\n")

        for token in new_pairs:
            try:
                address = token.get("tokenAddress") or token.get("address", "")
                if not address:
                    continue

                pair = self.dex.get_token(address)
                if not pair:
                    continue

                symbol = pair.get("baseToken", {}).get("symbol", "???")
                name = pair.get("baseToken", {}).get("name", "Unknown")
                mc = float(pair.get("marketCap") or pair.get("fdv") or 0)
                liq = float(pair.get("liquidity", {}).get("usd", 0) or 0)
                vol = float(pair.get("volume", {}).get("h24", 0) or 0)
                price = float(pair.get("priceUsd", 0) or 0)
                price_change = float(pair.get("priceChange", {}).get("h24", 0) or 0)

                if liq < MIN_LIQUIDITY:
                    continue
                if mc > MAX_MARKET_CAP and mc > 0:
                    continue

                candidate = {
                    "address": address,
                    "symbol": symbol,
                    "name": name,
                    "liquidity": liq,
                    "market_cap": mc,
                    "volume_24h": vol,
                    "price": price,
                    "price_change_24h": price_change,
                    "dex": pair.get("dexId", ""),
                    "source": "dexscreener",
                    "found_at": datetime.now().isoformat()
                }

                candidates.append(candidate)
                change_str = f"{price_change:+.1f}%" if price_change else "N/A"
                print(f"  ✅ {symbol:10} | ${mc:>10,.0f} MC | ${liq:>10,.0f} liq | {change_str}")

            except Exception:
                continue

        print(f"\n🎯 Found {len(candidates)} candidates")
        self._log_scan(candidates)
        return candidates

    def dex_search(self, query: str) -> List[Dict]:
        """Search tokens on DexScreener"""
        print(f"\n🔎 Searching: {query}")
        print("=" * 50)

        pairs = self.dex.search_tokens(query)
        solana_pairs = [p for p in pairs if p.get("chainId") == "solana"]

        print(f"Found {len(solana_pairs)} Solana pairs\n")
        print(f"{'Symbol':10} | {'MC':>12} | {'Liq':>10} | {'24h':>8} | {'DEX':>10}")
        print("-" * 60)

        for p in solana_pairs[:15]:
            symbol = p.get("baseToken", {}).get("symbol", "???")[:10]
            mc = float(p.get("marketCap") or p.get("fdv") or 0)
            liq = float(p.get("liquidity", {}).get("usd", 0) or 0)
            change = float(p.get("priceChange", {}).get("h24", 0) or 0)
            dex = p.get("dexId", "???")[:10]
            print(f"{symbol:10} | ${mc:>11,.0f} | ${liq:>9,.0f} | {change:>+7.1f}% | {dex:>10}")

        return solana_pairs

    # =========================================================================
    # BIRDEYE SCANNING (Rate Limited)
    # =========================================================================

    def birdeye_scan(self) -> List[Dict]:
        """Scan with Birdeye - has rate limits but deeper data"""
        print("\n🦅 BIRDEYE SCAN")
        print("=" * 50)

        candidates = []
        tokens = self.birdeye.get_token_list(limit=50)

        print(f"📊 Analyzing {len(tokens)} tokens...\n")

        for token in tokens:
            try:
                mc = token.get("mc", 0) or 0
                liq = token.get("liquidity", 0) or 0
                vol = token.get("v24hUSD", 0) or 0

                if mc > MAX_MARKET_CAP and mc > 0:
                    continue
                if liq < MIN_LIQUIDITY:
                    continue
                if vol < MIN_VOLUME_24H:
                    continue

                candidate = {
                    "address": token.get("address", ""),
                    "symbol": token.get("symbol", "???"),
                    "name": token.get("name", "Unknown"),
                    "liquidity": liq,
                    "market_cap": mc,
                    "volume_24h": vol,
                    "price": token.get("price", 0),
                    "source": "birdeye",
                    "found_at": datetime.now().isoformat()
                }

                candidates.append(candidate)
                print(f"  ✅ {candidate['symbol']:10} | ${mc:>10,.0f} MC | ${liq:>10,.0f} liq")

            except Exception:
                continue

        print(f"\n🎯 Found {len(candidates)} candidates")
        self._log_scan(candidates)
        return candidates

    # =========================================================================
    # HELIUS DEEP ANALYSIS
    # =========================================================================

    def deep_dive(self, address: str) -> Dict:
        """Deep analysis using Helius"""
        print(f"\n🔬 HELIUS DEEP DIVE")
        print("=" * 50)
        print(f"Token: {address[:20]}...{address[-8:]}")

        result = {}

        # Get metadata
        print("\n📋 Metadata:")
        metadata = self.helius.get_token_metadata(address)
        if "error" not in metadata:
            result["metadata"] = metadata
            content = metadata.get("content", {})
            name = content.get("metadata", {}).get("name", "Unknown")
            symbol = content.get("metadata", {}).get("symbol", "???")
            print(f"   Name: {name}")
            print(f"   Symbol: {symbol}")
        else:
            print(f"   Error: {metadata.get('error')}")

        # Holder concentration analysis
        print("\n👥 Holder Analysis:")
        concentration = self.helius.get_holder_concentration(address)
        result["concentration"] = concentration

        if "error" not in concentration:
            print(f"   Top 1 wallet:  {concentration['top1_percent']:.1f}%")
            print(f"   Top 5 wallets: {concentration['top5_percent']:.1f}%")
            print(f"   Top 10 wallets: {concentration['top10_percent']:.1f}%")
            print(f"\n   Risk Level: {concentration['risk_level']}")
            print(f"   Assessment: {concentration['message']}")
        else:
            print(f"   Error: {concentration.get('error')}")

        # Recent activity
        print("\n📊 Recent Activity:")
        sigs = self.helius.get_signatures(address, limit=5)
        result["recent_txs"] = len(sigs)
        print(f"   {len(sigs)} recent transactions")

        return result

    # =========================================================================
    # UTILITIES
    # =========================================================================

    def analyze_token(self, address: str) -> Dict:
        """Full Birdeye analysis of a token"""
        print(f"\n🔍 BIRDEYE ANALYSIS")
        print("=" * 50)

        overview = self.birdeye.get_token_overview(address)
        security = self.birdeye.get_token_security(address)
        price = self.birdeye.get_price(address)
        trades = self.birdeye.get_trades(address, limit=20)

        if "error" in overview:
            print(f"❌ Error: {overview.get('error')}")
            return overview

        print(f"\n📌 {overview.get('symbol', '???')} - {overview.get('name', 'Unknown')}")
        print(f"\n💰 PRICE DATA:")
        print(f"   Current: ${price.get('value', 0):.10f}")
        print(f"   Market Cap: ${overview.get('mc', 0):,.0f}")
        print(f"   Liquidity: ${overview.get('liquidity', 0):,.0f}")
        print(f"   24h Volume: ${overview.get('v24hUSD', 0):,.0f}")

        print(f"\n🔒 SECURITY:")
        print(f"   Honeypot: {'❌ YES' if security.get('isHoneypot') else '✅ No'}")
        print(f"   Mintable: {'⚠️ Yes' if security.get('isMintable') else '✅ No'}")
        print(f"   Freezeable: {'⚠️ Yes' if security.get('isFreezeable') else '✅ No'}")

        return {"overview": overview, "security": security, "price": price, "trades": trades}

    def get_trending(self) -> List[Dict]:
        """Get trending meme tokens"""
        print("\n🔥 TRENDING MEME TOKENS")
        print("=" * 50)

        trending = self.birdeye.get_trending(limit=20)

        memes = []
        for token in trending:
            mc = token.get("mc", 0) or 0
            if mc < 10000000:
                memes.append(token)
                symbol = token.get("symbol", "???")
                v24h = token.get("v24hUSD", 0) or 0
                change = token.get("v24hChangePercent", 0) or 0
                print(f"  {symbol:10} | MC: ${mc:>12,.0f} | Vol: ${v24h:>10,.0f} | {change:+.1f}%")

        return memes

    def watch_token(self, address: str, duration_minutes: int = 60):
        """Watch a token's price live"""
        import time
        from datetime import timedelta

        print(f"\n👁️ Watching: {address[:20]}...")
        print("Press Ctrl+C to stop\n")

        start_price = None
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)

        try:
            while datetime.now() < end_time:
                data = self.birdeye.get_price(address)

                if "error" in data:
                    print(f"❌ Error: {data['error']}")
                    time.sleep(10)
                    continue

                price = data.get("value", 0)

                if start_price is None:
                    start_price = price

                change = ((price - start_price) / start_price * 100) if start_price else 0
                change_str = f"+{change:.2f}%" if change >= 0 else f"{change:.2f}%"

                print(f"  {datetime.now().strftime('%H:%M:%S')} | ${price:.10f} | {change_str}")
                time.sleep(5)

        except KeyboardInterrupt:
            print("\n\n👋 Stopped watching")

    def _log_scan(self, candidates: List[Dict]):
        """Log scan results"""
        try:
            if self.log_file.exists():
                with open(self.log_file) as f:
                    log = json.load(f)
            else:
                log = {"scans": []}

            log["scans"].append({
                "timestamp": datetime.now().isoformat(),
                "count": len(candidates),
                "top_candidates": candidates[:5]
            })

            log["scans"] = log["scans"][-100:]

            with open(self.log_file, 'w') as f:
                json.dump(log, f, indent=2)

        except Exception as e:
            print(f"[!] Log error: {e}")

    # =========================================================================
    # PUMP.FUN SCANNING (Earliest Entry Point)
    # =========================================================================

    def pumpfun_scan(self, limit: int = 30) -> List[Dict]:
        """
        Scan pump.fun for newest launches
        This is the EARLIEST possible entry - tokens just created
        """
        print("\n🚀 PUMP.FUN SCAN (New Launches)")
        print("=" * 60)
        print("⚠️  WARNING: These are BRAND NEW - extremely high risk!\n")

        coins = self.pumpfun.get_new_coins(limit=limit)

        if not coins:
            print("❌ Could not fetch pump.fun data")
            return []

        print(f"{'Symbol':12} | {'Name':20} | {'MC':>10} | {'Progress':>8} | {'Replies':>7}")
        print("-" * 75)

        results = []
        for coin in coins:
            formatted = self.pumpfun.format_token(coin)
            mc = formatted["market_cap"]
            progress = formatted["bonding_progress"]
            replies = formatted["reply_count"]

            # Progress bar
            prog_bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))

            print(f"{formatted['symbol'][:12]:12} | {formatted['name'][:20]:20} | ${mc:>9,.0f} | {prog_bar} | {replies:>7}")

            results.append(formatted)

        print(f"\n✅ Found {len(results)} new launches")
        print("\n💡 TIP: Look for tokens with high reply counts - indicates community interest")

        return results

    def pumpfun_graduating(self) -> List[Dict]:
        """
        Find tokens about to graduate from pump.fun to Raydium
        These get real liquidity soon - critical moment
        """
        print("\n🎓 GRADUATING TOKENS (Near Raydium Launch)")
        print("=" * 60)
        print("Tokens close to $69k bonding curve completion\n")

        coins = self.pumpfun.get_graduating(limit=50)

        if not coins:
            print("❌ No graduating tokens found")
            return []

        print(f"{'Symbol':12} | {'Name':20} | {'MC':>10} | {'Progress':>8}")
        print("-" * 60)

        results = []
        for coin in coins:
            formatted = self.pumpfun.format_token(coin)
            mc = formatted["market_cap"]
            progress = formatted["bonding_progress"]

            # Only show tokens 70%+ through bonding curve
            if progress >= 70:
                prog_bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
                print(f"{formatted['symbol'][:12]:12} | {formatted['name'][:20]:20} | ${mc:>9,.0f} | {prog_bar} {progress:.0f}%")
                results.append(formatted)

        print(f"\n✅ Found {len(results)} tokens near graduation")
        print("\n💡 TIP: Graduation = Raydium listing = real liquidity + volatility")

        return results

    def pumpfun_kings(self) -> List[Dict]:
        """
        Get 'King of the Hill' tokens - most momentum right now
        """
        print("\n👑 KING OF THE HILL (Hottest Right Now)")
        print("=" * 60)

        coins = self.pumpfun.get_king_of_hill()

        if not coins:
            print("❌ Could not fetch king of the hill")
            return []

        print(f"{'Symbol':12} | {'Name':20} | {'MC':>10} | {'Progress':>8}")
        print("-" * 60)

        results = []
        for coin in coins[:10]:
            formatted = self.pumpfun.format_token(coin)
            mc = formatted["market_cap"]
            progress = formatted["bonding_progress"]

            prog_bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
            print(f"{formatted['symbol'][:12]:12} | {formatted['name'][:20]:20} | ${mc:>9,.0f} | {prog_bar}")
            results.append(formatted)

        print(f"\n✅ Top {len(results)} momentum tokens")

        return results
