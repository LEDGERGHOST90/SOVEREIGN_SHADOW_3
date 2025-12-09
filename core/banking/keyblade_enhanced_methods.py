#!/usr/bin/env python3
"""
KeybladeAI Enhanced Methods for Strategy Engine
Additional methods to support KeybladeAI integration in the strategy engine
"""

import json
import datetime
import logging
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

logger = logging.getLogger(__name__)

def prepare_portfolio_data(flip_memories) -> Dict[str, Any]:
    """Prepare portfolio data for KeybladeAI analysis"""
    
    if not flip_memories:
        # Default portfolio data
        return {
            'total_value': 1543.40,
            'change_24h': 0.0567,
            'holdings': [
                {'symbol': 'WIF', 'value': 464.69, 'allocation_percent': 30.1, 'change_24h': 0.12},
                {'symbol': 'BONK', 'value': 205.58, 'allocation_percent': 13.3, 'change_24h': -0.11},
                {'symbol': 'XRP', 'value': 202.06, 'allocation_percent': 13.1, 'change_24h': 0.08},
                {'symbol': 'BTC', 'value': 150.00, 'allocation_percent': 9.7, 'change_24h': -0.02}
            ]
        }
    
    # Calculate total value and holdings from flip memories
    total_value = sum([flip.current_price * 100 for flip in flip_memories])  # Approximate
    holdings = []
    
    for flip in flip_memories:
        if flip.status == 'ACTIVE':
            value = flip.current_price * 100  # Approximate position size
            allocation_percent = (value / total_value) * 100 if total_value > 0 else 0
            
            holdings.append({
                'symbol': flip.symbol,
                'value': value,
                'allocation_percent': allocation_percent,
                'change_24h': flip.pnl_percent / 100.0  # Convert to decimal
            })
    
    # Overall portfolio change
    if flip_memories:
        avg_pnl = np.mean([flip.pnl_percent for flip in flip_memories]) / 100.0
    else:
        avg_pnl = 0.0
    
    return {
        'total_value': total_value,
        'change_24h': avg_pnl,
        'holdings': holdings
    }

def prepare_market_data(whale_signals, market_volatility) -> Dict[str, Any]:
    """Prepare market data for KeybladeAI analysis"""
    
    market_data = {
        'volatility': market_volatility.get('overall_volatility', 0.045),
        'sentiment': 'NEUTRAL_BULLISH'
    }
    
    # Add whale signal data
    for signal in whale_signals:
        symbol = signal.symbol
        market_data[f'{symbol}_volume_change'] = signal.volume_spike
        market_data[f'{symbol}_price_impact'] = signal.price_impact
        
        # Estimate price change from whale activity
        if signal.signal_type == 'ACCUMULATION':
            price_change = signal.strength * 0.1  # Up to 10% positive
        elif signal.signal_type == 'DISTRIBUTION':
            price_change = -signal.strength * 0.08  # Up to 8% negative
        else:
            price_change = 0.0
        
        market_data[f'{symbol}_change_24h'] = price_change
        market_data[f'{symbol}_price'] = 1.0  # Placeholder price
    
    # Add some default market data for common symbols
    default_symbols = ['WIF', 'BONK', 'XRP', 'BTC', 'ETH']
    for symbol in default_symbols:
        if f'{symbol}_change_24h' not in market_data:
            # Generate realistic price changes
            change = np.random.normal(0, 0.05)  # 5% volatility
            market_data[f'{symbol}_change_24h'] = change
            market_data[f'{symbol}_volume_change'] = np.random.uniform(0.8, 2.0)
            market_data[f'{symbol}_price'] = np.random.uniform(0.1, 100.0)
    
    return market_data

def generate_keyblade_enhanced_commands(flip_memories, whale_signals, market_volatility,
                                      risk_evaluation, heat_maps, ladder_strategies):
    """Generate enhanced tactical commands using KeybladeAI intelligence"""
    
    from strategy_engine import TacticalCommand  # Import here to avoid circular import
    
    commands = []
    
    # PRIMARY COMMANDS - Based on KeybladeAI risk evaluation
    if risk_evaluation['recommendation'] == 'HALT':
        # High risk - defensive commands
        primary_command = TacticalCommand(
            priority="PRIMARY",
            action="RISK_MANAGEMENT",
            symbol="PORTFOLIO",
            reasoning="KeybladeAI risk evaluation recommends defensive posture",
            target_price=0.0,
            stop_loss=0.0,
            position_size=0.0,
            deadline=_generate_deadline(2),
            emotional_state=risk_evaluation['emotional_state']
        )
        commands.append(primary_command)
        
    elif risk_evaluation['recommendation'] == 'PROCEED':
        # Low risk - aggressive opportunities
        # Find highest heat score asset for primary action
        if heat_maps:
            best_opportunity = max(heat_maps.items(), key=lambda x: x[1]['opportunity_score'])
            symbol, heat_map = best_opportunity
            
            if heat_map['opportunity_score'] > 0.7:
                action = "FLIP_ENTRY" if heat_map['heat_score'] > 0.6 else "ACCUMULATE"
                primary_command = TacticalCommand(
                    priority="PRIMARY",
                    action=action,
                    symbol=symbol,
                    reasoning=f"KeybladeAI identifies high opportunity: {heat_map['opportunity_score']:.1%} score",
                    target_price=0.0,
                    stop_loss=0.0,
                    position_size=min(heat_map['opportunity_score'] * 0.15, 0.10),  # Max 10% position
                    deadline=_generate_deadline(6),
                    emotional_state=risk_evaluation['emotional_state']
                )
                commands.append(primary_command)
    
    # SECONDARY COMMANDS - Based on ladder strategies
    for symbol, ladder_strategy in ladder_strategies.items():
        if len(commands) >= 5:  # Limit total commands
            break
            
        secondary_command = TacticalCommand(
            priority="SECONDARY",
            action="LADDER_SETUP",
            symbol=symbol,
            reasoning=f"KeybladeAI ladder strategy: {ladder_strategy['aggression_mode']} mode",
            target_price=ladder_strategy['tp_levels'][0] if ladder_strategy['tp_levels'] else 0.0,
            stop_loss=ladder_strategy['sl_levels'][0] if ladder_strategy['sl_levels'] else 0.0,
            position_size=ladder_strategy['position_sizes'][0] if ladder_strategy['position_sizes'] else 0.05,
            deadline=_generate_deadline(12),
            emotional_state=risk_evaluation['emotional_state']
        )
        commands.append(secondary_command)
    
    # WATCHLIST COMMANDS - Based on heat maps
    for symbol, heat_map in heat_maps.items():
        if len(commands) >= 8:  # Limit total commands
            break
            
        if heat_map['urgency_score'] > 0.6 and symbol not in [cmd.symbol for cmd in commands]:
            watchlist_command = TacticalCommand(
                priority="WATCHLIST",
                action="MONITOR",
                symbol=symbol,
                reasoning=f"KeybladeAI heat map: {heat_map['urgency_score']:.1%} urgency",
                target_price=0.0,
                stop_loss=0.0,
                position_size=0.0,
                deadline=_generate_deadline(24),
                emotional_state=risk_evaluation['emotional_state']
            )
            commands.append(watchlist_command)
    
    # VAULT COMMANDS - Based on existing positions
    for flip in flip_memories:
        if len(commands) >= 10:  # Limit total commands
            break
            
        if flip.pnl_percent > 15.0 and flip.status == 'ACTIVE':  # 15%+ gains
            vault_command = TacticalCommand(
                priority="VAULT",
                action="VAULT_ROTATION",
                symbol=flip.symbol,
                reasoning=f"KeybladeAI recommends securing {flip.pnl_percent:.1f}% gains",
                target_price=flip.current_price,
                stop_loss=flip.entry_price * 1.05,  # 5% above entry
                position_size=0.5,  # Take 50% profits
                deadline=_generate_deadline(8),
                emotional_state=risk_evaluation['emotional_state']
            )
            commands.append(vault_command)
    
    return commands

def determine_enhanced_market_phase(whale_signals, market_volatility, risk_evaluation) -> str:
    """Determine market phase with KeybladeAI risk assessment"""
    
    # Base phase from whale signals
    accumulation_signals = sum(1 for signal in whale_signals if signal.signal_type == 'ACCUMULATION')
    distribution_signals = sum(1 for signal in whale_signals if signal.signal_type == 'DISTRIBUTION')
    
    # KeybladeAI risk adjustment
    risk_score = risk_evaluation['risk_score']
    
    if accumulation_signals > distribution_signals and risk_score < 0.4:
        return "ACCUMULATION_PHASE"
    elif distribution_signals > accumulation_signals or risk_score > 0.7:
        return "DISTRIBUTION_PHASE"
    elif risk_score < 0.3:
        return "BULL_MARKET"
    elif risk_score > 0.6:
        return "BEAR_MARKET"
    else:
        return "NEUTRAL_MARKET"

def _generate_deadline(hours: int) -> str:
    """Generate deadline string"""
    deadline = datetime.datetime.now() + datetime.timedelta(hours=hours)
    return deadline.strftime("%Y-%m-%d %H:%M")

