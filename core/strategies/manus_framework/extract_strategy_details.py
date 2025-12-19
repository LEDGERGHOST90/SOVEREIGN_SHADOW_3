#!/usr/bin/env python3.11
import os
import re
import json
from pathlib import Path

def extract_strategy_info(filepath):
    """Extract key information from a strategy Python file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        info = {
            "risk_per_trade": None,
            "indicators": [],
            "entry_conditions": [],
            "exit_conditions": [],
            "stop_loss": False,
            "take_profit": False,
            "trailing_stop": False
        }
        
        # Extract risk percentage
        risk_patterns = [
            r'risk[_\s]*(?:per[_\s]*trade|pct|percentage)[_\s]*=\s*([\d.]+)',
            r'risk[_\s]*=\s*([\d.]+)'
        ]
        for pattern in risk_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                info["risk_per_trade"] = float(match.group(1))
                break
        
        # Detect indicators
        indicator_map = {
            'EMA': r'(?:talib\.)?EMA',
            'SMA': r'(?:talib\.)?SMA',
            'RSI': r'(?:talib\.)?RSI',
            'ADX': r'(?:talib\.)?ADX',
            'ATR': r'(?:talib\.)?ATR',
            'BBANDS': r'(?:talib\.)?BBANDS|Bollinger',
            'CMO': r'(?:talib\.)?CMO',
            'OBV': r'(?:talib\.)?OBV',
            'MACD': r'(?:talib\.)?MACD',
            'Stochastic': r'(?:talib\.)?STOCH',
            'Volume': r'\.Volume',
            'VWAP': r'VWAP|vwap',
            'Fisher': r'Fisher|fisher',
            'Fibonacci': r'Fibonacci|fibonacci|fib',
            'VIX': r'vix|VIX'
        }
        
        for indicator, pattern in indicator_map.items():
            if re.search(pattern, content):
                info["indicators"].append(indicator)
        
        # Detect position management features
        if re.search(r'\.sl\s*=|stop[_\s]*loss|sl\s*=', content, re.IGNORECASE):
            info["stop_loss"] = True
        if re.search(r'\.tp\s*=|take[_\s]*profit|tp\s*=', content, re.IGNORECASE):
            info["take_profit"] = True
        if re.search(r'trailing', content, re.IGNORECASE):
            info["trailing_stop"] = True
        
        # Extract entry logic hints
        entry_patterns = [
            r'# Entry|# Long Entry|# Short Entry',
            r'if.*buy\(|if.*sell\(',
            r'crossover|cross over|golden cross'
        ]
        for pattern in entry_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                info["entry_conditions"].extend(matches[:3])
        
        # Extract exit logic hints
        exit_patterns = [
            r'# Exit|# Take Profit|# Stop Loss',
            r'position\.close\(',
            r'death cross|backwardation'
        ]
        for pattern in exit_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                info["exit_conditions"].extend(matches[:3])
        
        return info
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None

def categorize_strategy(name, indicators):
    """Categorize strategy based on name and indicators."""
    name_lower = name.lower()
    
    if 'arbitrage' in name_lower or 'contango' in name_lower:
        return "Arbitrage"
    elif any(x in name_lower for x in ['breakout', 'spike', 'pulse']):
        return "Breakout"
    elif any(x in name_lower for x in ['reversion', 'convergence', 'divergence']):
        return "Mean Reversion"
    elif any(x in name_lower for x in ['volatility', 'vol', 'atr', 'bandwidth']):
        return "Volatility"
    elif any(x in name_lower for x in ['trend', 'crossfire', 'momentum', 'ema', 'sma']):
        return "Trend Following"
    elif len(indicators) >= 4:
        return "Multi-Factor"
    else:
        return "Breakout"  # Default

# Load strategy analysis
with open('/home/ubuntu/strategy_analysis.json', 'r') as f:
    strategy_data = json.load(f)

upload_dir = Path("/home/ubuntu/upload")
detailed_strategies = []

for strategy_name, data in strategy_data["strategies"].items():
    strategy_info = {
        "name": strategy_name,
        "versions_count": len(data["python_versions"]),
        "json_results_count": data["json_results_count"],
        "has_doc": data["has_strategy_doc"],
        "has_pkg": data["has_pkg_file"],
        "type": None,
        "risk_per_trade": None,
        "indicators": [],
        "features": []
    }
    
    # Analyze the first (or WORKING) Python version if available
    if data["python_versions"]:
        # Prefer WORKING version
        working_version = next((v for v in data["python_versions"] if 'WORKING' in v), None)
        target_file = working_version or data["python_versions"][0]
        
        filepath = upload_dir / target_file
        extracted = extract_strategy_info(filepath)
        
        if extracted:
            strategy_info["risk_per_trade"] = extracted["risk_per_trade"]
            strategy_info["indicators"] = extracted["indicators"]
            
            if extracted["stop_loss"]:
                strategy_info["features"].append("Stop Loss")
            if extracted["take_profit"]:
                strategy_info["features"].append("Take Profit")
            if extracted["trailing_stop"]:
                strategy_info["features"].append("Trailing Stop")
    
    # Categorize strategy
    strategy_info["type"] = categorize_strategy(strategy_name, strategy_info["indicators"])
    
    detailed_strategies.append(strategy_info)

# Save detailed analysis
output = {
    "total_strategies": len(detailed_strategies),
    "strategies": detailed_strategies
}

with open('/home/ubuntu/detailed_strategy_analysis.json', 'w') as f:
    json.dump(output, indent=2, fp=f)

print(json.dumps(output, indent=2))
