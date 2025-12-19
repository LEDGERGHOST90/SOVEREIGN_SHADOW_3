# Manus → Claude Code → GitHub Integration Guide

## Overview

This guide explains how to automatically push crypto analysis from Manus to your GitHub repository (LedgerGhost90) using Claude Code as the bridge.

---

## Option 1: Direct Claude Code Push (Recommended)

### Step 1: Set Up GitHub Token

In Claude Code, create a GitHub Personal Access Token:
1. Go to GitHub → Settings → Developer Settings → Personal Access Tokens → Fine-grained tokens
2. Create new token with permissions:
   - `repo` (full control)
   - `workflow` (if using GitHub Actions)
3. Copy the token

### Step 2: In Claude Code Terminal

```bash
# Set your GitHub token
export GITHUB_TOKEN="ghp_your_token_here"

# Clone this analysis directory (or copy files)
git clone https://github.com/LedgerGhost90/crypto-analysis.git
cd crypto-analysis

# Copy analysis files from Manus output
# (Manus can provide these via file download)

# Push to GitHub
git add -A
git commit -m "Analysis update $(date +%Y-%m-%d)"
git push origin main
```

### Step 3: Automate with Claude Code

Tell Claude Code:
```
"Push the crypto analysis files to my LedgerGhost90/crypto-analysis repository"
```

Claude Code will:
1. Clone your repo
2. Copy the analysis files
3. Commit and push

---

## Option 2: Manus Webhook → GitHub Actions

### Step 1: Create GitHub Action

Add this file to your repo at `.github/workflows/sync-analysis.yml`:

```yaml
name: Sync Crypto Analysis from Manus

on:
  repository_dispatch:
    types: [manus-analysis-update]
  workflow_dispatch:
    inputs:
      analysis_url:
        description: 'URL to analysis JSON'
        required: false

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Download analysis from Manus
        run: |
          # If triggered via dispatch with payload
          if [ -n "${{ github.event.client_payload.analysis_data }}" ]; then
            echo '${{ github.event.client_payload.analysis_data }}' > data/latest_opportunities.json
          fi
      
      - name: Generate report
        run: |
          # Convert JSON to Markdown if needed
          python scripts/json_to_markdown.py || true
      
      - name: Commit and push
        run: |
          git config user.name "Manus Bot"
          git config user.email "manus@bot.com"
          git add -A
          git diff --staged --quiet || git commit -m "Analysis update from Manus"
          git push
```

### Step 2: Trigger from Manus

When Manus completes analysis, trigger the GitHub Action:

```bash
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/repos/LedgerGhost90/crypto-analysis/dispatches \
  -d '{"event_type":"manus-analysis-update","client_payload":{"analysis_data":"..."}}'
```

---

## Option 3: Claude Code as Middleware

### Workflow

```
Manus (Analysis) 
    ↓ [Export Files]
Claude Code (Bridge)
    ↓ [Git Push]
GitHub (LedgerGhost90)
    ↓ [GitHub Actions]
Your Apps/Dashboards
```

### Claude Code Script

Save this in Claude Code and run after each Manus analysis:

```python
import subprocess
import os

# Configuration
GITHUB_REPO = "LedgerGhost90/crypto-analysis"
BRANCH = "main"

def push_analysis(analysis_files):
    """Push analysis files to GitHub"""
    
    # Clone repo
    subprocess.run(["git", "clone", f"https://github.com/{GITHUB_REPO}.git", "repo"])
    os.chdir("repo")
    
    # Copy files
    for src, dst in analysis_files.items():
        subprocess.run(["cp", src, dst])
    
    # Commit and push
    subprocess.run(["git", "add", "-A"])
    subprocess.run(["git", "commit", "-m", "Analysis update"])
    subprocess.run(["git", "push", "origin", BRANCH])
    
    print(f"Pushed to {GITHUB_REPO}")

# Example usage
push_analysis({
    "/path/to/ELITE_TOKEN_TRADING_REPORT.md": "README.md",
    "/path/to/elite_token_opportunities.json": "data/latest.json"
})
```

---

## Option 4: Scheduled Sync (Cron)

### GitHub Action with Schedule

```yaml
name: Scheduled Analysis Sync

on:
  schedule:
    - cron: '0 */4 * * *'  # Every 4 hours
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Fetch from Manus API
        env:
          MANUS_API_KEY: ${{ secrets.MANUS_API_KEY }}
        run: |
          # Call Manus API to get latest analysis
          curl -H "Authorization: Bearer $MANUS_API_KEY" \
            https://api.manus.ai/analysis/latest \
            -o data/latest_opportunities.json
      
      - name: Update README
        run: |
          # Generate updated README from JSON
          python scripts/generate_readme.py
      
      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add -A
          git diff --staged --quiet || git commit -m "Scheduled analysis update"
          git push
```

---

## Quick Start Commands

### For Claude Code (copy-paste ready):

```bash
# 1. Set up authentication
export GITHUB_TOKEN="your_token_here"

# 2. Clone your repo
git clone https://github.com/LedgerGhost90/crypto-analysis.git
cd crypto-analysis

# 3. Create directory structure
mkdir -p analysis/daily data scripts

# 4. Copy Manus analysis files (adjust paths as needed)
cp /path/to/ELITE_TOKEN_TRADING_REPORT.md README.md
cp /path/to/elite_token_opportunities.json data/latest_opportunities.json

# 5. Commit and push
git add -A
git commit -m "Crypto analysis update $(date +%Y-%m-%d_%H-%M)"
git push origin main

echo "Done! Check: https://github.com/LedgerGhost90/crypto-analysis"
```

---

## Repository Structure

```
LedgerGhost90/crypto-analysis/
├── README.md                          # Latest analysis report
├── CLAUDE_CODE_INSTRUCTIONS.md        # Integration guide
├── analysis/
│   └── daily/
│       ├── REPORT_2025-12-18.md
│       └── REPORT_2025-12-17.md
├── data/
│   ├── latest_opportunities.json      # Current opportunities
│   └── opportunities_2025-12-18.json  # Historical
├── scripts/
│   ├── elite_token_analysis.py        # Analysis script
│   ├── claude_code_push.py            # Push automation
│   └── generate_readme.py             # Report generator
└── .github/
    └── workflows/
        └── sync-analysis.yml          # GitHub Action
```

---

## Troubleshooting

### Authentication Issues
```bash
# Check gh CLI auth
gh auth status

# Re-authenticate
gh auth login

# Or use token directly
git remote set-url origin https://TOKEN@github.com/LedgerGhost90/crypto-analysis.git
```

### Push Rejected
```bash
# Force push (careful - overwrites remote)
git push -f origin main

# Or pull first
git pull --rebase origin main
git push origin main
```

### Claude Code Can't Find Files
```bash
# List available files
ls -la /path/to/analysis/

# Check current directory
pwd
```

---

## Security Notes

1. **Never commit tokens** to the repository
2. Use **GitHub Secrets** for sensitive data in Actions
3. Use **fine-grained tokens** with minimal permissions
4. **Rotate tokens** periodically

---

*Last Updated: December 18, 2025*
