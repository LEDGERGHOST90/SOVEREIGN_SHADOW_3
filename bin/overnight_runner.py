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
            from agents.execution.paper_trader import PaperTrader
            from agents.base_agent import Signal
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

        # 2. Research Swarm (dispatch async)
        if self.research_swarm:
            logger.info("\n[2/4] Research Swarm...")
            try:
                # Only run deep research every 4 cycles (1 hour if 15min interval)
                if self.cycle_count % 4 == 1:
                    swarm_result = self.research_swarm.research(
                        query="Current crypto market conditions, regime, and top opportunities",
                        context=f"SS_III cycle {self.cycle_count}",
                        asset="BTC"
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

        # 5. Execute Paper Trades
        if self.paper_trader and self.paper_mode and opportunities:
            logger.info("\n[5/5] Paper Trade Execution...")
            for opp in opportunities:
                if opp['confidence'] >= 50:
                    try:
                        # Create Signal object
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
                        # Execute paper trade
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

        for symbol, signal in results.get('signals', {}).items():
            # Filter criteria
            confidence = signal.get('confidence', 0)
            direction = signal.get('direction', 'NEUTRAL')

            if direction == 'NEUTRAL':
                continue
            if confidence < 50:  # Minimum 50% confidence
                continue

            position_size = min(50, capital * 0.02 / 0.03)  # 2% risk, 3% stop

            opportunities.append({
                'symbol': symbol,
                'direction': direction,
                'entry': signal.get('entry_price', 0),
                'stop_loss': signal.get('stop_loss', 0),
                'take_profit': signal.get('take_profit', 0),
                'position_size': round(position_size * (confidence / 100), 2),
                'confidence': confidence,
                'regime': signal.get('regime', 'Unknown'),
                'reasoning': signal.get('reasoning', ''),
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
