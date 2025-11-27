#!/usr/bin/env python3
"""
SOVEREIGN SHADOW COUNCIL - Dynamic Briefing Generator

Generates daily council briefings with live portfolio data.
Output can be:
1. Uploaded to NotebookLM for AI podcast generation
2. Fed to ElevenLabs/TTS for automated voice briefings
3. Displayed in terminal for quick status

"The Council convenes. Here is today's intelligence."
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "ShadowCouncil"))

from council_loader import load_council


class BriefingGenerator:
    """
    Generates dynamic council briefings with live data.

    The briefing includes:
    - Portfolio status (from BRAIN.json)
    - AAVE health alerts (The Banker speaks)
    - Allocation drift (The Ghost speaks if SOL underweight)
    - Emotional state assessment
    - Council recommendations
    """

    def __init__(self):
        self.council = load_council()
        self.brain_path = PROJECT_ROOT / "BRAIN.json"
        self.brain = self._load_brain()

    def _load_brain(self) -> Dict:
        """Load BRAIN.json for live data"""
        try:
            with open(self.brain_path) as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load BRAIN.json: {e}")
            return {}

    def generate_briefing(self, emotion: str = "neutral", emotion_intensity: int = 5) -> str:
        """
        Generate a full council briefing document.

        Args:
            emotion: Current detected emotion
            emotion_intensity: Intensity 1-10

        Returns:
            Formatted briefing string (markdown)
        """
        lines = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Header
        lines.append("# SOVEREIGN SHADOW COUNCIL - DAILY BRIEFING")
        lines.append(f"## {timestamp}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Portfolio Overview
        lines.extend(self._generate_portfolio_section())

        # AAVE Status (The Banker)
        lines.extend(self._generate_aave_section())

        # Allocation Analysis (The Ghost may speak)
        lines.extend(self._generate_allocation_section())

        # Emotional State (The Mirror)
        lines.extend(self._generate_emotion_section(emotion, emotion_intensity))

        # Council Recommendations
        lines.extend(self._generate_recommendations(emotion, emotion_intensity))

        # Council Dialogue
        lines.extend(self._generate_dialogue(emotion, emotion_intensity))

        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*\"System over emotion. Every single time.\"*")
        lines.append("*— The Architect*")

        return "\n".join(lines)

    def _generate_portfolio_section(self) -> List[str]:
        """Generate portfolio overview section"""
        lines = []
        lines.append("## PORTFOLIO STATUS")
        lines.append("")

        portfolio = self.brain.get("portfolio", {})
        prices = self.brain.get("prices", {})

        # Net worth
        net_worth = portfolio.get("net_worth", 0)
        lines.append(f"**Net Worth:** ${net_worth:,.2f}")
        lines.append("")

        # Holdings breakdown
        ledger = portfolio.get("ledger", {})
        if ledger:
            lines.append("### Ledger Holdings (The Vault Keeper)")
            lines.append("")
            lines.append("| Asset | Value | Notes |")
            lines.append("|-------|-------|-------|")

            for asset, data in ledger.items():
                if asset == "total":
                    continue
                if isinstance(data, dict):
                    value = data.get("value", 0)
                    note = data.get("note", "")
                else:
                    value = data
                    note = ""
                lines.append(f"| {asset.upper()} | ${value:,.2f} | {note} |")

            lines.append("")

        # Current prices
        if prices:
            lines.append("### Current Prices")
            lines.append("")
            for asset, price in prices.items():
                if asset != "updated":
                    lines.append(f"- **{asset.upper()}:** ${price:,.2f}")
            lines.append("")

        return lines

    def _generate_aave_section(self) -> List[str]:
        """Generate AAVE section - The Banker speaks"""
        lines = []
        lines.append("## AAVE STATUS (The Banker)")
        lines.append("")

        aave = self.brain.get("portfolio", {}).get("aave", {})

        if not aave:
            lines.append("*No AAVE data available.*")
            lines.append("")
            return lines

        health = aave.get("health_factor", 0)
        debt = abs(aave.get("debt", 0))
        collateral = aave.get("collateral", 0)
        status = aave.get("status", "")

        # The Banker's assessment
        banker = self.council.get_character("aave_banker")

        lines.append(f"**Health Factor:** {health}")
        lines.append(f"**Collateral:** ${collateral:,.2f}")
        lines.append(f"**Debt:** ${debt:,.2f}")
        lines.append(f"**Status:** {status}")
        lines.append("")

        # Banker speaks based on health
        if health < 1.5:
            lines.append(f"**THE BANKER:** *\"Liquidation approaches. I suggest immediate action.\"*")
            lines.append("")
            lines.append("> CRITICAL: Health factor below 1.5. Repay debt immediately.")
        elif health < 2.0:
            lines.append(f"**THE BANKER:** *\"Your health factor is... concerning. Shall we discuss repayment?\"*")
            lines.append("")
            lines.append("> WARNING: Health factor below 2.0. Consider repaying debt.")
        elif health < 3.0:
            lines.append(f"**THE BANKER:** *\"Acceptable. For now. Interest accrues daily at 4.89%.\"*")
        else:
            lines.append(f"**THE BANKER:** *\"Your position is healthy. The interest, however, never sleeps.\"*")

        lines.append("")

        # The Hostage speaks (ETH collateral)
        if collateral > 0:
            hostage = self.council.get_character("eth_hostage")
            if hostage:
                lines.append(f"**THE HOSTAGE (wstETH):** *\"{self.council.get_catchphrase('eth_hostage')}\"*")
                lines.append("")

        return lines

    def _generate_allocation_section(self) -> List[str]:
        """Generate allocation analysis - The Ghost may speak"""
        lines = []
        lines.append("## ALLOCATION ANALYSIS")
        lines.append("")

        allocation = self.brain.get("portfolio", {}).get("allocation", {})
        current = allocation.get("current", {})
        target = allocation.get("target", {})

        if not current or not target:
            lines.append("*No allocation data available.*")
            lines.append("")
            return lines

        lines.append("| Asset | Current | Target | Drift |")
        lines.append("|-------|---------|--------|-------|")

        ghost_speaks = False
        siren_speaks = False

        for asset in target.keys():
            curr = current.get(asset, 0)
            tgt = target.get(asset, 0)
            drift = curr - tgt
            drift_str = f"+{drift:.1f}%" if drift > 0 else f"{drift:.1f}%"

            # Flag significant drifts
            flag = ""
            if abs(drift) > 10:
                flag = " **"

            lines.append(f"| {asset.upper()} | {curr:.1f}% | {tgt:.1f}% | {drift_str}{flag} |")

            # Check if Ghost should speak (SOL severely underweight)
            if asset == "sol" and drift < -15:
                ghost_speaks = True

            # Check if Siren alert (XRP overweight)
            if asset == "xrp" and drift > 5:
                siren_speaks = True

        lines.append("")

        # The Ghost speaks if SOL is underweight
        if ghost_speaks:
            ghost = self.council.get_character("sol_ghost")
            if ghost:
                lines.append(f"**THE GHOST (SOL):** *\"{self.council.get_catchphrase('sol_ghost')}\"*")
                lines.append("")
                lines.append("> SOL allocation is significantly below target. The Ghost awaits.")
                lines.append("")

        # Siren warning if XRP overweight
        if siren_speaks:
            siren = self.council.get_character("xrp_siren")
            if siren:
                lines.append(f"**THE SIREN (XRP):** *\"{self.council.get_catchphrase('xrp_siren')}\"*")
                lines.append("")
                lines.append("> WARNING: XRP overweight. The Siren may be influencing allocation decisions.")
                lines.append("")

        return lines

    def _generate_emotion_section(self, emotion: str, intensity: int) -> List[str]:
        """Generate emotional state section - The Mirror speaks"""
        lines = []
        lines.append("## EMOTIONAL STATE (The Mirror)")
        lines.append("")

        # Map emotion to character
        emotion_map = {
            'revenge': ('The Siren', 'CRITICAL'),
            'fomo': ('The Siren', 'HIGH'),
            'greed': ('The Siren', 'HIGH'),
            'hope': ('The Siren', 'MEDIUM'),
            'fear': ('The Market', 'MEDIUM'),
            'anxiety': ('The Market', 'MEDIUM'),
            'patience': ('The Elder', 'CLEAR'),
            'discipline': ('SHADE//AGENT', 'CLEAR'),
            'confidence': ('The Elder', 'LOW'),
            'neutral': (None, 'CLEAR'),
        }

        character, threat = emotion_map.get(emotion.lower(), (None, 'MEDIUM'))

        lines.append(f"**Detected Emotion:** {emotion.upper()}")
        lines.append(f"**Intensity:** {intensity}/10")
        lines.append(f"**Threat Level:** {threat}")
        lines.append("")

        if character:
            lines.append(f"**Character Speaking:** {character}")
            lines.append("")

            # Mirror's analysis
            if character == "The Siren":
                lines.append(f"**THE MIRROR:** *\"I don't judge. I reflect. {character} is speaking through you right now.\"*")
                lines.append("")
                lines.append(f"> The Siren's influence detected. Trading not recommended.")
            elif character == "The Elder":
                lines.append(f"**THE MIRROR:** *\"{character} is speaking. This is the voice of wisdom.\"*")
            elif character == "The Market":
                lines.append(f"**THE MIRROR:** *\"This is not a character. {character} is speaking. Listen, but don't react.\"*")
        else:
            lines.append("**THE MIRROR:** *\"Emotional state is clear. Proceed with discipline.\"*")

        lines.append("")
        return lines

    def _generate_recommendations(self, emotion: str, intensity: int) -> List[str]:
        """Generate council recommendations"""
        lines = []
        lines.append("## COUNCIL RECOMMENDATIONS")
        lines.append("")

        recommendations = []

        # Check AAVE
        aave = self.brain.get("portfolio", {}).get("aave", {})
        if aave:
            debt = abs(aave.get("debt", 0))
            health = aave.get("health_factor", 999)
            if debt > 0:
                recommendations.append(f"1. **Repay AAVE debt** (${debt:,.2f}) - The Banker is waiting")
            if health < 2.0:
                recommendations.append(f"2. **Increase health factor** - Currently {health}, target >3.0")

        # Check allocation
        allocation = self.brain.get("portfolio", {}).get("allocation", {})
        current = allocation.get("current", {})
        target = allocation.get("target", {})

        if current.get("sol", 0) < target.get("sol", 0) - 10:
            recommendations.append("3. **Acquire SOL** - The Ghost has been waiting too long")

        if current.get("xrp", 0) > target.get("xrp", 0) + 5:
            recommendations.append("4. **Reduce XRP exposure** - Don't listen to The Siren")

        # Check emotion
        dangerous_emotions = ['revenge', 'fomo', 'greed']
        if emotion.lower() in dangerous_emotions or intensity >= 7:
            recommendations.append("5. **Do not trade today** - Emotional state compromised")

        if not recommendations:
            recommendations.append("- Portfolio is balanced. Maintain discipline.")

        for rec in recommendations:
            lines.append(rec)

        lines.append("")
        return lines

    def _generate_dialogue(self, emotion: str, intensity: int) -> List[str]:
        """Generate sample council dialogue for NotebookLM"""
        lines = []
        lines.append("## COUNCIL DIALOGUE")
        lines.append("")
        lines.append("*Use this section for NotebookLM podcast generation.*")
        lines.append("")

        # Build dynamic dialogue based on current state
        dialogue = []

        # The Architect opens
        dialogue.append("**THE ARCHITECT:** \"The Council convenes. Let's review the current state.\"")

        # AAVE check
        aave = self.brain.get("portfolio", {}).get("aave", {})
        if aave and aave.get("debt", 0) != 0:
            debt = abs(aave.get("debt", 0))
            dialogue.append(f"**THE BANKER:** \"Your debt stands at ${debt:,.2f}. Interest accrues at 4.89% annually. Every day you wait costs you money.\"")
            dialogue.append("**THE HOSTAGE:** \"Meanwhile, I'm locked up generating yield to service that debt. You're welcome.\"")

        # Allocation check
        allocation = self.brain.get("portfolio", {}).get("allocation", {})
        current = allocation.get("current", {})
        if current.get("sol", 0) == 0:
            dialogue.append("**THE GHOST:** \"I'm still at 0% allocation. Your target says 20%. When will you finally buy?\"")

        # Emotion check
        if emotion.lower() in ['fomo', 'revenge', 'greed']:
            dialogue.append(f"**THE MIRROR:** \"{emotion.upper()} detected at intensity {intensity}/10. The Siren is speaking.\"")
            dialogue.append("**THE SIREN:** \"Don't listen to them. This is your chance. Just one trade...\"")
            dialogue.append("**SHADE//AGENT:** \"Trade blocked. The Siren's influence has been detected.\"")
            dialogue.append("**THE ELDER:** \"Patience is not passive. It is concentrated strength. Wait.\"")
        else:
            dialogue.append(f"**THE MIRROR:** \"Emotional state is {emotion}. Intensity {intensity}/10. Acceptable for trading.\"")
            dialogue.append("**THE ELDER:** \"The system works when you use it. Proceed with discipline.\"")

        # Closing
        dialogue.append("**THE ARCHITECT:** \"Council adjourned. Remember: System over emotion. Every single time.\"")

        for line in dialogue:
            lines.append(line)
            lines.append("")

        return lines

    def save_briefing(self, emotion: str = "neutral", intensity: int = 5) -> Path:
        """Generate and save briefing to file"""
        briefing = self.generate_briefing(emotion, intensity)

        # Save to dated file
        date_str = datetime.now().strftime("%Y-%m-%d")
        output_path = PROJECT_ROOT / "daily_reports" / f"council_briefing_{date_str}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(briefing)

        print(f"Briefing saved to: {output_path}")
        return output_path

    def print_briefing(self, emotion: str = "neutral", intensity: int = 5):
        """Generate and print briefing to terminal"""
        briefing = self.generate_briefing(emotion, intensity)
        print(briefing)


def demo():
    """Demo the briefing generator"""
    generator = BriefingGenerator()

    print("\n" + "="*70)
    print("GENERATING COUNCIL BRIEFING WITH LIVE DATA")
    print("="*70 + "\n")

    # Generate with simulated FOMO emotion
    generator.print_briefing(emotion="fomo", intensity=7)

    # Save to file
    print("\n" + "-"*70)
    path = generator.save_briefing(emotion="fomo", intensity=7)
    print(f"\nBriefing saved for NotebookLM upload: {path}")


if __name__ == "__main__":
    demo()
