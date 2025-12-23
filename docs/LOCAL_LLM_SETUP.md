# Local LLM Setup for SS_III
## Claude Desktop Prompt for M3 Mac 16GB

---

## SYSTEM CONTEXT

You are helping Memphis set up local LLMs for the SOVEREIGN_SHADOW_3 trading system.

**Hardware:**
- Mac M3 chip
- 16GB unified RAM
- macOS
- LM Studio installed

**Goal:** Run AI models locally for crypto trading analysis with zero API costs.

---

## RECOMMENDED MODELS (In Priority Order)

### 1. Qwen2.5-14B-Instruct (PRIMARY)
- **Search in LM Studio:** `Qwen2.5-14B-Instruct GGUF`
- **Download variant:** Q4_K_M
- **RAM usage:** ~9GB
- **Speed:** 18-25 tok/sec
- **Why:** Won Alpha Arena crypto trading competition with 22% returns. Best balance of speed and capability for 16GB.

### 2. DeepSeek-R1-Distill-Qwen-32B (ADVANCED)
- **Search in LM Studio:** `DeepSeek-R1-Distill-Qwen-32B GGUF`
- **Download variant:** Q4_K_M
- **RAM usage:** ~20GB (requires swap, close other apps)
- **Speed:** 8-12 tok/sec
- **Why:** Built by hedge fund quants. Best reasoning for complex trading decisions.

### 3. Gemma-2-9B-Instruct (FAST)
- **Search in LM Studio:** `Gemma-2-9B-Instruct GGUF`
- **Download variant:** Q5_K_M
- **RAM usage:** ~7GB
- **Speed:** 25-35 tok/sec
- **Why:** Fastest on Apple Silicon. Use for rapid market scans.

### 4. DeepSeek-Coder-6.7B (CODE)
- **Search in LM Studio:** `DeepSeek-Coder-6.7B-Instruct GGUF`
- **Download variant:** Q4_K_M
- **RAM usage:** ~4GB
- **Speed:** 30+ tok/sec
- **Why:** Analyze and debug trading algorithms.

---

## LM STUDIO SETUP STEPS

### Step 1: Configure External Storage (2TB LegacySafe Drive)

1. In LM Studio → **Settings** (gear icon)
2. Find **Models Directory**
3. Change to: `/Volumes/LegacySafe/LMStudio/models/`
4. Create the folder if needed: `mkdir -p /Volumes/LegacySafe/LMStudio/models`
5. Restart LM Studio

**Why external drive?**
- Models are 4-11GB each
- Store all models without filling internal SSD
- Load time only slightly longer (few seconds)
- Once loaded, performance is identical

### Step 2: Download Models

1. Open LM Studio
2. Go to **Search** tab (magnifying glass icon)
3. Search for model name above
4. Find the **GGUF** version with **Q4_K_M** or **Q5_K_M** quantization
5. Click Download (saves to LegacySafe)
6. Once downloaded, go to **Chat** tab
7. Select the model from dropdown
8. Enable **MLX** backend in settings (faster on M3)

### Recommended Model Library

Store all on `/Volumes/LegacySafe/LMStudio/models/`:

```
/Volumes/LegacySafe/LMStudio/models/
├── qwen2.5-14b-instruct-q4_k_m.gguf    (~9GB)  - Crypto trading champ
├── gemma-2-9b-instruct-q5_k_m.gguf     (~7GB)  - Fastest on M3
├── deepseek-coder-6.7b-q4_k_m.gguf     (~4GB)  - Code analysis
└── [any other models you download]
```

Total space needed: ~31GB (you have 2TB)

---

## API SERVER SETUP (For SS_III Integration)

1. In LM Studio, go to **Local Server** tab
2. Select your loaded model
3. Click **Start Server**
4. Server runs at: `http://localhost:1234/v1`
5. Compatible with OpenAI API format

**Test the API:**
```bash
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local-model",
    "messages": [{"role": "user", "content": "Analyze BTC at $88,000"}]
  }'
```

---

## SS_III INTEGRATION CODE

Create `/Volumes/LegacySafe/SS_III/core/integrations/local_llm.py`:

```python
#!/usr/bin/env python3
"""
Local LLM Integration via LM Studio
Zero API costs - runs on M3 Mac
"""

import requests
from typing import Dict, Optional

class LocalLLM:
    """Connect to LM Studio local server."""

    def __init__(self, base_url: str = "http://localhost:1234/v1"):
        self.base_url = base_url
        self.model = "local-model"  # LM Studio uses this identifier

    def analyze(self, prompt: str, max_tokens: int = 500) -> str:
        """Send analysis request to local LLM."""
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.3  # Lower = more consistent
                },
                timeout=120
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
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
            import json
            return json.loads(result)
        except:
            return {"error": result}


# Quick test
if __name__ == "__main__":
    llm = LocalLLM()

    print("Testing Local LLM...")
    response = llm.analyze("What is Bitcoin's primary use case? One sentence.")
    print(f"Response: {response}")

    print("\nTesting Market Analysis...")
    analysis = llm.market_analysis("BTC", 88000, {
        "change_24h": 1.2,
        "volume": 25000000000,
        "support": 81300,
        "resistance": 93000
    })
    print(f"Analysis: {analysis}")
```

---

## MEMORY OPTIMIZATION

If models run slow or crash:

1. **Close all other apps** (browsers especially)
2. **In LM Studio Settings:**
   - GPU Layers: Maximum (offload to Neural Engine)
   - Context Length: 4096 (reduce from 8192 if needed)
   - Batch Size: 512 (reduce if OOM)
3. **Use smaller quantization:** Q4_K_S instead of Q4_K_M
4. **Monitor Activity Monitor** for memory pressure

---

## TRADING PROMPTS

### Market Structure Analysis
```
Analyze {SYMBOL} market structure:
- Price: ${PRICE}
- 24h Volume: ${VOLUME}
- BTC Dominance: {DOM}%
- Fear & Greed Index: {FGI}

Determine:
1. Current regime (trending up/down, ranging, volatile)
2. Key support/resistance levels
3. Risk/reward for entry here
4. Recommended position size (% of portfolio)

Be concise. Focus on actionable insights.
```

### Trade Validation
```
Validate this trade setup:
- Asset: {SYMBOL}
- Direction: {LONG/SHORT}
- Entry: ${ENTRY}
- Stop Loss: ${SL}
- Take Profit: ${TP}
- Position Size: ${SIZE}

Check:
1. Does R:R ratio make sense?
2. Is stop loss at logical level?
3. Any red flags?
4. Confidence score 0-100

Be critical. Find problems.
```

### Risk Assessment
```
Assess portfolio risk:
Current Positions:
{LIST_POSITIONS}

Total Exposure: ${TOTAL}
Available Capital: ${AVAILABLE}

Evaluate:
1. Correlation risk (are positions correlated?)
2. Concentration risk
3. Drawdown if BTC drops 20%
4. Recommendations to reduce risk
```

---

## COST COMPARISON

| Service | Cost/Month | Tokens |
|---------|------------|--------|
| Claude API | $20-100+ | Limited |
| OpenAI API | $20-100+ | Limited |
| Gemini API | $0-50+ | Limited |
| **Local LLM** | **$0** | **Unlimited** |

Running locally = unlimited analysis at zero marginal cost.

---

## PERFORMANCE BENCHMARKS (M3 16GB)

| Model | Tokens/Sec | RAM | Quality |
|-------|------------|-----|---------|
| Gemma 2 9B | 25-35 | 7GB | Good |
| Qwen2.5 14B | 18-25 | 9GB | Excellent |
| DeepSeek-R1 32B | 8-12 | 20GB | Outstanding |

---

## TROUBLESHOOTING

**Model won't load:**
- Check RAM in Activity Monitor
- Try smaller model or more aggressive quantization
- Restart LM Studio

**Slow responses:**
- Enable MLX backend
- Reduce context length
- Close other apps

**API not responding:**
- Check server is running (green status in LM Studio)
- Verify port 1234 is not blocked
- Test with curl command above

---

## SOURCES

- Alpha Arena Results: Qwen 22% returns, DeepSeek 4.9%
- LM Studio MLX: 26-30% faster than Ollama on Apple Silicon
- Model downloads: HuggingFace GGUF repositories

---

Last Updated: 2025-12-21
For: SOVEREIGN_SHADOW_3 Trading System
