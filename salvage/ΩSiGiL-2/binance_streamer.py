import asyncio
import json
import websockets
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Define base WebSocket URL for Binance
BASE_STREAM_URL = "wss://stream.binance.com:9443/ws"

# Define symbols to subscribe to
SYMBOLS = ["btcusdt", "ethusdt", "suiusdt"]

# API endpoint of your local NuralAI signal processor
LOCAL_SIGNAL_ENDPOINT = "http://localhost:5050/api/signal"

# Function to send POST to NuralAI
async def send_to_local_api(symbol, price, volume):
    payload = {
        "symbol": symbol.upper(),
        "price": float(price),
        "volume": float(volume),
        "source": "binance",
        "signal_type": "neutral"  # Placeholder, can be updated with logic later
    }
    try:
        response = requests.post(LOCAL_SIGNAL_ENDPOINT, json=payload)
        print(f"[SEND] {symbol} | Price: {price} | Volume: {volume} => {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Sending to NuralAI: {e}")

# Combined stream for selected symbols
stream_query = "/".join([f"{sym}@ticker" for sym in SYMBOLS])
full_stream_url = f"{BASE_STREAM_URL}/{stream_query}"

async def stream():
    async with websockets.connect(full_stream_url) as ws:
        print(f"[CONNECTED] Streaming Binance live data for: {', '.join(SYMBOLS).upper()}")
        while True:
            try:
                message = await ws.recv()
                data = json.loads(message)
                symbol = data.get("s", "").lower()
                price = data.get("c")
                volume = data.get("v")

                if symbol and price and volume:
                    await send_to_local_api(symbol, price, volume)
            except Exception as err:
                print(f"[STREAM ERROR] {err}")
                await asyncio.sleep(2)  # Retry delay

if __name__ == "__main__":
    asyncio.run(stream())
