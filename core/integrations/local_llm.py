#!/usr/bin/env python3
"""
Local LLM Integration via LM Studio
Zero API costs - runs on M3 Mac

Models stored at: /Volumes/LegacySafe/LMStudio/models/
"""

import requests
import json
from typing import Dict, Optional


class LocalLLM:
    """Connect to LM Studio local server."""

    def __init__(self, base_url: str = "http://localhost:1234/v1"):
        self.base_url = base_url
        self.model = "local-model"  # LM Studio uses this identifier

    def is_available(self) -> bool:
        """Check if LM Studio server is running."""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=5)
            return response.status_code == 200
        except:
            return False

    def _parse_json_response(self, text: str) -> dict:
        """Parse JSON from model response, handling markdown blocks."""
        import re

        # Try direct parse first
        try:
            return json.loads(text.strip())
        except:
            pass

        # Extract JSON from markdown code blocks
        patterns = [
            r'```json\s*([\s\S]*?)\s*```',  # ```json ... ```
            r'```\s*([\s\S]*?)\s*```',       # ``` ... ```
            r'\{[\s\S]*\}',                   # Raw { ... }
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    json_str = match.group(1) if '```' in pattern else match.group(0)
                    return json.loads(json_str.strip())
                except:
                    continue

        raise ValueError(f"Could not parse JSON from: {text[:200]}")

    def analyze(self, prompt: str, max_tokens: int = 500, temperature: float = 0.3) -> str:
        """Send analysis request to local LLM."""
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": temperature  # Lower = more consistent
                },
                timeout=120
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.ConnectionError:
            return "Error: LM Studio server not running. Start it at http://localhost:1234"
        except Exception as e:
            return f"Error: {e}"

    def market_analysis(self, symbol: str, price: float, data: Dict) -> Dict:
        """Structured market analysis."""
        prompt = f"""Analyze {symbol} for trading:

Current Price: ${price:,.2f}
24h Change: {data.get('change_24h', 'N/A')}%
Volume: ${data.get('volume', 'N/A')}
Support: ${data.get('support', 'N/A')}
Resistance: ${data.get('resistance', 'N/A')}

Respond in JSON format:
{{
    "regime": "trending|ranging|volatile",
    "bias": "bullish|bearish|neutral",
    "confidence": 0-100,
    "entry": price or null,
    "stop_loss": price or null,
    "take_profit": price or null,
    "reasoning": "brief explanation"
}}

JSON only, no markdown:"""

        result = self.analyze(prompt)

        try:
            return self._parse_json_response(result)
        except:
            return {"error": result, "raw_response": True}

    def validate_trade(self, trade: Dict) -> Dict:
        """Validate a trade setup before execution."""
        prompt = f"""Validate this trade setup:

Asset: {trade.get('symbol')}
Direction: {trade.get('side', 'unknown').upper()}
Entry: ${trade.get('entry', 0):,.2f}
Stop Loss: ${trade.get('stop_loss', 0):,.2f}
Take Profit: ${trade.get('take_profit', 0):,.2f}
Position Size: ${trade.get('size', 0):,.2f}

Check:
1. Does R:R ratio make sense?
2. Is stop loss at logical level?
3. Any red flags?
4. Confidence score 0-100

Respond in JSON:
{{
    "approved": true/false,
    "confidence": 0-100,
    "rr_ratio": number,
    "issues": ["list of concerns"],
    "recommendation": "proceed|adjust|reject"
}}

JSON only:"""

        result = self.analyze(prompt)

        try:
            return self._parse_json_response(result)
        except:
            return {"approved": False, "error": result}

    def portfolio_risk(self, positions: list, total_value: float) -> Dict:
        """Assess portfolio risk."""
        positions_str = "\n".join([
            f"- {p.get('symbol')}: ${p.get('value', 0):,.2f} ({p.get('pct', 0):.1f}%)"
            for p in positions
        ])

        prompt = f"""Assess portfolio risk:

Current Positions:
{positions_str}

Total Portfolio Value: ${total_value:,.2f}

Evaluate:
1. Correlation risk (are positions correlated?)
2. Concentration risk
3. Estimated drawdown if BTC drops 20%
4. Risk score 1-10 (10 = highest risk)

Respond in JSON:
{{
    "risk_score": 1-10,
    "correlation_risk": "low|medium|high",
    "concentration_risk": "low|medium|high",
    "btc_drop_20_impact": percentage,
    "recommendations": ["list"]
}}

JSON only:"""

        result = self.analyze(prompt, max_tokens=800)

        try:
            return self._parse_json_response(result)
        except:
            return {"error": result}


# Quick test
if __name__ == "__main__":
    llm = LocalLLM()

    print("=== LOCAL LLM TEST ===\n")

    # Check availability
    if not llm.is_available():
        print("LM Studio server not running!")
        print("Start it at: LM Studio -> Local Server -> Start Server")
        print("Default URL: http://localhost:1234")
        exit(1)

    print("LM Studio server is running\n")

    print("Testing Basic Analysis...")
    response = llm.analyze("What is Bitcoin's primary use case? One sentence.")
    print(f"Response: {response}\n")

    print("Testing Market Analysis...")
    analysis = llm.market_analysis("BTC", 88000, {
        "change_24h": 1.2,
        "volume": 25000000000,
        "support": 81300,
        "resistance": 93000
    })
    print(f"Analysis: {json.dumps(analysis, indent=2)}\n")

    print("Testing Trade Validation...")
    validation = llm.validate_trade({
        "symbol": "BTC",
        "side": "long",
        "entry": 88000,
        "stop_loss": 85000,
        "take_profit": 95000,
        "size": 500
    })
    print(f"Validation: {json.dumps(validation, indent=2)}")
