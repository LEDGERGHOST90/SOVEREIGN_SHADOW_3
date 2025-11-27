#!/usr/bin/env python3
"""
SOVEREIGN SHADOW COUNCIL - Integration Layer
Bridges The Mirror (psychology) with SHADE//AGENT (enforcement)

When you feel an emotion, The Mirror identifies WHO is speaking.
SHADE//AGENT then decides whether to allow or veto the trade.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

# Add project paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "ShadowCouncil"))

from council_loader import CouncilLoader, load_council


class EmotionThreat(Enum):
    """Threat levels for emotional states"""
    CRITICAL = "critical"   # Immediate veto
    HIGH = "high"           # Strong warning, likely veto
    MEDIUM = "medium"       # Warning, proceed with caution
    LOW = "low"             # Acceptable
    CLEAR = "clear"         # Optimal trading state


@dataclass
class MirrorReading:
    """Output from The Mirror's emotion analysis"""
    emotion: str
    intensity: int  # 1-10
    threat_level: EmotionThreat
    character_speaking: Optional[str]
    character_quote: str
    recommendation: str
    veto_advised: bool


@dataclass
class CouncilVerdict:
    """Combined verdict from council members"""
    approved: bool
    primary_speaker: str
    speaking_characters: List[str]
    mirror_reading: MirrorReading
    shade_decision: str
    council_dialogue: List[str]


class TheMirror:
    """
    The Mirror - Psychology Tracker with Council Voice

    "I don't judge. I reflect. You judge yourself."

    Maps emotions to characters, providing insight into
    WHO is influencing your trading decisions.
    """

    # Emotion to character mapping
    EMOTION_CHARACTER_MAP = {
        'revenge': 'xrp_siren',
        'fomo': 'xrp_siren',
        'greed': 'xrp_siren',
        'hope': 'xrp_siren',      # "Hope is not a strategy" - Siren manipulation
        'fear': None,              # Market speaking, not a character
        'anxiety': None,           # Market speaking
        'patience': 'btc_elder',
        'discipline': 'shade_guardian',
        'confidence': 'btc_elder',
        'neutral': None,
    }

    # Threat levels by emotion
    THREAT_LEVELS = {
        'revenge': EmotionThreat.CRITICAL,
        'fomo': EmotionThreat.HIGH,
        'greed': EmotionThreat.HIGH,
        'hope': EmotionThreat.MEDIUM,
        'fear': EmotionThreat.MEDIUM,
        'anxiety': EmotionThreat.MEDIUM,
        'confidence': EmotionThreat.LOW,
        'patience': EmotionThreat.CLEAR,
        'discipline': EmotionThreat.CLEAR,
        'neutral': EmotionThreat.CLEAR,
    }

    def __init__(self):
        self.council = load_council()
        self.trust_score = 85  # The Mirror's trust score

    def analyze_emotion(self, emotion: str, intensity: int, context: Dict = None) -> MirrorReading:
        """
        Analyze an emotion and identify who's speaking.

        Args:
            emotion: The detected emotion (revenge, fomo, greed, etc.)
            intensity: 1-10 scale
            context: Optional context (asset being considered, recent losses, etc.)

        Returns:
            MirrorReading with character identification and recommendation
        """
        emotion_lower = emotion.lower()

        # Get character speaking
        char_name = self.EMOTION_CHARACTER_MAP.get(emotion_lower)
        character = self.council.get_character(char_name) if char_name else None

        # Get threat level (modified by intensity)
        base_threat = self.THREAT_LEVELS.get(emotion_lower, EmotionThreat.MEDIUM)
        threat_level = self._adjust_threat_by_intensity(base_threat, intensity)

        # Generate character quote
        if character:
            quote = self.council.get_catchphrase(char_name)
            speaker = character.name
        else:
            quote = "The market is speaking. Listen."
            speaker = "The Market"

        # Generate recommendation
        recommendation, veto_advised = self._generate_recommendation(
            emotion_lower, intensity, threat_level, speaker
        )

        return MirrorReading(
            emotion=emotion_lower,
            intensity=intensity,
            threat_level=threat_level,
            character_speaking=speaker,
            character_quote=quote,
            recommendation=recommendation,
            veto_advised=veto_advised
        )

    def _adjust_threat_by_intensity(self, base: EmotionThreat, intensity: int) -> EmotionThreat:
        """Adjust threat level based on intensity"""
        if intensity >= 8:
            # High intensity elevates threat
            if base == EmotionThreat.MEDIUM:
                return EmotionThreat.HIGH
            elif base == EmotionThreat.LOW:
                return EmotionThreat.MEDIUM
        elif intensity <= 3:
            # Low intensity reduces threat
            if base == EmotionThreat.HIGH:
                return EmotionThreat.MEDIUM
            elif base == EmotionThreat.MEDIUM:
                return EmotionThreat.LOW
        return base

    def _generate_recommendation(
        self,
        emotion: str,
        intensity: int,
        threat: EmotionThreat,
        speaker: str
    ) -> tuple:
        """Generate recommendation and veto advice"""

        if threat == EmotionThreat.CRITICAL:
            return (
                f"STOP. {speaker} has control. Walk away NOW.",
                True
            )
        elif threat == EmotionThreat.HIGH:
            return (
                f"WARNING: {speaker} is influencing you. Do not trade.",
                True
            )
        elif threat == EmotionThreat.MEDIUM:
            return (
                f"CAUTION: {speaker} detected. Proceed only if setup is perfect.",
                False
            )
        elif threat == EmotionThreat.LOW:
            return (
                f"Acceptable state. {speaker} influence is manageable.",
                False
            )
        else:  # CLEAR
            return (
                "Clear mind. The Elder approves.",
                False
            )

    def format_reading(self, reading: MirrorReading) -> str:
        """Format mirror reading for display"""
        lines = [
            "=" * 60,
            "THE MIRROR - Emotion Analysis",
            "=" * 60,
            f"Detected: {reading.emotion.upper()} (Intensity: {reading.intensity}/10)",
            f"Threat Level: {reading.threat_level.value.upper()}",
            "",
            f"Character Speaking: {reading.character_speaking}",
            f'"{reading.character_quote}"',
            "",
            f"Recommendation: {reading.recommendation}",
            f"Veto Advised: {'YES' if reading.veto_advised else 'No'}",
            "=" * 60
        ]
        return "\n".join(lines)


class ShadeEnforcer:
    """
    SHADE//AGENT with Council Awareness

    "Trade blocked. The system has spoken."

    Enforces rules with character-aware messaging.
    """

    def __init__(self):
        self.council = load_council()
        self.trust_score = 100  # Perfect when obeyed

    def evaluate_with_council(
        self,
        trade: Dict[str, Any],
        mirror_reading: MirrorReading,
        daily_losses: int = 0
    ) -> CouncilVerdict:
        """
        Evaluate trade with full council input.

        Args:
            trade: Trade details (symbol, direction, entry, stop, target)
            mirror_reading: The Mirror's emotion analysis
            daily_losses: Number of losses today

        Returns:
            CouncilVerdict with approval status and council dialogue
        """
        dialogue = []
        speaking_characters = []

        # The Mirror speaks first
        dialogue.append(f"THE MIRROR: {mirror_reading.emotion.upper()} detected. "
                       f"Intensity {mirror_reading.intensity}/10.")

        if mirror_reading.character_speaking:
            dialogue.append(f"THE MIRROR: {mirror_reading.character_speaking} is speaking.")
            speaking_characters.append(mirror_reading.character_speaking)

        # Check 3-strike rule
        if daily_losses >= 3:
            dialogue.append("SHADE//AGENT: 3-strike rule triggered. TRADE BLOCKED.")
            return CouncilVerdict(
                approved=False,
                primary_speaker="SHADE//AGENT",
                speaking_characters=speaking_characters + ["SHADE//AGENT"],
                mirror_reading=mirror_reading,
                shade_decision="BLOCKED: 3-strike rule",
                council_dialogue=dialogue
            )

        # Check emotional veto
        if mirror_reading.veto_advised:
            siren = self.council.get_character('xrp_siren')
            if siren and mirror_reading.character_speaking == siren.name:
                dialogue.append(f"SHADE//AGENT: The Siren is manipulating you. TRADE BLOCKED.")
            else:
                dialogue.append(f"SHADE//AGENT: Emotional state compromised. TRADE BLOCKED.")

            # The Elder weighs in
            elder = self.council.get_character('btc_elder')
            if elder:
                dialogue.append(f"THE ELDER: \"{self.council.get_catchphrase('btc_elder')}\"")
                speaking_characters.append(elder.name)

            return CouncilVerdict(
                approved=False,
                primary_speaker="SHADE//AGENT",
                speaking_characters=speaking_characters + ["SHADE//AGENT"],
                mirror_reading=mirror_reading,
                shade_decision="BLOCKED: Emotional veto",
                council_dialogue=dialogue
            )

        # Check asset character
        asset = trade.get('asset', trade.get('symbol', '')).split('/')[0].upper()
        asset_char = self.council.get_by_asset(asset)

        if asset_char:
            speaking_characters.append(asset_char.name)
            trust = asset_char.trust_score.get('current', 50)

            if trust < 30:
                dialogue.append(f"{asset_char.name.upper()}: \"{self.council.get_catchphrase(asset_char.name.lower().replace(' ', '_'))}\"")
                dialogue.append(f"SHADE//AGENT: {asset_char.name} has low trust ({trust}/100). Extra caution required.")
            else:
                dialogue.append(f"{asset_char.name.upper()}: Trust score {trust}/100.")

        # Check technical requirements (basic)
        has_stop = trade.get('stop') is not None
        has_target = trade.get('target') is not None or trade.get('target_1') is not None

        if not has_stop:
            dialogue.append("SHADE//AGENT: No stop loss defined. TRADE BLOCKED.")
            return CouncilVerdict(
                approved=False,
                primary_speaker="SHADE//AGENT",
                speaking_characters=speaking_characters + ["SHADE//AGENT"],
                mirror_reading=mirror_reading,
                shade_decision="BLOCKED: No stop loss",
                council_dialogue=dialogue
            )

        if not has_target:
            dialogue.append("SHADE//AGENT: No target defined. TRADE BLOCKED.")
            return CouncilVerdict(
                approved=False,
                primary_speaker="SHADE//AGENT",
                speaking_characters=speaking_characters + ["SHADE//AGENT"],
                mirror_reading=mirror_reading,
                shade_decision="BLOCKED: No target",
                council_dialogue=dialogue
            )

        # Trade approved
        dialogue.append("SHADE//AGENT: All checks passed. TRADE APPROVED.")
        dialogue.append("THE ARCHITECT: The system works. Use it.")
        speaking_characters.append("SHADE//AGENT")
        speaking_characters.append("The Architect")

        return CouncilVerdict(
            approved=True,
            primary_speaker="SHADE//AGENT",
            speaking_characters=speaking_characters,
            mirror_reading=mirror_reading,
            shade_decision="APPROVED",
            council_dialogue=dialogue
        )

    def format_verdict(self, verdict: CouncilVerdict) -> str:
        """Format council verdict for display"""
        lines = [
            "",
            "=" * 70,
            "SOVEREIGN SHADOW COUNCIL - VERDICT",
            "=" * 70,
            ""
        ]

        # Council dialogue
        lines.append("COUNCIL PROCEEDINGS:")
        lines.append("-" * 70)
        for line in verdict.council_dialogue:
            lines.append(f"  {line}")

        lines.append("")
        lines.append("-" * 70)
        lines.append(f"FINAL DECISION: {'APPROVED' if verdict.approved else 'BLOCKED'}")
        lines.append(f"Primary Speaker: {verdict.primary_speaker}")
        lines.append(f"Characters Consulted: {', '.join(verdict.speaking_characters)}")
        lines.append("=" * 70)

        return "\n".join(lines)


class CouncilSession:
    """
    Full council session combining Mirror + SHADE

    Usage:
        session = CouncilSession()
        verdict = session.evaluate_trade(
            emotion="fomo",
            intensity=7,
            trade={'asset': 'XRP', 'stop': 2.10, 'target': 2.50},
            daily_losses=1
        )
    """

    def __init__(self):
        self.mirror = TheMirror()
        self.shade = ShadeEnforcer()
        self.council = load_council()

    def evaluate_trade(
        self,
        emotion: str,
        intensity: int,
        trade: Dict[str, Any],
        daily_losses: int = 0
    ) -> CouncilVerdict:
        """
        Full council evaluation of a trade.

        Args:
            emotion: Current emotional state
            intensity: Emotion intensity (1-10)
            trade: Trade details
            daily_losses: Number of losses today

        Returns:
            CouncilVerdict
        """
        # Step 1: Mirror analyzes emotion
        mirror_reading = self.mirror.analyze_emotion(emotion, intensity)

        # Step 2: SHADE evaluates with council input
        verdict = self.shade.evaluate_with_council(trade, mirror_reading, daily_losses)

        return verdict

    def quick_check(self, emotion: str, intensity: int) -> MirrorReading:
        """Quick emotion check without full trade evaluation"""
        return self.mirror.analyze_emotion(emotion, intensity)

    def print_full_evaluation(
        self,
        emotion: str,
        intensity: int,
        trade: Dict[str, Any],
        daily_losses: int = 0
    ):
        """Print formatted full evaluation"""
        # Mirror reading
        reading = self.mirror.analyze_emotion(emotion, intensity)
        print(self.mirror.format_reading(reading))

        # Full verdict
        verdict = self.shade.evaluate_with_council(trade, reading, daily_losses)
        print(self.shade.format_verdict(verdict))


def demo():
    """Demo the integrated council system"""
    session = CouncilSession()

    print("\n" + "=" * 70)
    print("SOVEREIGN SHADOW COUNCIL - INTEGRATION DEMO")
    print("=" * 70)

    # Scenario 1: FOMO on XRP
    print("\n SCENARIO 1: User wants to buy XRP during FOMO")
    print("-" * 70)

    session.print_full_evaluation(
        emotion="fomo",
        intensity=8,
        trade={
            'asset': 'XRP',
            'direction': 'LONG',
            'entry': 2.30,
            'stop': 2.10,
            'target': 2.80
        },
        daily_losses=0
    )

    # Scenario 2: Disciplined BTC trade
    print("\n SCENARIO 2: Disciplined BTC trade")
    print("-" * 70)

    session.print_full_evaluation(
        emotion="patience",
        intensity=4,
        trade={
            'asset': 'BTC',
            'direction': 'LONG',
            'entry': 97000,
            'stop': 95000,
            'target': 103000
        },
        daily_losses=0
    )

    # Scenario 3: Revenge trading after losses
    print("\n SCENARIO 3: Revenge trading after 2 losses")
    print("-" * 70)

    session.print_full_evaluation(
        emotion="revenge",
        intensity=9,
        trade={
            'asset': 'SOL',
            'direction': 'LONG',
            'entry': 145,
            'stop': 140,
            'target': 160
        },
        daily_losses=2
    )


if __name__ == "__main__":
    demo()
