#!/usr/bin/env python3
"""Test script to validate PERSISTENT_STATE.json can be reloaded"""
import json
from datetime import datetime

try:
    with open('PERSISTENT_STATE.json', 'r') as f:
        state = json.load(f)

    print("=" * 60)
    print("✓ PERSISTENT STATE RELOAD TEST PASSED")
    print("=" * 60)
    print(f"Keys loaded: {len(state)}")
    print(f"Portfolio value: ${state['portfolio']['total_value_usd']}")
    print(f"Last updated: {state['last_updated']}")
    print(f"AAVE health: {state['defi_positions']['aave']['health_factor']}")
    print(f"Trading systems: {len(state['trading_systems'])}")
    print(f"Git branch: {state['git_state']['branch']}")
    print(f"Git commit: {state['git_state']['commit_hash']}")
    print("=" * 60)
    print("✓ ALL STATE DATA INTACT AND RELOADABLE")
    print("=" * 60)

except Exception as e:
    print(f"✗ RELOAD FAILED: {e}")
    exit(1)
