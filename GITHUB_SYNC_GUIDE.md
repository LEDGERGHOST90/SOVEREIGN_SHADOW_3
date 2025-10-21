# 🔄 GITHUB SYNC GUIDE - Sovereign Shadow Empire

**Quick reference for syncing your trading empire to GitHub**

Repository: `https://github.com/Memphispradda/sovereign_legacy_loop.git`
Branch: `main`
Status: ✅ Connected & Ready

---

## 🚀 QUICK COMMANDS

### 1. Check Status
```bash
cd /Volumes/LegacySafe/SovereignShadow
git status
```

Shows:
- Modified files (M)
- New files (?)
- Deleted files (D)
- Staged changes

### 2. Stage & Commit Everything
```bash
# Stage all changes
git add .

# Commit with message
git commit -m "🧠 Your commit message here

Detailed description if needed

🏴 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to GitHub
git push origin main
```

### 3. Pull Latest Changes
```bash
git pull origin main
```

---

## 📝 COMMIT MESSAGE TEMPLATES

### New Feature
```bash
git commit -m "✨ Add feature: BTC range scalper

- Optimized for $109K-$116K consolidation
- 3-step TP ladder implementation
- OTC spike detection
- Dynamic position sizing

🏴 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Bug Fix
```bash
git commit -m "🐛 Fix: Risk manager position limits

- Corrected max position calculation
- Fixed consecutive loss tracking
- Updated safety thresholds

🏴 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Documentation
```bash
git commit -m "📚 Docs: API integration guide

- Coinbase setup instructions
- OKX IP whitelist requirements
- Infura Web3 configuration

🏴 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Integration
```bash
git commit -m "🔗 Integrate: Neural consciousness + Shadow SDK

- AI orchestration layer complete
- Market regime detection
- Strategy selection logic
- 33/33 validation tests passed

🏴 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## 🌿 BRANCH WORKFLOW

### Create Feature Branch
```bash
# For API integration work
git checkout -b feature/api-integration

# Make changes...
git add .
git commit -m "WIP: API integration"

# Push feature branch
git push origin feature/api-integration
```

### Merge to Main
```bash
# Switch to main
git checkout main

# Merge feature branch
git merge feature/api-integration

# Push to GitHub
git push origin main

# Delete feature branch (optional)
git branch -d feature/api-integration
```

### Common Branches
```bash
feature/api-integration       # API key setup
feature/abacus-integration    # Abacus AI work
feature/strategy-development  # New strategies
hotfix/critical-bug          # Emergency fixes
```

---

## 🔍 VIEW HISTORY

### Recent Commits
```bash
# Last 10 commits (one line each)
git log --oneline -10

# Last 5 commits (detailed)
git log -5

# Commits with file changes
git log --stat -5

# Visual branch graph
git log --graph --oneline --all -10
```

### Specific File History
```bash
# See changes to specific file
git log -- MASTER_TRADING_LOOP.py

# Show file at specific commit
git show abc123:MASTER_TRADING_LOOP.py
```

---

## 🔄 SYNC WORKFLOWS

### Daily Workflow
```bash
# Morning: Pull latest
git pull origin main

# Work on files...
# (edit, create, delete)

# Evening: Commit & push
git add .
git commit -m "📊 Daily update: $(date +%Y-%m-%d)

- Market scanning improvements
- Strategy performance tracking
- Log analysis

🏴 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin main
```

### Before Major Changes
```bash
# Create backup branch
git checkout -b backup-$(date +%Y%m%d)
git push origin backup-$(date +%Y%m%d)

# Return to main
git checkout main

# Make your changes...
```

---

## ⚠️ HANDLE CONFLICTS

### Pull Conflict
```bash
git pull origin main
# ERROR: conflict in file.py

# Option 1: Keep your version
git checkout --ours file.py
git add file.py

# Option 2: Keep remote version
git checkout --theirs file.py
git add file.py

# Option 3: Manual merge
nano file.py  # Edit and resolve conflicts
git add file.py

# Complete merge
git commit
git push origin main
```

### Abort Merge
```bash
# If merge goes wrong, abort it
git merge --abort

# Reset to last commit
git reset --hard HEAD
```

---

## 🔐 SENSITIVE FILES

### Already Gitignored
```
.env                    # API keys
*.log                   # Log files
__pycache__/            # Python cache
node_modules/           # Node modules
.DS_Store               # Mac metadata
```

### Check Gitignore
```bash
# View ignored files
cat .gitignore

# Test if file is ignored
git check-ignore -v .env
```

### Remove Accidentally Committed Secret
```bash
# Remove from git but keep local
git rm --cached .env

# Commit removal
git commit -m "🔒 Security: Remove .env from tracking"
git push origin main
```

---

## 📊 USEFUL ALIASES

### Add to ~/.gitconfig
```bash
[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = log --graph --oneline --all
```

### Use Aliases
```bash
git st          # Instead of git status
git co main     # Instead of git checkout main
git visual      # Pretty branch graph
```

---

## 🚨 EMERGENCY COMMANDS

### Undo Last Commit (Keep Changes)
```bash
git reset --soft HEAD~1
```

### Undo Last Commit (Discard Changes)
```bash
git reset --hard HEAD~1
```

### Discard All Local Changes
```bash
git reset --hard HEAD
git clean -fd
```

### Restore Deleted File
```bash
git checkout HEAD -- deleted_file.py
```

---

## 📦 COMMIT YOUR CURRENT WORK

**Your recent changes to commit:**

```bash
cd /Volumes/LegacySafe/SovereignShadow

# Check what's changed
git status

# Stage everything
git add .

# Commit with descriptive message
git commit -m "🧠 Deploy neural trading empire + BTC scalper

Major Updates:
- Neural consciousness AI orchestration (90% confidence)
- BTC range scalper for $109K-$116K consolidation
- Shadow SDK full integration (33/33 tests passed)
- API integration tracker with IP whitelist
- Abacus AI integration roadmap
- GitHub sync documentation
- Comprehensive deployment guides

Components:
- neural_consciousness_integration.py
- btc_range_scalper_110k.py
- API_INTEGRATION_TRACKER.md
- GITHUB_SYNC_GUIDE.md
- NEURAL_STACK_DEPLOYMENT.md
- DEPLOYMENT_COMPLETE.md

Status: Operational & ready for live trading
Philosophy: Fearless. Bold. Smiling through chaos.

🏴 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to GitHub
git push origin main
```

---

## 🎯 CURRENT STATUS

**Repository:** Connected ✅
**Branch:** main
**Remote:** GitHub (Memphispradda/sovereign_legacy_loop)

**Recent Activity:**
- Last commit: Professional folder structure
- Pending changes: Neural consciousness + BTC scalper + docs
- Ready to push: Yes

**Your Next Command:**
```bash
cd /Volumes/LegacySafe/SovereignShadow && \
git add . && \
git commit -m "🧠 Deploy neural empire: AI consciousness + BTC scalper" && \
git push origin main
```

---

## 📚 REFERENCES

**Git Documentation:**
- Basics: https://git-scm.com/book/en/v2
- Workflow: https://www.atlassian.com/git/tutorials

**GitHub Help:**
- SSH Keys: https://docs.github.com/en/authentication
- Pull Requests: https://docs.github.com/en/pull-requests

**Your Repository:**
- URL: https://github.com/Memphispradda/sovereign_legacy_loop
- Clone: `git clone https://github.com/Memphispradda/sovereign_legacy_loop.git`

---

**Status:** GitHub sync ready
**Action:** Commit current work
**Philosophy:** "Fearless. Bold. Smiling through chaos."

🏴 **Your empire is version-controlled** 🏴
