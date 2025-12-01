#!/usr/bin/env python3
"""
TRANSPARENT ANALYST - Step-By-Step Execution Visibility
Provides readable process summaries alongside final recommendations
"""

import json
import re
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from functools import wraps


@dataclass
class AnalysisResult:
    """Result with separated process and recommendation"""
    process_overview: List[str]
    final_recommendation: str
    raw_output: Optional[str] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def format(self) -> str:
        """Format for display"""
        output = "[PROCESS OVERVIEW]\n"
        for i, step in enumerate(self.process_overview, 1):
            output += f"{i}. {step}\n"
        output += f"\n[FINAL RECOMMENDATION]\n{self.final_recommendation}"
        return output


class TransparentAnalyst:
    """
    Transparent execution wrapper for Sovereign Shadow 3

    Wraps analysis functions to provide:
    - Step-by-step process summary
    - Clear final recommendation
    - Audit trail logging
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.steps: List[str] = []
        self.current_analysis: str = ""

        # Load system prompt
        self.system_prompt = self._load_system_prompt()

        # Logs directory
        self.log_dir = Path(__file__).parent.parent.parent / "logs" / "transparent_analyst"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _load_system_prompt(self) -> str:
        """Load the Transparent Analyst system prompt"""
        import yaml
        prompt_file = Path(__file__).parent.parent / "configs" / "system_prompts.yaml"
        if prompt_file.exists():
            with open(prompt_file, 'r') as f:
                prompts = yaml.safe_load(f)
                return prompts.get("transparent_analyst", "")
        return ""

    def start_analysis(self, description: str):
        """Start a new analysis session"""
        self.steps = []
        self.current_analysis = description
        self.record_step(f"Started analysis: {description}")

    def record_step(self, step: str):
        """Record a step in the analysis process"""
        self.steps.append(step)

    def complete_analysis(self, recommendation: str) -> AnalysisResult:
        """Complete analysis and return formatted result"""
        result = AnalysisResult(
            process_overview=self.steps.copy(),
            final_recommendation=recommendation
        )

        # Log the analysis
        self._log_analysis(result)

        # Reset for next analysis
        self.steps = []
        self.current_analysis = ""

        return result

    def parse_llm_response(self, response: str) -> AnalysisResult:
        """
        Parse an LLM response that follows the Transparent Analyst format.

        Handles various LLM formatting styles:
        - [PROCESS OVERVIEW]
        - **PROCESS OVERVIEW**
        - ## PROCESS OVERVIEW
        - ### Process Overview
        - PROCESS OVERVIEW:
        """
        process = []
        recommendation = ""

        # Flexible patterns for PROCESS OVERVIEW section
        # Handles: [PROCESS OVERVIEW], **PROCESS OVERVIEW**, ## PROCESS OVERVIEW, etc.
        process_patterns = [
            r'(?:\[|\*\*|#{1,3}\s*)?\s*PROCESS\s+OVERVIEW\s*(?:\]|\*\*|:)?\s*(.*?)(?=(?:\[|\*\*|#{1,3}\s*)?\s*(?:FINAL\s+)?RECOMMENDATION|$)',
            r'(?:STEPS|ANALYSIS\s+STEPS|PROCESS)\s*:?\s*(.*?)(?=(?:FINAL\s+)?RECOMMENDATION|CONCLUSION|$)',
        ]

        for pattern in process_patterns:
            process_match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if process_match:
                process_text = process_match.group(1).strip()
                # Parse numbered steps (handle various bullet styles)
                steps = re.findall(r'^\s*(?:\d+\.|-|\*|•)\s*(.+)$', process_text, re.MULTILINE)
                if steps:
                    process = [s.strip() for s in steps if s.strip()]
                    break
                else:
                    # Fallback: split by newlines
                    lines = [line.strip() for line in process_text.split('\n') if line.strip()]
                    if lines:
                        process = lines
                        break

        # Flexible patterns for RECOMMENDATION section
        recommendation_patterns = [
            r'(?:\[|\*\*|#{1,3}\s*)?\s*(?:FINAL\s+)?RECOMMENDATION\s*(?:\]|\*\*|:)?\s*(.*?)$',
            r'(?:CONCLUSION|SUMMARY|VERDICT)\s*:?\s*(.*?)$',
        ]

        for pattern in recommendation_patterns:
            rec_match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if rec_match:
                recommendation = rec_match.group(1).strip()
                # Clean up any trailing formatting
                recommendation = re.sub(r'\s*\*+\s*$', '', recommendation)
                break

        # Final fallback if no sections found
        if not process and not recommendation:
            # Try to intelligently split the response
            lines = response.strip().split('\n')
            if len(lines) > 3:
                # Assume first half is process, last paragraph is recommendation
                midpoint = len(lines) // 2
                process = [l.strip() for l in lines[:midpoint] if l.strip()]
                recommendation = ' '.join(l.strip() for l in lines[midpoint:] if l.strip())
            else:
                recommendation = response.strip()

        if not recommendation:
            recommendation = "See analysis above." if process else response.strip()

        return AnalysisResult(
            process_overview=process,
            final_recommendation=recommendation,
            raw_output=response
        )

    def wrap_function(self, func: Callable, description: str = None) -> Callable:
        """
        Decorator to wrap a function with transparent analysis

        Usage:
            @analyst.wrap_function
            def my_analysis(data):
                analyst.record_step("Loaded data")
                ...
                return result
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            desc = description or func.__name__
            self.start_analysis(desc)

            try:
                result = func(*args, **kwargs)

                # If result is a string, use as recommendation
                if isinstance(result, str):
                    return self.complete_analysis(result)

                # If result is a dict with 'recommendation' key
                if isinstance(result, dict) and 'recommendation' in result:
                    return self.complete_analysis(result['recommendation'])

                # Otherwise, convert to string
                return self.complete_analysis(str(result))

            except Exception as e:
                self.record_step(f"Error occurred: {str(e)}")
                return self.complete_analysis(f"Analysis failed: {str(e)}")

        return wrapper

    def analyze_with_context(
        self,
        context: Dict[str, Any],
        llm_func: Optional[Callable] = None
    ) -> AnalysisResult:
        """
        Perform transparent analysis with provided context

        Args:
            context: Data context for analysis
            llm_func: Optional LLM function to generate recommendation

        Returns:
            AnalysisResult with process and recommendation
        """
        self.start_analysis("Context-based analysis")

        # Record what data we have
        for key, value in context.items():
            if isinstance(value, (list, dict)):
                self.record_step(f"Loaded {key}: {len(value) if hasattr(value, '__len__') else 'complex'} items")
            else:
                self.record_step(f"Loaded {key}: {value}")

        # Generate recommendation
        if llm_func:
            try:
                recommendation = llm_func(context)
                self.record_step("Generated recommendation via LLM")
            except Exception as e:
                recommendation = f"Could not generate recommendation: {e}"
                self.record_step(f"LLM call failed: {e}")
        else:
            # Simple rule-based recommendation
            recommendation = self._generate_simple_recommendation(context)

        return self.complete_analysis(recommendation)

    def _generate_simple_recommendation(self, context: Dict[str, Any]) -> str:
        """Generate a simple recommendation from context (non-LLM fallback)"""
        recommendations = []

        # Check for common context keys
        if "score" in context:
            score = context["score"]
            if score >= 70:
                recommendations.append(f"Score of {score}/100 indicates favorable conditions.")
            elif score <= 30:
                recommendations.append(f"Score of {score}/100 suggests caution.")
            else:
                recommendations.append(f"Score of {score}/100 is neutral.")

        if "trend" in context:
            trend = context["trend"]
            recommendations.append(f"Current trend is {trend}.")

        if "risk_level" in context:
            risk = context["risk_level"]
            recommendations.append(f"Risk level: {risk}.")

        if not recommendations:
            recommendations.append("Analysis complete. Review process steps for details.")

        return " ".join(recommendations)

    def _log_analysis(self, result: AnalysisResult):
        """Log analysis for audit trail"""
        log_entry = {
            "timestamp": result.timestamp,
            "analysis": self.current_analysis,
            "steps_count": len(result.process_overview),
            "steps": result.process_overview,
            "recommendation": result.final_recommendation[:500]  # Truncate long recommendations
        }

        log_file = self.log_dir / f"analysis_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")

    def format_for_ui(self, result: AnalysisResult) -> Dict[str, Any]:
        """
        Format result for frontend UI display

        Returns:
        {
            "main_content": str (recommendation),
            "expandable": {
                "title": "How this was generated",
                "content": List[str] (steps)
            }
        }
        """
        return {
            "main_content": result.final_recommendation,
            "expandable": {
                "title": "How this was generated",
                "content": result.process_overview
            },
            "timestamp": result.timestamp
        }


# Convenience functions
def transparent_analysis(description: str = None):
    """
    Decorator for transparent analysis

    Usage:
        @transparent_analysis("Portfolio Analysis")
        def analyze_portfolio(data, analyst):
            analyst.record_step("Loaded portfolio data")
            ...
            return "Recommendation here"
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            analyst = TransparentAnalyst()
            analyst.start_analysis(description or func.__name__)

            # Inject analyst into kwargs if function accepts it
            import inspect
            sig = inspect.signature(func)
            if 'analyst' in sig.parameters:
                kwargs['analyst'] = analyst

            try:
                result = func(*args, **kwargs)

                if isinstance(result, str):
                    return analyst.complete_analysis(result)
                elif isinstance(result, dict) and 'recommendation' in result:
                    return analyst.complete_analysis(result['recommendation'])
                else:
                    return analyst.complete_analysis(str(result))

            except Exception as e:
                analyst.record_step(f"Error: {str(e)}")
                return analyst.complete_analysis(f"Analysis failed: {str(e)}")

        return wrapper
    return decorator


# CLI Demo
if __name__ == "__main__":
    analyst = TransparentAnalyst()

    print(f"\n{'='*60}")
    print("TRANSPARENT ANALYST - Demo")
    print('='*60)

    # Demo 1: Manual step recording
    analyst.start_analysis("BTC Market Analysis")
    analyst.record_step("Loaded BTC 30-day OHLCV data")
    analyst.record_step("Calculated 20-day volatility: 3.2%")
    analyst.record_step("Compared to 30-day average volatility: 2.8%")
    analyst.record_step("Checked RSI: 58 (neutral)")
    analyst.record_step("Reviewed on-chain flows: slight accumulation")

    result = analyst.complete_analysis(
        "BTC is showing slightly elevated volatility (15% above average) with neutral "
        "momentum indicators. On-chain data suggests accumulation. Consider maintaining "
        "current positions with tight stops around the 20-day low."
    )

    print("\n--- Manual Analysis ---")
    print(result.format())

    # Demo 2: Parse LLM response
    llm_response = """
    [PROCESS OVERVIEW]
    1. Retrieved ETH price data for past 7 days
    2. Calculated daily returns and volatility
    3. Compared current price to 50-day moving average
    4. Analyzed gas fees and network activity

    [FINAL RECOMMENDATION]
    ETH is trading 5% below its 50-day MA with declining gas fees suggesting reduced
    network activity. This could be a consolidation phase before the next move.
    Wait for a clear breakout above the MA before adding to positions.
    """

    parsed = analyst.parse_llm_response(llm_response)

    print("\n--- Parsed LLM Response ---")
    print(parsed.format())

    # Demo 3: Format for UI
    print("\n--- UI Format ---")
    ui_format = analyst.format_for_ui(parsed)
    print(json.dumps(ui_format, indent=2))

    print('='*60)
