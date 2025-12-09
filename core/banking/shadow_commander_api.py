#!/usr/bin/env python3
"""
ShadowCommander API - REST endpoints for the Sovereign Brainstem
Provides API access to daily tactical strategies and command generation
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import datetime
from pathlib import Path
import logging
from shadow_commander_engine import ShadowCommanderEngine, DailyBattlePlan, TacticalCommand
from strategy_engine import StrategyEngine, DailyStrategy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize engines
commander = ShadowCommanderEngine()
strategy_engine = StrategyEngine()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'operational',
        'service': 'ShadowCommander API',
        'version': '2.0.0',
        'engines': {
            'shadow_commander': 'operational',
            'strategy_engine': 'operational'
        },
        'timestamp': datetime.datetime.now().isoformat()
    })

@app.route('/api/strategy', methods=['GET'])
def get_daily_strategy():
    """Get today's complete tactical strategy"""
    try:
        # Check if we have a cached strategy for today
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        strategy_file = f"/home/ubuntu/LLF-Beta/daily_strategies/strategy_{today}.json"
        
        if Path(strategy_file).exists():
            # Load existing strategy
            with open(strategy_file, 'r') as f:
                strategy_data = json.load(f)
        else:
            # Generate new strategy
            strategy = strategy_engine.generate_daily_strategy()
            strategy_engine.save_strategy(strategy)
            
            # Convert to dict for JSON response
            strategy_data = {
                'date': strategy.date,
                'emotional_state': strategy.emotional_state,
                'market_phase': strategy.market_phase,
                'primary_directive': strategy.primary_directive,
                'commands': [
                    {
                        'priority': cmd.priority,
                        'action': cmd.action,
                        'symbol': cmd.symbol,
                        'reasoning': cmd.reasoning,
                        'target_price': cmd.target_price,
                        'stop_loss': cmd.stop_loss,
                        'position_size': cmd.position_size,
                        'deadline': cmd.deadline,
                        'emotional_state': cmd.emotional_state
                    } for cmd in strategy.commands
                ],
                'risk_level': strategy.risk_level,
                'confidence_score': strategy.confidence_score,
                'generated_at': strategy.generated_at
            }
        
        return jsonify({
            'success': True,
            'data': strategy_data
        })
        
    except Exception as e:
        logger.error(f"Error generating daily strategy: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/strategy/notion', methods=['GET'])
def get_strategy_notion_format():
    """Get today's strategy in Notion-compatible markdown format"""
    try:
        # Generate strategy
        strategy = strategy_engine.generate_daily_strategy()
        
        # Format for Notion
        notion_markdown = strategy_engine.format_for_notion(strategy)
        
        return jsonify({
            'success': True,
            'data': {
                'markdown': notion_markdown,
                'date': strategy.date,
                'emotional_state': strategy.emotional_state,
                'generated_at': strategy.generated_at
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating Notion format: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/strategy/commands', methods=['GET'])
def get_tactical_commands():
    """Get today's tactical commands as simple action items"""
    try:
        # Generate strategy
        strategy = strategy_engine.generate_daily_strategy()
        
        # Convert to simple command strings
        command_strings = []
        priority_emojis = {
            'PRIMARY': '🎯',
            'SECONDARY': '⚡',
            'WATCHLIST': '👁️',
            'VAULT': '🏛️'
        }
        
        for cmd in strategy.commands:
            emoji = priority_emojis.get(cmd.priority, '📋')
            command_strings.append(f"{cmd.emotional_state} {emoji} {cmd.action}: {cmd.reasoning}")
        
        return jsonify({
            'success': True,
            'data': {
                'commands': command_strings,
                'emotional_state': strategy.emotional_state,
                'primary_directive': strategy.primary_directive,
                'count': len(command_strings),
                'generated_at': strategy.generated_at
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting tactical commands: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/strategy/emotional-state', methods=['GET'])
def get_emotional_state():
    """Get current emotional state and market assessment"""
    try:
        # Generate quick assessment
        flip_memories = strategy_engine.read_flip_memory()
        whale_signals = strategy_engine.analyze_whale_signals()
        market_volatility = strategy_engine.assess_market_volatility()
        
        emotional_state = strategy_engine.determine_emotional_state(
            flip_memories, whale_signals, market_volatility
        )
        
        market_phase = strategy_engine._determine_market_phase(whale_signals, market_volatility)
        
        return jsonify({
            'success': True,
            'data': {
                'emotional_state': emotional_state,
                'market_phase': market_phase,
                'risk_level': market_volatility.get('overall_risk', 'MEDIUM'),
                'whale_signals_count': len(whale_signals),
                'active_positions': len(flip_memories),
                'assessment_time': datetime.datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting emotional state: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/battle-plan', methods=['GET'])
def get_battle_plan():
    """Get today's battle plan (legacy ShadowCommander format)"""
    try:
        # Check if we have a cached battle plan for today
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        battle_plan_file = f"/home/ubuntu/LLF-Beta/battle_plans/battle_plan_{today}.json"
        
        if Path(battle_plan_file).exists():
            # Load existing battle plan
            with open(battle_plan_file, 'r') as f:
                battle_plan_data = json.load(f)
        else:
            # Generate new battle plan
            sample_portfolio = {
                'total_value': 1543.40,
                'change_24h': 0.0567,
                'holdings': [
                    {'symbol': 'WIF', 'value': 464.69, 'change_24h': 0.12, 'allocation_percent': 30.1},
                    {'symbol': 'BONK', 'value': 205.58, 'change_24h': -0.03, 'allocation_percent': 13.3},
                    {'symbol': 'XRP', 'value': 202.06, 'change_24h': 0.08, 'allocation_percent': 13.1},
                    {'symbol': 'BTC', 'value': 150.00, 'change_24h': -0.07, 'allocation_percent': 9.7}
                ]
            }
            
            battle_plan = commander.generate_daily_battle_plan(sample_portfolio)
            commander.save_battle_plan(battle_plan)
            
            # Convert to dict for JSON response
            battle_plan_data = {
                'date': battle_plan.date,
                'plan_id': battle_plan.plan_id,
                'market_sentiment': battle_plan.market_sentiment,
                'overall_strategy': battle_plan.overall_strategy,
                'primary_objectives': battle_plan.primary_objectives,
                'commands': [
                    {
                        'id': cmd.id,
                        'command_type': cmd.command_type.value,
                        'priority': cmd.priority.value,
                        'title': cmd.title,
                        'description': cmd.description,
                        'action_required': cmd.action_required,
                        'target_asset': cmd.target_asset,
                        'target_amount': cmd.target_amount,
                        'confidence_score': cmd.confidence_score,
                        'ray_score': cmd.ray_score,
                        'deadline': cmd.deadline,
                        'prerequisites': cmd.prerequisites,
                        'expected_outcome': cmd.expected_outcome,
                        'risk_level': cmd.risk_level
                    } for cmd in battle_plan.commands
                ],
                'risk_assessment': battle_plan.risk_assessment,
                'performance_targets': battle_plan.performance_targets,
                'emergency_protocols': battle_plan.emergency_protocols,
                'generated_at': battle_plan.generated_at,
                'confidence_level': battle_plan.confidence_level
            }
        
        return jsonify({
            'success': True,
            'data': battle_plan_data
        })
        
    except Exception as e:
        logger.error(f"Error generating battle plan: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get ShadowCommander system status"""
    try:
        # Check if battle plans directory exists
        battle_plans_dir = Path("/home/ubuntu/LLF-Beta/battle_plans")
        battle_plans_count = len(list(battle_plans_dir.glob("*.json"))) if battle_plans_dir.exists() else 0
        
        # Check if daily strategies directory exists
        strategies_dir = Path("/home/ubuntu/LLF-Beta/daily_strategies")
        strategies_count = len(list(strategies_dir.glob("*.json"))) if strategies_dir.exists() else 0
        
        # Get today's plan status
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        todays_plan_exists = (battle_plans_dir / f"battle_plan_{today}.json").exists() if battle_plans_dir.exists() else False
        todays_strategy_exists = (strategies_dir / f"strategy_{today}.json").exists() if strategies_dir.exists() else False
        
        return jsonify({
            'success': True,
            'data': {
                'status': 'OPERATIONAL',
                'mode': 'AUTONOMOUS',
                'intelligence_level': 'SOVEREIGN',
                'engines': {
                    'shadow_commander': 'operational',
                    'strategy_engine': 'operational'
                },
                'battle_plans_generated': battle_plans_count,
                'daily_strategies_generated': strategies_count,
                'todays_plan_ready': todays_plan_exists,
                'todays_strategy_ready': todays_strategy_exists,
                'last_heartbeat': datetime.datetime.now().isoformat(),
                'ray_rules_active': True,
                'flip_memory_active': True,
                'whale_signals_active': True,
                'confidence_threshold': commander.config.get('min_confidence_threshold', 0.6),
                'max_daily_commands': commander.config.get('max_daily_commands', 8)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    logger.info("Starting ShadowCommander API with Strategy Engine...")
    app.run(host='0.0.0.0', port=5001, debug=True)

