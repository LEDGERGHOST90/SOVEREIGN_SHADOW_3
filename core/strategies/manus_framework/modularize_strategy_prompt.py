#!/usr/bin/env python3.11
"""
Strategy Modularization Prompt System
Provides a prompt and a method to break down strategies into reusable components.
"""

import json
from pathlib import Path

# --- The Optimal Prompt for Strategy Decomposition ---
# This prompt is optimized for advanced code-analysis models like Gemini 2.5 Flash or GPT-4.1

MODULARIZATION_PROMPT_TEMPLATE = """
**Act as an expert trading system architect and quantitative developer.**

Your task is to decompose the provided Python trading strategy code into its core, modular, and reusable components. Analyze the code and extract the logic for each component into a structured JSON format.

**Objective:** Create a machine-readable, structured representation of the strategy's logic that can be used for automated analysis, backtesting, and execution by a master trading orchestrator.

**Input Python Code:**
```python
{strategy_code}
```

**Decomposition Schema (Output JSON Format):**

Strictly adhere to the following JSON schema. Do not add any extra commentary or explanations outside of the JSON structure.

```json
{
  "strategy_name": "<Name of the strategy class>",
  "strategy_type": "<Classify as one of: Trend Following, Mean Reversion, Breakout, Volatility, Momentum, Scalping, Arbitrage, etc.>",
  "description": "<A brief, one-sentence description of the strategy's core logic>",
  "components": {
    "parameters": [
      {
        "name": "<parameter_name>",
        "default_value": "<value>",
        "description": "<What this parameter controls>"
      }
    ],
    "data_requirements": {
      "timeframe": "<e.g., 15m, 1h, 1d>",
      "indicators": [
        {
          "name": "<Indicator Name, e.g., EMA, RSI, BollingerBands>",
          "parameters": "<Parameters used, e.g., period=20, std_dev=2>",
          "code_snippet": "<The exact line(s) of Python code that calculate this indicator>"
        }
      ]
    },
    "logic": {
      "entry_conditions_long": {
        "description": "<Plain English description of the long entry logic>",
        "code_snippet": "<The exact Python code block for long entry conditions>"
      },
      "entry_conditions_short": {
        "description": "<Plain English description of the short entry logic>",
        "code_snippet": "<The exact Python code block for short entry conditions>"
      },
      "exit_conditions_long": {
        "description": "<Plain English description of the long exit logic (take profit, stop loss)>",
        "code_snippet": "<The exact Python code block for long exit conditions>"
      },
      "exit_conditions_short": {
        "description": "<Plain English description of the short exit logic (take profit, stop loss)>",
        "code_snippet": "<The exact Python code block for short exit conditions>"
      }
    },
    "risk_management": {
      "position_sizing": {
        "method": "<e.g., Fixed Size, Percent of Equity, ATR-based>",
        "code_snippet": "<The Python code for calculating position size>"
      },
      "stop_loss": {
        "method": "<e.g., Fixed Percentage, ATR Trailing, Indicator-based>",
        "code_snippet": "<The Python code for calculating stop-loss levels>"
      },
      "take_profit": {
        "method": "<e.g., Fixed R:R Ratio, Indicator Target, Price Level>",
        "code_snippet": "<The Python code for calculating take-profit levels>"
      }
    }
  }
}
```

**Instructions:**
1.  **Analyze the entire script** to understand the strategy's flow.
2.  **Identify the main strategy class** and its parameters.
3.  **Extract all technical indicators** used, including their specific parameters.
4.  **Isolate the exact conditional logic** for long/short entries and exits.
5.  **Pinpoint the risk management logic**, including how position size, stop-loss, and take-profit are determined.
6.  **Populate the JSON schema** with the extracted information. Ensure all `code_snippet` fields contain valid, verbatim Python code from the input.
7.  **If a component is not present** (e.g., no short conditions), provide an empty list `[]` or an empty string `""` for the corresponding field.

**Begin analysis and generate the JSON output now.**
"""

def generate_modularization_prompt(strategy_code: str) -> str:
    """Fills the template with the strategy code."""
    return MODULARIZATION_PROMPT_TEMPLATE.replace("{strategy_code}", strategy_code)


if __name__ == "__main__":
    # --- Example Usage ---
    
    # 1. Select a strategy file to modularize
    # Using one of the files uploaded by the user
    strategy_file_path = Path("/home/ubuntu/upload/VolatilityBandit_BTFinal.py")
    
    if not strategy_file_path.exists():
        print(f"Error: Strategy file not found at {strategy_file_path}")
        # Create a dummy file for demonstration if it doesn't exist
        dummy_code = """
class VolatilityBandit(Strategy):
    def init(self):
        self.atr = self.I(self.atr, self.data.High, self.data.Low, self.data.Close, 14)
    def next(self):
        if self.position:
            if self.data.Close[-1] > self.position.entry_price * 1.02:
                self.position.close()
        elif self.atr[-1] > 50:
            self.buy()
"""
        strategy_code = dummy_code
        print("Using dummy code for demonstration.")
    else:
        # 2. Read the strategy code
        with open(strategy_file_path, 'r') as f:
            strategy_code = f.read()
    
    # 3. Generate the complete prompt
    final_prompt = generate_modularization_prompt(strategy_code)
    
    # 4. Save the prompt to a file for inspection
    prompt_output_path = Path("/home/ubuntu/generated_modularization_prompt.txt")
    with open(prompt_output_path, 'w') as f:
        f.write(final_prompt)
        
    print("="*80)
    print("✅ STRATEGY MODULARIZATION PROMPT GENERATED")
    print("="*80)
    print(f"\nThis script has generated a detailed, optimized prompt to break down a trading strategy into modular components.")
    print(f"\n💡 HOW TO USE:")
    print("1. Copy the content from the generated file:")
    print(f"   `{prompt_output_path}`")
    print("2. Paste it into a powerful AI model with code analysis capabilities (e.g., Gemini 2.5 Flash, GPT-4.1).")
    print("3. The AI will return a structured JSON file containing the decomposed strategy logic.")
    print("4. This JSON can then be used by your Master Trading Orchestrator for analysis and execution.")
    print("\nAn example prompt has been generated for the 'VolatilityBandit_BTFinal.py' strategy.")
    print("You can now automate this process for all 294+ of your strategies.")
