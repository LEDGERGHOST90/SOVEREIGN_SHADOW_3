#!/usr/bin/env python3
"""
📊 VALIDATION METRICS - SOVEREIGNSHADOW.AI
Track and validate paper trading performance
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from pathlib import Path

logger = logging.getLogger("validation_metrics")

class ValidationFramework:
    """Track and validate paper trading performance"""
    
    def __init__(self, config_path: str = "environments/staging/config_staging.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.trades = []
        self.daily_returns = []
        self.validation_start = datetime.now()
        self.log_file = Path("environments/staging/logs/paper_trades.json")
        
        # Validation targets from config
        self.targets = self.config['validation_metrics']
        
    def _load_config(self) -> Dict:
        """Load staging configuration"""
        try:
            import yaml
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def load_paper_trades(self) -> bool:
        """Load paper trading history from log file"""
        try:
            if not self.log_file.exists():
                logger.warning("No paper trades log file found")
                return False
            
            self.trades = []
            with open(self.log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            trade = json.loads(line.strip())
                            self.trades.append(trade)
                        except json.JSONDecodeError:
                            continue
            
            if self.trades:
                # Sort by timestamp
                self.trades.sort(key=lambda x: x.get('timestamp', ''))
                
                # Set validation start from first trade
                first_trade_time = datetime.fromisoformat(self.trades[0]['timestamp'].replace('Z', '+00:00'))
                self.validation_start = first_trade_time.replace(tzinfo=None)
                
                logger.info(f"📊 Loaded {len(self.trades)} paper trades")
                return True
            else:
                logger.warning("No valid trades found in log file")
                return False
                
        except Exception as e:
            logger.error(f"Error loading paper trades: {e}")
            return False
    
    def calculate_performance_metrics(self) -> Dict:
        """Calculate comprehensive performance metrics"""
        if not self.trades:
            return {"error": "No trades to analyze"}
        
        try:
            # Convert to DataFrame for easier analysis
            df = pd.DataFrame(self.trades)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Calculate trade returns
            trade_pairs = self._pair_buy_sell_trades(df)
            
            if not trade_pairs:
                return {"error": "No complete buy-sell pairs found"}
            
            returns = []
            for buy_trade, sell_trade in trade_pairs:
                # Calculate return for this pair
                buy_price = buy_trade['fill_price']
                sell_price = sell_trade['fill_price']
                size = buy_trade['size']
                buy_fees = buy_trade['fees']
                sell_fees = sell_trade['fees']
                
                # Return calculation
                gross_return = (sell_price - buy_price) * size
                net_return = gross_return - buy_fees - sell_fees
                return_pct = net_return / (buy_price * size)
                
                returns.append({
                    'timestamp': sell_trade['timestamp'],
                    'symbol': buy_trade['symbol'],
                    'buy_price': buy_price,
                    'sell_price': sell_price,
                    'size': size,
                    'gross_return': gross_return,
                    'net_return': net_return,
                    'return_pct': return_pct,
                    'buy_fees': buy_fees,
                    'sell_fees': sell_fees
                })
            
            returns_df = pd.DataFrame(returns)
            
            # Performance metrics
            total_return = returns_df['net_return'].sum()
            win_trades = returns_df[returns_df['net_return'] > 0]
            lose_trades = returns_df[returns_df['net_return'] <= 0]
            
            win_rate = len(win_trades) / len(returns_df) if len(returns_df) > 0 else 0
            avg_win = win_trades['net_return'].mean() if len(win_trades) > 0 else 0
            avg_loss = abs(lose_trades['net_return'].mean()) if len(lose_trades) > 0 else 0
            
            # Risk metrics
            returns_array = returns_df['return_pct'].values
            sharpe_ratio = np.mean(returns_array) / np.std(returns_array) if len(returns_array) > 1 and np.std(returns_array) > 0 else 0
            max_drawdown = self._calculate_max_drawdown(returns_df)
            
            # Time-based metrics
            days_trading = (datetime.now() - self.validation_start).days
            if days_trading == 0:
                days_trading = 1  # Avoid division by zero
            
            # Calculate monthly return
            starting_balance = self.config.get('trading_config', {}).get('starting_balance', 10000)
            monthly_return = (total_return / starting_balance) * (30 / days_trading)
            
            # Consistency calculation
            daily_returns = self._calculate_daily_returns(returns_df)
            consistency_score = self._calculate_consistency(daily_returns)
            
            # Validation status
            validation_status = self._determine_validation_status(
                monthly_return, win_rate, max_drawdown, days_trading
            )
            
            metrics = {
                'validation_period_days': days_trading,
                'total_trades': len(returns_df),
                'complete_trade_pairs': len(trade_pairs),
                'total_return': total_return,
                'monthly_return_pct': monthly_return * 100,
                'win_rate': win_rate,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': avg_win / avg_loss if avg_loss > 0 else 0,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown_pct': max_drawdown * 100,
                'consistency_score': consistency_score,
                'daily_returns': daily_returns,
                'validation_status': validation_status,
                'starting_balance': starting_balance,
                'current_portfolio_value': returns_df.iloc[-1].get('portfolio_value', starting_balance) if len(returns_df) > 0 else starting_balance,
                'timestamp': datetime.now().isoformat()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return {"error": f"Calculation error: {e}"}
    
    def _pair_buy_sell_trades(self, df: pd.DataFrame) -> List[tuple]:
        """Pair buy and sell trades for return calculation"""
        trade_pairs = []
        
        # Group by symbol
        for symbol, symbol_trades in df.groupby('symbol'):
            symbol_trades = symbol_trades.sort_values('timestamp')
            
            buys = symbol_trades[symbol_trades['side'] == 'BUY'].copy()
            sells = symbol_trades[symbol_trades['side'] == 'SELL'].copy()
            
            # Match buys with subsequent sells
            for _, buy_trade in buys.iterrows():
                # Find the next sell trade for the same symbol
                potential_sells = sells[sells['timestamp'] > buy_trade['timestamp']]
                if len(potential_sells) > 0:
                    sell_trade = potential_sells.iloc[0]
                    trade_pairs.append((buy_trade, sell_trade))
        
        return trade_pairs
    
    def _calculate_max_drawdown(self, returns_df: pd.DataFrame) -> float:
        """Calculate maximum drawdown"""
        try:
            # Calculate cumulative returns
            cumulative_returns = (1 + returns_df['return_pct']).cumprod()
            
            # Calculate running maximum
            running_max = cumulative_returns.expanding().max()
            
            # Calculate drawdowns
            drawdowns = (cumulative_returns - running_max) / running_max
            
            return abs(drawdowns.min()) if len(drawdowns) > 0 else 0
        except:
            return 0
    
    def _calculate_daily_returns(self, returns_df: pd.DataFrame) -> List[float]:
        """Calculate daily returns"""
        try:
            returns_df['date'] = returns_df['timestamp'].dt.date
            daily_returns = returns_df.groupby('date')['return_pct'].sum().tolist()
            return daily_returns
        except:
            return []
    
    def _calculate_consistency(self, daily_returns: List[float]) -> float:
        """Calculate consistency score (0-1, higher is better)"""
        if len(daily_returns) < 3:
            return 0.0
        
        try:
            mean_return = np.mean(daily_returns)
            if mean_return == 0:
                return 0.0
            
            std_dev = np.std(daily_returns)
            cv = std_dev / abs(mean_return)  # Coefficient of variation
            
            # Convert to consistency score (higher is better)
            consistency = max(0, 1 - cv)
            return min(1.0, consistency)
        except:
            return 0.0
    
    def _determine_validation_status(self, monthly_return: float, win_rate: float, 
                                   max_drawdown: float, days_trading: int) -> str:
        """Determine if system passes validation"""
        targets = self.targets
        
        criteria = {
            'monthly_return': monthly_return >= targets['target_monthly_return'],
            'win_rate': win_rate >= targets['min_win_rate'],
            'max_drawdown': max_drawdown <= targets['max_drawdown'],
            'min_days': days_trading >= targets['paper_trading_duration'],
            'min_trades': len(self.trades) >= 20  # Minimum trades for validation
        }
        
        passed_criteria = sum(criteria.values())
        
        if passed_criteria == 5:
            return "VALIDATION_PASSED"
        elif passed_criteria >= 4:
            return "VALIDATION_PROMISING"
        elif passed_criteria >= 3:
            return "VALIDATION_NEEDS_IMPROVEMENT"
        else:
            return "VALIDATION_FAILED"
    
    def generate_validation_report(self) -> str:
        """Generate comprehensive validation report"""
        metrics = self.calculate_performance_metrics()
        
        if "error" in metrics:
            return f"❌ Error generating report: {metrics['error']}"
        
        targets = self.targets
        
        report = f"""
📊 PAPER TRADING VALIDATION REPORT
{'='*60}
Validation Period: {metrics['validation_period_days']} days
Total Trades: {metrics['total_trades']} ({metrics['complete_trade_pairs']} complete pairs)
Starting Balance: ${metrics['starting_balance']:,.2f}
Current Portfolio: ${metrics['current_portfolio_value']:,.2f}

📈 PERFORMANCE METRICS:
Monthly Return: {metrics['monthly_return_pct']:.2f}% (Target: {targets['target_monthly_return']*100:.0f}%)
Win Rate: {metrics['win_rate']*100:.1f}% (Target: {targets['min_win_rate']*100:.0f}%)
Profit Factor: {metrics['profit_factor']:.2f}
Sharpe Ratio: {metrics['sharpe_ratio']:.2f} (Target: {targets['min_sharpe_ratio']})
Max Drawdown: {metrics['max_drawdown_pct']:.2f}% (Target: ≤{targets['max_drawdown']*100:.0f}%)
Consistency Score: {metrics['consistency_score']*100:.1f}%

🎯 VALIDATION STATUS: {metrics['validation_status']}

CRITERIA CHECK:
✅ Monthly Return ≥ {targets['target_monthly_return']*100:.0f}%: {'PASS' if metrics['monthly_return_pct'] >= targets['target_monthly_return']*100 else 'FAIL'}
✅ Win Rate ≥ {targets['min_win_rate']*100:.0f}%: {'PASS' if metrics['win_rate'] >= targets['min_win_rate'] else 'FAIL'}
✅ Max Drawdown ≤ {targets['max_drawdown']*100:.0f}%: {'PASS' if metrics['max_drawdown_pct'] <= targets['max_drawdown']*100 else 'FAIL'}
✅ Min {targets['paper_trading_duration']} Days: {'PASS' if metrics['validation_period_days'] >= targets['paper_trading_duration'] else 'FAIL'}
✅ Min 20 Trades: {'PASS' if metrics['total_trades'] >= 20 else 'FAIL'}

📋 RECOMMENDATIONS:
"""
        
        if metrics['validation_status'] == "VALIDATION_PASSED":
            report += """
🚀 SYSTEM READY FOR LIVE TRADING!

Next Steps:
1. Configure live API keys
2. Set starting capital ($100-500)
3. Deploy production environment
4. Monitor closely for first week
"""
        elif metrics['validation_status'] == "VALIDATION_PROMISING":
            report += """
⏳ SYSTEM SHOWING PROMISE

Continue paper trading for additional validation:
- Monitor consistency improvements
- Optimize risk management
- Consider extending validation period
"""
        else:
            report += """
⚠️ VALIDATION NEEDS IMPROVEMENT

Recommendations:
- Review trading strategy
- Adjust risk parameters
- Extend paper trading period
- Consider system optimization
"""
        
        return report
    
    def save_validation_report(self, report: str):
        """Save validation report to file"""
        try:
            report_file = Path("environments/staging/logs/validation_report.txt")
            report_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_file, 'w') as f:
                f.write(report)
            
            logger.info(f"📋 Validation report saved to: {report_file}")
        except Exception as e:
            logger.error(f"Error saving validation report: {e}")

def main():
    """Generate validation report"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate paper trading validation report')
    parser.add_argument('--config', default='environments/staging/config_staging.yaml', 
                       help='Configuration file path')
    parser.add_argument('--save', action='store_true', help='Save report to file')
    
    args = parser.parse_args()
    
    # Create validation framework
    validator = ValidationFramework(args.config)
    
    # Load trades
    if not validator.load_paper_trades():
        print("❌ No paper trades found. Run paper trading first.")
        return
    
    # Generate report
    report = validator.generate_validation_report()
    print(report)
    
    # Save if requested
    if args.save:
        validator.save_validation_report(report)

if __name__ == "__main__":
    main()
