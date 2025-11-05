# 🏴 PERSISTENT STATE - Automated Hourly Updates

## Overview

Your `PERSISTENT_STATE.json` file will now automatically update every hour to maintain a fresh snapshot of your system status.

---

## 📦 What Was Created

### 1. Update Script
**Location:** `scripts/update_persistent_state.py`

**What It Does:**
- Updates PERSISTENT_STATE.json every hour
- Fetches current balance data (if APIs working)
- Updates psychology tracker state (strikes, lockouts)
- Updates trade journal statistics (win rate, total trades)
- Updates mentor system progress
- Checks disk space
- Logs all updates to `logs/persistent_state_updates.log`

### 2. Wrapper Script
**Location:** `bin/update_state_hourly.sh`

**What It Does:**
- Activates Python virtual environment
- Runs the update script
- Handles exit codes for monitoring

### 3. LaunchAgent Plist
**Location:** `config/com.sovereignshadow.state-updater.plist`

**What It Does:**
- Schedules hourly execution (every 3600 seconds)
- Runs at system load (immediate first run)
- Logs output to `logs/state_updater_stdout.log`
- Logs errors to `logs/state_updater_stderr.log`

---

## 🚀 Installation

### Option A: LaunchAgent (Recommended for macOS)

```bash
# 1. Copy plist to LaunchAgents folder
cp /Volumes/LegacySafe/SovereignShadow_II/config/com.sovereignshadow.state-updater.plist \
   ~/Library/LaunchAgents/

# 2. Load the agent (starts immediately + runs every hour)
launchctl load ~/Library/LaunchAgents/com.sovereignshadow.state-updater.plist

# 3. Verify it's running
launchctl list | grep sovereignshadow
```

**To stop:**
```bash
launchctl unload ~/Library/LaunchAgents/com.sovereignshadow.state-updater.plist
```

**To restart:**
```bash
launchctl unload ~/Library/LaunchAgents/com.sovereignshadow.state-updater.plist
launchctl load ~/Library/LaunchAgents/com.sovereignshadow.state-updater.plist
```

---

### Option B: Cron (Alternative Method)

```bash
# 1. Edit your crontab
crontab -e

# 2. Add this line (runs at the top of every hour)
0 * * * * /Volumes/LegacySafe/SovereignShadow_II/bin/update_state_hourly.sh

# 3. Save and exit (ESC then :wq in vim)
```

**To verify cron job:**
```bash
crontab -l
```

**To remove:**
```bash
crontab -e
# Delete the line, save and exit
```

---

## 🧪 Manual Testing

### Test the update script directly:
```bash
cd /Volumes/LegacySafe/SovereignShadow_II
python3 scripts/update_persistent_state.py
```

### Test the wrapper script:
```bash
/Volumes/LegacySafe/SovereignShadow_II/bin/update_state_hourly.sh
```

### Check if it actually updated:
```bash
# View last updated timestamp
cat PERSISTENT_STATE.json | python3 -c "import json,sys; print(json.load(sys.stdin)['last_updated'])"

# View full recent actions
cat PERSISTENT_STATE.json | python3 -c "import json,sys; print(json.dumps(json.load(sys.stdin)['recent_actions'], indent=2))"
```

---

## 📊 Monitoring

### Check Update Logs
```bash
# View update history
tail -50 /Volumes/LegacySafe/SovereignShadow_II/logs/persistent_state_updates.log

# Watch live updates (when running)
tail -f /Volumes/LegacySafe/SovereignShadow_II/logs/persistent_state_updates.log
```

### Check LaunchAgent Logs
```bash
# Standard output
tail -20 /Volumes/LegacySafe/SovereignShadow_II/logs/state_updater_stdout.log

# Errors (if any)
tail -20 /Volumes/LegacySafe/SovereignShadow_II/logs/state_updater_stderr.log
```

### Verify LaunchAgent Status
```bash
# Check if running
launchctl list | grep sovereignshadow

# Get detailed info
launchctl print gui/$(id -u)/com.sovereignshadow.state-updater
```

---

## 📝 What Gets Updated

The script automatically updates these sections:

### 1. Timestamp
```json
"last_updated": "2025-11-05T01:00:00-08:00"
```

### 2. Portfolio Data (if APIs working)
- Current balance values
- AAVE position health
- Exchange account status

### 3. Psychology State
```json
"trading_systems": {
  "psychology_tracker": {
    "strikes": 0,
    "locked_out": false
  }
}
```

### 4. Trade Statistics
```json
"trading_systems": {
  "trade_journal": {
    "total_trades": 5,
    "win_rate_percent": 60.0
  }
}
```

### 5. Disk Space
```json
"disk_space": {
  "used_percent": 3,
  "available_tb": 1.8
}
```

### 6. Recent Actions
```json
"recent_actions": {
  "last_auto_update": {
    "timestamp": "2025-11-05T01:00:00-08:00",
    "method": "automated_hourly"
  }
}
```

---

## ⚠️ Important Notes

### 1. External Drive Must Be Mounted
If your LegacySafe drive disconnects, the updates will fail. LaunchAgent will keep trying each hour.

### 2. API Rate Limits
The script respects API rate limits. If APIs fail, it uses cached data.

### 3. Virtual Environment
If you use a Python venv, the wrapper script automatically activates it.

### 4. Disk Space
Updates only take a few KB, so no disk space concerns.

### 5. Battery Impact
Minimal - script runs for <5 seconds per hour.

---

## 🔧 Troubleshooting

### LaunchAgent Not Running
```bash
# Check if loaded
launchctl list | grep sovereignshadow

# If not found, load it
launchctl load ~/Library/LaunchAgents/com.sovereignshadow.state-updater.plist
```

### Script Errors
```bash
# Check error log
cat /Volumes/LegacySafe/SovereignShadow_II/logs/state_updater_stderr.log

# Run manually to see errors
cd /Volumes/LegacySafe/SovereignShadow_II
python3 scripts/update_persistent_state.py
```

### No Updates Happening
```bash
# Verify script is executable
ls -la /Volumes/LegacySafe/SovereignShadow_II/scripts/update_persistent_state.py

# Should show: -rwxr-xr-x (the 'x' means executable)

# If not:
chmod +x /Volumes/LegacySafe/SovereignShadow_II/scripts/update_persistent_state.py
chmod +x /Volumes/LegacySafe/SovereignShadow_II/bin/update_state_hourly.sh
```

### Drive Path Changed
If you rename or move the LegacySafe drive, update the plist:
```bash
# Edit the plist
nano ~/Library/LaunchAgents/com.sovereignshadow.state-updater.plist

# Update paths to new location
# Save (Ctrl+O) and exit (Ctrl+X)

# Reload
launchctl unload ~/Library/LaunchAgents/com.sovereignshadow.state-updater.plist
launchctl load ~/Library/LaunchAgents/com.sovereignshadow.state-updater.plist
```

---

## 🎯 Quick Commands

```bash
# Install (one-time setup)
cp /Volumes/LegacySafe/SovereignShadow_II/config/com.sovereignshadow.state-updater.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.sovereignshadow.state-updater.plist

# Check status
launchctl list | grep sovereignshadow

# View logs
tail -20 /Volumes/LegacySafe/SovereignShadow_II/logs/persistent_state_updates.log

# Stop updates
launchctl unload ~/Library/LaunchAgents/com.sovereignshadow.state-updater.plist

# Start updates
launchctl load ~/Library/LaunchAgents/com.sovereignshadow.state-updater.plist

# Force manual update now
/Volumes/LegacySafe/SovereignShadow_II/bin/update_state_hourly.sh
```

---

## 🏴 Installation Complete

Once installed, your PERSISTENT_STATE.json will:
- ✅ Update automatically every hour
- ✅ Survive system reboots (auto-loads on startup)
- ✅ Log all updates for monitoring
- ✅ Gracefully handle API failures
- ✅ Keep your system state fresh

**Next step: Run the installation command to activate hourly updates.**
