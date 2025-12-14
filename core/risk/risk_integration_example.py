#!/usr/bin/env python3
"""
RISK INTEGRATION EXAMPLE - Sovereign Shadow III
Demonstrates how to use AdvancedRiskManager and OmegaEnhancedRiskManager together

This example shows the complete workflow for institutional-grade risk management.

Created: 2025-12-14
"""

from advanced_risk_module import AdvancedRiskManager
from omega_enhanced_risk_manager import OmegaEnhancedRiskManager


def evaluate_trade_opportunity(
    symbol: str,
    sector: str,
    current_price: float,
    atr_value: float,
    portfolio_value: float,
    current_positions: dict,
    strategy: str = "swing_trade",
    win_rate: float = 0.55,
    avg_win: float = 100,
    avg_loss: float = 80
):
    """
    Evaluate a trade opportunity using both risk managers.

    Args:
        symbol: Trading symbol (e.g., "BTC/USD")
        sector: Asset sector (e.g., "Infrastructure")
        current_price: Current market price
        atr_value: Average True Range value
        portfolio_value: Total portfolio value
        current_positions: Dict of current positions {symbol: value}
        strategy: Strategy name
        win_rate: Historical win rate (0-1)
        avg_win: Average winning trade amount
        avg_loss: Average losing trade amount

    Returns:
        Dict with trade evaluation and recommendations
    """
    # Initialize risk managers
    advanced_risk = AdvancedRiskManager(
        base_risk_pct=0.02,
        max_portfolio_heat=0.06,
        max_position_heat=0.02,
        kelly_max_fraction=0.25
    )

    omega_risk = OmegaEnhancedRiskManager()

    print(f"\n{'='*70}")
    print(f"EVALUATING TRADE: {symbol} @ ${current_price}")
    print(f"{'='*70}")

    # STEP 1: Omega Correlation Analysis
    print("\n[1] CORRELATION RISK ANALYSIS (Omega)")
    print("-" * 70)

    correlation_analysis = omega_risk.analyze_portfolio_correlation_risk(current_positions)

    print(f"Portfolio Risk Level: {correlation_analysis['risk_level']}")
    print(f"Max Correlation: {correlation_analysis['max_correlation']:.3f}")
    print(f"HHI Score: {correlation_analysis['hhi_score']:.3f}")
    print(f"Violations: {len(correlation_analysis['violations'])}")

    if correlation_analysis['violations']:
        print("\nViolations:")
        for v in correlation_analysis['violations']:
            print(f"  - {v['type']}: {v}")

    # Check if correlation risk is acceptable
    correlation_approved = correlation_analysis['risk_level'] not in ['CRITICAL', 'HIGH']

    # STEP 2: Advanced Position Sizing
    print("\n[2] POSITION SIZING (Advanced Risk Module)")
    print("-" * 70)

    position_result = advanced_risk.calculate_position_size(
        equity=portfolio_value,
        symbol=symbol,
        atr_value=atr_value,
        sector=sector,
        strategy=strategy,
        win_rate=win_rate,
        avg_win=avg_win,
        avg_loss=avg_loss,
        use_kelly=True
    )

    print(f"Method: {position_result.method}")
    print(f"Position Size: {position_result.size:.6f}")
    print(f"Risk Amount: ${position_result.risk_amount:.2f}")
    print(f"Stop Distance: ${position_result.stop_distance:.2f}")

    if position_result.warnings:
        print("\nWarnings:")
        for warning in position_result.warnings:
            print(f"  - {warning}")

    # Check if position sizing approves
    sizing_approved = position_result.size > 0

    # STEP 3: Combined Decision
    print("\n[3] COMBINED RISK DECISION")
    print("-" * 70)

    trade_approved = correlation_approved and sizing_approved

    print(f"Correlation Approved: {correlation_approved}")
    print(f"Position Sizing Approved: {sizing_approved}")
    print(f"FINAL DECISION: {'APPROVED' if trade_approved else 'REJECTED'}")

    # STEP 4: Recommendations
    print("\n[4] RECOMMENDATIONS")
    print("-" * 70)

    recommendations = []

    if not correlation_approved:
        recommendations.extend(correlation_analysis['recommendations'])

    if not sizing_approved:
        if position_result.method == "CIRCUIT_BREAKER_PAUSED":
            recommendations.append("Trading paused due to consecutive losses - wait for reset")
        elif position_result.method == "PORTFOLIO_HEAT_EXCEEDED":
            recommendations.append("Portfolio heat limit reached - close positions before new trades")

    if trade_approved:
        # Calculate stop loss
        stop_loss = current_price - position_result.stop_distance

        recommendations.append(f"Execute: Buy {position_result.size:.6f} {symbol}")
        recommendations.append(f"Entry: ${current_price:.2f}")
        recommendations.append(f"Stop Loss: ${stop_loss:.2f}")
        recommendations.append(f"Risk: ${position_result.risk_amount:.2f}")

        # Calculate position value
        position_value = position_result.size * current_price
        recommendations.append(f"Position Value: ${position_value:.2f}")

    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")

    # Return comprehensive evaluation
    return {
        "approved": trade_approved,
        "correlation_analysis": correlation_analysis,
        "position_sizing": {
            "size": position_result.size,
            "risk_amount": position_result.risk_amount,
            "stop_distance": position_result.stop_distance,
            "method": position_result.method,
            "warnings": position_result.warnings,
            "metadata": position_result.metadata
        },
        "recommendations": recommendations,
        "risk_metrics": {
            "correlation_risk": correlation_analysis['risk_level'],
            "correlation_score": correlation_analysis['max_correlation'],
            "hhi_score": correlation_analysis['hhi_score'],
            "portfolio_heat": position_result.metadata.get('heat_status', {}).get('total_heat', 0),
            "circuit_breaker_active": position_result.metadata.get('circuit_breaker', {}).get('active', False)
        }
    }


def main():
    """Run examples of risk integration."""
    print("="*70)
    print("RISK INTEGRATION EXAMPLE - Sovereign Shadow III")
    print("Combining Omega Correlation + Advanced Risk Management")
    print("="*70)

    # Current portfolio (from BRAIN.json)
    current_portfolio = {
        "BTC": 1508.32,   # Ledger
        "ETH": 14.56,     # Ledger
        "XRP": 1099.17,   # Ledger
        "USDC": 53.61     # Ledger
    }

    portfolio_value = sum(current_portfolio.values())

    print(f"\nCurrent Portfolio Value: ${portfolio_value:.2f}")
    print(f"Current Holdings: {list(current_portfolio.keys())}")

    # Example 1: Evaluate BTC trade (should be rejected - already holding)
    print("\n" + "="*70)
    print("EXAMPLE 1: BTC/USD Trade Evaluation")
    print("="*70)

    btc_evaluation = evaluate_trade_opportunity(
        symbol="BTC/USD",
        sector="Infrastructure",
        current_price=42000,
        atr_value=1200,
        portfolio_value=portfolio_value,
        current_positions=current_portfolio,
        strategy="swing_trade",
        win_rate=0.55,
        avg_win=100,
        avg_loss=75
    )

    # Example 2: Evaluate SOL trade (diversification opportunity)
    print("\n" + "="*70)
    print("EXAMPLE 2: SOL/USD Trade Evaluation (Diversification)")
    print("="*70)

    sol_evaluation = evaluate_trade_opportunity(
        symbol="SOL/USD",
        sector="Infrastructure",
        current_price=98,
        atr_value=5.2,
        portfolio_value=portfolio_value,
        current_positions=current_portfolio,
        strategy="swing_trade",
        win_rate=0.60,
        avg_win=120,
        avg_loss=80
    )

    # Example 3: Evaluate RNDR trade (AI sector - lower correlation)
    print("\n" + "="*70)
    print("EXAMPLE 3: RNDR/USD Trade Evaluation (AI Sector)")
    print("="*70)

    rndr_evaluation = evaluate_trade_opportunity(
        symbol="RNDR/USD",
        sector="AI",
        current_price=7.5,
        atr_value=0.35,
        portfolio_value=portfolio_value,
        current_positions=current_portfolio,
        strategy="swing_trade",
        win_rate=0.52,
        avg_win=90,
        avg_loss=85
    )

    # Summary
    print("\n" + "="*70)
    print("EVALUATION SUMMARY")
    print("="*70)

    evaluations = [
        ("BTC/USD", btc_evaluation),
        ("SOL/USD", sol_evaluation),
        ("RNDR/USD", rndr_evaluation)
    ]

    for symbol, eval_result in evaluations:
        status = "APPROVED" if eval_result['approved'] else "REJECTED"
        corr_risk = eval_result['risk_metrics']['correlation_risk']
        print(f"\n{symbol}:")
        print(f"  Status: {status}")
        print(f"  Correlation Risk: {corr_risk}")
        print(f"  HHI Score: {eval_result['risk_metrics']['hhi_score']:.3f}")
        if eval_result['approved']:
            print(f"  Position Size: {eval_result['position_sizing']['size']:.6f}")
            print(f"  Risk Amount: ${eval_result['position_sizing']['risk_amount']:.2f}")

    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("""
1. DUAL-LAYER PROTECTION:
   - Omega checks correlation and sector concentration
   - Advanced checks position sizing, heat, and circuit breakers

2. RISK METRICS TRACKED:
   - Correlation risk between assets
   - Portfolio heat (2%/6% rule)
   - Sector concentration
   - Consecutive loss streaks
   - Volatility-adjusted Kelly sizing

3. INTEGRATION PATTERN:
   - Always check BOTH managers before executing trades
   - Omega prevents correlation disasters
   - Advanced prevents overleveraging and emotional trading

4. FOR SOVEREIGN SHADOW III:
   - Use this pattern in all trading agents
   - Log all risk decisions to BRAIN.json
   - Review risk metrics daily
   - Adjust parameters based on market conditions
    """)


if __name__ == "__main__":
    main()
