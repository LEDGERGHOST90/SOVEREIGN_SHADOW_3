#!/usr/bin/env python3
"""
OVERNIGHT RUNNER - SS_III Autonomous Trading System
Runs overnight monitoring, analysis, and signal generation

Components:
- Live Data Pipeline → Real-time prices
- Research Swarm → Multi-AI analysis (Manus, Gemini, DS-Star)
- Strategy Engine → Regime detection
- Agent Council → Trading signals
- Replit Push → Results persistence

Usage:
    python bin/overnight_runner.py [--interval 15] [--paper]
"""

import os
import sys
import json
import time
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
SS3_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SS3_ROOT))
sys.path.insert(0, str(SS3_ROOT / 'src'))  # For pandas_ta shim

from dotenv import load_dotenv
load_dotenv(SS3_ROOT / '.env', override=True)

# Trading profiles
try:
    from core.config.trading_profiles import get_profile_for_symbol, ProfileType, PROFILES
except ImportError:
    get_profile_for_symbol = None
    ProfileType = None
    PROFILES = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(SS3_ROOT / 'logs' / f'overnight_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('overnight_runner')


class OvernightRunner:
    """
    SS_III Overnight Autonomous Runner

    Continuously monitors markets and generates signals
    """

    def __init__(self, interval_minutes: int = 15, paper_mode: bool = True):
        self.interval = interval_minutes * 60  # Convert to seconds
        self.paper_mode = paper_mode
        self.running = False
        self.cycle_count = 0

        # Load BRAIN.json
        self.brain_path = SS3_ROOT / 'BRAIN.json'
        self.brain = self._load_brain()

        # Initialize components
        self._init_components()

        # Results storage
        self.results_path = SS3_ROOT / 'data' / 'overnight_results'
        self.results_path.mkdir(exist_ok=True)

        # Alpha Executor (bias-driven execution)
        try:
            from core.alpha_executor import AlphaExecutor
            self.alpha_executor = AlphaExecutor()
            logger.info("✓ Alpha Executor (bias-driven execution)")
        except Exception as e:
            logger.warning(f"✗ Alpha Executor: {e} (falling back to direct execution)")
            self.alpha_executor = None

        # MoonDev Signals (verified strategies)
        try:
            from core.signals.moondev_signals import MoonDevSignals
            self.moondev = MoonDevSignals()
            logger.info("✓ MoonDev Signals (3 verified strategies)")
        except Exception as e:
            logger.warning(f"✗ MoonDev Signals: {e}")
            self.moondev = None

        # Outrageous Filter (final gate - only undeniable signals)
        try:
            from core.outrageous_filter import OutrageousFilter
            self.outrageous_filter = OutrageousFilter()
            logger.info("✓ Outrageous Filter (only undeniable signals execute)")
        except Exception as e:
            logger.warning(f"✗ Outrageous Filter: {e}")
            self.outrageous_filter = None

    def _load_brain(self) -> dict:
        """Load BRAIN.json"""
        try:
            with open(self.brain_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load BRAIN.json: {e}")
            return {}

    def _init_components(self):
        """Initialize all trading components"""
        logger.info("Initializing components...")

        # Live Data Pipeline
        try:
            from core.integrations.live_data_pipeline import LiveDataPipeline
            self.data_pipeline = LiveDataPipeline()
            logger.info("✓ Live Data Pipeline")
        except Exception as e:
            logger.error(f"✗ Live Data Pipeline: {e}")
            self.data_pipeline = None

        # Research Swarm
        try:
            from core.integrations.research_swarm import ResearchSwarm
            self.research_swarm = ResearchSwarm()
            logger.info("✓ Research Swarm")
        except Exception as e:
            logger.error(f"✗ Research Swarm: {e}")
            self.research_swarm = None

        # Strategy Engine
        try:
            from core.strategies.strategy_engine import StrategyEngine
            self.strategy_engine = StrategyEngine()
            logger.info("✓ Strategy Engine")
        except Exception as e:
            logger.warning(f"⚠ Strategy Engine: {e}")
            self.strategy_engine = None

        # Agent Orchestrator
        try:
            from core.orchestrator import AgentOrchestrator
            self.orchestrator = AgentOrchestrator()
            logger.info(f"✓ Agent Orchestrator ({len(self.orchestrator.agents)} agents)")
        except Exception as e:
            logger.warning(f"⚠ Agent Orchestrator: {e}")
            self.orchestrator = None

        # Paper Trader
        try:
            from core.agents_highlevel.execution.paper_trader import PaperTrader
            from core.agents_highlevel.base_agent import Signal
            self.paper_trader = PaperTrader()
            self.Signal = Signal
            logger.info("✓ Paper Trader")
        except Exception as e:
            logger.warning(f"⚠ Paper Trader: {e}")
            self.paper_trader = None
            self.Signal = None

    def run_cycle(self) -> dict:
        """Run one analysis cycle"""
        self.cycle_count += 1
        cycle_start = datetime.now()

        logger.info(f"\n{'='*60}")
        logger.info(f"CYCLE {self.cycle_count} - {cycle_start.isoformat()}")
        logger.info(f"{'='*60}")

        # Check open positions for SL/TP hits
        if self.paper_trader and self.data_pipeline:
            try:
                prices = self.data_pipeline.get_current_prices()
                current_prices = {s: p.get('price', 0) for s, p in prices.items()}
                triggered = self.paper_trader.check_stops(current_prices)

                for trade_id, exit_price, reason in triggered:
                    result = self.paper_trader.close_trade(trade_id, exit_price)
                    emoji = "✅" if result.get('pnl_usd', 0) > 0 else "❌"
                    logger.info(f"  {emoji} {reason}: Closed {trade_id} @ ${exit_price:.2f} | PnL: ${result.get('pnl_usd', 0):.2f}")
            except Exception as e:
                logger.warning(f"Stop check error: {e}")

        results = {
            'cycle': self.cycle_count,
            'timestamp': cycle_start.isoformat(),
            'paper_mode': self.paper_mode,
            'components': {},
            'signals': {},
            'opportunities': []
        }

        # 1. Live Data Scan
        if self.data_pipeline:
            logger.info("\n[1/4] Live Data Pipeline...")
            try:
                scan_results = self.data_pipeline.scan_all()
                results['components']['live_data'] = 'OK'
                results['signals'] = scan_results.get('signals', {})
                results['summary'] = scan_results.get('summary', {})

                # Log signals
                for symbol, signal in results['signals'].items():
                    logger.info(f"  {symbol}: {signal.get('direction')} ({signal.get('confidence')}%)")

            except Exception as e:
                logger.error(f"  Live data error: {e}")
                results['components']['live_data'] = f'ERROR: {e}'

        # 1.5. MoonDev Signals (verified strategies)
        if self.moondev:
            logger.info("\n[1.5/5] MoonDev Strategy Signals...")
            try:
                import ccxt
                import pandas as pd

                # Exchanges: binance.us, kraken, coinbase (user confirmed)
                exchanges = [
                    ('binanceus', ccxt.binanceus()),
                    ('kraken', ccxt.kraken()),
                    ('coinbase', ccxt.coinbase()),
                ]

                def get_ohlcv_multi(sym: str):
                    """Try multiple exchanges for OHLCV data"""
                    for name, ex in exchanges:
                        try:
                            pair = f"{sym}/USD"
                            ohlcv = ex.fetch_ohlcv(pair, '1h', limit=200)
                            if ohlcv and len(ohlcv) > 100:
                                return ohlcv, name
                        except:
                            try:
                                pair = f"{sym}/USDT"
                                ohlcv = ex.fetch_ohlcv(pair, '1h', limit=200)
                                if ohlcv and len(ohlcv) > 100:
                                    return ohlcv, name
                            except:
                                continue
                    return None, None

                # Symbols: BRAIN watchlist + Manus immediate + Hayes rotation
                moondev_symbols = ['BTC', 'ETH', 'SOL', 'ENA', 'PENDLE', 'LDO']
                moondev_results = {}

                for symbol in moondev_symbols:
                    try:
                        ohlcv, source = get_ohlcv_multi(symbol)

                        if ohlcv and len(ohlcv) > 100:
                            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                            df.set_index('timestamp', inplace=True)

                            consensus = self.moondev.get_consensus(df)
                            consensus['source'] = source
                            moondev_results[symbol] = consensus

                            if consensus['action'] != 'WAIT':
                                logger.info(f"  {symbol}: {consensus['action']} (score: {consensus['score']:.2f}, conf: {consensus['confidence']:.0%}) [{source}]")
                            else:
                                logger.info(f"  {symbol}: WAIT [{source}]")
                        else:
                            logger.warning(f"  {symbol}: No data on any exchange")

                    except Exception as e:
                        logger.warning(f"  {symbol}: {e}")

                results['moondev_signals'] = moondev_results
                results['components']['moondev'] = 'OK'

            except Exception as e:
                logger.error(f"  MoonDev error: {e}")
                results['components']['moondev'] = f'ERROR: {e}'

        # 2. Research Swarm (dispatch async)
        if self.research_swarm:
            logger.info("\n[2/4] Research Swarm...")
            try:
                # Only run deep research every 4 cycles (1 hour if 15min interval)
                if self.cycle_count % 4 == 1:
                    swarm_result = self.research_swarm.research(
                        query="Current crypto market conditions, regime, and top opportunities",
                        context=f"SS_III cycle {self.cycle_count}",
                        asset="BTC",
                        wait_for_manus=False,  # Don't block - Manus runs async
                        manus_timeout=30  # Short timeout if we do wait
                    )
                    results['components']['research_swarm'] = 'DISPATCHED'
                    results['manus_task'] = swarm_result.get('sources', {}).get('manus', {}).get('url')
                    logger.info(f"  Manus task: {results.get('manus_task')}")
                else:
                    results['components']['research_swarm'] = 'SKIPPED (runs hourly)'
                    logger.info("  Skipped (runs hourly)")

            except Exception as e:
                logger.error(f"  Research swarm error: {e}")
                results['components']['research_swarm'] = f'ERROR: {e}'

        # 3. Agent Council Opinion
        if self.orchestrator:
            logger.info("\n[3/4] Agent Council...")
            try:
                # Get council opinion on top opportunity
                long_signals = results.get('summary', {}).get('long', [])
                short_signals = results.get('summary', {}).get('short', [])

                if long_signals:
                    symbol = long_signals[0]
                    opinion = self.orchestrator.get_council_opinion(symbol)
                    results['council_opinion'] = opinion
                    results['components']['agent_council'] = 'OK'
                    logger.info(f"  {symbol}: {opinion.get('recommendation')} ({opinion.get('confidence')}%)")
                elif short_signals:
                    symbol = short_signals[0]
                    opinion = self.orchestrator.get_council_opinion(symbol)
                    results['council_opinion'] = opinion
                    results['components']['agent_council'] = 'OK'
                    logger.info(f"  {symbol}: {opinion.get('recommendation')} ({opinion.get('confidence')}%)")
                else:
                    results['components']['agent_council'] = 'NO_SIGNALS'
                    logger.info("  No actionable signals")

            except Exception as e:
                logger.error(f"  Agent council error: {e}")
                results['components']['agent_council'] = f'ERROR: {e}'

        # 4. Generate Opportunities
        logger.info("\n[4/4] Opportunity Analysis...")
        opportunities = self._analyze_opportunities(results)
        results['opportunities'] = opportunities

        if opportunities:
            for opp in opportunities:
                logger.info(f"  🎯 {opp['symbol']}: {opp['direction']} @ ${opp['entry']:.2f}")
                logger.info(f"     SL: ${opp['stop_loss']:.2f} | TP: ${opp['take_profit']:.2f}")
                logger.info(f"     Size: ${opp['position_size']:.2f} | Confidence: {opp['confidence']}%")
        else:
            logger.info("  No opportunities meeting criteria")

        # 5. Execute via Alpha Executor (tiered execution)
        if opportunities:
            logger.info("\n[5/5] Alpha Executor Processing...")

            if self.alpha_executor:
                # Use bias-driven tiered execution
                for opp in opportunities:
                    try:
                        # Convert opportunity to raw signal format
                        raw_signal = {
                            "symbol": opp['symbol'],
                            "side": "BUY" if opp['direction'] == 'LONG' else "SELL",
                            "confidence": opp['confidence'],
                            "entry_price": opp['entry'],
                            "position_size_usd": opp['position_size'],
                            "source": "overnight_runner"
                        }

                        # Apply alpha bias
                        biased_signal = self.alpha_executor.apply_bias(raw_signal)

                        if biased_signal:
                            # Process through tier system
                            result = self.alpha_executor.process_signal(biased_signal)
                            logger.info(f"  [{result['tier']}] {result['action']}: {opp['symbol']} (conf: {biased_signal.confidence:.0f}%)")

                            results['alpha_executions'] = results.get('alpha_executions', [])
                            results['alpha_executions'].append(result)

                            # Also create paper trade if TIER_1_AUTO
                            if result['tier'] == 'TIER_1_AUTO' and self.paper_trader and self.paper_mode:
                                signal = self.Signal(
                                    symbol=opp['symbol'],
                                    action=opp['direction'],
                                    confidence=biased_signal.confidence,
                                    reasoning=f"Alpha Executor Auto: {opp.get('reasoning', '')}",
                                    source_agent='alpha_executor',
                                    entry_price=opp['entry'],
                                    stop_loss=biased_signal.stop_loss,
                                    take_profit=biased_signal.take_profit_1
                                )
                                paper_result = self.paper_trader.execute_signal(signal, biased_signal.position_size_usd)
                                logger.info(f"  📝 PAPER TRADE: {paper_result['symbol']} {paper_result['action']} @ ${paper_result['entry_price']:.2f}")
                                results['paper_trades'] = results.get('paper_trades', [])
                                results['paper_trades'].append(paper_result)
                        else:
                            logger.info(f"  ⏭️ {opp['symbol']}: Filtered by bias (below threshold)")

                    except Exception as e:
                        logger.error(f"  Alpha executor error for {opp['symbol']}: {e}")

            # Fallback to direct paper trading if no alpha executor
            elif self.paper_trader and self.paper_mode:
                logger.info("  (Fallback: Direct paper trading)")
                for opp in opportunities:
                    if opp['confidence'] >= 50:
                        try:
                            signal = self.Signal(
                                symbol=opp['symbol'],
                                action=opp['direction'],
                                confidence=opp['confidence'],
                                reasoning=opp.get('reasoning', 'Overnight runner signal'),
                                source_agent='overnight_runner',
                                entry_price=opp['entry'],
                                stop_loss=opp['stop_loss'],
                                take_profit=opp['take_profit']
                            )
                            result = self.paper_trader.execute_signal(signal, opp['position_size'])
                            logger.info(f"  📝 PAPER TRADE: {result['symbol']} {result['action']} @ ${result['entry_price']:.2f}")
                            results['paper_trades'] = results.get('paper_trades', [])
                            results['paper_trades'].append(result)
                        except Exception as e:
                            logger.error(f"  Paper trade error: {e}")

        # Save results
        self._save_results(results)

        # Push to Replit
        self._push_to_replit(results)

        cycle_time = (datetime.now() - cycle_start).total_seconds()
        logger.info(f"\nCycle completed in {cycle_time:.1f}s")

        return results

    def _analyze_opportunities(self, results: dict) -> list:
        """Analyze results and generate trading opportunities"""
        opportunities = []
        capital = self.brain.get('portfolio', {}).get('exchange_total', {}).get('total_usd', 734)

        # Priority 1: MoonDev signals (verified strategies)
        moondev_signals = results.get('moondev_signals', {})
        for symbol, moon in moondev_signals.items():
            if moon.get('action') in ['BUY', 'STRONG BUY']:
                # Convert MoonDev format to standard signal
                confidence = int(moon.get('confidence', 0) * 100)
                if confidence < 50:
                    continue

                # Get profile for this symbol
                if get_profile_for_symbol:
                    profile = get_profile_for_symbol(symbol)
                    sl_pct = profile.stop_loss_pct / 100
                    risk_pct = profile.risk_per_trade_pct / 100
                else:
                    sl_pct = 0.03
                    risk_pct = 0.02

                position_size = min(50, capital * risk_pct / sl_pct)

                opportunities.append({
                    'symbol': symbol,
                    'direction': 'LONG',
                    'entry': moon.get('entry', 0),
                    'stop_loss': moon.get('stop_loss', 0),
                    'take_profit': moon.get('take_profit', 0),
                    'position_size': round(position_size * (confidence / 100), 2),
                    'confidence': confidence,
                    'original_confidence': confidence,
                    'whale_boost': 0,
                    'regime': 'MoonDev',
                    'reasoning': f"🌙 MoonDev: {', '.join(moon.get('reasons', []))}",
                    'paper_mode': self.paper_mode,
                    'source': 'moondev'
                })

        # Priority 2: Live pipeline signals (fallback if no MoonDev)
        for symbol, signal in results.get('signals', {}).items():
            # Skip if we already have MoonDev signal for this symbol
            if symbol in moondev_signals and moondev_signals[symbol].get('action') != 'WAIT':
                continue
            # Filter criteria
            confidence = signal.get('confidence', 0)
            direction = signal.get('direction', 'NEUTRAL')

            if direction == 'NEUTRAL':
                continue
            if direction == 'SHORT':
                continue  # Skip shorts - Coinbase spot only (no margin/futures)

            # Get profile for this symbol
            if get_profile_for_symbol:
                profile = get_profile_for_symbol(symbol)
                min_conf = profile.min_confidence
                sl_pct = profile.stop_loss_pct / 100
                risk_pct = profile.risk_per_trade_pct / 100
            else:
                min_conf = 50
                sl_pct = 0.03
                risk_pct = 0.02

            if confidence < min_conf:
                continue

            position_size = min(50, capital * risk_pct / sl_pct)

            # Check whale activity for confidence boost
            whale_boost = 0
            whale_note = ""
            if self.data_pipeline:
                try:
                    whale = self.data_pipeline.get_whale_activity(symbol)
                    if whale and whale.net_flow != 0:
                        if whale.exchange_flow == 'accumulation' and direction == 'LONG':
                            whale_boost = min(15, abs(whale.net_flow))  # Up to +15% confidence
                            whale_note = f"🐋 Whale accumulation ({whale.net_flow:+.1f}%). "
                        elif whale.exchange_flow == 'distribution' and direction == 'SHORT':
                            whale_boost = min(15, abs(whale.net_flow))
                            whale_note = f"🐋 Whale distribution ({whale.net_flow:+.1f}%). "
                except Exception as e:
                    logger.warning(f"Whale check error for {symbol}: {e}")

            boosted_confidence = min(100, confidence + whale_boost)

            opportunities.append({
                'symbol': symbol,
                'direction': direction,
                'entry': signal.get('entry_price', 0),
                'stop_loss': signal.get('stop_loss', 0),
                'take_profit': signal.get('take_profit', 0),
                'position_size': round(position_size * (boosted_confidence / 100), 2),
                'confidence': boosted_confidence,
                'original_confidence': confidence,
                'whale_boost': whale_boost,
                'regime': signal.get('regime', 'Unknown'),
                'reasoning': whale_note + signal.get('reasoning', ''),
                'paper_mode': self.paper_mode
            })

        # Sort by confidence
        opportunities.sort(key=lambda x: x['confidence'], reverse=True)

        return opportunities[:3]  # Top 3 only

    def _save_results(self, results: dict):
        """Save results to file"""
        filename = f"cycle_{self.cycle_count}_{datetime.now().strftime('%H%M%S')}.json"
        filepath = self.results_path / filename

        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"Results saved: {filepath.name}")

    def _push_to_replit(self, results: dict):
        """Push results to Replit"""
        import requests

        replit_url = os.getenv('REPLIT_API_URL')
        if not replit_url:
             # Fallback to the known working Replit instance
             replit_url = "https://1cba4940-c378-451a-a9f4-741e180329ee-00-togxk2caarue.picard.replit.dev"
             logger.info(f"Using fallback Replit URL: {replit_url}")
             
        if not replit_url:
            logger.warning("No Replit URL configured - skipping Replit push")
            return

        try:
            response = requests.post(
                f"{replit_url}/api/manus-webhook",
                json={
                    'event': 'overnight.cycle',
                    'task_id': f'cycle_{self.cycle_count}',
                    'task_title': f'Overnight Cycle {self.cycle_count}',
                    'data': {
                        'timestamp': results.get('timestamp'),
                        'opportunities': len(results.get('opportunities', [])),
                        'summary': results.get('summary')
                    }
                },
                timeout=10
            )
            if response.status_code == 200:
                logger.info("Pushed to Replit ✓")
        except Exception as e:
            logger.warning(f"Replit push failed: {e}")

    def start(self, duration_hours: int = 8):
        """Start overnight monitoring"""
        end_time = datetime.now() + timedelta(hours=duration_hours)

        logger.info(f"\n{'='*60}")
        logger.info("SS_III OVERNIGHT RUNNER STARTING")
        logger.info(f"{'='*60}")
        logger.info(f"Mode: {'PAPER' if self.paper_mode else 'LIVE'}")
        logger.info(f"Interval: {self.interval // 60} minutes")
        logger.info(f"Duration: {duration_hours} hours")
        logger.info(f"End time: {end_time.isoformat()}")
        logger.info(f"{'='*60}\n")

        self.running = True

        try:
            while self.running and datetime.now() < end_time:
                self.run_cycle()

                if datetime.now() < end_time:
                    logger.info(f"\nSleeping {self.interval // 60} minutes until next cycle...")
                    time.sleep(self.interval)

        except KeyboardInterrupt:
            logger.info("\nShutdown requested by user")
        except Exception as e:
            logger.error(f"Runner error: {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop the runner"""
        self.running = False
        logger.info(f"\n{'='*60}")
        logger.info("OVERNIGHT RUNNER STOPPED")
        logger.info(f"Total cycles: {self.cycle_count}")
        logger.info(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description='SS_III Overnight Runner')
    parser.add_argument('--interval', type=int, default=15, help='Check interval in minutes')
    parser.add_argument('--duration', type=int, default=8, help='Run duration in hours')
    parser.add_argument('--paper', action='store_true', default=True, help='Paper trading mode')
    parser.add_argument('--live', action='store_true', help='Live trading mode (use with caution)')
    parser.add_argument('--once', action='store_true', help='Run single cycle and exit')

    args = parser.parse_args()

    paper_mode = not args.live

    runner = OvernightRunner(
        interval_minutes=args.interval,
        paper_mode=paper_mode
    )

    if args.once:
        runner.run_cycle()
    else:
        runner.start(duration_hours=args.duration)


if __name__ == '__main__':
    main()
