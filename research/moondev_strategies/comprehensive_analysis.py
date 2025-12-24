#!/usr/bin/env python3.11
"""
Comprehensive Trading Strategy Analysis
Analyzes all strategies and provides strengthening recommendations
"""
import json
import re
from pathlib import Path

# Load detailed strategy data
with open('/home/ubuntu/detailed_strategy_analysis.json', 'r') as f:
    data = json.load(f)

def analyze_strategy_weaknesses(strategy):
    """Identify potential weaknesses in a strategy."""
    weaknesses = []
    
    # Risk management analysis
    if strategy["risk_per_trade"] is None:
        weaknesses.append({
            "category": "Risk Management",
            "issue": "No explicit risk per trade defined",
            "severity": "HIGH",
            "impact": "Uncontrolled position sizing can lead to catastrophic losses"
        })
    elif strategy["risk_per_trade"] > 0.02:
        weaknesses.append({
            "category": "Risk Management",
            "issue": f"High risk per trade ({strategy['risk_per_trade']*100}%)",
            "severity": "MEDIUM",
            "impact": "Aggressive sizing increases drawdown potential"
        })
    
    # Stop loss analysis
    if "Stop Loss" not in strategy["features"]:
        weaknesses.append({
            "category": "Risk Management",
            "issue": "No stop loss mechanism detected",
            "severity": "CRITICAL",
            "impact": "Unlimited downside risk on each trade"
        })
    
    # Take profit analysis
    if "Take Profit" not in strategy["features"]:
        weaknesses.append({
            "category": "Exit Strategy",
            "issue": "No take profit mechanism",
            "severity": "MEDIUM",
            "impact": "May miss optimal exit points, reducing profitability"
        })
    
    # Trailing stop analysis
    if "Trailing Stop" not in strategy["features"]:
        weaknesses.append({
            "category": "Exit Strategy",
            "issue": "No trailing stop for profit protection",
            "severity": "LOW",
            "impact": "Cannot lock in profits during favorable moves"
        })
    
    # Indicator diversity
    if len(strategy["indicators"]) < 2:
        weaknesses.append({
            "category": "Signal Quality",
            "issue": "Limited indicator diversity",
            "severity": "MEDIUM",
            "impact": "Single-indicator strategies prone to false signals"
        })
    
    # Volatility adaptation
    has_volatility_indicator = any(ind in strategy["indicators"] for ind in ["ATR", "BBANDS"])
    if not has_volatility_indicator:
        weaknesses.append({
            "category": "Market Adaptation",
            "issue": "No volatility-based indicators",
            "severity": "MEDIUM",
            "impact": "Strategy may not adapt to changing market conditions"
        })
    
    # Volume confirmation
    if "Volume" not in strategy["indicators"] and strategy["type"] == "Breakout":
        weaknesses.append({
            "category": "Signal Quality",
            "issue": "Breakout strategy without volume confirmation",
            "severity": "HIGH",
            "impact": "False breakouts more likely without volume validation"
        })
    
    return weaknesses

def generate_recommendations(strategy, weaknesses):
    """Generate actionable strengthening recommendations."""
    recommendations = []
    
    # Group weaknesses by category
    weakness_categories = {}
    for w in weaknesses:
        cat = w["category"]
        if cat not in weakness_categories:
            weakness_categories[cat] = []
        weakness_categories[cat].append(w)
    
    # Risk Management recommendations
    if "Risk Management" in weakness_categories:
        recommendations.append({
            "priority": "CRITICAL",
            "category": "Risk Management Enhancement",
            "actions": [
                "Implement fixed 1-2% risk per trade based on account equity",
                "Add dynamic position sizing based on ATR (Average True Range)",
                "Implement maximum daily drawdown limit (e.g., 6% of equity)",
                "Add correlation checks to avoid overexposure to similar assets",
                "Implement Kelly Criterion for optimal position sizing"
            ]
        })
    
    # Stop Loss recommendations
    if any(w["issue"] == "No stop loss mechanism detected" for w in weaknesses):
        recommendations.append({
            "priority": "CRITICAL",
            "category": "Stop Loss Implementation",
            "actions": [
                "Add ATR-based stop loss (2-3x ATR from entry)",
                "Implement swing low/high stop placement for trend strategies",
                "Add time-based stop (exit if no movement after N bars)",
                "Consider volatility-adjusted stops that widen in choppy markets",
                "Implement break-even stop after 1:1 risk/reward achieved"
            ]
        })
    
    # Exit Strategy recommendations
    if "Exit Strategy" in weakness_categories:
        recommendations.append({
            "priority": "HIGH",
            "category": "Exit Strategy Optimization",
            "actions": [
                "Implement scaled exits (take 50% at 2R, let 50% run)",
                "Add trailing stop using ATR or percentage-based method",
                "Use opposite signal as exit trigger",
                "Implement time-based exits for mean reversion strategies",
                "Add profit target based on historical average win size"
            ]
        })
    
    # Signal Quality recommendations
    if "Signal Quality" in weakness_categories:
        recommendations.append({
            "priority": "HIGH",
            "category": "Signal Quality Improvement",
            "actions": [
                "Add volume confirmation for all entry signals",
                "Implement multi-timeframe analysis (confirm on higher TF)",
                "Add regime filter (trend vs. range detection)",
                "Use RSI divergence for reversal confirmation",
                "Implement signal strength scoring system"
            ]
        })
    
    # Market Adaptation recommendations
    if "Market Adaptation" in weakness_categories:
        recommendations.append({
            "priority": "MEDIUM",
            "category": "Market Regime Adaptation",
            "actions": [
                "Add ADX filter to distinguish trending vs. ranging markets",
                "Implement volatility regime detection (high/low vol periods)",
                "Adjust parameters dynamically based on ATR percentile",
                "Add correlation analysis to detect market regime shifts",
                "Implement separate parameter sets for different regimes"
            ]
        })
    
    # Strategy-specific recommendations
    if strategy["type"] == "Breakout":
        recommendations.append({
            "priority": "HIGH",
            "category": "Breakout-Specific Enhancements",
            "actions": [
                "Add volume surge requirement (2-3x average volume)",
                "Implement false breakout filter (wait for retest)",
                "Add volatility contraction detection before breakout",
                "Use multiple timeframe breakout confirmation",
                "Implement breakout strength measurement"
            ]
        })
    
    elif strategy["type"] == "Mean Reversion":
        recommendations.append({
            "priority": "HIGH",
            "category": "Mean Reversion Enhancements",
            "actions": [
                "Add oversold/overbought confirmation (RSI < 30 or > 70)",
                "Implement Bollinger Band width filter (only trade in low vol)",
                "Add mean reversion zone identification",
                "Use multiple mean reversion indicators (RSI + BB + Stoch)",
                "Implement quick exit if mean reversion fails"
            ]
        })
    
    elif strategy["type"] == "Trend Following":
        recommendations.append({
            "priority": "HIGH",
            "category": "Trend Following Enhancements",
            "actions": [
                "Add ADX > 25 filter to confirm strong trend",
                "Implement pullback entry instead of breakout entry",
                "Add higher timeframe trend confirmation",
                "Use multiple EMAs for trend strength assessment",
                "Implement trend exhaustion detection (RSI divergence)"
            ]
        })
    
    elif strategy["type"] == "Volatility":
        recommendations.append({
            "priority": "HIGH",
            "category": "Volatility Strategy Enhancements",
            "actions": [
                "Add volatility percentile ranking (trade extremes)",
                "Implement volatility expansion/contraction detection",
                "Add correlation to VIX or crypto volatility index",
                "Use Bollinger Band width for volatility measurement",
                "Implement volatility breakout confirmation"
            ]
        })
    
    # Portfolio integration recommendations
    recommendations.append({
        "priority": "MEDIUM",
        "category": "Portfolio Integration",
        "actions": [
            "Test strategy on BTC, ETH, and major altcoins separately",
            "Implement asset-specific parameter optimization",
            "Add correlation filters to avoid simultaneous correlated trades",
            "Consider strategy allocation based on market regime",
            "Implement portfolio-level risk management"
        ]
    })
    
    # Backtesting and validation
    recommendations.append({
        "priority": "HIGH",
        "category": "Validation & Robustness",
        "actions": [
            "Perform walk-forward analysis (out-of-sample testing)",
            "Test across multiple market cycles (bull, bear, sideways)",
            "Implement Monte Carlo simulation for drawdown analysis",
            "Add parameter sensitivity analysis",
            "Test on multiple cryptocurrencies for robustness"
        ]
    })
    
    return recommendations

def calculate_strategy_score(strategy, weaknesses):
    """Calculate overall strategy quality score (0-100)."""
    score = 100
    
    # Deduct points for weaknesses
    for weakness in weaknesses:
        if weakness["severity"] == "CRITICAL":
            score -= 20
        elif weakness["severity"] == "HIGH":
            score -= 10
        elif weakness["severity"] == "MEDIUM":
            score -= 5
        elif weakness["severity"] == "LOW":
            score -= 2
    
    # Bonus points for good features
    if strategy["risk_per_trade"] and 0.01 <= strategy["risk_per_trade"] <= 0.02:
        score += 5
    if "Stop Loss" in strategy["features"]:
        score += 10
    if "Take Profit" in strategy["features"]:
        score += 5
    if "Trailing Stop" in strategy["features"]:
        score += 5
    if len(strategy["indicators"]) >= 3:
        score += 5
    
    return max(0, min(100, score))

# Analyze all strategies
analysis_results = []

for strategy in data["strategies"]:
    weaknesses = analyze_strategy_weaknesses(strategy)
    recommendations = generate_recommendations(strategy, weaknesses)
    score = calculate_strategy_score(strategy, weaknesses)
    
    analysis_results.append({
        "name": strategy["name"],
        "type": strategy["type"],
        "score": score,
        "grade": "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D",
        "weaknesses_count": len(weaknesses),
        "critical_issues": sum(1 for w in weaknesses if w["severity"] == "CRITICAL"),
        "weaknesses": weaknesses,
        "recommendations": recommendations,
        "indicators": strategy["indicators"],
        "features": strategy["features"],
        "versions": strategy["versions_count"]
    })

# Sort by score (best first)
analysis_results.sort(key=lambda x: x["score"], reverse=True)

# Save comprehensive analysis
output = {
    "analysis_date": "2025-12-13",
    "total_strategies": len(analysis_results),
    "average_score": sum(r["score"] for r in analysis_results) / len(analysis_results),
    "strategies": analysis_results,
    "summary": {
        "grade_distribution": {
            "A": sum(1 for r in analysis_results if r["grade"] == "A"),
            "B": sum(1 for r in analysis_results if r["grade"] == "B"),
            "C": sum(1 for r in analysis_results if r["grade"] == "C"),
            "D": sum(1 for r in analysis_results if r["grade"] == "D")
        },
        "critical_issues_total": sum(r["critical_issues"] for r in analysis_results),
        "top_5_strategies": [r["name"] for r in analysis_results[:5]],
        "needs_urgent_attention": [r["name"] for r in analysis_results if r["critical_issues"] > 0]
    }
}

with open('/home/ubuntu/comprehensive_strategy_analysis.json', 'w') as f:
    json.dump(output, indent=2, fp=f)

print(json.dumps(output, indent=2))
