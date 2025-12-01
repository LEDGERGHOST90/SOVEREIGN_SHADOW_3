#!/usr/bin/env python3
"""
SOVEREIGN SHADOW - Text-to-Speech Reader
Reads text aloud using ElevenLabs George voice

Usage:
    python bin/speak.py "Your text here"
    echo "text" | python bin/speak.py
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def speak(text: str):
    """Generate and play speech using ElevenLabs"""
    try:
        from elevenlabs import ElevenLabs
        from elevenlabs.types import VoiceSettings

        api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not api_key:
            # Load from .env
            env_path = Path(__file__).parent.parent / ".env"
            if env_path.exists():
                for line in env_path.read_text().splitlines():
                    if line.startswith("ELEVENLABS_API_KEY="):
                        api_key = line.split("=", 1)[1].strip()
                        break

        if not api_key:
            print("No API key, using macOS say...")
            subprocess.run(["say", "-v", "Alex", text])
            return

        client = ElevenLabs(api_key=api_key)

        # Generate with Aurora (Jessica voice) - Sovereign Shadow alert voice
        audio = client.text_to_speech.convert(
            text=text,
            voice_id="cgSgspJ2msm6clMCkdW9",  # Aurora
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.8,
                style=0.6,
                use_speaker_boost=True
            )
        )

        # Save to temp file and play
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            for chunk in audio:
                f.write(chunk)
            temp_path = f.name

        subprocess.run(["afplay", temp_path])
        os.unlink(temp_path)

    except Exception as e:
        print(f"ElevenLabs error: {e}")
        print("Falling back to macOS say...")
        subprocess.run(["say", "-v", "Alex", text])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = sys.stdin.read().strip()

    if text:
        speak(text)
    else:
        print("Usage: python bin/speak.py 'text to speak'")
