"""
Core Integrations Package

External service integrations:
- manus_client: Manus AI API
- research_swarm: Multi-AI research coordination
- live_data_pipeline: Real-time market data
- exchange_consensus: Multi-exchange price consensus
"""

from .manus_client import ManusClient
from .research_swarm import ResearchSwarm

__all__ = [
    'ManusClient',
    'ResearchSwarm'
]
