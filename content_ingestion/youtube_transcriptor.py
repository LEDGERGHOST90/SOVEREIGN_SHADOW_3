#!/usr/bin/env python3
"""
YouTube Strategy Transcriptor
Downloads and transcribes trading content, extracts actionable strategies
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

BASE_DIR = Path('/Volumes/LegacySafe/SOVEREIGN_SHADOW_3/content_ingestion')
TRANSCRIPTS_DIR = BASE_DIR / 'transcripts'
STRATEGIES_DIR = BASE_DIR / 'strategies'


class YouTubeTranscriptor:
    """
    Downloads YouTube videos and extracts trading strategies

    Flow:
    1. yt-dlp downloads audio
    2. whisper transcribes to text
    3. AI extracts strategy rules
    4. Saves to strategies/ for DS-STAR to consume
    """

    def __init__(self):
        self.transcripts_dir = TRANSCRIPTS_DIR
        self.strategies_dir = STRATEGIES_DIR
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        self.strategies_dir.mkdir(parents=True, exist_ok=True)

    def download_audio(self, url: str) -> Optional[Path]:
        """Download audio from YouTube video"""
        try:
            output_template = str(self.transcripts_dir / '%(title)s.%(ext)s')
            cmd = [
                'yt-dlp',
                '-x',  # Extract audio
                '--audio-format', 'mp3',
                '-o', output_template,
                '--no-playlist',
                url
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                # Find the downloaded file
                for line in result.stdout.split('\n'):
                    if 'Destination:' in line or 'has already been downloaded' in line:
                        # Extract filename
                        pass

                # Get most recent mp3
                mp3_files = list(self.transcripts_dir.glob('*.mp3'))
                if mp3_files:
                    return max(mp3_files, key=lambda p: p.stat().st_mtime)

            return None

        except Exception as e:
            print(f"Error downloading: {e}")
            return None

    def transcribe(self, audio_path: Path) -> Optional[str]:
        """Transcribe audio using whisper"""
        try:
            output_file = audio_path.with_suffix('.txt')

            cmd = [
                'whisper',
                str(audio_path),
                '--model', 'base',
                '--output_format', 'txt',
                '--output_dir', str(self.transcripts_dir)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0 and output_file.exists():
                return output_file.read_text()

            return None

        except Exception as e:
            print(f"Error transcribing: {e}")
            return None

    def extract_strategy(self, transcript: str, source_url: str) -> Dict:
        """
        Parse transcript to extract trading strategy elements
        Returns structured strategy for DS-STAR
        """
        # Strategy template
        strategy = {
            "source": source_url,
            "extracted_at": datetime.now().isoformat(),
            "transcript_preview": transcript[:500] + "..." if len(transcript) > 500 else transcript,
            "indicators": [],
            "entry_rules": [],
            "exit_rules": [],
            "timeframe": "unknown",
            "assets": [],
            "risk_management": {},
            "confidence": 0.0,
            "requires_review": True
        }

        # Basic keyword extraction (AI enhancement would go here)
        keywords = {
            'indicators': ['rsi', 'macd', 'ema', 'sma', 'volume', 'vwap', 'bollinger'],
            'timeframes': ['1m', '5m', '15m', '1h', '4h', 'daily', 'weekly'],
            'assets': ['btc', 'eth', 'sol', 'xrp', 'bitcoin', 'ethereum'],
            'actions': ['buy', 'sell', 'long', 'short', 'entry', 'exit']
        }

        transcript_lower = transcript.lower()

        for indicator in keywords['indicators']:
            if indicator in transcript_lower:
                strategy['indicators'].append(indicator.upper())

        for tf in keywords['timeframes']:
            if tf in transcript_lower:
                strategy['timeframe'] = tf
                break

        for asset in keywords['assets']:
            if asset in transcript_lower:
                strategy['assets'].append(asset.upper())

        # Confidence based on how much structure we found
        found_elements = len(strategy['indicators']) + len(strategy['assets'])
        strategy['confidence'] = min(found_elements * 0.15, 0.8)

        return strategy

    def process_video(self, url: str) -> Optional[Dict]:
        """Full pipeline: download → transcribe → extract"""
        print(f"Processing: {url}")

        # Download
        audio_path = self.download_audio(url)
        if not audio_path:
            print("Failed to download audio")
            return None

        print(f"Downloaded: {audio_path}")

        # Transcribe
        transcript = self.transcribe(audio_path)
        if not transcript:
            print("Failed to transcribe")
            return None

        print(f"Transcribed: {len(transcript)} chars")

        # Extract strategy
        strategy = self.extract_strategy(transcript, url)

        # Save strategy
        strategy_file = self.strategies_dir / f"yt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        strategy_file.write_text(json.dumps(strategy, indent=2))

        print(f"Strategy saved: {strategy_file}")

        return strategy

    def list_pending_strategies(self) -> List[Dict]:
        """List strategies pending review"""
        strategies = []
        for f in self.strategies_dir.glob('*.json'):
            try:
                data = json.loads(f.read_text())
                if data.get('requires_review', False):
                    data['_file'] = str(f)
                    strategies.append(data)
            except:
                pass
        return strategies


def main():
    """CLI interface"""
    import sys

    transcriptor = YouTubeTranscriptor()

    if len(sys.argv) < 2:
        print("Usage: youtube_transcriptor.py <youtube_url>")
        print("       youtube_transcriptor.py --list (show pending strategies)")
        return

    if sys.argv[1] == '--list':
        strategies = transcriptor.list_pending_strategies()
        print(f"\nPending Strategies: {len(strategies)}")
        for s in strategies:
            print(f"  - {s.get('source', 'unknown')} ({s.get('confidence', 0):.0%} confidence)")
    else:
        url = sys.argv[1]
        strategy = transcriptor.process_video(url)
        if strategy:
            print(f"\nExtracted Strategy:")
            print(json.dumps(strategy, indent=2))


if __name__ == "__main__":
    main()
