import pandas as pd
from datetime import datetime, timedelta
import importlib
import sys
import os

# Add workspace to path to allow importing strategies
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

class BacktestEngine:
    def __init__(self, historical_data_path, performance_tracker):
        self.data = self._load_historical_data(historical_data_path)
        self.tracker = performance_tracker
    
    def _load_historical_data(self, path):
        """Load Raymond's 1,896 transactions from Jan-Aug 2024"""
        if path.endswith('.csv'):
             return pd.read_csv(path)
        elif path.endswith('.json'):
             return pd.read_json(path)
        # Placeholder for mock data if file doesn't exist
        print(f"Warning: Data file {path} not found or format not supported. returning empty DF.")
        return pd.DataFrame()

    def backtest_strategy(self, strategy_name, regime, timeframe='15m', 
                         start_date=None, end_date=None):
        """
        Run backtest for modularized strategy
        """
        # Import strategy modules dynamically
        try:
            entry_module = importlib.import_module(
                f'strategies.modularized.{strategy_name}.entry'
            )
            exit_module = importlib.import_module(
                f'strategies.modularized.{strategy_name}.exit'
            )
            risk_module = importlib.import_module(
                f'strategies.modularized.{strategy_name}.risk'
            )
        except ImportError as e:
            return {'error': f"Could not import strategy {strategy_name}: {e}"}
        
        # Convert snake_case to CamelCase for class names
        class_name_base = ''.join(x.title() for x in strategy_name.split('_'))
        
        EntryClass = getattr(entry_module, f'{class_name_base}Entry')
        ExitClass = getattr(exit_module, f'{class_name_base}Exit')
        RiskClass = getattr(risk_module, f'{class_name_base}Risk')
        
        entry = EntryClass()
        exit_logic = ExitClass()
        risk = RiskClass()
        
        # Filter data by date range
        df = self.data.copy()
        if df.empty:
             return {'error': 'No data loaded'}

        if start_date:
            df = df[df['timestamp'] >= start_date]
        if end_date:
            df = df[df['timestamp'] <= end_date]
        
        # Backtest simulation
        portfolio_value = 10000  # Starting capital
        trades = []
        position = None
        
        for i in range(100, len(df)):  # Need 100 candles for indicators
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
                    
                    position = {
                        'entry_price': current_price,
                        'entry_time': current_slice['timestamp'].iloc[-1],
                        'quantity': position_sizing['quantity'],
                        'stop_loss': position_sizing['stop_loss_price'],
                        'take_profit': position_sizing['take_profit_price']
                    }
            
            # Check for exit signal if in position
            else:
                exit_signal = exit_logic.generate_signal(
                    current_slice, position['entry_price']
                )
                
                if exit_signal['signal'] == 'SELL':
                    exit_price = current_slice['close'].iloc[-1]
                    pnl = (exit_price - position['entry_price']) * position['quantity']
                    pnl_percent = ((exit_price - position['entry_price']) / 
                                  position['entry_price']) * 100
                    
                    trades.append({
                        'entry_time': position['entry_time'],
                        'exit_time': current_slice['timestamp'].iloc[-1],
                        'entry_price': position['entry_price'],
                        'exit_price': exit_price,
                        'quantity': position['quantity'],
                        'pnl_usd': pnl,
                        'pnl_percent': pnl_percent,
                        'exit_reason': exit_signal['reason']
                    })
                    
                    portfolio_value += pnl
                    position = None
        
        # Calculate metrics
        if trades:
            wins = [t for t in trades if t['pnl_usd'] > 0]
            win_rate = (len(wins) / len(trades)) * 100
            avg_win = sum(t['pnl_usd'] for t in wins) / len(wins) if wins else 0
            losses = [t for t in trades if t['pnl_usd'] <= 0]
            avg_loss = sum(t['pnl_usd'] for t in losses) / len(losses) if losses else 0
            
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
        
        return {'error': 'No trades executed'}
    
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
        std_dev = pd.Series(returns).std()
        if std_dev == 0:
            return 0
        return (sum(returns) / len(returns)) / (std_dev + 0.0001)
    
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
