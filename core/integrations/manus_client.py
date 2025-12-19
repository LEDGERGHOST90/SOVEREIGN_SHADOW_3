#!/usr/bin/env python3
"""
Manus AI Client - Autonomous Agent Integration
Connects SOVEREIGN SHADOW III to Manus AI for strategy analysis and task execution

API Reference: https://open.manus.ai/docs
"""

import os
import json
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

# Load environment
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / '.env')


class ManusClient:
    """Client for Manus AI API integration"""

    BASE_URL = os.getenv('MANUS_API_URL', 'https://api.manus.ai/v1')

    # Agent profiles
    PROFILE_STANDARD = 'manus-1.6'
    PROFILE_LITE = 'manus-1.6-lite'
    PROFILE_MAX = 'manus-1.6-max'

    # Task modes
    MODE_CHAT = 'chat'
    MODE_ADAPTIVE = 'adaptive'
    MODE_AGENT = 'agent'

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('MANUS_API_KEY')
        if not self.api_key:
            raise ValueError("MANUS_API_KEY not found. Set in .env or pass to constructor.")

        self.session = requests.Session()
        self.session.headers.update({
            'API_KEY': self.api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    # =========================================================================
    # TASK MANAGEMENT
    # =========================================================================

    def create_task(
        self,
        prompt: str,
        agent_profile: str = PROFILE_STANDARD,
        task_mode: str = MODE_AGENT,
        attachments: List[Dict] = None,
        project_id: str = None,
        connectors: List[str] = None,
        create_shareable_link: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new Manus AI task

        Args:
            prompt: Task instructions for Manus
            agent_profile: 'manus-1.6', 'manus-1.6-lite', or 'manus-1.6-max'
            task_mode: 'chat', 'adaptive', or 'agent'
            attachments: List of file attachments
            project_id: Associate with a project
            connectors: List of connector IDs to enable
            create_shareable_link: Make task publicly accessible

        Returns:
            {
                'task_id': str,
                'task_title': str,
                'task_url': str,
                'share_url': str (if shareable)
            }
        """
        payload = {
            'prompt': prompt,
            'agentProfile': agent_profile,
            'taskMode': task_mode
        }

        if attachments:
            payload['attachments'] = attachments
        if project_id:
            payload['projectId'] = project_id
        if connectors:
            payload['connectors'] = connectors
        if create_shareable_link:
            payload['createShareableLink'] = True

        response = self.session.post(f'{self.BASE_URL}/tasks', json=payload)
        response.raise_for_status()
        return response.json()

    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get task details by ID"""
        response = self.session.get(f'{self.BASE_URL}/tasks/{task_id}')
        response.raise_for_status()
        return response.json()

    def list_tasks(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List recent tasks"""
        params = {'limit': limit, 'offset': offset}
        response = self.session.get(f'{self.BASE_URL}/tasks', params=params)
        response.raise_for_status()
        return response.json()

    def continue_task(self, task_id: str, prompt: str) -> Dict[str, Any]:
        """Continue a multi-turn conversation task"""
        payload = {
            'prompt': prompt,
            'taskId': task_id
        }
        response = self.session.post(f'{self.BASE_URL}/tasks', json=payload)
        response.raise_for_status()
        return response.json()

    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID"""
        response = self.session.delete(f'{self.BASE_URL}/tasks/{task_id}')
        return response.status_code == 200

    # =========================================================================
    # FILE MANAGEMENT
    # =========================================================================

    def upload_file(self, filename: str, file_path: str) -> Dict[str, Any]:
        """
        Create file record and get presigned URL for upload

        Returns:
            {
                'file_id': str,
                'upload_url': str,
                'filename': str
            }
        """
        payload = {'filename': filename}
        response = self.session.post(f'{self.BASE_URL}/files', json=payload)
        response.raise_for_status()
        result = response.json()

        # Upload to S3 if we have a file
        if file_path and 'upload_url' in result:
            with open(file_path, 'rb') as f:
                upload_response = requests.put(
                    result['upload_url'],
                    data=f.read(),
                    headers={'Content-Type': 'application/octet-stream'}
                )
                upload_response.raise_for_status()

        return result

    def list_files(self) -> List[Dict[str, Any]]:
        """List recent files (last 10)"""
        response = self.session.get(f'{self.BASE_URL}/files')
        response.raise_for_status()
        return response.json()

    # =========================================================================
    # PROJECT MANAGEMENT
    # =========================================================================

    def create_project(self, name: str, instructions: str = None) -> Dict[str, Any]:
        """Create a project to organize tasks"""
        payload = {'name': name}
        if instructions:
            payload['instructions'] = instructions
        response = self.session.post(f'{self.BASE_URL}/projects', json=payload)
        response.raise_for_status()
        return response.json()

    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects"""
        response = self.session.get(f'{self.BASE_URL}/projects')
        response.raise_for_status()
        return response.json()

    # =========================================================================
    # WEBHOOKS
    # =========================================================================

    def create_webhook(self, url: str, events: List[str] = None) -> Dict[str, Any]:
        """Register a webhook for task events"""
        payload = {'url': url}
        if events:
            payload['events'] = events
        response = self.session.post(f'{self.BASE_URL}/webhooks', json=payload)
        response.raise_for_status()
        return response.json()

    def delete_webhook(self, webhook_id: str) -> bool:
        """Remove a webhook"""
        response = self.session.delete(f'{self.BASE_URL}/webhooks/{webhook_id}')
        return response.status_code == 200

    # =========================================================================
    # SOVEREIGN SHADOW INTEGRATION HELPERS
    # =========================================================================

    def analyze_strategy(self, strategy_code: str, strategy_name: str = None) -> Dict[str, Any]:
        """
        Send a strategy to Manus for analysis
        Uses the 451-strategy framework context
        """
        prompt = f"""Analyze this trading strategy and provide:
1. Strategy type classification (Trend Following, Mean Reversion, Breakout, Volatility, Arbitrage)
2. Risk score (0-100)
3. Identified weaknesses
4. Improvement recommendations
5. Optimal market regime (Trending, Range-bound, High Volatility, Low Volatility)

Strategy Name: {strategy_name or 'Unknown'}

```python
{strategy_code}
```

Return analysis as structured JSON."""

        return self.create_task(
            prompt=prompt,
            agent_profile=self.PROFILE_MAX,
            task_mode=self.MODE_AGENT
        )

    def get_trade_recommendation(
        self,
        symbol: str,
        portfolio_value: float,
        current_positions: Dict,
        market_regime: str
    ) -> Dict[str, Any]:
        """
        Get Manus AI trade recommendation

        Args:
            symbol: Trading pair (e.g., 'BTC-USD')
            portfolio_value: Total portfolio value
            current_positions: Current holdings
            market_regime: From RegimeAgent ('VOLATILE', 'TRENDING', etc.)
        """
        prompt = f"""As a trading analyst, evaluate this trade opportunity:

Symbol: {symbol}
Portfolio Value: ${portfolio_value:,.2f}
Current Positions: {json.dumps(current_positions, indent=2)}
Market Regime: {market_regime}

Provide:
1. Recommendation (BUY/SELL/HOLD)
2. Confidence score (0-100)
3. Suggested position size as % of portfolio
4. Stop loss level
5. Take profit target
6. Key reasoning (3-5 bullet points)

Use conservative risk management (max 2% portfolio risk per trade)."""

        return self.create_task(
            prompt=prompt,
            agent_profile=self.PROFILE_STANDARD,
            task_mode=self.MODE_AGENT
        )

    def research_market(self, query: str) -> Dict[str, Any]:
        """
        Use Manus for market research with web access

        Args:
            query: Research question (e.g., "What's driving BTC price today?")
        """
        return self.create_task(
            prompt=f"Research and summarize: {query}\n\nProvide sources and key data points.",
            agent_profile=self.PROFILE_STANDARD,
            task_mode=self.MODE_AGENT
        )

    def batch_analyze_strategies(self, strategy_files: List[str]) -> Dict[str, Any]:
        """
        Send multiple strategies for batch analysis

        Args:
            strategy_files: List of strategy file paths
        """
        strategies_text = []
        for path in strategy_files[:10]:  # Limit to 10
            try:
                with open(path, 'r') as f:
                    name = Path(path).stem
                    strategies_text.append(f"### {name}\n```python\n{f.read()}\n```")
            except Exception as e:
                strategies_text.append(f"### {path}\nError reading: {e}")

        prompt = f"""Analyze these {len(strategies_text)} trading strategies.

For each strategy, provide:
1. Type classification
2. Strengths
3. Weaknesses
4. Score (0-100)
5. Recommended improvements

{chr(10).join(strategies_text)}

Return as structured JSON array."""

        return self.create_task(
            prompt=prompt,
            agent_profile=self.PROFILE_MAX,
            task_mode=self.MODE_AGENT
        )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def test_connection() -> bool:
    """Test Manus API connection"""
    try:
        client = ManusClient()
        result = client.create_task(
            prompt="Return 'MANUS_OK' to confirm connection.",
            agent_profile=ManusClient.PROFILE_LITE,
            task_mode=ManusClient.MODE_CHAT
        )
        print(f"Manus connection OK: task_id={result.get('task_id')}")
        return True
    except Exception as e:
        print(f"Manus connection FAILED: {e}")
        return False


if __name__ == '__main__':
    # Test the client
    print("Testing Manus AI Client...")

    api_key = os.getenv('MANUS_API_KEY')
    if not api_key:
        print("ERROR: MANUS_API_KEY not set in .env")
        print("Get your key from: https://manus.im/app?show_settings=integrations&app_name=api")
    else:
        test_connection()
