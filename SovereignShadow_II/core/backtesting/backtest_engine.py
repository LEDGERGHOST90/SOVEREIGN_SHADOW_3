import pandas as pd
from datetime import datetime, timedelta
import importlib
import sys
import os

# Ensure the root directory is in the path to allow dynamic imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

class BacktestEngine:
    def __init__(self, historical_data_path, performance_tracker):
        self.data = self._load_historical_data(historical_data_path)
        self.tracker = performance_tracker
    
    def _load_historical_data(self, path):
        """Load historical data"""
        if not os.path.exists(path):
            print(f"Warning: Data file {path} not found. Returning empty DataFrame.")
            return pd.DataFrame()
            
        # Assuming CSV has timestamp, open, high, low, close, volume
        try:
            df = pd.read_csv(path)
            # Ensure timestamp is datetime
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()
    
    def backtest_strategy(self, strategy_name, regime, timeframe='15m', 
                         start_date=None, end_date=None):
        """
        Run backtest for modularized strategy
        """
        if self.data.empty:
            return {'error': 'No historical data available'}

        try:
            # Import strategy modules dynamically
            # We assume the structure is strategies.modularized.<strategy_name>.<module>
            # And the class names are TitleCase
            
            # Helper to convert snake_case to TitleCase
            class_prefix = "".join(x.title() for x in strategy_name.split('_'))
            
            entry_module = importlib.import_module(
                f'strategies.modularized.{strategy_name}.entry'
            )
            exit_module = importlib.import_module(
                f'strategies.modularized.{strategy_name}.exit'
            )
            risk_module = importlib.import_module(
                f'strategies.modularized.{strategy_name}.risk'
            )
            
            EntryClass = getattr(entry_module, f'{class_prefix}Entry')
            ExitClass = getattr(exit_module, f'{class_prefix}Exit')
            RiskClass = getattr(risk_module, f'{class_prefix}Risk')
            
            entry = EntryClass()
            exit_logic = ExitClass()
            risk = RiskClass()
        except ImportError as e:
            return {'error': f'Could not import strategy modules: {e}'}
        except AttributeError as e:
            return {'error': f'Could not find strategy classes: {e}'}
        
        # Filter data by date range
        df = self.data.copy()
        if start_date:
            df = df[df['timestamp'] >= start_date]
        if end_date:
            df = df[df['timestamp'] <= end_date]
            
        if len(df) < 100:
             return {'error': 'Insufficient data for backtest (need > 100 rows)'}
        
        # Backtest simulation
        portfolio_value = 10000  # Starting capital
        trades = []
        position = None
        
        # Simple loop
        # Note: This is slow for large datasets, but follows the prompt's logic
        for i in range(100, len(df)):  
            current_slice = df.iloc[i-100:i]
            
            # Check for entry signal if not in position
            if position is None:
                entry_signal = entry.generate_signal(current_slice)
                
                if entry_signal['signal'] == 'BUY':
                    # Calculate position size
                    current_price = current_slice['close'].iloc[-1]
                    atr = self._calculate_atr(current_slice)
                    position_sizing = risk.calculate_position_size(
                        portfolio_value, current_price, atr
                    )
                    
                    if position_sizing['quantity'] > 0:
                        position = {
                            'entry_price': current_price,
                            'entry_time': current_slice['timestamp'].iloc[-1] if 'timestamp' in current_slice else i,
                            'quantity': position_sizing['quantity'],
                            'stop_loss': position_sizing['stop_loss_price'],
                            'take_profit': position_sizing['take_profit_price']
                        }
            
            # Check for exit signal if in position
            else:
                exit_signal = exit_logic.generate_signal(
                    current_slice, position['entry_price']
                )
                
                # Also check SL/TP via Price if logic doesn't catch it immediately (e.g. intraday high/low)
                # But here we just use close price for simplicity as per prompt
                
                if exit_signal['signal'] == 'SELL':
                    exit_price = current_slice['close'].iloc[-1]
                    pnl = (exit_price - position['entry_price']) * position['quantity']
                    pnl_percent = ((exit_price - position['entry_price']) / 
                                  position['entry_price']) * 100
                    
                    trades.append({
                        'entry_time': position['entry_time'],
                        'exit_time': current_slice['timestamp'].iloc[-1] if 'timestamp' in current_slice else i,
                        'entry_price': position['entry_price'],
                        'exit_price': exit_price,
                        'quantity': position['quantity'],
                        'pnl_usd': pnl,
                        'pnl_percent': pnl_percent,
                        'exit_reason': exit_signal.get('reason', 'UNKNOWN')
                    })
                    
                    portfolio_value += pnl
                    position = None
        
        # Calculate metrics
        if trades:
            wins = [t for t in trades if t['pnl_usd'] > 0]
            win_rate = (len(wins) / len(trades)) * 100
            
            return {
                'strategy_name': strategy_name,
                'regime': regime,
                'total_trades': len(trades),
                'win_rate': win_rate,
                'avg_pnl_percent': sum(t['pnl_percent'] for t in trades) / len(trades),
                'total_pnl_usd': portfolio_value - 10000,
                'sharpe_ratio': self._calculate_sharpe(trades),
                'max_drawdown': self._calculate_max_drawdown(trades),
                'trades': trades
            }
        
        return {'strategy_name': strategy_name, 'total_trades': 0, 'status': 'No trades executed'}
    
    def _calculate_atr(self, df, period=14):
        high = df['high']
        low = df['low']
        close = df['close']
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean().iloc[-1]
    
    def _calculate_sharpe(self, trades):
        if not trades:
            return 0
        returns = [t['pnl_percent'] for t in trades]
        if len(returns) < 2: return 0
        return (sum(returns) / len(returns)) / (pd.Series(returns).std() + 0.0001)
    
    def _calculate_max_drawdown(self, trades):
        cumulative = 0
        peak = 0
        max_dd = 0
        
        for trade in trades:
            cumulative += trade['pnl_usd']
            if cumulative > peak:
                peak = cumulative
            drawdown = peak - cumulative
            if drawdown > max_dd:
                max_dd = drawdown
        
        return max_dd
