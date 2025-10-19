#!/bin/bash
#
# 🔥 SOVEREIGN SHADOW NUCLEAR LAUNCH SEQUENCE
# This script will FORCE your trading system online
# Double-click this file on your Mac to execute
#

clear
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║     🔥 SOVEREIGN SHADOW AI - NUCLEAR LAUNCH SEQUENCE 🔥         ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "Initiating in 3..."
sleep 1
echo "2..."
sleep 1
echo "1..."
sleep 1
echo ""
echo "🚀 LAUNCHING TRADING EMPIRE..."
echo ""

# Navigate to your fortress
cd /Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]/ 2>/dev/null

if [ $? -ne 0 ]; then
    echo "❌ ERROR: Cannot find SovereignShadow directory"
    echo ""
    echo "Creating emergency activation..."
    
    # Emergency Python launcher
    cat > /tmp/emergency_sovereign.py << 'EOF'
import os
import sys
print("\n🏰 SOVEREIGN SHADOW - EMERGENCY MODE")
print("=====================================")
print("System Status: READY FOR MANUAL ACTIVATION")
print("\nRUN THESE COMMANDS IN TERMINAL:")
print("1. cd /Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]/")
print("2. export ENV=dev && export SANDBOX=1")
print("3. python3 sovereign_shadow_unified.py --autonomy")
print("\n✅ Your system is built. You just need to run it!")
EOF
    
    python3 /tmp/emergency_sovereign.py
    echo ""
    echo "Press any key to exit..."
    read -n 1
    exit 1
fi

echo "✅ Located Sovereign Shadow Fortress"
echo "📁 Directory: $(pwd)"
echo ""

# Set all safety flags
export ENV=dev
export SANDBOX=1
export DISABLE_REAL_EXCHANGES=1
export ALLOW_LIVE_EXCHANGE=0
export LEGACY_NO_LEDGER=1

echo "🛡️ Safety Mode: ACTIVATED (No real trades)"
echo ""

# Check if Python exists
python3 --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found!"
    echo "Install it with: brew install python@3.11"
    echo "Press any key to exit..."
    read -n 1
    exit 1
fi

echo "✅ Python: $(python3 --version)"
echo ""

# Check if main file exists
if [ ! -f "sovereign_shadow_unified.py" ]; then
    echo "❌ sovereign_shadow_unified.py not found!"
    echo "Your files may be in a different location."
    echo ""
    echo "Looking for alternatives..."
    
    # Try to find it
    find . -name "sovereign_shadow_unified.py" -type f 2>/dev/null | head -5
    
    echo "Press any key to exit..."
    read -n 1
    exit 1
fi

echo "✅ Main system file: FOUND"
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "                    🔥 SYSTEM LAUNCH IMMINENT 🔥                   "
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Create a launch wrapper that will keep running
cat > /tmp/sovereign_launcher.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
import time

os.environ['ENV'] = 'dev'
os.environ['SANDBOX'] = '1'
os.environ['DISABLE_REAL_EXCHANGES'] = '1'

print("\n🏰 SOVEREIGN SHADOW AI - LAUNCHING...\n")

try:
    # Add the path
    sys.path.insert(0, os.getcwd())
    
    # Import and run
    from sovereign_shadow_unified import SovereignShadowUnified
    import asyncio
    
    platform = SovereignShadowUnified()
    
    # Quick health check
    health = platform.check_system_health()
    print(f"✅ System Status: {health['overall_status'].upper()}")
    print(f"✅ Mode: {health['guardrails']['effective_mode']}")
    print("\n🚀 STARTING AUTONOMOUS LOOP...\n")
    
    # Run the autonomy demo
    asyncio.run(platform.autonomy_demo(interval=60, monitor=False))
    
except KeyboardInterrupt:
    print("\n\n🛑 System stopped by user")
except Exception as e:
    print(f"\n⚠️ Error: {e}")
    print("\n📝 MANUAL LAUNCH COMMANDS:")
    print("cd /Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]/")
    print("python3 sovereign_shadow_unified.py --autonomy --interval 60")
    
print("\n🏴 SOVEREIGN SHADOW - SESSION COMPLETE")
EOF

# Try to launch it
echo "🔥 EXECUTING LAUNCH SEQUENCE..."
echo "════════════════════════════════════════════════════════════════════"
echo ""

cd /Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]/
python3 /tmp/sovereign_launcher.py

# If we get here, the script finished
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "                    📊 LAUNCH SEQUENCE COMPLETE                     "
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "TO RESTART THE SYSTEM:"
echo "python3 sovereign_shadow_unified.py --autonomy --interval 60"
echo ""
echo "TO MONITOR LOGS:"
echo "tail -f logs/ai_enhanced/sovereign_shadow_unified.log"
echo ""
echo "Press any key to exit..."
read -n 1
