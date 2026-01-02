import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ReflectAgent:
    """
    REFLECT: Reflect Agent Pattern
    Provides verbal critique and meta-analysis of trading decisions, performance,
    and market conditions. This agent helps identify biases, evaluate strategy
    effectiveness, and suggest improvements based on a holistic view.
    """

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.critique_history: List[Dict] = []
        self.performance_thresholds = self.config.get("performance_thresholds", {
            "daily_pnl_warn_pct": -0.5,  # -0.5% daily PnL triggers warning
            "daily_pnl_critical_pct": -1.0, # -1.0% daily PnL triggers critical alert
            "consecutive_losses_warn": 2,
            "consecutive_losses_critical": 4
        })
        logger.info("REFLECT Agent initialized.")

    def analyze_trade_decision(self, trade_request: Dict, validation_result: Dict, current_market_data: Dict) -> str:
        """
        Analyzes a single trade decision and its validation outcome.
        Provides a critique based on various factors.
        """
        critique_messages = []

        if not validation_result["approved"]:
            critique_messages.append(f"Trade REJECTED: {validation_result['reason']}. Good risk adherence.")
        else:
            critique_messages.append(f"Trade APPROVED. Notional: ${trade_request['notional_usd']:.2f}, Side: {trade_request['side']}.")

        # Critique based on market filters (ORACLE)
        if "fng_signal" in current_market_data:
            fng = current_market_data["fng_signal"]
            if fng == "SELL_SIGNAL_EXTREME_GREED":
                critique_messages.append("Market showing Extreme Greed (ORACLE). Caution advised for long positions.")
            elif fng == "BUY_OPPORTUNITY_EXTREME_FEAR":
                critique_messages.append("Market showing Extreme Fear (ORACLE). Potential contrarian long opportunity.")

        if "dxy_signal" in current_market_data:
            dxy = current_market_data["dxy_signal"]
            if dxy == "STRONG_DOLLAR_RISK_OFF":
                critique_messages.append("DXY is strong (ORACLE). Overall risk-off sentiment prevails. Favoring shorts or cash.")
            elif dxy == "WEAK_DOLLAR_RISK_ON":
                critique_messages.append("DXY is weak (ORACLE). Potential for risk-on assets, but proceed with caution if shorting.")

        # Critique based on HMM Regime (REGIME)
        if "regime" in current_market_data:
            regime = current_market_data["regime"]
            if regime == "Bear":
                critique_messages.append("HMM detects Bearish regime (REGIME). Longs are high risk; shorts preferred.")
            elif regime == "Bull":
                critique_messages.append("HMM detects Bullish regime (REGIME). Favoring long positions.")
            elif regime == "Volatile":
                critique_messages.append("HMM detects Volatile regime (REGIME). Reduce size and tighten stops.")

        # Critique based on Sentinel Risk Module
        if validation_result.get("stop_adjustment_bps") and validation_result["stop_adjustment_bps"] > trade_request["stop_loss_bps"]:
            critique_messages.append(f"SENTINEL: Stop loss widened from {trade_request['stop_loss_bps']} bps to {validation_result['stop_adjustment_bps']} bps due to market conditions.")

        if validation_result.get("size_adjustment") and validation_result["size_adjustment"] < 1.0:
            critique_messages.append(f"SENTINEL: Position size reduced by {1 - validation_result['size_adjustment']:.1%} due to risk factors.")

        final_critique = "REFLECT Agent Critique:\n" + "\n".join([f"- {msg}" for msg in critique_messages])
        self.critique_history.append({
            "timestamp": datetime.now().isoformat(),
            "trade_request": trade_request,
            "validation_result": validation_result,
            "current_market_data": current_market_data,
            "critique": final_critique
        })
        logger.info(f"Trade critique generated for {trade_request['asset']}.\n{final_critique}")
        return final_critique

    def analyze_session_performance(self, session_stats: Dict) -> str:
        """
        Provides a meta-analysis of overall session performance.
        """
        performance_critique = []

        daily_pnl_pct = (session_stats.get("session_pnl_usd", 0) / self.config.get("initial_capital", 1660.0)) * 100
        consecutive_losses = session_stats.get("consecutive_losses", 0)

        # Daily PnL critique
        if daily_pnl_pct <= self.performance_thresholds["daily_pnl_critical_pct"]:
            performance_critique.append(f"CRITICAL PERFORMANCE ALERT: Daily PnL is {daily_pnl_pct:.2f}%. Significant drawdown. Review strategies immediately.")
        elif daily_pnl_pct <= self.performance_thresholds["daily_pnl_warn_pct"]:
            performance_critique.append(f"WARNING: Daily PnL is {daily_pnl_pct:.2f}%. Monitor closely and consider reducing exposure.")
        else:
            performance_critique.append(f"Daily PnL at {daily_pnl_pct:.2f}%. Performance is within acceptable bounds.")

        # Consecutive losses critique
        if consecutive_losses >= self.performance_thresholds["consecutive_losses_critical"]:
            performance_critique.append(f"CRITICAL LOSS STREAK: {consecutive_losses} consecutive losses. Consider halting trading and re-evaluating.")
        elif consecutive_losses >= self.performance_thresholds["consecutive_losses_warn"]:
            performance_critique.append(f"WARNING: {consecutive_losses} consecutive losses. Review recent trades and market context.")
        
        # Other metrics
        performance_critique.append(f"Total trades: {session_stats.get('total_trades', 0)}, Open trades: {session_stats.get('open_trades', 0)}.")
        performance_critique.append(f"Aave Health Factor: {session_stats.get('aave_health_factor', 'N/A'):.2f}, OI Change 24h: {session_stats.get('oi_change_24h_pct', 'N/A'):+.2f}%")

        final_critique = "REFLECT Agent Session Performance Analysis:\n" + "\n".join([f"- {msg}" for msg in performance_critique])
        self.critique_history.append({
            "timestamp": datetime.now().isoformat(),
            "session_stats": session_stats,
            "critique": final_critique
        })
        logger.info(f"Session performance critique generated.\n{final_critique}")
        return final_critique

    def get_critique_history(self, limit: int = 5) -> List[Dict]:
        """
        Retrieves a limited history of critiques.
        """
        return self.critique_history[-limit:]

# Example usage (for testing)
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    reflect_agent = ReflectAgent(config={
        "initial_capital": 1000.0,
        "performance_thresholds": {
            "daily_pnl_warn_pct": -0.2, 
            "daily_pnl_critical_pct": -0.5,
            "consecutive_losses_warn": 1,
            "consecutive_losses_critical": 2
        }
    })

    print("\n--- Trade Decision Analysis ---")
    # Simulate a trade request, validation result, and market data
    trade_req_1 = {
        "strategy_name": "test_scalp",
        "asset": "BTC",
        "side": "long",
        "notional_usd": 100.0,
        "stop_loss_bps": 50,
        "entry_price": 30000,
        "conditions_met": {"signal_a": True},
        "timestamp": datetime.now().isoformat()
    }
    validation_res_1 = {
        "approved": True,
        "reason": "All checks passed",
        "size_adjustment": 0.8,
        "stop_adjustment_bps": 60,
        "warnings": ["ORACLE DXY: Weak dollar / Risk-on detected - short size reduced to 0.8x"]
    }
    market_data_1 = {
        "fng_signal": "BUY_OPPORTUNITY_FEAR",
        "dxy_signal": "WEAK_DOLLAR_RISK_ON",
        "regime": "Bull"
    }
    critique_1 = reflect_agent.analyze_trade_decision(trade_req_1, validation_res_1, market_data_1)
    print(critique_1)

    trade_req_2 = {
        "strategy_name": "test_scalp",
        "asset": "ETH",
        "side": "short",
        "notional_usd": 200.0,
        "stop_loss_bps": 70,
        "entry_price": 2000,
        "conditions_met": {"signal_b": True},
        "timestamp": datetime.now().isoformat()
    }
    validation_res_2 = {
        "approved": False,
        "reason": "❌ REGIME HMM: Bear market detected - halting new long entries",
        "size_adjustment": 1.0,
        "stop_adjustment_bps": None,
        "warnings": []
    }
    market_data_2 = {
        "fng_signal": "NEUTRAL",
        "dxy_signal": "NEUTRAL_DOLLAR",
        "regime": "Bear"
    }
    critique_2 = reflect_agent.analyze_trade_decision(trade_req_2, validation_res_2, market_data_2)
    print(critique_2)

    print("\n--- Session Performance Analysis ---")
    session_stats_1 = {
        "session_pnl_usd": -15.0,
        "consecutive_losses": 1,
        "total_trades": 5,
        "open_trades": 1,
        "aave_health_factor": 2.30,
        "oi_change_24h_pct": 1.5
    }
    perf_critique_1 = reflect_agent.analyze_session_performance(session_stats_1)
    print(perf_critique_1)

    session_stats_2 = {
        "session_pnl_usd": -5.5,
        "consecutive_losses": 3,
        "total_trades": 10,
        "open_trades": 0,
        "aave_health_factor": 2.10,
        "oi_change_24h_pct": -0.8
    }
    perf_critique_2 = reflect_agent.analyze_session_performance(session_stats_2)
    print(perf_critique_2)

    print("\n--- Critique History ---")
    history = reflect_agent.get_critique_history()
    for item in history:
        print(f"[{item['timestamp']}] {item['critique'][:50]}...")
