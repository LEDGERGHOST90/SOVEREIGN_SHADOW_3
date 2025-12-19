#!/usr/bin/env python3
"""
Research Swarm - Multi-AI Collaboration System
Coordinates Manus, Gemini/GIO, and DS-Star for unified research output

Each AI performs independent analysis, then results are synthesized into
one authoritative source. All results pushed to Replit for persistence.
"""

import os
import json
import asyncio
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / '.env', override=True)

# Import AI clients
from core.integrations.manus_client import ManusClient

# Gemini
import google.generativeai as genai

@dataclass
class ResearchResult:
    """Standardized research result from any AI"""
    source: str  # 'manus', 'gemini', 'ds_star'
    query: str
    analysis: str
    confidence: float  # 0-100
    sources_cited: List[str]
    scholarly_refs: List[str]
    timestamp: str
    raw_response: Dict = None


class GeminiResearcher:
    """Gemini/GIO - The Researcher"""

    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def research(self, query: str, context: str = "") -> ResearchResult:
        """Perform research with scholarly focus"""
        prompt = f"""You are GIO, the Research AI for SOVEREIGN SHADOW III trading system.

RESEARCH QUERY: {query}

CONTEXT: {context}

INSTRUCTIONS:
1. Provide thorough, scholarly analysis
2. Cite academic papers, research, and authoritative sources where possible
3. Include quantitative data and specific numbers
4. Be objective and evidence-based
5. Acknowledge uncertainty where it exists

FORMAT YOUR RESPONSE AS:

## Analysis
[Your detailed analysis]

## Key Findings
- [Finding 1]
- [Finding 2]
- [Finding 3]

## Scholarly References
- [Paper/Study 1]
- [Paper/Study 2]

## Data Sources
- [Source 1]
- [Source 2]

## Confidence Level
[0-100]% - [Brief justification]

## Recommendations
[Actionable recommendations based on analysis]
"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text

            # Extract confidence (simple parsing)
            confidence = 70.0  # default
            if "Confidence Level" in text:
                try:
                    conf_line = [l for l in text.split('\n') if 'Confidence' in l and '%' in l][0]
                    confidence = float(conf_line.split('%')[0].split()[-1])
                except:
                    pass

            # Extract scholarly refs
            scholarly = []
            if "Scholarly References" in text:
                in_refs = False
                for line in text.split('\n'):
                    if "Scholarly References" in line:
                        in_refs = True
                        continue
                    if in_refs and line.startswith('- '):
                        scholarly.append(line[2:].strip())
                    elif in_refs and line.startswith('##'):
                        break

            return ResearchResult(
                source='gemini',
                query=query,
                analysis=text,
                confidence=confidence,
                sources_cited=[],
                scholarly_refs=scholarly,
                timestamp=datetime.now().isoformat(),
                raw_response={'text': text}
            )
        except Exception as e:
            return ResearchResult(
                source='gemini',
                query=query,
                analysis=f"Error: {str(e)}",
                confidence=0,
                sources_cited=[],
                scholarly_refs=[],
                timestamp=datetime.now().isoformat()
            )


class DSStarAnalyzer:
    """DS-Star - Decision Support System"""

    def __init__(self):
        self.ds_star_path = Path("/Volumes/LegacySafe/SS_III/ds_star")
        self.synoptic_core = None

        # Try to initialize Synoptic Core
        try:
            import sys
            sys.path.insert(0, str(self.ds_star_path.parent))
            from ds_star.synoptic_core.core import SynopticCore
            self.synoptic_core = SynopticCore()
        except Exception as e:
            print(f"DS-Star SynopticCore init: {e}")

    def analyze(self, query: str, asset: str = None) -> ResearchResult:
        """Use DS-Star modules for analysis"""
        results = []
        confidence = 50.0
        signals = []

        # Use Synoptic Core for asset assessment
        if asset and self.synoptic_core:
            try:
                assessment = self.synoptic_core.assess(asset)
                results.append(f"## Synoptic Core Assessment: {asset}")
                results.append(f"**Smart Asset Score:** {assessment.smart_asset_score}/100")
                results.append(f"**Dominant Driver:** {assessment.dominant_driver}")
                results.append(f"**Thesis:** {assessment.thesis}")
                results.append(f"\n**Risks:**")
                for risk in assessment.risks:
                    results.append(f"- {risk}")
                results.append(f"\n**Supporting Signals:**")
                for category, sigs in assessment.supporting_signals.items():
                    results.append(f"*{category.upper()}:*")
                    for sig in sigs:
                        results.append(f"  - {sig}")
                        signals.append(sig)

                confidence = float(assessment.smart_asset_score)
            except Exception as e:
                results.append(f"Synoptic Core error: {e}")
        elif not asset:
            results.append("No asset specified for DS-Star analysis")
        else:
            results.append("Synoptic Core not initialized")

        analysis = "\n".join(results) if results else "DS-Star analysis unavailable"

        return ResearchResult(
            source='ds_star',
            query=query,
            analysis=analysis,
            confidence=confidence,
            sources_cited=['DS-Star Synoptic Core', 'Local Technical Analysis'],
            scholarly_refs=[],
            timestamp=datetime.now().isoformat()
        )


class ResearchSwarm:
    """
    Coordinates all three AIs for unified research

    Flow:
    1. Dispatch query to all three AIs in parallel
    2. Collect independent analyses
    3. Synthesize into unified report
    4. Push to Replit for persistence
    """

    def __init__(self):
        self.manus = ManusClient()
        self.gemini = GeminiResearcher()
        self.ds_star = DSStarAnalyzer()
        self.replit_url = os.getenv('REPLIT_API_URL')

    def research(
        self,
        query: str,
        context: str = "",
        asset: str = None,
        require_scholarly: bool = True
    ) -> Dict[str, Any]:
        """
        Execute multi-AI research

        Args:
            query: Research question
            context: Additional context (SS_III state, portfolio, etc.)
            asset: Specific asset being analyzed (BTC, ETH, etc.)
            require_scholarly: Enforce academic/scholarly sources

        Returns:
            Unified research report with all sources
        """
        print(f"\n{'='*70}")
        print("RESEARCH SWARM - Multi-AI Collaboration")
        print(f"{'='*70}")
        print(f"Query: {query}")
        print(f"Asset: {asset or 'General'}")
        print(f"{'='*70}\n")

        results = {}

        # 1. Dispatch to Manus (async task - will complete later)
        print("[1/3] Dispatching to MANUS (Deep Research)...")
        manus_prompt = f"""RESEARCH SWARM TASK - Deep Analysis Required

QUERY: {query}

CONTEXT: {context}

REQUIREMENTS:
1. Perform comprehensive web research
2. Find and cite scholarly/academic sources (papers, studies, research)
3. Include quantitative data with specific numbers
4. Verify claims against multiple sources
5. Be thorough - this feeds into a trading decision system

FOCUS AREAS:
- Academic research and papers
- On-chain data and analytics
- Market microstructure
- Historical precedents
- Risk factors

Provide a detailed, evidence-based analysis with full source citations.
"""
        try:
            manus_task = self.manus.create_task(
                prompt=manus_prompt,
                agent_profile='manus-1.6-max',
                task_mode='agent'
            )
            results['manus'] = {
                'status': 'dispatched',
                'task_id': manus_task.get('task_id'),
                'url': manus_task.get('task_url')
            }
            print(f"   ✓ Manus task created: {manus_task.get('task_id')}")
        except Exception as e:
            results['manus'] = {'status': 'error', 'error': str(e)}
            print(f"   ✗ Manus error: {e}")

        # 2. Query Gemini (synchronous)
        print("\n[2/3] Querying GEMINI/GIO (Research Analysis)...")
        try:
            gemini_result = self.gemini.research(query, context)
            results['gemini'] = asdict(gemini_result)
            print(f"   ✓ Gemini complete (confidence: {gemini_result.confidence}%)")
            print(f"   Scholarly refs: {len(gemini_result.scholarly_refs)}")
        except Exception as e:
            results['gemini'] = {'status': 'error', 'error': str(e)}
            print(f"   ✗ Gemini error: {e}")

        # 3. Query DS-Star (local)
        print("\n[3/3] Analyzing with DS-STAR (Decision Support)...")
        try:
            ds_result = self.ds_star.analyze(query, asset)
            results['ds_star'] = asdict(ds_result)
            print(f"   ✓ DS-Star complete")
        except Exception as e:
            results['ds_star'] = {'status': 'error', 'error': str(e)}
            print(f"   ✗ DS-Star error: {e}")

        # 4. Create unified report
        print("\n[SYNTHESIS] Creating unified report...")
        unified = self._synthesize(query, results)

        # 5. Push to Replit
        print("\n[PUSH] Sending to Replit...")
        self._push_to_replit(unified)

        return unified

    def _synthesize(self, query: str, results: Dict) -> Dict[str, Any]:
        """Synthesize multiple AI results into unified report"""

        unified = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'sources': {},
            'synthesis': {
                'consensus': None,
                'confidence': 0,
                'key_findings': [],
                'scholarly_refs': [],
                'recommendations': []
            },
            'raw_results': results
        }

        # Collect all scholarly refs
        all_refs = []
        all_findings = []
        confidence_scores = []

        # Process Gemini result
        if 'gemini' in results and results['gemini'].get('analysis'):
            gemini = results['gemini']
            unified['sources']['gemini'] = {
                'status': 'complete',
                'confidence': gemini.get('confidence', 0)
            }
            all_refs.extend(gemini.get('scholarly_refs', []))
            confidence_scores.append(gemini.get('confidence', 0))

        # Process Manus (may be async)
        if 'manus' in results:
            manus = results['manus']
            if manus.get('status') == 'dispatched':
                unified['sources']['manus'] = {
                    'status': 'pending',
                    'task_id': manus.get('task_id'),
                    'url': manus.get('url')
                }
            elif manus.get('analysis'):
                unified['sources']['manus'] = {
                    'status': 'complete',
                    'confidence': manus.get('confidence', 0)
                }

        # Process DS-Star
        if 'ds_star' in results and results['ds_star'].get('analysis'):
            unified['sources']['ds_star'] = {
                'status': 'complete',
                'analysis': results['ds_star'].get('analysis')
            }

        # Calculate average confidence
        if confidence_scores:
            unified['synthesis']['confidence'] = sum(confidence_scores) / len(confidence_scores)

        # Deduplicate scholarly refs
        unified['synthesis']['scholarly_refs'] = list(set(all_refs))

        return unified

    def _push_to_replit(self, data: Dict) -> bool:
        """Push unified results to Replit"""
        if not self.replit_url:
            print("   ✗ REPLIT_API_URL not set")
            return False

        try:
            # Push to research endpoint
            endpoint = f"{self.replit_url}/api/research"
            response = requests.post(
                endpoint,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            if response.status_code == 200:
                print(f"   ✓ Pushed to Replit: {endpoint}")
                return True
            else:
                print(f"   ⚠ Replit returned {response.status_code}")
                # Try generic webhook
                webhook = f"{self.replit_url}/api/manus-webhook"
                response = requests.post(
                    webhook,
                    json={
                        'event': 'research.completed',
                        'data': data
                    },
                    timeout=10
                )
                print(f"   → Fallback to webhook: {response.status_code}")
                return response.status_code == 200

        except Exception as e:
            print(f"   ✗ Replit push failed: {e}")
            return False

    def poll_manus(self, task_id: str) -> Optional[ResearchResult]:
        """Poll Manus for completed task results"""
        try:
            result = self.manus.get_task(task_id)
            if result.get('status') == 'completed':
                # Extract analysis from output
                output = result.get('output', [])
                analysis = ""
                for msg in output:
                    if msg.get('role') == 'assistant':
                        for content in msg.get('content', []):
                            if content.get('type') == 'output_text':
                                analysis += content.get('text', '')

                return ResearchResult(
                    source='manus',
                    query='',
                    analysis=analysis,
                    confidence=85.0,  # Manus with web access gets high confidence
                    sources_cited=[],
                    scholarly_refs=[],  # Would need to parse from analysis
                    timestamp=datetime.now().isoformat(),
                    raw_response=result
                )
            return None
        except Exception as e:
            print(f"Error polling Manus: {e}")
            return None


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def quick_research(query: str, asset: str = None) -> Dict:
    """Quick research query to all AIs"""
    swarm = ResearchSwarm()
    return swarm.research(query, asset=asset)


def deep_dive(asset: str) -> Dict:
    """Deep dive analysis on specific asset"""
    swarm = ResearchSwarm()

    context = f"""
    SOVEREIGN SHADOW III Trading System
    Portfolio: $4,972 net worth
    Trading Capital: $734
    Current Holdings: BTC, wstETH (AAVE), XRP
    Mission: Generate $662 profit to repay AAVE debt
    """

    query = f"""
    Perform comprehensive analysis of {asset}:

    1. TECHNICAL ANALYSIS
       - Multi-timeframe trend analysis
       - Key support/resistance levels
       - Chart patterns and indicators

    2. FUNDAMENTAL ANALYSIS
       - Recent developments and news
       - On-chain metrics (if crypto)
       - Macro factors affecting price

    3. SENTIMENT ANALYSIS
       - Social media sentiment
       - Institutional positioning
       - Retail vs whale behavior

    4. SCHOLARLY RESEARCH
       - Academic papers on {asset} or related assets
       - Market microstructure research
       - Behavioral finance insights

    5. TRADING RECOMMENDATION
       - Entry/exit levels
       - Position sizing for $734 capital
       - Risk/reward analysis
    """

    return swarm.research(query, context=context, asset=asset)


if __name__ == '__main__':
    print("Research Swarm - Multi-AI Collaboration System")
    print("=" * 70)

    # Test with a simple query
    result = quick_research(
        "What is the current market regime for Bitcoin and what trading strategies are optimal?",
        asset="BTC"
    )

    print("\n" + "=" * 70)
    print("UNIFIED RESULT:")
    print(json.dumps(result, indent=2, default=str)[:2000])
