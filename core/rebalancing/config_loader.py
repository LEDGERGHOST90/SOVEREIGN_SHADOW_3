#!/usr/bin/env python3
# Sovereign Shadow - Configuration Loader
# Location: /home/sovereign_shadow/core_portfolio/config_loader.py

import os
import yaml
from pathlib import Path

# Default fallback targets (if config file missing)
DEFAULT_TARGETS = {"ETH": 0.40, "BTC": 0.30, "SOL": 0.20, "XRP": 0.10}

def get_config_path():
    """Find portfolio_config.yaml in common locations"""
    possible_paths = [
        # Go up from core/rebalancing/ to project root
        Path(__file__).parent.parent.parent / "config" / "portfolio_config.yaml",
        Path(os.getenv("SOVEREIGN_SHADOW_ROOT", "")) / "config" / "portfolio_config.yaml",
    ]
    
    # Try relative path from current working directory
    cwd = Path.cwd()
    if (cwd / "config" / "portfolio_config.yaml").exists():
        possible_paths.insert(0, cwd / "config" / "portfolio_config.yaml")
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None

def load_portfolio_targets():
    """
    Load portfolio target weights from portfolio_config.yaml
    
    Returns:
        dict: {asset_symbol: target_weight} e.g. {"ETH": 0.40, "BTC": 0.30, ...}
    
    Falls back to DEFAULT_TARGETS if config file not found or invalid.
    """
    config_path = get_config_path()
    
    if config_path is None:
        print(f"⚠️ portfolio_config.yaml not found, using default targets: {DEFAULT_TARGETS}")
        return DEFAULT_TARGETS.copy()
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Extract assets and build targets dict
        assets = config.get("assets", [])
        targets = {}
        
        for asset in assets:
            symbol = asset.get("symbol", "").upper()
            weight = asset.get("target_weight", 0.0)
            
            if symbol and weight > 0:
                targets[symbol] = weight
        
        # Validate weights sum to ~1.0 (allow small rounding error)
        total = sum(targets.values())
        if abs(total - 1.0) > 0.01:
            print(f"⚠️ Target weights sum to {total:.2%}, not 100%. Using defaults.")
            return DEFAULT_TARGETS.copy()
        
        print(f"✅ Loaded {len(targets)} assets from {config_path}")
        return targets
        
    except yaml.YAMLError as e:
        print(f"⚠️ YAML parse error in {config_path}: {e}")
        print(f"   Using default targets: {DEFAULT_TARGETS}")
        return DEFAULT_TARGETS.copy()
    except Exception as e:
        print(f"⚠️ Error loading config from {config_path}: {e}")
        print(f"   Using default targets: {DEFAULT_TARGETS}")
        return DEFAULT_TARGETS.copy()

def get_all_asset_symbols():
    """
    Get list of all asset symbols from config
    
    Returns:
        list: ["ETH", "BTC", "SOL", "XRP", ...]
    """
    targets = load_portfolio_targets()
    return list(targets.keys())

if __name__ == "__main__":
    print("🔍 Testing config_loader.py\n")
    print("=" * 60)
    
    targets = load_portfolio_targets()
    
    print(f"\n📊 Loaded Portfolio Targets:")
    for asset, weight in sorted(targets.items()):
        print(f"  {asset}: {weight:.1%}")
    
    print(f"\n✅ Total: {sum(targets.values()):.1%}")
    print(f"✅ Assets: {len(targets)}")
    
    symbols = get_all_asset_symbols()
    print(f"\n📋 Asset Symbols: {', '.join(symbols)}")

