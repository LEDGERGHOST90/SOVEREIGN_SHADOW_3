#!/usr/bin/env python3
"""
SOVEREIGN SHADOW - Custom Alert Sound Generator
Uses ElevenLabs Voice Design API to create dramatic trading alerts

Usage:
    ELEVENLABS_API_KEY=your_key python bin/generate_alert_sound.py

Or set in .env file:
    ELEVENLABS_API_KEY=sk_xxxxx
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SOUNDS_DIR = PROJECT_ROOT / "sounds"
SOUNDS_DIR.mkdir(exist_ok=True)

# Alert messages to generate
ALERTS = {
    "shadow_alert": "Shadow alert. Signal locked. Execute now.",
    "snipe_ready": "Snipe target acquired. Token above seventy. Move fast.",
    "high_score": "High score detected. Breakout imminent.",
    "whale_alert": "Whale activity detected. Smart money moving.",
    "council_convenes": "The Council convenes. Trading signal ready."
}

def generate_with_elevenlabs(text: str, output_path: Path, voice_id: str = None):
    """Generate audio using ElevenLabs API"""
    try:
        from elevenlabs import ElevenLabs
        from elevenlabs.types import VoiceSettings

        api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not api_key:
            print("ERROR: ELEVENLABS_API_KEY not set")
            print("Set it with: export ELEVENLABS_API_KEY=your_key")
            return False

        client = ElevenLabs(api_key=api_key)

        # Use George - British, mature, narrative_story (dramatic movie trailer feel)
        selected_voice = voice_id or "JBFqnCBsd6RMkjVDRZzb"  # George

        audio = client.text_to_speech.convert(
            text=text,
            voice_id=selected_voice,
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.4,  # Lower = more dramatic variation
                similarity_boost=0.85,
                style=0.8,  # High style for dramatic delivery
                use_speaker_boost=True
            )
        )

        # Save audio file
        with open(output_path, 'wb') as f:
            for chunk in audio:
                f.write(chunk)

        print(f"Generated: {output_path}")
        return True

    except ImportError:
        print("ElevenLabs not installed. Run: pip install elevenlabs")
        return False
    except Exception as e:
        print(f"ElevenLabs error: {e}")
        return False

def list_voices():
    """List available ElevenLabs voices"""
    try:
        from elevenlabs import ElevenLabs

        api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not api_key:
            print("ERROR: ELEVENLABS_API_KEY not set")
            return

        client = ElevenLabs(api_key=api_key)
        voices = client.voices.get_all()

        print("\nAvailable Voices:")
        print("-" * 50)
        for voice in voices.voices[:20]:  # First 20
            print(f"  {voice.name}: {voice.voice_id}")
            if voice.labels:
                print(f"    Labels: {voice.labels}")

    except Exception as e:
        print(f"Error listing voices: {e}")

def generate_all_alerts():
    """Generate all alert sounds"""
    print("=" * 50)
    print("SOVEREIGN SHADOW - Alert Sound Generator")
    print("=" * 50)

    api_key = os.environ.get("ELEVENLABS_API_KEY")

    if not api_key:
        print("\nNo ELEVENLABS_API_KEY found.")
        print("\nTo set up ElevenLabs:")
        print("  1. Get API key from: https://elevenlabs.io/app/settings/api-keys")
        print("  2. Run: export ELEVENLABS_API_KEY=your_key")
        print("  3. Re-run this script")
        print("\nUsing macOS fallback for now...")
        generate_macos_fallback()
        return

    print(f"\nAPI Key: {api_key[:10]}...")
    print(f"Output directory: {SOUNDS_DIR}")
    print()

    for name, text in ALERTS.items():
        output_path = SOUNDS_DIR / f"{name}.mp3"
        print(f"\nGenerating: {name}")
        print(f"  Text: '{text}'")
        generate_with_elevenlabs(text, output_path)

    print("\n" + "=" * 50)
    print("Generation complete!")
    print(f"Files saved to: {SOUNDS_DIR}")
    print("=" * 50)

def generate_macos_fallback():
    """Generate alert using macOS say command with AIFF output"""
    import subprocess

    # Create a dramatic alert using say command with output file
    text = "Shadow alert. Signal locked."
    output_path = SOUNDS_DIR / "shadow_alert.aiff"

    try:
        # Use Alex voice (deeper) with output to file
        subprocess.run([
            "say", "-v", "Alex",
            "-r", "150",  # Slower rate for dramatic effect
            "-o", str(output_path),
            text
        ], check=True)

        print(f"Created fallback alert: {output_path}")
        print("\nTo use ElevenLabs for premium quality:")
        print("  export ELEVENLABS_API_KEY=your_key")
        print("  python bin/generate_alert_sound.py")

    except Exception as e:
        print(f"Fallback generation failed: {e}")

def test_sound():
    """Test the generated sound"""
    import subprocess

    # Try MP3 first (ElevenLabs), then AIFF (fallback)
    mp3_path = SOUNDS_DIR / "shadow_alert.mp3"
    aiff_path = SOUNDS_DIR / "shadow_alert.aiff"

    if mp3_path.exists():
        print(f"Playing: {mp3_path}")
        subprocess.run(["afplay", str(mp3_path)])
    elif aiff_path.exists():
        print(f"Playing: {aiff_path}")
        subprocess.run(["afplay", str(aiff_path)])
    else:
        print("No alert sound found. Run: python bin/generate_alert_sound.py")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate Sovereign Shadow alert sounds")
    parser.add_argument("--list-voices", action="store_true", help="List available ElevenLabs voices")
    parser.add_argument("--test", action="store_true", help="Test the generated sound")
    parser.add_argument("--fallback", action="store_true", help="Generate macOS fallback only")

    args = parser.parse_args()

    if args.list_voices:
        list_voices()
    elif args.test:
        test_sound()
    elif args.fallback:
        generate_macos_fallback()
    else:
        generate_all_alerts()
