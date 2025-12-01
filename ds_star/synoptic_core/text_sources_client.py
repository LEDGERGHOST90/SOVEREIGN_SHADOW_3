#!/usr/bin/env python3
"""
Text Sources Client for Synoptic Core
Provides fundamental data and sentiment analysis from text sources
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path


class TextSourcesClient:
    """
    Aggregates text-based data sources:
    - Fundamental data (dev activity, tokenomics)
    - Sentiment analysis (news, social media)
    - Document retrieval (whitepapers, updates)
    """

    def __init__(self):
        # API keys
        self.coingecko_key = os.getenv("COINGECKO_API_KEY", "")

        # Local document store
        self.docs_dir = Path(__file__).parent.parent.parent / "docs" / "assets"
        self.docs_dir.mkdir(parents=True, exist_ok=True)

        # CoinGecko ID mapping
        self.cg_ids = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana",
            "XRP": "ripple",
            "AAVE": "aave",
            "LINK": "chainlink",
            "UNI": "uniswap",
            "ARB": "arbitrum",
            "OP": "optimism"
        }

    def get_fundamentals(self, asset: str) -> Dict[str, Any]:
        """
        Get fundamental data for an asset

        Args:
            asset: Asset symbol

        Returns:
            Dict with fundamental metrics
        """
        # Try CoinGecko for basic data
        cg_data = self._get_coingecko_data(asset)

        # Get GitHub activity if available
        github_data = self._get_github_activity(asset)

        # Merge data
        return {
            **cg_data,
            **github_data,
            "data_source": "coingecko+github"
        }

    def get_sentiment(self, asset: str) -> Dict[str, Any]:
        """
        Get sentiment data for an asset

        Args:
            asset: Asset symbol

        Returns:
            Dict with sentiment metrics
        """
        # Try to get from CoinGecko community data
        cg_id = self.cg_ids.get(asset.upper(), asset.lower())

        try:
            url = f"https://api.coingecko.com/api/v3/coins/{cg_id}"
            params = {
                "localization": "false",
                "tickers": "false",
                "market_data": "false",
                "community_data": "true",
                "developer_data": "false"
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                community = data.get("community_data", {})
                sentiment = data.get("sentiment_votes_up_percentage", 50)

                # Calculate composite score
                twitter_followers = community.get("twitter_followers", 0)
                reddit_subscribers = community.get("reddit_subscribers", 0)

                # Simple social volume score
                social_score = min(100, (twitter_followers / 100000 + reddit_subscribers / 50000) * 10)

                return {
                    "composite_score": int(sentiment if sentiment else 50),
                    "twitter_followers": twitter_followers,
                    "reddit_subscribers": reddit_subscribers,
                    "social_volume_change_pct": 0,  # Would need historical data
                    "fear_greed_index": self._get_fear_greed(),
                    "social_score": social_score
                }

        except Exception as e:
            pass

        # Return neutral mock data
        return {
            "composite_score": 50,
            "twitter_followers": 0,
            "reddit_subscribers": 0,
            "social_volume_change_pct": 0,
            "fear_greed_index": 50,
            "social_score": 50
        }

    def _get_coingecko_data(self, asset: str) -> Dict[str, Any]:
        """Get data from CoinGecko API"""
        cg_id = self.cg_ids.get(asset.upper(), asset.lower())

        try:
            url = f"https://api.coingecko.com/api/v3/coins/{cg_id}"
            params = {
                "localization": "false",
                "tickers": "false",
                "market_data": "true",
                "community_data": "false",
                "developer_data": "true"
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                dev_data = data.get("developer_data", {})
                market_data = data.get("market_data", {})

                return {
                    "github_commits_30d": dev_data.get("commit_count_4_weeks", 0),
                    "github_stars": dev_data.get("stars", 0),
                    "github_forks": dev_data.get("forks", 0),
                    "last_major_update_days": 30,  # Would need additional API call
                    "market_cap_rank": data.get("market_cap_rank", 999),
                    "annual_inflation_pct": self._estimate_inflation(asset),
                    "max_supply": market_data.get("max_supply"),
                    "circulating_supply": market_data.get("circulating_supply")
                }

        except Exception as e:
            pass

        # Return mock data
        return {
            "github_commits_30d": 50,
            "github_stars": 1000,
            "github_forks": 200,
            "last_major_update_days": 30,
            "market_cap_rank": 999,
            "annual_inflation_pct": 2.0,
            "max_supply": None,
            "circulating_supply": None
        }

    def _get_github_activity(self, asset: str) -> Dict[str, Any]:
        """Get GitHub activity metrics"""
        # GitHub repo mapping
        repos = {
            "BTC": "bitcoin/bitcoin",
            "ETH": "ethereum/go-ethereum",
            "SOL": "solana-labs/solana",
            "AAVE": "aave/aave-v3-core"
        }

        repo = repos.get(asset.upper())
        if not repo:
            return {}

        try:
            url = f"https://api.github.com/repos/{repo}"
            headers = {}
            if os.getenv("GITHUB_TOKEN"):
                headers["Authorization"] = f"token {os.getenv('GITHUB_TOKEN')}"

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    "github_repo": repo,
                    "github_stars": data.get("stargazers_count", 0),
                    "github_forks": data.get("forks_count", 0),
                    "open_issues": data.get("open_issues_count", 0),
                    "last_push": data.get("pushed_at", "")
                }

        except Exception:
            pass

        return {}

    def _get_fear_greed(self) -> int:
        """Get Crypto Fear & Greed Index"""
        try:
            url = "https://api.alternative.me/fng/"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return int(data["data"][0]["value"])

        except Exception:
            pass

        return 50  # Neutral

    def _estimate_inflation(self, asset: str) -> float:
        """Estimate annual inflation rate for common assets"""
        # Known approximate inflation rates
        inflation_rates = {
            "BTC": 1.7,  # ~1.7% annual issuance
            "ETH": 0.5,  # Post-merge, can be deflationary
            "SOL": 5.5,  # ~5.5% current
            "XRP": 0.0,  # Pre-mined
            "AAVE": 0.0,  # Fixed supply
            "LINK": 0.0,  # Fixed supply
        }

        return inflation_rates.get(asset.upper(), 2.0)

    def search_documents(self, query: str, asset: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search local document store

        Args:
            query: Search query
            asset: Optional asset filter

        Returns:
            List of matching documents
        """
        results = []

        # Simple keyword search in local docs
        for doc_file in self.docs_dir.glob("**/*.md"):
            try:
                content = doc_file.read_text()
                if query.lower() in content.lower():
                    if asset is None or asset.lower() in doc_file.name.lower():
                        results.append({
                            "file": str(doc_file),
                            "name": doc_file.name,
                            "snippet": self._extract_snippet(content, query)
                        })
            except Exception:
                pass

        return results

    def _extract_snippet(self, content: str, query: str, context: int = 200) -> str:
        """Extract snippet around query match"""
        idx = content.lower().find(query.lower())
        if idx == -1:
            return content[:context]

        start = max(0, idx - context // 2)
        end = min(len(content), idx + len(query) + context // 2)

        return "..." + content[start:end] + "..."


# Test
if __name__ == "__main__":
    client = TextSourcesClient()

    print("Testing Text Sources Client...")

    for asset in ["BTC", "ETH", "SOL"]:
        print(f"\n=== {asset} ===")

        print("\nFundamentals:")
        fundamentals = client.get_fundamentals(asset)
        for k, v in fundamentals.items():
            print(f"  {k}: {v}")

        print("\nSentiment:")
        sentiment = client.get_sentiment(asset)
        for k, v in sentiment.items():
            print(f"  {k}: {v}")
