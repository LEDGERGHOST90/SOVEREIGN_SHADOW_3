"""
SS_III Voice Research Ingest Module

Pipeline: WealthWhisperer -> fetch_voice_research.py -> voice_to_brain.py -> BRAIN.json -> Agents

Usage:
    from ingest import fetch_voice_research, voice_to_brain

    # Fetch new research
    fetch_voice_research.ingest_all()

    # Extract signals
    voice_to_brain.process_research_feed()

    # Get actionable signals for agents
    signals = voice_to_brain.get_actionable_signals(min_confidence=0.6)
"""

from . import fetch_voice_research
from . import voice_to_brain

__all__ = ["fetch_voice_research", "voice_to_brain"]
