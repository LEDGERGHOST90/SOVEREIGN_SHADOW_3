#!/usr/bin/env python3
"""
ORACLE INTERFACE - Natural Language → Visualization Layer
Ask questions, get charts and insights
"""

import json
import base64
import io
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import numpy as np


class OracleInterface:
    """
    Natural language market query interface for Sovereign Shadow 3

    Converts plain English questions into:
    - Data queries
    - Metric calculations
    - Visualizations
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

        # Load system prompt
        self.system_prompt = self._load_system_prompt()

        # Query logs
        self.log_dir = Path(__file__).parent.parent.parent / "logs" / "oracle_interface"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Import data client
        from ..synoptic_core.market_data_client import MarketDataClient
        self.data_client = MarketDataClient()

    def _load_system_prompt(self) -> str:
        """Load the Oracle Interface system prompt"""
        import yaml
        prompt_file = Path(__file__).parent.parent / "configs" / "system_prompts.yaml"
        if prompt_file.exists():
            with open(prompt_file, 'r') as f:
                prompts = yaml.safe_load(f)
                return prompts.get("oracle_interface", "")
        return ""

    def query(self, question: str) -> Dict[str, Any]:
        """
        Process a natural language market question

        Args:
            question: Natural language question

        Returns:
            {
                "caption": str,
                "data": any,
                "chart": str (base64 PNG or plotly JSON),
                "chart_type": str,
                "code": str (optional)
            }
        """
        # Parse the question
        parsed = self._parse_question(question)

        # Fetch required data
        data = self._fetch_data(parsed)

        # Calculate metrics
        metrics = self._calculate_metrics(data, parsed)

        # Generate visualization
        chart_result = self._generate_chart(data, metrics, parsed)

        # Generate caption
        caption = self._generate_caption(metrics, parsed)

        result = {
            "caption": caption,
            "data": metrics,
            "chart": chart_result.get("chart"),
            "chart_type": chart_result.get("type"),
            "symbols": parsed.get("symbols", []),
            "timeframe": parsed.get("timeframe", "1d"),
            "metric": parsed.get("metric", "price")
        }

        # Log the query
        self._log_query(question, result)

        return result

    def _parse_question(self, question: str) -> Dict[str, Any]:
        """
        Parse natural language question into structured query

        Extracts:
        - symbols
        - timeframe
        - metric type
        - comparison flag
        - visualization type
        """
        question_lower = question.lower()

        # Extract symbols
        symbols = []
        known_symbols = ["btc", "eth", "sol", "xrp", "aave", "link", "uni", "arb", "op", "matic"]
        for sym in known_symbols:
            if sym in question_lower:
                symbols.append(sym.upper())

        if not symbols:
            symbols = ["BTC"]  # Default

        # Extract timeframe
        timeframe = "1d"  # Default
        if "hourly" in question_lower or "1h" in question_lower:
            timeframe = "1h"
        elif "4h" in question_lower or "4 hour" in question_lower:
            timeframe = "4h"
        elif "weekly" in question_lower or "1w" in question_lower:
            timeframe = "1w"

        # Extract lookback period (days)
        days = 30  # Default
        if "7 day" in question_lower or "week" in question_lower:
            days = 7
        elif "14 day" in question_lower or "two week" in question_lower:
            days = 14
        elif "30 day" in question_lower or "month" in question_lower:
            days = 30
        elif "90 day" in question_lower or "quarter" in question_lower:
            days = 90
        elif "year" in question_lower or "365" in question_lower:
            days = 365

        # Extract metric
        metric = "price"
        if "volatility" in question_lower or "vol" in question_lower:
            metric = "volatility"
        elif "volume" in question_lower:
            metric = "volume"
        elif "correlation" in question_lower or "corr" in question_lower:
            metric = "correlation"
        elif "rsi" in question_lower:
            metric = "rsi"
        elif "sharpe" in question_lower:
            metric = "sharpe"
        elif "drawdown" in question_lower:
            metric = "drawdown"
        elif "return" in question_lower or "performance" in question_lower:
            metric = "returns"

        # Comparison?
        comparison = len(symbols) > 1 or "compare" in question_lower or "vs" in question_lower

        # Chart type
        chart_type = "line"
        if "bar" in question_lower:
            chart_type = "bar"
        elif "heatmap" in question_lower:
            chart_type = "heatmap"
        elif "scatter" in question_lower:
            chart_type = "scatter"
        elif metric == "correlation":
            chart_type = "heatmap"

        return {
            "symbols": symbols,
            "timeframe": timeframe,
            "days": days,
            "metric": metric,
            "comparison": comparison,
            "chart_type": chart_type,
            "original_question": question
        }

    def _fetch_data(self, parsed: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """Fetch market data for all requested symbols"""
        data = {}
        for symbol in parsed["symbols"]:
            df = self.data_client.get_ohlcv(
                symbol,
                parsed["timeframe"],
                parsed["days"]
            )
            data[symbol] = df
        return data

    def _calculate_metrics(
        self,
        data: Dict[str, pd.DataFrame],
        parsed: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate requested metrics from data"""
        metric = parsed["metric"]
        metrics = {"metric_type": metric}

        for symbol, df in data.items():
            close = df['close']

            if metric == "price":
                metrics[symbol] = {
                    "current": float(close.iloc[-1]),
                    "high": float(close.max()),
                    "low": float(close.min()),
                    "change_pct": float((close.iloc[-1] - close.iloc[0]) / close.iloc[0] * 100)
                }

            elif metric == "volatility":
                returns = close.pct_change().dropna()
                vol = returns.std() * np.sqrt(252)  # Annualized
                metrics[symbol] = {
                    "daily_vol": float(returns.std() * 100),
                    "annualized_vol": float(vol * 100),
                    "current_vs_avg": float(returns.iloc[-5:].std() / returns.std())
                }

            elif metric == "volume":
                vol = df['volume']
                metrics[symbol] = {
                    "current": float(vol.iloc[-1]),
                    "avg": float(vol.mean()),
                    "ratio": float(vol.iloc[-1] / vol.mean())
                }

            elif metric == "rsi":
                delta = close.diff()
                gain = delta.where(delta > 0, 0).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                metrics[symbol] = {
                    "current": float(rsi.iloc[-1]),
                    "avg": float(rsi.mean()),
                    "high": float(rsi.max()),
                    "low": float(rsi.min())
                }

            elif metric == "returns":
                ret = (close.iloc[-1] - close.iloc[0]) / close.iloc[0]
                metrics[symbol] = {
                    "total_return_pct": float(ret * 100),
                    "daily_avg_pct": float(close.pct_change().mean() * 100)
                }

            elif metric == "sharpe":
                returns = close.pct_change().dropna()
                sharpe = returns.mean() / returns.std() * np.sqrt(252)
                metrics[symbol] = {
                    "sharpe_ratio": float(sharpe),
                    "annualized_return": float(returns.mean() * 252 * 100),
                    "annualized_vol": float(returns.std() * np.sqrt(252) * 100)
                }

            elif metric == "drawdown":
                cummax = close.cummax()
                dd = (close - cummax) / cummax
                metrics[symbol] = {
                    "current_dd_pct": float(dd.iloc[-1] * 100),
                    "max_dd_pct": float(dd.min() * 100),
                    "avg_dd_pct": float(dd.mean() * 100)
                }

        # Correlation if multiple symbols
        if metric == "correlation" and len(data) > 1:
            closes = pd.DataFrame({s: df['close'] for s, df in data.items()})
            corr = closes.corr()
            metrics["correlation_matrix"] = corr.to_dict()

        return metrics

    def _generate_chart(
        self,
        data: Dict[str, pd.DataFrame],
        metrics: Dict[str, Any],
        parsed: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate visualization"""
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates

            fig, ax = plt.subplots(figsize=(10, 6))

            chart_type = parsed["chart_type"]
            metric = parsed["metric"]

            if chart_type == "line":
                for symbol, df in data.items():
                    if metric == "price":
                        ax.plot(df.index, df['close'], label=symbol)
                    elif metric == "volatility":
                        vol = df['close'].pct_change().rolling(20).std() * np.sqrt(252) * 100
                        ax.plot(df.index, vol, label=f"{symbol} Vol")
                    elif metric == "rsi":
                        close = df['close']
                        delta = close.diff()
                        gain = delta.where(delta > 0, 0).rolling(14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                        rsi = 100 - (100 / (1 + gain / loss))
                        ax.plot(df.index, rsi, label=f"{symbol} RSI")
                        ax.axhline(y=70, color='r', linestyle='--', alpha=0.5)
                        ax.axhline(y=30, color='g', linestyle='--', alpha=0.5)

            elif chart_type == "bar" and metric == "returns":
                symbols = list(metrics.keys())
                symbols = [s for s in symbols if s != "metric_type"]
                returns = [metrics[s].get("total_return_pct", 0) for s in symbols]
                colors = ['green' if r > 0 else 'red' for r in returns]
                ax.bar(symbols, returns, color=colors)
                ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

            elif chart_type == "heatmap" and "correlation_matrix" in metrics:
                corr_dict = metrics["correlation_matrix"]
                corr_df = pd.DataFrame(corr_dict)
                im = ax.imshow(corr_df.values, cmap='RdYlGn', vmin=-1, vmax=1)
                ax.set_xticks(range(len(corr_df.columns)))
                ax.set_yticks(range(len(corr_df.index)))
                ax.set_xticklabels(corr_df.columns)
                ax.set_yticklabels(corr_df.index)
                plt.colorbar(im)

                # Add correlation values
                for i in range(len(corr_df.index)):
                    for j in range(len(corr_df.columns)):
                        ax.text(j, i, f'{corr_df.iloc[i, j]:.2f}',
                               ha='center', va='center', fontsize=10)

            # Formatting
            ax.set_title(f"{parsed['metric'].upper()} - {', '.join(parsed['symbols'])}")
            ax.legend()
            ax.grid(True, alpha=0.3)

            if chart_type == "line":
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                plt.xticks(rotation=45)

            plt.tight_layout()

            # Convert to base64
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            chart_b64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()

            return {"chart": chart_b64, "type": "png_base64"}

        except Exception as e:
            return {"chart": None, "type": "error", "error": str(e)}

    def _generate_caption(self, metrics: Dict[str, Any], parsed: Dict[str, Any]) -> str:
        """Generate human-readable caption for the results"""
        metric = parsed["metric"]
        symbols = parsed["symbols"]

        captions = []

        for symbol in symbols:
            if symbol not in metrics:
                continue

            m = metrics[symbol]

            if metric == "price":
                captions.append(
                    f"{symbol}: ${m['current']:,.2f} ({m['change_pct']:+.1f}% over {parsed['days']}d)"
                )

            elif metric == "volatility":
                captions.append(
                    f"{symbol}: {m['annualized_vol']:.1f}% annualized volatility"
                )

            elif metric == "rsi":
                rsi = m['current']
                status = "oversold" if rsi < 30 else "overbought" if rsi > 70 else "neutral"
                captions.append(f"{symbol} RSI: {rsi:.1f} ({status})")

            elif metric == "returns":
                captions.append(
                    f"{symbol}: {m['total_return_pct']:+.1f}% return over {parsed['days']}d"
                )

            elif metric == "sharpe":
                captions.append(
                    f"{symbol} Sharpe: {m['sharpe_ratio']:.2f}"
                )

            elif metric == "drawdown":
                captions.append(
                    f"{symbol}: Currently {m['current_dd_pct']:.1f}% from peak (Max: {m['max_dd_pct']:.1f}%)"
                )

        if "correlation_matrix" in metrics and len(symbols) > 1:
            captions.append(f"Correlation matrix shown for {', '.join(symbols)}")

        return " | ".join(captions) if captions else "Analysis complete."

    def _log_query(self, question: str, result: Dict[str, Any]):
        """Log query for analytics"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "symbols": result.get("symbols"),
            "metric": result.get("metric"),
            "caption": result.get("caption")
        }

        log_file = self.log_dir / f"query_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")


# CLI
if __name__ == "__main__":
    import sys

    oracle = OracleInterface()

    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Compare BTC and ETH volatility over 30 days"

    print(f"\n{'='*60}")
    print("ORACLE INTERFACE")
    print('='*60)
    print(f"Question: {question}\n")

    result = oracle.query(question)

    print(f"Caption: {result['caption']}")
    print(f"\nSymbols: {result['symbols']}")
    print(f"Metric: {result['metric']}")
    print(f"Chart: {'Generated' if result['chart'] else 'None'} ({result['chart_type']})")

    if result['data']:
        print(f"\nData: {json.dumps(result['data'], indent=2, default=str)}")

    print('='*60)
