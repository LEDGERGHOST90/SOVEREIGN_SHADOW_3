#!/bin/bash
# Collect all artifacts from 24-hour test for analysis/archival

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARTIFACT_DIR="test_results_${TIMESTAMP}"

echo "════════════════════════════════════════════════════════════════════════════════"
echo "📦 Collecting 24-Hour Test Artifacts"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Create artifact directory
mkdir -p "$ARTIFACT_DIR"
echo "Created: $ARTIFACT_DIR"

# Run final analysis
echo ""
echo "📊 Running final analysis..."
./analyze_test.sh > "$ARTIFACT_DIR/final_analysis.txt" 2>&1

# Copy log files
echo "📄 Collecting logs..."
cp -r logs/ai_enhanced "$ARTIFACT_DIR/" 2>/dev/null || echo "⚠️  No logs found"

# Copy reports
echo "📊 Collecting reports..."
[ -f logs/ai_enhanced/sovereign_shadow_unified_report.json ] && \
    cp logs/ai_enhanced/sovereign_shadow_unified_report.json "$ARTIFACT_DIR/"
[ -f logs/ai_enhanced/system_status.json ] && \
    cp logs/ai_enhanced/system_status.json "$ARTIFACT_DIR/"

# Collect test metadata
echo "📝 Generating metadata..."
cat > "$ARTIFACT_DIR/test_metadata.txt" <<EOF
Test Completion Report
═══════════════════════════════════════════════════════════════════════════════

Collection Date: $(date)
System: $(uname -a)
Python Version: $(python3 --version)

Test Parameters:
  - Duration Target: 24 hours
  - Interval: 60 seconds
  - Expected Heartbeats: ~1440

EOF

# Add heartbeat count
if [ -f logs/ai_enhanced/autonomy_24h_test.log ]; then
    BEATS=$(grep -c "Heartbeat" logs/ai_enhanced/autonomy_24h_test.log)
    echo "  - Actual Heartbeats: $BEATS" >> "$ARTIFACT_DIR/test_metadata.txt"
fi

# Add error count
if [ -f logs/ai_enhanced/autonomy_24h_test.log ]; then
    ERRORS=$(grep -Ei "error|exception|failed" logs/ai_enhanced/autonomy_24h_test.log | wc -l | xargs)
    echo "  - Errors: $ERRORS" >> "$ARTIFACT_DIR/test_metadata.txt"
fi

# Generate statistical summary
echo ""
echo "Statistical Summary:" >> "$ARTIFACT_DIR/test_metadata.txt"
echo "─────────────────────" >> "$ARTIFACT_DIR/test_metadata.txt"

if [ -f logs/ai_enhanced/system_status.jsonl ]; then
    echo ""
    echo "📈 Generating statistics from JSONL..."
    
    # CPU stats
    jq -r '.system_health.cpu_percent' logs/ai_enhanced/system_status.jsonl 2>/dev/null | \
        awk '{sum+=$1; sumsq+=$1*$1; n+=1} END {
            avg=sum/n; 
            stddev=sqrt(sumsq/n - (sum/n)^2);
            print "CPU Usage:"
            print "  Average: " avg "%"
            print "  Std Dev: " stddev "%"
        }' >> "$ARTIFACT_DIR/test_metadata.txt"
    
    # Memory stats
    jq -r '.system_health.memory_percent' logs/ai_enhanced/system_status.jsonl 2>/dev/null | \
        awk '{sum+=$1; sumsq+=$1*$1; n+=1} END {
            avg=sum/n; 
            stddev=sqrt(sumsq/n - (sum/n)^2);
            print "\nMemory Usage:"
            print "  Average: " avg "%"
            print "  Std Dev: " stddev "%"
        }' >> "$ARTIFACT_DIR/test_metadata.txt"
    
    # Network stats
    jq -r '.system_health.net_bytes_sent_per_s' logs/ai_enhanced/system_status.jsonl 2>/dev/null | \
        awk '{sum+=$1; n+=1} END {
            print "\nNetwork Throughput:"
            print "  Avg TX: " sum/n " bytes/sec"
        }' >> "$ARTIFACT_DIR/test_metadata.txt"
    
    jq -r '.system_health.net_bytes_recv_per_s' logs/ai_enhanced/system_status.jsonl 2>/dev/null | \
        awk '{sum+=$1; n+=1} END {
            print "  Avg RX: " sum/n " bytes/sec"
        }' >> "$ARTIFACT_DIR/test_metadata.txt"
    
    # Mode consistency
    echo "" >> "$ARTIFACT_DIR/test_metadata.txt"
    echo "Guardrail Consistency:" >> "$ARTIFACT_DIR/test_metadata.txt"
    jq -r '.guardrails.effective_mode' logs/ai_enhanced/system_status.jsonl 2>/dev/null | \
        sort | uniq -c >> "$ARTIFACT_DIR/test_metadata.txt"
fi

# Create README
cat > "$ARTIFACT_DIR/README.md" <<'EOF'
# 24-Hour Test Results

## Contents

- `final_analysis.txt` - Complete test analysis with pass/fail results
- `test_metadata.txt` - Test parameters and statistical summary
- `ai_enhanced/` - All log files and reports
  - `autonomy_24h_test.log` - Main test log (heartbeats, operations)
  - `sovereign_shadow_unified_report.json` - Latest unified report
  - `system_status.json` - Latest system health snapshot
  - `system_status.jsonl` - Time-series system health data
  - Other monitoring logs

## Quick Analysis Commands

```bash
# View final analysis
cat final_analysis.txt

# Count heartbeats
grep -c "Heartbeat" ai_enhanced/autonomy_24h_test.log

# Check errors
grep -Ei "error|exception" ai_enhanced/autonomy_24h_test.log

# View latest report
cat ai_enhanced/sovereign_shadow_unified_report.json | jq '.'

# Analyze memory trend
jq -r '.system_health.memory_percent' ai_enhanced/system_status.jsonl | \
    awk '{sum+=$1;n+=1} END{print "avg:",sum/n"%"}'
```

## Test Objectives

1. ✓ Stability & Uptime (~1440 heartbeats)
2. ✓ Memory Behavior (no leaks)
3. ✓ Guardrails Enforcement (FAKE mode throughout)
4. ✓ Resource Baselines (CPU, RAM, Disk, Network)
5. ✓ Process & Dependency Health
6. ✓ Telemetry Completeness
7. ✓ Report/Logging Integrity
8. ✓ Arbitrage Loop Liveness

See `final_analysis.txt` for detailed results.
EOF

# Create tarball for easy sharing/archival
echo ""
echo "📦 Creating archive..."
tar -czf "${ARTIFACT_DIR}.tar.gz" "$ARTIFACT_DIR"
ARCHIVE_SIZE=$(du -h "${ARTIFACT_DIR}.tar.gz" | cut -f1)

# Summary
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "✅ Artifact Collection Complete"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📁 Directory: $ARTIFACT_DIR/"
echo "📦 Archive:   ${ARTIFACT_DIR}.tar.gz ($ARCHIVE_SIZE)"
echo ""
echo "Contents:"
echo "  - final_analysis.txt (8-point test evaluation)"
echo "  - test_metadata.txt (stats & parameters)"
echo "  - README.md (analysis guide)"
echo "  - ai_enhanced/ (all logs & reports)"
echo ""
echo "Next Steps:"
echo "  1. Review: cat $ARTIFACT_DIR/final_analysis.txt"
echo "  2. Share:  scp ${ARTIFACT_DIR}.tar.gz user@server:/path/"
echo "  3. Clean:  rm -rf $ARTIFACT_DIR ${ARTIFACT_DIR}.tar.gz"
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"

