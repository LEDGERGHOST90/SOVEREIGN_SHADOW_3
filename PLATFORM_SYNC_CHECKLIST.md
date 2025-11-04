# 🔄 PLATFORM SYNC CHECKLIST

**Purpose:** Keep Mobile, Mac, Cursor, Claude Code, and Website perfectly aligned
**Last Updated:** 2025-11-03

---

## 📱 MOBILE (Claude on Phone)

### Before Each Session:
- [ ] Check GitHub for latest commits
- [ ] Read `SYSTEM_STATUS_REPORT.md` for current state
- [ ] Review any recent changes in `SYSTEM_ALIGNMENT_MASTER.md`
- [ ] Check if any critical issues are listed

### What to Focus On:
- ✅ Architecture planning
- ✅ High-level strategy
- ✅ Documentation review
- ✅ Giving instructions to Claude Code
- ❌ Don't try to execute code
- ❌ Don't make file changes directly

### After Each Session:
- [ ] Note any decisions made
- [ ] Update docs if architecture changed
- [ ] Create tasks for Mac/Cursor implementation
- [ ] Inform Claude Code of next actions

---

## 💻 MAC (with Cursor IDE)

### Daily Startup Routine:
- [ ] `cd /path/to/SovereignShadow_II`
- [ ] `git fetch origin`
- [ ] `git pull origin claude/commit-push-011CUmEfr3xmbKF2s2zuamA5`
- [ ] Read `SYSTEM_STATUS_REPORT.md`
- [ ] Check running processes: `ps aux | grep python`
- [ ] Verify API keys: `cat config/.env` (check it exists)

### Before Coding:
- [ ] Open `SYSTEM_ALIGNMENT_MASTER.md` in Cursor
- [ ] Review the section you're working on
- [ ] Check for any "NEEDS" or "TODO" markers
- [ ] Verify dependencies are installed

### During Development:
- [ ] Test code locally before committing
- [ ] Update relevant documentation sections
- [ ] Add comments to complex logic
- [ ] Keep `SYSTEM_STATUS_REPORT.md` updated

### Before Closing:
- [ ] Run tests if available
- [ ] Commit with clear, descriptive message
- [ ] Push to feature branch
- [ ] Update `SYSTEM_STATUS_REPORT.md` with changes
- [ ] Note any issues for next session

---

## 🖥️ TERMINAL (Claude Code)

### Session Start:
- [ ] `cd /home/user/SovereignShadow_II`
- [ ] `git status` (check branch)
- [ ] `cat SYSTEM_STATUS_REPORT.md | head -50` (quick scan)
- [ ] `ps aux | grep python` (check what's running)

### During Session:
- [ ] Document any changes made
- [ ] Keep todo list updated
- [ ] Test commands before executing critical operations
- [ ] Log important findings

### Session End:
- [ ] Commit any file changes
- [ ] Push commits to branch
- [ ] Update `SYSTEM_STATUS_REPORT.md` if needed
- [ ] Stop running services (or leave running if monitoring)

---

## 🌐 WEBSITE / DOCUMENTATION

### Keep These Synced:
- [ ] `SYSTEM_ALIGNMENT_MASTER.md` → Website architecture page
- [ ] `QUICK_START_GUIDE.md` → Website getting started
- [ ] `SYSTEM_STATUS_REPORT.md` → Website status dashboard
- [ ] API documentation → Website API reference

### Update Frequency:
- **Daily:** System status
- **Weekly:** Architecture docs if changed
- **Per Release:** Full documentation review

---

## 🔄 CROSS-PLATFORM SYNC POINTS

### Every Morning:
```bash
# On Mac
git pull origin claude/commit-push-011CUmEfr3xmbKF2s2zuamA5

# Read these three files:
cat SYSTEM_ALIGNMENT_MASTER.md
cat SYSTEM_STATUS_REPORT.md
cat PLATFORM_SYNC_CHECKLIST.md

# Check what changed
git log --oneline -5
```

### After Major Changes:
1. [ ] Update `SYSTEM_ALIGNMENT_MASTER.md` (if structure changed)
2. [ ] Update `SYSTEM_STATUS_REPORT.md` (if status changed)
3. [ ] Update `QUICK_START_GUIDE.md` (if workflow changed)
4. [ ] Commit and push all three files together
5. [ ] Notify all platforms (mobile, Mac, website)

### Weekly Full Sync:
- [ ] Review all documentation for accuracy
- [ ] Test all quick start commands
- [ ] Update dependency versions
- [ ] Clean up old logs
- [ ] Archive resolved issues
- [ ] Update website documentation

---

## 📊 ALIGNMENT VERIFICATION

### Quick Check (Run Anytime):
```bash
#!/bin/bash
echo "=== ALIGNMENT CHECK ==="
echo ""
echo "1. Git Status:"
git status --short
echo ""
echo "2. Current Branch:"
git branch --show-current
echo ""
echo "3. Latest Commit:"
git log --oneline -1
echo ""
echo "4. Doc Files Present:"
ls -1 *.md | head -5
echo ""
echo "5. Last Modified:"
ls -lt *.md | head -5 | awk '{print $9, $6, $7, $8}'
```

**Save as:** `scripts/alignment_check.sh`

---

## 🎯 CONFLICT RESOLUTION

### If Docs Are Out of Sync:

**Problem:** Mobile has different info than Mac
**Solution:**
1. Check git commits for latest changes
2. Read `SYSTEM_STATUS_REPORT.md` first (most up-to-date)
3. If conflict, trust this priority:
   - Git commits (source of truth)
   - `SYSTEM_STATUS_REPORT.md` (current state)
   - `SYSTEM_ALIGNMENT_MASTER.md` (architecture)
   - Memory (least reliable)

**Problem:** Code doesn't match documentation
**Solution:**
1. Test the code to see actual behavior
2. Update docs to match reality
3. Or fix code to match desired behavior
4. Commit both together

**Problem:** Different platforms have different dependencies
**Solution:**
1. Check `config/requirements.txt` (source of truth)
2. Run `pip3 list` on each platform
3. Standardize using `pip3 install -r config/requirements.txt`
4. Update requirements.txt if new deps added

---

## 🔐 SECRETS & CREDENTIALS SYNC

### API Keys Location:
**File:** `config/.env` (gitignored)

### Keep These SEPARATE per Platform:
- 🚫 Never commit `.env` to git
- 🚫 Never share in docs
- 🚫 Never hardcode in Python files

### Sync Process:
1. Keep master copy in secure location (password manager)
2. Copy `.env.template` on each platform
3. Fill in from secure master copy
4. Verify with: `cat config/.env | grep KEY=`

### API Key Checklist:
- [ ] COINBASE_API_KEY set
- [ ] COINBASE_API_SECRET set
- [ ] OKX_API_KEY set (if using OKX)
- [ ] OKX_API_SECRET set
- [ ] OKX_API_PASSPHRASE set
- [ ] KRAKEN_API_KEY set (if using Kraken)
- [ ] KRAKEN_API_SECRET set
- [ ] ANTHROPIC_API_KEY set

---

## 📝 COMMIT MESSAGE STANDARDS

### Format:
```
<type>: <short description>

<detailed description if needed>
<list changes>
```

### Types:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

### Examples:
```
feat: Add arbitrage detection to Master Loop

- Implement cross-exchange price monitoring
- Add profit calculation after fees
- Create alert system for >1% opportunities

---

fix: Resolve hardcoded paths in MASTER_LOOP_CONTROL.sh

Replace /Volumes/LegacySafe/SovereignShadow with dynamic
path resolution based on script location.

---

docs: Create alignment documentation for all platforms

- SYSTEM_ALIGNMENT_MASTER.md
- SYSTEM_STATUS_REPORT.md
- QUICK_START_GUIDE.md
- PLATFORM_SYNC_CHECKLIST.md
```

---

## 🚨 EMERGENCY SYNC

### If Everything Is Out of Sync:

**Step 1: Establish Source of Truth**
```bash
# Pull absolute latest from GitHub
git fetch --all
git reset --hard origin/claude/commit-push-011CUmEfr3xmbKF2s2zuamA5

# This is now your source of truth
```

**Step 2: Read Core Docs**
```bash
cat SYSTEM_ALIGNMENT_MASTER.md
cat SYSTEM_STATUS_REPORT.md
```

**Step 3: Verify State**
```bash
# Check dependencies
pip3 list | grep -E "(aiohttp|ccxt|dotenv|fastapi)"

# Check configs
ls -la config/

# Check running processes
ps aux | grep python
```

**Step 4: Update All Platforms**
- Mobile: Note the git commit hash
- Mac: Pull the commit
- Terminal: Verify at commit
- Website: Update from docs

**Step 5: Test**
```bash
# Test basic system
./bin/START_API_SERVER.sh
curl http://localhost:8000/api/health
```

---

## ✅ DAILY CHECKLIST

### Morning (Before Starting):
- [ ] Check phone/mobile for any planning done
- [ ] Pull latest code on Mac
- [ ] Read system status report
- [ ] Verify what's running in terminal
- [ ] Check for any critical issues

### During Work:
- [ ] Keep docs updated as you code
- [ ] Commit frequently (every 30-60 minutes)
- [ ] Test changes immediately
- [ ] Document any issues found

### Evening (Before Finishing):
- [ ] Commit all changes
- [ ] Push to branch
- [ ] Update `SYSTEM_STATUS_REPORT.md`
- [ ] Note what to work on tomorrow
- [ ] Decide what to leave running overnight

---

## 📞 SYNC VERIFICATION COMMANDS

```bash
# Full sync check
git status
git log --oneline -5
git diff origin/claude/commit-push-011CUmEfr3xmbKF2s2zuamA5

# Doc freshness
ls -lt *.md | head -10

# System state
ps aux | grep python | grep -v grep
pip3 list | grep -E "(aiohttp|ccxt|dotenv|fastapi)"
ls -la config/.env

# Test connectivity
curl http://localhost:8000/api/health
```

---

## 🎯 SUCCESS CRITERIA

**You're Fully Synced When:**
- ✅ All platforms show same git commit hash
- ✅ All doc files have same content across platforms
- ✅ Dependencies match on all systems
- ✅ API keys configured (where needed)
- ✅ No confusion about what's running
- ✅ Status report reflects reality
- ✅ Website matches repository docs

**You Need to Sync When:**
- ❌ Different code versions across platforms
- ❌ Docs don't match actual behavior
- ❌ Unclear what systems are running
- ❌ Import errors or missing dependencies
- ❌ Confusion about project state

---

**Remember:** These four docs are your alignment anchors:
1. `SYSTEM_ALIGNMENT_MASTER.md` - Architecture
2. `SYSTEM_STATUS_REPORT.md` - Current state
3. `QUICK_START_GUIDE.md` - How to use
4. `PLATFORM_SYNC_CHECKLIST.md` - This file

**Keep them updated, keep them synced, keep them accessible!**

---

**Last Updated:** 2025-11-03
**Next Review:** After major changes or weekly

