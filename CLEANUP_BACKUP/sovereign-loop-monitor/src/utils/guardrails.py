"""
Sovereign Loop Monitor - Guardrails & Safety System
Critical safeguards to prevent unauthorized trading
"""
import os
from typing import Dict, Any
from datetime import datetime

class GuardrailViolation(Exception):
    """Raised when a guardrail check fails"""
    pass

def real_trading_allowed() -> bool:
    """
    Triple-check system: ALL three must be true for live trading
    1. ENV must be 'prod'
    2. ALLOW_LIVE_EXCHANGE must be '1'
    3. DISABLE_REAL_EXCHANGES must be '0'
    """
    env = os.getenv("ENV", "dev")
    allow = os.getenv("ALLOW_LIVE_EXCHANGE", "0") == "1"
    disable = os.getenv("DISABLE_REAL_EXCHANGES", "1") == "1"
    
    return (env == "prod") and allow and (not disable)

def assert_fake_only():
    """Enforce FAKE mode - raises if real trading is enabled"""
    if real_trading_allowed():
        raise GuardrailViolation(
            "CRITICAL: Real trading is enabled but code attempted fake-only operation. "
            "Check ENV, ALLOW_LIVE_EXCHANGE, and DISABLE_REAL_EXCHANGES settings."
        )

def validate_trade_size(amount_usd: float) -> bool:
    """Validate trade size against configured limits"""
    max_size = float(os.getenv("MAX_TRADE_SIZE", "100"))
    if amount_usd > max_size:
        raise GuardrailViolation(
            f"Trade size ${amount_usd:.2f} exceeds maximum ${max_size:.2f}"
        )
    return True

def validate_daily_exposure(proposed_usd: float, existing_usd: float = 0) -> bool:
    """Validate total daily exposure"""
    max_daily = float(os.getenv("MAX_DAILY_EXPOSURE", "500"))
    total = proposed_usd + existing_usd
    if total > max_daily:
        raise GuardrailViolation(
            f"Daily exposure ${total:.2f} exceeds limit ${max_daily:.2f}"
        )
    return True

def validate_confidence(confidence: float) -> bool:
    """Validate confidence meets threshold for execution"""
    threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.85"))
    if confidence < threshold:
        return False  # Not a violation, just insufficient confidence
    return True

def log_guardrail_check(check_name: str, passed: bool, details: Dict[str, Any] = None):
    """Log guardrail check results"""
    timestamp = datetime.now().isoformat()
    status = "PASS" if passed else "FAIL"
    log_entry = f"[{timestamp}] GUARDRAIL {status}: {check_name}"
    if details:
        log_entry += f" | {details}"
    print(log_entry)
    
    # Append to guardrail log file
    log_path = os.getenv("LOG_PATH", "./logs")
    os.makedirs(log_path, exist_ok=True)
    with open(f"{log_path}/guardrails.log", "a") as f:
        f.write(log_entry + "\n")

def get_trading_mode() -> str:
    """Return current trading mode: FAKE, SIMULATION, or LIVE"""
    if not real_trading_allowed():
        return "FAKE"
    # Even in prod, we simulate first
    return "SIMULATION"  # Change to LIVE only after extensive testing

# Startup safety check
def startup_safety_check():
    """Run all safety checks on system startup"""
    checks = {
        "Trading Mode": get_trading_mode(),
        "ENV": os.getenv("ENV", "dev"),
        "ALLOW_LIVE_EXCHANGE": os.getenv("ALLOW_LIVE_EXCHANGE", "0"),
        "DISABLE_REAL_EXCHANGES": os.getenv("DISABLE_REAL_EXCHANGES", "1"),
        "Max Trade Size": os.getenv("MAX_TRADE_SIZE", "100"),
        "Max Daily Exposure": os.getenv("MAX_DAILY_EXPOSURE", "500"),
        "Confidence Threshold": os.getenv("CONFIDENCE_THRESHOLD", "0.85"),
    }
    
    print("=" * 60)
    print("SOVEREIGN LOOP MONITOR - SAFETY CHECK")
    print("=" * 60)
    for key, value in checks.items():
        print(f"{key:.<30} {value}")
    print("=" * 60)
    
    mode = get_trading_mode()
    if mode == "FAKE":
        print("✅ SAFE MODE: All trades will be simulated")
    elif mode == "SIMULATION":
        print("⚠️  SIMULATION MODE: Trades logged but not executed")
    else:
        print("🔴 LIVE MODE: Real trading enabled - USE CAUTION")
    print("=" * 60)
    
    log_guardrail_check("STARTUP", True, checks)
    return checks

if __name__ == "__main__":
    startup_safety_check()
