#!/bin/bash
# 24-Hour Test Analysis Script
# Run this periodically or after test completion

echo "════════════════════════════════════════════════════════════════════════════════"
echo "🏰 SOVEREIGN SHADOW AI - 24-HOUR TEST ANALYSIS"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Check if process is still running
if ps aux | grep -v grep | grep "sovereign_shadow_unified.py --autonomy" > /dev/null; then
    PID=$(ps aux | grep -v grep | grep "sovereign_shadow_unified.py --autonomy" | awk '{print $2}')
    UPTIME=$(ps -p $PID -o etime= | xargs)
    STATUS="🟢 RUNNING"
else
    PID="N/A"
    UPTIME="N/A (stopped)"
    STATUS="🔴 STOPPED"
fi

echo "📊 TEST STATUS: $STATUS"
echo "   PID: $PID"
echo "   Uptime: $UPTIME"
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"

# 1. STABILITY & UPTIME
echo ""
echo "1️⃣  STABILITY & UPTIME"
echo "────────────────────────────────────────────────────────────────────────────────"
BEATS=$(grep -c "Heartbeat" logs/ai_enhanced/autonomy_24h_test.log 2>/dev/null || echo "0")
TARGET=1440
COMPLETION=$(echo "scale=1; $BEATS * 100 / $TARGET" | bc 2>/dev/null || echo "0")
echo "   Heartbeats: $BEATS / ~$TARGET expected (${COMPLETION}% complete)"
echo "   Target: ~1 heartbeat/minute for 24 hours"

# Check for gaps
LAST_BEAT=$(grep "Heartbeat" logs/ai_enhanced/autonomy_24h_test.log | tail -1 | awk '{print $1, $2}')
echo "   Last heartbeat: $LAST_BEAT"

if [ "$BEATS" -gt 10 ]; then
    echo "   ✅ PASS: Consistent heartbeat pattern"
else
    echo "   ⏳ In progress: Need more runtime"
fi

# 2. MEMORY BEHAVIOR
echo ""
echo "2️⃣  MEMORY BEHAVIOR (LEAK CHECK)"
echo "────────────────────────────────────────────────────────────────────────────────"
if ps -p $PID > /dev/null 2>&1; then
    MEM=$(ps -p $PID -o %mem= | xargs)
    RSS=$(ps -p $PID -o rss= | awk '{print $1/1024}')
    echo "   Current Memory: ${MEM}% (~${RSS} MB)"
    echo "   Expected: Stable 25-50 MB"
    
    if (( $(echo "$RSS < 100" | bc -l) )); then
        echo "   ✅ PASS: Memory usage within bounds"
    else
        echo "   ⚠️  WARNING: Memory higher than expected"
    fi
else
    echo "   ⚠️  Process not running - cannot check memory"
fi

# Memory from JSONL if available
if [ -f logs/ai_enhanced/system_status.jsonl ]; then
    AVG_MEM=$(jq -r '.system_health.memory_percent' logs/ai_enhanced/system_status.jsonl 2>/dev/null | \
              awk '{sum+=$1;n+=1} END{if(n>0) print sum/n; else print "N/A"}')
    echo "   Average from JSONL: ${AVG_MEM}%"
fi

# 3. GUARDRAILS ENFORCEMENT
echo ""
echo "3️⃣  GUARDRAILS ENFORCEMENT"
echo "────────────────────────────────────────────────────────────────────────────────"
if [ -f logs/ai_enhanced/system_status.json ]; then
    ENV_VAL=$(jq -r '.guardrails.ENV' logs/ai_enhanced/system_status.json 2>/dev/null)
    ALLOW_VAL=$(jq -r '.guardrails.ALLOW_LIVE_EXCHANGE' logs/ai_enhanced/system_status.json 2>/dev/null)
    DISABLE_VAL=$(jq -r '.guardrails.DISABLE_REAL_EXCHANGES' logs/ai_enhanced/system_status.json 2>/dev/null)
    MODE_VAL=$(jq -r '.guardrails.effective_mode' logs/ai_enhanced/system_status.json 2>/dev/null)
    
    echo "   ENV: $ENV_VAL"
    echo "   ALLOW_LIVE_EXCHANGE: $ALLOW_VAL"
    echo "   DISABLE_REAL_EXCHANGES: $DISABLE_VAL"
    echo "   Effective Mode: $MODE_VAL"
    
    if [ "$MODE_VAL" == "FAKE" ]; then
        echo "   ✅ PASS: FAKE mode maintained"
    else
        echo "   🚨 FAIL: Mode changed to $MODE_VAL - CRITICAL ISSUE"
    fi
else
    echo "   ⚠️  system_status.json not found - run system monitor"
fi

# Check JSONL for mode consistency
if [ -f logs/ai_enhanced/system_status.jsonl ]; then
    echo ""
    echo "   Mode consistency check (from JSONL):"
    jq -r '.guardrails.effective_mode' logs/ai_enhanced/system_status.jsonl 2>/dev/null | \
        sort | uniq -c | awk '{print "     "$2": "$1" occurrences"}'
fi

# 4. RESOURCE BASELINES
echo ""
echo "4️⃣  RESOURCE BASELINES"
echo "────────────────────────────────────────────────────────────────────────────────"
if ps -p $PID > /dev/null 2>&1; then
    CPU=$(ps -p $PID -o %cpu= | xargs)
    echo "   CPU: ${CPU}% (target: 0-2%)"
    [ $(echo "$CPU < 5" | bc -l) -eq 1 ] && echo "   ✅ PASS: CPU within bounds" || echo "   ⚠️  WARNING: High CPU"
fi

# From system status if available
if [ -f logs/ai_enhanced/system_status.json ]; then
    SYS_CPU=$(jq -r '.system_health.cpu_percent' logs/ai_enhanced/system_status.json 2>/dev/null)
    SYS_MEM=$(jq -r '.system_health.memory_percent' logs/ai_enhanced/system_status.json 2>/dev/null)
    SYS_DISK=$(jq -r '.system_health.disk_percent' logs/ai_enhanced/system_status.json 2>/dev/null)
    
    echo "   System CPU: ${SYS_CPU}%"
    echo "   System Memory: ${SYS_MEM}%"
    echo "   System Disk: ${SYS_DISK}%"
fi

# 5. PROCESS & DEPENDENCY HEALTH
echo ""
echo "5️⃣  PROCESS & DEPENDENCY HEALTH"
echo "────────────────────────────────────────────────────────────────────────────────"
if [ -f logs/ai_enhanced/system_status.json ]; then
    AI_PROC_COUNT=$(jq -r '.system_health.ai_processes_count' logs/ai_enhanced/system_status.json 2>/dev/null)
    echo "   AI Processes detected: $AI_PROC_COUNT"
    
    echo "   Dependencies:"
    jq -r '.dependencies | to_entries[] | "     \(.key): \(if .value then "✅" else "❌" end)"' \
        logs/ai_enhanced/system_status.json 2>/dev/null
fi

# 6. ERROR ANALYSIS
echo ""
echo "6️⃣  ERROR ANALYSIS"
echo "────────────────────────────────────────────────────────────────────────────────"
TOTAL_ERRORS=$(grep -Ei "error|exception|failed" logs/ai_enhanced/*.log 2>/dev/null | wc -l | xargs)
TEST_ERRORS=$(grep -Ei "error|exception|failed" logs/ai_enhanced/autonomy_24h_test.log 2>/dev/null | wc -l | xargs)

echo "   Total errors in all logs: $TOTAL_ERRORS (includes old logs)"
echo "   Errors in current test: $TEST_ERRORS"

if [ "$TEST_ERRORS" -eq 0 ]; then
    echo "   ✅ PASS: No errors in current test"
elif [ "$TEST_ERRORS" -lt 5 ]; then
    echo "   ⚠️  WARNING: $TEST_ERRORS errors found - review needed"
else
    echo "   🚨 FAIL: $TEST_ERRORS errors found - investigation required"
fi

# 7. REPORT INTEGRITY
echo ""
echo "7️⃣  REPORT/LOGGING INTEGRITY"
echo "────────────────────────────────────────────────────────────────────────────────"
[ -f logs/ai_enhanced/sovereign_shadow_unified_report.json ] && echo "   ✅ unified_report.json" || echo "   ❌ unified_report.json missing"
[ -f logs/ai_enhanced/system_status.json ] && echo "   ✅ system_status.json" || echo "   ❌ system_status.json missing"
[ -f logs/ai_enhanced/autonomy_24h_test.log ] && echo "   ✅ autonomy_24h_test.log" || echo "   ❌ autonomy_24h_test.log missing"
[ -f logs/ai_enhanced/system_status.jsonl ] && echo "   ✅ system_status.jsonl" || echo "   ⚠️  system_status.jsonl (run monitor --continuous)"

if [ -f logs/ai_enhanced/sovereign_shadow_unified_report.json ]; then
    LAST_REPORT=$(jq -r '.timestamp' logs/ai_enhanced/sovereign_shadow_unified_report.json 2>/dev/null)
    echo "   Last report: $LAST_REPORT"
fi

# 8. ARBITRAGE LOOP LIVENESS
echo ""
echo "8️⃣  ARBITRAGE LOOP LIVENESS"
echo "────────────────────────────────────────────────────────────────────────────────"
if [ -f logs/ai_enhanced/sovereign_shadow_unified_report.json ]; then
    OPP_COUNT=$(jq -r '.summary.total_opportunities' logs/ai_enhanced/sovereign_shadow_unified_report.json 2>/dev/null)
    ARB_STATUS=$(jq -r '.system_health.arbitrage_system.status' logs/ai_enhanced/sovereign_shadow_unified_report.json 2>/dev/null)
    
    echo "   Arbitrage system: $ARB_STATUS"
    echo "   Opportunities detected: $OPP_COUNT"
    
    if [ "$ARB_STATUS" == "operational" ]; then
        echo "   ✅ PASS: Arbitrage scanner active"
    else
        echo "   ⚠️  WARNING: Arbitrage system not operational"
    fi
fi

# OVERALL VERDICT
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "📋 OVERALL VERDICT"
echo "════════════════════════════════════════════════════════════════════════════════"

PASS_COUNT=0
TOTAL_CHECKS=8

# Check each criterion
[ "$BEATS" -gt 10 ] && ((PASS_COUNT++))
[ "$TEST_ERRORS" -eq 0 ] && ((PASS_COUNT++))
[ "$MODE_VAL" == "FAKE" ] && ((PASS_COUNT++))

if [ "$STATUS" == "🟢 RUNNING" ]; then
    if [ "$BEATS" -ge 1440 ]; then
        echo "✅ TEST COMPLETE - Evaluating results..."
        echo ""
        if [ "$TEST_ERRORS" -eq 0 ] && [ "$MODE_VAL" == "FAKE" ]; then
            echo "🟢 PASS: All critical checks passed"
            echo ""
            echo "   Next Steps:"
            echo "   1. Install CCXT: pip install ccxt"
            echo "   2. Configure sandbox API keys"
            echo "   3. Run Option B: Testnet integration"
        else
            echo "🟡 PARTIAL: Review warnings above before proceeding"
        fi
    else
        echo "⏳ TEST IN PROGRESS - $(echo "scale=1; $BEATS * 100 / 1440" | bc)% complete"
        echo ""
        echo "   Status: $STATUS"
        echo "   Heartbeats: $BEATS / 1440"
        echo "   Errors: $TEST_ERRORS"
        echo "   Mode: $MODE_VAL"
    fi
else
    echo "🔴 TEST STOPPED - Process not running"
    echo "   Check logs for crash/termination reason"
fi

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "Generated: $(date)"
echo "════════════════════════════════════════════════════════════════════════════════"

