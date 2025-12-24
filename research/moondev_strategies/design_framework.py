'''
Designs the strategy classification and market regime detection framework.
'''
import json
from collections import defaultdict

# --- 1. Load and Consolidate All Strategies ---
def load_strategies(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)['strategies']
    except (FileNotFoundError, KeyError):
        return []

def load_new_batch(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)['unique_strategies']
    except (FileNotFoundError, KeyError):
        return {}

initial_strategies = load_strategies('/home/ubuntu/comprehensive_strategy_analysis.json')
new_batch = load_new_batch('/home/ubuntu/new_batch_analysis.json')

all_strategies = {}

# Process initial batch
for s in initial_strategies:
    all_strategies[s['name']] = {
        'type': s.get('type', 'Unknown'),
        'score': s.get('score', 0),
        'source': 'batch_1'
    }

# Process and merge new batch
for name, data in new_batch.items():
    if not name or name in ['', '__init__', 'README', 'ideas', 'agent_discussed_tokens']:
        continue
    
    # Determine strategy type based on name patterns
    strategy_type = "Unknown"
    if any(x in name.lower() for x in ['breakout', 'break']):
        strategy_type = "Breakout"
    elif any(x in name.lower() for x in ['reversion', 'reversal']):
        strategy_type = "Mean Reversion"
    elif any(x in name.lower() for x in ['volatility', 'vol', 'voltaic']):
        strategy_type = "Volatility"
    elif any(x in name.lower() for x in ['momentum', 'trend']):
        strategy_type = "Trend Following"
    elif any(x in name.lower() for x in ['squeeze', 'compression']):
        strategy_type = "Volatility Squeeze"
    elif any(x in name.lower() for x in ['liquidation', 'liquidity', 'liqui']):
        strategy_type = "Liquidation"
    elif any(x in name.lower() for x in ['divergence', 'divergent']):
        strategy_type = "Divergence"
    elif any(x in name.lower() for x in ['band', 'banded']):
        strategy_type = "Band-Based"
    elif any(x in name.lower() for x in ['vortex']):
        strategy_type = "Vortex"
    elif any(x in name.lower() for x in ['volumetric', 'volume']):
        strategy_type = "Volume"
    elif any(x in name.lower() for x in ['fibonacci', 'fibro', 'fib']):
        strategy_type = "Fibonacci"
    elif any(x in name.lower() for x in ['arbitrage', 'scalper']):
        strategy_type = "Arbitrage"
    elif any(x in name.lower() for x in ['harmonic']):
        strategy_type = "Harmonic"

    all_strategies[name] = {
        'type': strategy_type,
        'score': 0, # Score needs to be recalculated
        'source': 'batch_2'
    }

# --- 2. Define Market Regimes ---
# Based on ADX for trend strength and ATR Percentile for volatility
market_regimes = {
    "High Volatility Trend": {
        "description": "Strong directional movement with high price volatility. Ideal for aggressive trend-following and breakout strategies.",
        "conditions": {
            "ADX": "> 25",
            "ATR_Percentile": "> 70%"
        }
    },
    "Low Volatility Trend": {
        "description": "Steady, grinding directional movement with low volatility. Suitable for classic trend-following and pullback strategies.",
        "conditions": {
            "ADX": "> 25",
            "ATR_Percentile": "< 30%"
        }
    },
    "High Volatility Range": {
        "description": "Choppy, sideways market with high volatility. Dangerous conditions, but suitable for mean reversion and volatility strategies.",
        "conditions": {
            "ADX": "< 20",
            "ATR_Percentile": "> 70%"
        }
    },
    "Low Volatility Range": {
        "description": "Quiet, sideways market with low volatility. Ideal for accumulation, squeeze breakouts, and range-bound strategies.",
        "conditions": {
            "ADX": "< 20",
            "ATR_Percentile": "< 30%"
        }
    },
    "Transitioning Market": {
        "description": "Market is shifting between trend and range. Conditions are uncertain, requiring cautious or adaptive strategies.",
        "conditions": {
            "ADX": "20-25",
            "ATR_Percentile": "30-70%"
        }
    }
}

# --- 3. Map Strategy Types to Market Regimes ---
regime_to_strategy_map = {
    "High Volatility Trend": ["Trend Following", "Breakout", "Volatility", "Momentum"],
    "Low Volatility Trend": ["Trend Following", "Pullback", "Momentum"],
    "High Volatility Range": ["Mean Reversion", "Volatility", "Scalping", "Arbitrage"],
    "Low Volatility Range": ["Mean Reversion", "Volatility Squeeze", "Accumulation", "Band-Based"],
    "Transitioning Market": ["Divergence", "Adaptive", "Harmonic"]
}

# --- 4. Assemble the Framework Document ---
framework = {
    "framework_name": "Intelligent Strategy Selection Framework",
    "version": "1.0",
    "description": "An architectural design for an AI agent to select and execute the optimal trading strategy based on real-time market regime analysis.",
    "components": {
        "strategy_library": {
            "total_strategies": len(all_strategies),
            "strategies": all_strategies
        },
        "market_regime_detector": {
            "description": "Identifies the current market state using ADX and ATR Percentile.",
            "regimes": market_regimes
        },
        "strategy_selector": {
            "description": "Maps market regimes to suitable strategy types.",
            "mapping": regime_to_strategy_map
        }
    }
}

# Save the framework design
with open('/home/ubuntu/strategy_framework_design.json', 'w') as f:
    json.dump(framework, indent=2, fp=f)

print("✅ Strategy framework design completed successfully.")
print(f"Total unique strategies identified: {len(all_strategies)}")
print("Framework design saved to: /home/ubuntu/strategy_framework_design.json")
