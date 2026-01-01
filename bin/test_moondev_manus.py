#!/usr/bin/env python3
"""Test MoonDev + Manus research integration"""
import sys
sys.path.insert(0, '/Volumes/LegacySafe/SS_III')

import ccxt
import pandas as pd
import json
from core.signals.moondev_signals import MoonDevSignals

print('Testing MoonDev + Manus Research Flow')
print('='*60)

# Exchanges priority: binance.us, kraken, coinbase
exchanges = [
    ('binanceus', ccxt.binanceus()),
    ('kraken', ccxt.kraken()),
    ('coinbase', ccxt.coinbase()),
]

# Manus immediate watchlist
symbols = ['BTC', 'ETH', 'SOL', 'ENA', 'PENDLE', 'LDO']
moondev = MoonDevSignals()

print('\nMoonDev Strategy Signals (Multi-Exchange OHLCV):')
print('-'*60)

actionable = []

def get_ohlcv(sym: str) -> pd.DataFrame:
    """Try multiple exchanges to get OHLCV data"""
    for name, ex in exchanges:
        try:
            pair = f'{sym}/USD'
            ohlcv = ex.fetch_ohlcv(pair, '1h', limit=200)
            if ohlcv and len(ohlcv) > 100:
                return ohlcv, name
        except:
            try:
                # Try USDT pair as fallback
                pair = f'{sym}/USDT'
                ohlcv = ex.fetch_ohlcv(pair, '1h', limit=200)
                if ohlcv and len(ohlcv) > 100:
                    return ohlcv, name
            except:
                continue
    return None, None

for sym in symbols:
    try:
        ohlcv, source = get_ohlcv(sym)

        if ohlcv and len(ohlcv) > 100:
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            result = moondev.get_consensus(df)
            action = result['action']
            score = result['score']
            conf = result['confidence']

            icon = '🟢' if 'BUY' in action else '🔴' if 'SELL' in action else '⚪'
            print(f'{icon} {sym}: {action} | Score: {score:.2f} | Confidence: {conf:.0%} [{source}]')

            if action != 'WAIT':
                print(f'   Entry: ${result["entry"]:,.2f} | SL: ${result["stop_loss"]:,.2f} | TP: ${result["take_profit"]:,.2f}')
                for reason in result.get('reasons', []):
                    print(f'   └─ {reason}')
                actionable.append((sym, result))
        else:
            print(f'⚠️  {sym}: No data available on any exchange')
    except Exception as e:
        print(f'❌ {sym}: {e}')

print('\n' + '='*60)
print('Applying Manus Research Bias...')
print('='*60)

# Load alpha bias
with open('/Volumes/LegacySafe/SS_III/config/alpha_bias.json') as f:
    bias = json.load(f)

regime = bias['market_regime']
print(f'\nRegime: {regime["classification"]}')
print(f'Recommendation: {regime["recommendation"]}')
print(f'Fear/Greed: {regime["fear_greed_index"]} ({regime["fear_greed_status"]})')
print(f'Peak Progress: {regime["progress_to_peak_pct"]:.1f}%')

print(f'\nHayes Rotation: {bias["whale_signals"]["hayes_rotation"]["tokens"]}')
print(f'Immediate Watchlist: {bias["watchlist"]["immediate"]}')
print(f'Whale Tracking: {bias["watchlist"]["whale_tracking"]}')

# Apply bias to actionable signals
if actionable:
    print('\n' + '='*60)
    print('BIASED SIGNALS (Manus Applied):')
    print('='*60)

    hayes_tokens = bias['whale_signals']['hayes_rotation']['tokens']
    immediate = bias['watchlist']['immediate']

    for sym, result in actionable:
        base_conf = result['confidence']
        boost = 0
        boosts = []

        # Hayes rotation boost
        if sym in hayes_tokens:
            boost += 0.15
            boosts.append('Hayes rotation +15%')

        # Immediate watchlist boost
        if sym in immediate:
            boost += 0.10
            boosts.append('Manus immediate +10%')

        # Regime boost
        if regime['recommendation'] == 'ACCUMULATE':
            boost += 0.05
            boosts.append('ACCUMULATE regime +5%')

        # Extreme fear contrarian boost
        if regime['fear_greed_status'] == 'EXTREME_FEAR':
            boost += 0.05
            boosts.append('Contrarian (EXTREME_FEAR) +5%')

        final_conf = min(1.0, base_conf + boost)

        print(f'\n🎯 {sym}:')
        print(f'   Base: {base_conf:.0%} → Biased: {final_conf:.0%}')
        print(f'   Boosts: {", ".join(boosts) if boosts else "None"}')

        # Tier classification
        if final_conf >= 0.80:
            tier = 'TIER_1_AUTO (execute automatically)'
        elif final_conf >= 0.60:
            tier = 'TIER_2_QUEUE (queue for approval)'
        else:
            tier = 'TIER_3_ALERT (alert only)'
        print(f'   Execution: {tier}')
else:
    print('\nNo actionable signals from MoonDev strategies')
    print('(Market may be ranging or unclear)')

print('\n' + '='*60)
print('Integration test complete')
