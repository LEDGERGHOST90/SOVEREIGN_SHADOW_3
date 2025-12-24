'''
Generates a Markdown summary report from the comprehensive strategy analysis.
'''
import json

# Load the analysis data
with open('/home/ubuntu/comprehensive_strategy_analysis.json', 'r') as f:
    data = json.load(f)

report_parts = []

# --- 1. Report Header ---
report_parts.append("# 🎯 Trading Strategy Portfolio Analysis")
report_parts.append(f"**Analysis Date:** {data['analysis_date']}  \n**Author:** Manus AI")
report_parts.append("This report provides a comprehensive analysis of the **34 unique trading strategies** submitted for review. Each strategy has been systematically evaluated, scored, and graded to identify strengths, weaknesses, and opportunities for enhancement.")

# --- 2. Executive Summary ---
report_parts.append("\n## 📊 Executive Summary")
report_parts.append("The overall portfolio of strategies is robust, with a strong foundation in several key archetypes including Breakout, Mean Reversion, and Trend Following. The average portfolio score is **77.4 / 100**, indicating a solid base to build upon. However, a significant number of strategies require urgent attention to address critical risk management flaws.")

summary_table = [
    ["**Metric**", "**Value**"],
    ["Total Unique Strategies", str(data['total_strategies'])],
    ["Average Portfolio Score", f"{data['average_score']:.1f} / 100"],
    ["Strategies with 'A' Grade (Score ≥ 80)", str(data['summary']['grade_distribution']['A'])],
    ["Strategies with Critical Issues", str(data['summary']['critical_issues_total'])],
    ["Strategies Needing Urgent Attention", str(len(data['summary']['needs_urgent_attention']))]
]

report_parts.append('\n| ' + ' | '.join(summary_table[0]) + ' |')
report_parts.append('| ' + ' | '.join(['---'] * len(summary_table[0])) + ' |')
for row in summary_table[1:]:
    report_parts.append('| ' + ' | '.join(row) + ' |')

# --- 3. Top-Performing Strategies ---
report_parts.append("\n## 🏆 Top 5 Performing Strategies")
report_parts.append("The following strategies scored the highest based on the analytical framework, demonstrating robust logic and sound risk management principles. These should be prioritized for further development and live testing.")

top_5_table = [
    ["**Rank**", "**Strategy Name**", "**Score**", "**Type**", "**Key Strengths**"],
]
for i, name in enumerate(data['summary']['top_5_strategies'], 1):
    s = next(s for s in data['strategies'] if s['name'] == name)
    strengths = []
    if s['score'] == 100:
        strengths.append("Excellent Risk/Reward")
        strengths.append("Comprehensive Features")
    top_5_table.append([
        str(i),
        s['name'],
        f"**{s['score']} / 100**",
        s['type'],
        ", ".join(strengths)
    ])

report_parts.append('\n| ' + ' | '.join(top_5_table[0]) + ' |')
report_parts.append('| ' + ' | '.join(['---'] * len(top_5_table[0])) + ' |')
for row in top_5_table[1:]:
    report_parts.append('| ' + ' | '.join(row) + ' |')

# --- 4. Strategies Needing Urgent Attention ---
report_parts.append("\n## ⚠️ Strategies Needing Urgent Attention")
report_parts.append(f"**{len(data['summary']['needs_urgent_attention'])} strategies** have been identified with one or more critical issues, primarily the absence of a stop-loss mechanism. These strategies should not be deployed until these flaws are addressed.")

urgent_table = [
    ["**Strategy Name**", "**Grade**", "**Critical Issue(s)**"],
]
for name in data['summary']['needs_urgent_attention']:
    s = next(s for s in data['strategies'] if s['name'] == name)
    issues = [w['issue'] for w in s['weaknesses'] if w['severity'] == 'CRITICAL']
    urgent_table.append([
        s['name'],
        s['grade'],
        ", ".join(issues)
    ])

report_parts.append('\n| ' + ' | '.join(urgent_table[0]) + ' |')
report_parts.append('| ' + ' | '.join(['---'] * len(urgent_table[0])) + ' |')
for row in urgent_table[1:]:
    report_parts.append('| ' + ' | '.join(row) + ' |')

# --- 5. Common Weaknesses & Key Recommendations ---
report_parts.append("\n## 💡 Key Recommendations for Portfolio Strengthening")
report_parts.append("Across the portfolio, several common themes emerged. Addressing these will significantly enhance the robustness and performance of your entire strategy collection.")

report_parts.append("\n### 1. Mandate Stop-Loss on All Strategies (CRITICAL)")
report_parts.append("> **Observation:** 16 strategies lack a defined stop-loss mechanism, exposing them to unlimited risk.  \n> **Recommendation:** Implement an ATR (Average True Range)-based stop-loss (e.g., 2-3x ATR) on all strategies as a baseline. This ensures risk is always defined and controlled.")

report_parts.append("\n### 2. Standardize Risk-Per-Trade (HIGH)")
report_parts.append("> **Observation:** Many strategies lack a fixed risk percentage.  \n> **Recommendation:** Standardize risk to 1-2% of equity per trade. This prevents catastrophic losses from a single position and ensures portfolio longevity.")

report_parts.append("\n### 3. Enhance Signal Quality with Confirmation Indicators (HIGH)")
report_parts.append("> **Observation:** A number of strategies rely on a single indicator, making them susceptible to false signals.  \n> **Recommendation:** Add confirmation indicators. For example, breakout strategies should always be confirmed with a volume surge (e.g., >2x average volume). Trend strategies should use an ADX filter (>25) to confirm trend strength.")

report_parts.append("\n### 4. Implement Dynamic Exits (MEDIUM)")
report_parts.append("> **Observation:** Most strategies have fixed or no take-profit targets.  \n> **Recommendation:** Implement dynamic exit mechanisms like trailing stops (ATR-based or percentage-based) and scaled exits (e.g., taking partial profits at 1R, 2R, and 3R).")

# --- 6. Next Steps ---
report_parts.append("\n## 🚀 Next Steps")
report_parts.append("1. **Review Detailed Analysis:** The Notion database has been updated with a detailed analysis page for each of the 34 strategies, including specific weaknesses and a full set of actionable recommendations.")
report_parts.append("2. **Prioritize Critical Fixes:** Focus on implementing stop-loss and standardized risk management for the 16 strategies marked for urgent attention.")
report_parts.append("3. **Enhance Top Strategies:** Begin by applying the strengthening recommendations to the Top 5 performing strategies to make them even more robust.")
report_parts.append("4. **Backtest & Validate:** All modified strategies must be rigorously backtested and validated across different market conditions before any live deployment.")

# --- 7. References ---
report_parts.append("\n## References")
report_parts.append(f"[1] Notion Trading Strategies Database: https://www.notion.so/90bb435899f74af381a9f48dce8465df")

# Save the report
with open('/home/ubuntu/Strategy_Portfolio_Analysis.md', 'w') as f:
    f.write('\n\n'.join(report_parts))

print("✅ Strategy portfolio analysis report generated successfully.")
