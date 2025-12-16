"""
ElevenLabs Voice Alert System for Sovereign Shadow 3
Converts trade signals to spoken alerts using 11.AI TTS
"""

import os
import requests
from typing import Optional

ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY', '')

VOICES = {
    "rachel": "21m00Tcm4TlvDq8ikWAM",
    "adam": "pNInz6obpgDQGcFmaJgB",
    "bella": "EXAVITQu4vr4xnSDxMaL",
    "arnold": "VR6AewLTigWG4xSOukaG",
    "domi": "AZnzlk1XvdvUeBnXmlld",
}


def speak_alert(text: str, voice: str = "rachel") -> Optional[bytes]:
    """
    Convert text to speech using ElevenLabs
    Returns audio bytes (MP3) or None on error
    """
    if not ELEVENLABS_API_KEY:
        print("ElevenLabs API key not configured")
        return None
        
    voice_id = VOICES.get(voice, voice)
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.content
        else:
            print(f"ElevenLabs error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"ElevenLabs request failed: {e}")
        return None


def trade_alert(symbol: str, action: str, price: float, pnl: Optional[float] = None) -> Optional[bytes]:
    """Generate trade alert audio"""
    action = action.upper()
    
    if action == "BUY" or action == "ENTRY":
        text = f"Entry signal. Buying {symbol} at {price:.2f} dollars."
    elif action == "SELL" or action == "EXIT":
        text = f"Exit signal. Selling {symbol} at {price:.2f} dollars."
        if pnl:
            result = "profit" if pnl > 0 else "loss"
            text += f" {result} of {abs(pnl):.2f} dollars."
    elif action == "FILL":
        text = f"Ladder fill. {symbol} filled at {price:.4f}."
    else:
        text = f"{action} alert for {symbol}."

    return speak_alert(text, voice="rachel")


def ntfy_to_voice(message: str) -> Optional[bytes]:
    """Convert ntfy message to voice alert"""
    text = message.upper()
    
    if 'FILL' in text:
        return speak_alert(f"Fill alert received. {message}", voice="rachel")
    elif 'EXIT' in text or 'SELL' in text:
        return speak_alert(f"Exit signal. {message}", voice="rachel")
    elif 'ENTRY' in text or 'BUY' in text:
        return speak_alert(f"Entry signal. {message}", voice="rachel")
    else:
        return speak_alert(message, voice="rachel")


def system_status(status: str) -> Optional[bytes]:
    """Generate system status voice alert"""
    return speak_alert(status, voice="adam")
