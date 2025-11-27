#!/usr/bin/env python3
"""
SOVEREIGN SHADOW COUNCIL - Character Loader
Loads character profiles from YAML files for use by SHADE//AGENT and other systems.

Trust Score Priority:
1. BRAIN.json (dynamic, updated by trades)
2. YAML files (baseline defaults)
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

COUNCIL_ROOT = Path(__file__).parent
PROJECT_ROOT = COUNCIL_ROOT.parent
BRAIN_PATH = PROJECT_ROOT / "BRAIN.json"


@dataclass
class Character:
    """Represents a council character."""
    name: str
    archetype: str
    personality: Dict
    trust_score: Dict
    quotes: Dict
    raw_data: Dict


class CouncilLoader:
    """Loads and manages council characters."""

    def __init__(self, council_path: Optional[Path] = None):
        self.council_path = council_path or COUNCIL_ROOT
        self.assets: Dict[str, Character] = {}
        self.guardians: Dict[str, Character] = {}
        self.platforms: Dict[str, Character] = {}
        self._loaded = False
        self._brain_trust_scores = self._load_brain_trust_scores()

    def _load_brain_trust_scores(self) -> Dict:
        """Load dynamic trust scores from BRAIN.json"""
        try:
            if BRAIN_PATH.exists():
                with open(BRAIN_PATH) as f:
                    brain = json.load(f)
                return brain.get('projects', {}).get('shadow_council', {}).get('trust_scores', {})
        except Exception:
            pass
        return {}

    def load_all(self) -> None:
        """Load all character files."""
        self._load_category('assets', self.assets)
        self._load_category('guardians', self.guardians)
        self._load_category('platforms', self.platforms)
        self._apply_brain_trust_scores()
        self._loaded = True
        print(f"Council loaded: {len(self.assets)} assets, {len(self.guardians)} guardians, {len(self.platforms)} platforms")

    def _apply_brain_trust_scores(self) -> None:
        """Apply trust scores from BRAIN.json (overrides YAML defaults)"""
        for storage in [self.assets, self.guardians, self.platforms]:
            for name, char in storage.items():
                if name in self._brain_trust_scores:
                    brain_score = self._brain_trust_scores[name]
                    if isinstance(brain_score, dict):
                        char.trust_score['current'] = brain_score.get('current', char.trust_score.get('current', 50))
                        char.trust_score['baseline'] = brain_score.get('baseline', char.trust_score.get('current', 50))
                        char.trust_score['reason'] = brain_score.get('reason', '')
                    else:
                        char.trust_score['current'] = brain_score

    def _load_category(self, category: str, storage: Dict) -> None:
        """Load all characters in a category."""
        category_path = self.council_path / 'characters' / category
        if not category_path.exists():
            print(f"Warning: {category_path} does not exist")
            return

        for yaml_file in category_path.glob('*.yaml'):
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)

                char = Character(
                    name=data.get('name', yaml_file.stem),
                    archetype=data.get('archetype', 'Unknown'),
                    personality=data.get('personality', {}),
                    trust_score=data.get('trust_score', {}),
                    quotes=data.get('quotes', {}),
                    raw_data=data
                )
                storage[yaml_file.stem] = char
            except Exception as e:
                print(f"Error loading {yaml_file}: {e}")

    def get_character(self, name: str) -> Optional[Character]:
        """Get a character by filename (without .yaml)."""
        for storage in [self.assets, self.guardians, self.platforms]:
            if name in storage:
                return storage[name]
        return None

    def get_by_asset(self, asset_symbol: str) -> Optional[Character]:
        """Get character by asset symbol (BTC, ETH, etc.)."""
        symbol_map = {
            'BTC': 'btc_elder',
            'XRP': 'xrp_siren',
            'ETH': 'eth_hostage',
            'SOL': 'sol_ghost',
            'AAVE': 'aave_banker',
        }
        char_name = symbol_map.get(asset_symbol.upper())
        return self.get_character(char_name) if char_name else None

    def get_speaking_character(self, emotion: str) -> Optional[Character]:
        """
        Determine which character is 'speaking' based on emotion state.
        Used by The Mirror to map emotions to character influences.
        """
        emotion_map = {
            'REVENGE': 'xrp_siren',
            'FOMO': 'xrp_siren',
            'GREED': 'xrp_siren',
            'FEAR': None,  # Market speaking, not a character
            'PATIENCE': 'btc_elder',
            'DISCIPLINE': 'shade_guardian',
        }
        char_name = emotion_map.get(emotion.upper())
        return self.get_character(char_name) if char_name else None

    def get_trust_score(self, character_name: str) -> int:
        """Get trust score for a character."""
        char = self.get_character(character_name)
        if char and char.trust_score:
            return char.trust_score.get('current', 50)
        return 50  # Default neutral score

    def update_trust_score(self, character_name: str, change: int, reason: str = "") -> int:
        """
        Update a character's trust score and save to BRAIN.json.

        Args:
            character_name: Character key (e.g., 'btc_elder', 'xrp_siren')
            change: Points to add (positive) or remove (negative)
            reason: Reason for the change

        Returns:
            New trust score
        """
        # Update in-memory
        char = self.get_character(character_name)
        if not char:
            return 50

        old_score = char.trust_score.get('current', 50)
        new_score = max(0, min(100, old_score + change))  # Clamp 0-100
        char.trust_score['current'] = new_score

        # Update BRAIN.json
        try:
            with open(BRAIN_PATH) as f:
                brain = json.load(f)

            trust_scores = brain.get('projects', {}).get('shadow_council', {}).get('trust_scores', {})

            if character_name not in trust_scores:
                trust_scores[character_name] = {'current': new_score, 'baseline': old_score}
            else:
                if isinstance(trust_scores[character_name], dict):
                    trust_scores[character_name]['current'] = new_score
                    if reason:
                        trust_scores[character_name]['reason'] = reason
                else:
                    trust_scores[character_name] = {'current': new_score, 'baseline': trust_scores[character_name]}

            brain['projects']['shadow_council']['trust_scores'] = trust_scores

            with open(BRAIN_PATH, 'w') as f:
                json.dump(brain, f, indent=2)

        except Exception as e:
            print(f"Warning: Could not save trust score to BRAIN.json: {e}")

        return new_score

    def get_catchphrase(self, character_name: str) -> str:
        """Get a random catchphrase from a character."""
        import random
        char = self.get_character(character_name)
        if char and char.personality:
            phrases = char.personality.get('catchphrases', [])
            if phrases:
                return random.choice(phrases)
        return ""

    def format_council_status(self) -> str:
        """Format current council status for display."""
        if not self._loaded:
            self.load_all()

        lines = ["=" * 50]
        lines.append("SOVEREIGN SHADOW COUNCIL STATUS")
        lines.append("=" * 50)

        lines.append("\n📊 ASSETS:")
        for name, char in self.assets.items():
            trust = char.trust_score.get('current', '?')
            lines.append(f"  {char.name}: Trust {trust}/100")

        lines.append("\n🛡️ GUARDIANS:")
        for name, char in self.guardians.items():
            trust = char.trust_score.get('current', '?')
            lines.append(f"  {char.name}: Trust {trust}/100")

        lines.append("\n🏛️ PLATFORMS:")
        for name, char in self.platforms.items():
            trust = char.trust_score.get('current', '?')
            lines.append(f"  {char.name}: Trust {trust}/100")

        return "\n".join(lines)

    def who_is_speaking(self, trade_context: Dict) -> List[str]:
        """
        Analyze a trade context and determine which characters are influencing.

        Args:
            trade_context: Dict with keys like 'asset', 'emotion', 'action'

        Returns:
            List of character names that are 'speaking'
        """
        speakers = []

        # Check asset
        if 'asset' in trade_context:
            asset_char = self.get_by_asset(trade_context['asset'])
            if asset_char:
                speakers.append(asset_char.name)

        # Check emotion
        if 'emotion' in trade_context:
            emotion_char = self.get_speaking_character(trade_context['emotion'])
            if emotion_char:
                speakers.append(emotion_char.name)

        return speakers


# Convenience function
def load_council() -> CouncilLoader:
    """Load and return the council."""
    loader = CouncilLoader()
    loader.load_all()
    return loader


if __name__ == '__main__':
    # Demo usage
    council = load_council()
    print(council.format_council_status())

    print("\n" + "=" * 50)
    print("DEMO: Who's speaking?")
    print("=" * 50)

    # Simulate trade context
    context = {'asset': 'XRP', 'emotion': 'FOMO'}
    speakers = council.who_is_speaking(context)
    print(f"Trade: Buy XRP during FOMO")
    print(f"Characters speaking: {speakers}")

    siren = council.get_character('xrp_siren')
    if siren:
        print(f"\nThe Siren says: '{council.get_catchphrase('xrp_siren')}'")
