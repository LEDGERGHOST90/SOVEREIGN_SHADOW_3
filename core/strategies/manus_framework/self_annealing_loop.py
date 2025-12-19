#!/usr/bin/env python3.11
"""
Self-Annealing Loop: Adaptive Strategy Improvement System
Implements the error detection, analysis, and automatic improvement cycle
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class PerformanceTracker:
    """Tracks strategy performance across different market regimes"""
    
    def __init__(self, db_path: str = "/home/ubuntu/strategy_performance.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for performance tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create performance log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                strategy_name TEXT NOT NULL,
                regime TEXT NOT NULL,
                action TEXT NOT NULL,
                entry_price REAL,
                exit_price REAL,
                pnl_percent REAL,
                success INTEGER,
                error_message TEXT,
                context TEXT
            )
        """)
        
        # Create strategy statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_stats (
                strategy_name TEXT NOT NULL,
                regime TEXT NOT NULL,
                total_trades INTEGER DEFAULT 0,
                successful_trades INTEGER DEFAULT 0,
                failed_trades INTEGER DEFAULT 0,
                avg_pnl REAL DEFAULT 0.0,
                confidence_score REAL DEFAULT 0.5,
                last_updated TEXT,
                PRIMARY KEY (strategy_name, regime)
            )
        """)
        
        # Create improvement log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS improvement_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                strategy_name TEXT NOT NULL,
                issue_detected TEXT NOT NULL,
                analysis TEXT NOT NULL,
                proposed_fix TEXT NOT NULL,
                status TEXT DEFAULT 'pending'
            )
        """)
        
        conn.commit()
        conn.close()
    
    def log_trade(self, strategy_name: str, regime: str, action: str, 
                  entry_price: float, exit_price: Optional[float] = None,
                  success: bool = True, error_message: str = None,
                  context: Dict = None):
        """Log a trade execution"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        pnl_percent = None
        if exit_price and entry_price:
            if action == "LONG":
                pnl_percent = ((exit_price - entry_price) / entry_price) * 100
            elif action == "SHORT":
                pnl_percent = ((entry_price - exit_price) / entry_price) * 100
        
        cursor.execute("""
            INSERT INTO performance_log 
            (timestamp, strategy_name, regime, action, entry_price, exit_price, 
             pnl_percent, success, error_message, context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            strategy_name,
            regime,
            action,
            entry_price,
            exit_price,
            pnl_percent,
            1 if success else 0,
            error_message,
            json.dumps(context) if context else None
        ))
        
        conn.commit()
        conn.close()
        
        # Update statistics
        self._update_statistics(strategy_name, regime, success, pnl_percent)
    
    def _update_statistics(self, strategy_name: str, regime: str, 
                          success: bool, pnl_percent: Optional[float]):
        """Update strategy statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current stats
        cursor.execute("""
            SELECT total_trades, successful_trades, failed_trades, avg_pnl
            FROM strategy_stats
            WHERE strategy_name = ? AND regime = ?
        """, (strategy_name, regime))
        
        result = cursor.fetchone()
        
        if result:
            total, successful, failed, avg_pnl = result
            total += 1
            if success:
                successful += 1
            else:
                failed += 1
            
            # Update average PnL
            if pnl_percent is not None:
                avg_pnl = ((avg_pnl * (total - 1)) + pnl_percent) / total
            
            # Calculate confidence score (success rate with recency bias)
            confidence_score = (successful / total) * 0.7 + 0.3  # Base confidence
            
            cursor.execute("""
                UPDATE strategy_stats
                SET total_trades = ?, successful_trades = ?, failed_trades = ?,
                    avg_pnl = ?, confidence_score = ?, last_updated = ?
                WHERE strategy_name = ? AND regime = ?
            """, (total, successful, failed, avg_pnl, confidence_score,
                  datetime.now().isoformat(), strategy_name, regime))
        else:
            # Insert new record
            confidence_score = 0.5  # Default confidence
            cursor.execute("""
                INSERT INTO strategy_stats
                (strategy_name, regime, total_trades, successful_trades, 
                 failed_trades, avg_pnl, confidence_score, last_updated)
                VALUES (?, ?, 1, ?, ?, ?, ?, ?)
            """, (strategy_name, regime, 1 if success else 0, 0 if success else 1,
                  pnl_percent or 0.0, confidence_score, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_strategy_confidence(self, strategy_name: str, regime: str) -> float:
        """Get confidence score for a strategy in a specific regime"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT confidence_score FROM strategy_stats
            WHERE strategy_name = ? AND regime = ?
        """, (strategy_name, regime))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 0.5  # Default confidence
    
    def get_underperforming_strategies(self, threshold: float = 0.4) -> List[Dict]:
        """Identify strategies that need improvement"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT strategy_name, regime, total_trades, successful_trades,
                   failed_trades, avg_pnl, confidence_score
            FROM strategy_stats
            WHERE confidence_score < ? AND total_trades >= 5
            ORDER BY confidence_score ASC
        """, (threshold,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'strategy_name': r[0],
            'regime': r[1],
            'total_trades': r[2],
            'successful_trades': r[3],
            'failed_trades': r[4],
            'avg_pnl': r[5],
            'confidence_score': r[6]
        } for r in results]


class SelfAnnealingLoop:
    """Implements the self-improvement cycle"""
    
    def __init__(self, tracker: PerformanceTracker):
        self.tracker = tracker
    
    def detect_errors(self) -> List[Dict]:
        """Step 1: Detect underperforming strategies"""
        print("🔍 Step 1: Detecting errors and underperformance...")
        underperforming = self.tracker.get_underperforming_strategies()
        
        if underperforming:
            print(f"   Found {len(underperforming)} strategies needing improvement")
            for strategy in underperforming:
                print(f"   - {strategy['strategy_name']} in {strategy['regime']}: "
                      f"{strategy['confidence_score']:.2%} confidence")
        else:
            print("   ✅ All strategies performing within acceptable range")
        
        return underperforming
    
    def analyze_failures(self, strategy_info: Dict) -> Dict:
        """Step 2: Analyze why a strategy is failing"""
        print(f"\n🔬 Step 2: Analyzing {strategy_info['strategy_name']}...")
        
        conn = sqlite3.connect(self.tracker.db_path)
        cursor = conn.cursor()
        
        # Get recent failed trades
        cursor.execute("""
            SELECT action, entry_price, exit_price, pnl_percent, error_message, context
            FROM performance_log
            WHERE strategy_name = ? AND regime = ? AND success = 0
            ORDER BY timestamp DESC
            LIMIT 10
        """, (strategy_info['strategy_name'], strategy_info['regime']))
        
        failures = cursor.fetchall()
        conn.close()
        
        # Analyze patterns
        analysis = {
            'strategy_name': strategy_info['strategy_name'],
            'regime': strategy_info['regime'],
            'failure_count': len(failures),
            'common_issues': [],
            'avg_loss': strategy_info['avg_pnl'],
            'success_rate': (strategy_info['successful_trades'] / 
                           strategy_info['total_trades'] * 100)
        }
        
        # Identify common failure patterns
        error_messages = [f[4] for f in failures if f[4]]
        if error_messages:
            analysis['common_issues'].append(f"Errors: {', '.join(set(error_messages))}")
        
        if analysis['avg_loss'] < -5:
            analysis['common_issues'].append("Large average losses")
        
        if analysis['success_rate'] < 30:
            analysis['common_issues'].append("Very low success rate")
        
        print(f"   Success Rate: {analysis['success_rate']:.1f}%")
        print(f"   Average PnL: {analysis['avg_loss']:.2f}%")
        print(f"   Issues: {', '.join(analysis['common_issues'])}")
        
        return analysis
    
    def propose_fix(self, analysis: Dict) -> Dict:
        """Step 3: Propose improvements"""
        print(f"\n🔧 Step 3: Proposing fixes...")
        
        fixes = {
            'strategy_name': analysis['strategy_name'],
            'regime': analysis['regime'],
            'recommendations': []
        }
        
        # Generate specific recommendations based on analysis
        if analysis['avg_loss'] < -5:
            fixes['recommendations'].append({
                'issue': 'Large average losses',
                'fix': 'Tighten stop-loss from current level to 2% max loss',
                'priority': 'HIGH'
            })
        
        if analysis['success_rate'] < 30:
            fixes['recommendations'].append({
                'issue': 'Low success rate',
                'fix': 'Add additional confirmation indicators (e.g., volume filter)',
                'priority': 'HIGH'
            })
        
        if 'Errors' in str(analysis['common_issues']):
            fixes['recommendations'].append({
                'issue': 'Execution errors',
                'fix': 'Add error handling and retry logic',
                'priority': 'MEDIUM'
            })
        
        # Regime-specific fixes
        if analysis['regime'] == 'High Volatility Trend':
            fixes['recommendations'].append({
                'issue': 'Volatility mismatch',
                'fix': 'Increase position sizing caution, use wider stops',
                'priority': 'MEDIUM'
            })
        
        for i, rec in enumerate(fixes['recommendations'], 1):
            print(f"   {i}. [{rec['priority']}] {rec['issue']}")
            print(f"      → {rec['fix']}")
        
        return fixes
    
    def log_improvement(self, analysis: Dict, fixes: Dict):
        """Step 4: Log the improvement plan"""
        print(f"\n📝 Step 4: Logging improvement plan...")
        
        conn = sqlite3.connect(self.tracker.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO improvement_log
            (timestamp, strategy_name, issue_detected, analysis, proposed_fix, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        """, (
            datetime.now().isoformat(),
            analysis['strategy_name'],
            ', '.join(analysis['common_issues']),
            json.dumps(analysis),
            json.dumps(fixes),
        ))
        
        conn.commit()
        conn.close()
        
        print(f"   ✅ Improvement plan logged for {analysis['strategy_name']}")
    
    def run_cycle(self):
        """Execute the complete self-annealing cycle"""
        print("\n" + "="*70)
        print("🔄 SELF-ANNEALING LOOP: Starting Improvement Cycle")
        print("="*70)
        
        # Step 1: Detect errors
        underperforming = self.detect_errors()
        
        if not underperforming:
            print("\n✅ System is healthy. No improvements needed at this time.")
            return
        
        # Process each underperforming strategy
        for strategy_info in underperforming[:3]:  # Limit to top 3
            # Step 2: Analyze
            analysis = self.analyze_failures(strategy_info)
            
            # Step 3: Propose fixes
            fixes = self.propose_fix(analysis)
            
            # Step 4: Log improvement
            self.log_improvement(analysis, fixes)
        
        print("\n" + "="*70)
        print("✅ Self-Annealing Cycle Complete")
        print("="*70)
        print("\n💡 Next Steps:")
        print("   1. Review improvement logs in the database")
        print("   2. Implement recommended fixes to strategy code")
        print("   3. Re-test strategies with updated parameters")
        print("   4. Monitor performance in next cycle\n")


if __name__ == "__main__":
    # Initialize tracker
    tracker = PerformanceTracker()
    
    # Simulate some performance data for demonstration
    print("📊 Simulating strategy performance data...\n")
    
    # Good strategy
    for i in range(10):
        tracker.log_trade(
            "VolatilityBandit", "High Volatility Range", "LONG",
            100, 102, success=True
        )
    
    # Underperforming strategy
    for i in range(8):
        tracker.log_trade(
            "MomentumBandwidth", "Low Volatility Trend", "LONG",
            100, 97, success=False, error_message="Stop loss hit"
        )
    
    # Run self-annealing loop
    loop = SelfAnnealingLoop(tracker)
    loop.run_cycle()
