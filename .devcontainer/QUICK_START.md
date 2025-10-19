# 🚀 Dev Container Quick Start Guide

## 🎯 What You Just Got

A **fully configured development container** for Sovereign Shadow that includes:
- ✅ Python 3.11 with all trading dependencies
- ✅ Development tools (debugger, linters, formatters)
- ✅ VS Code extensions pre-installed
- ✅ Zsh with Oh My Zsh
- ✅ Custom trading aliases and shortcuts
- ✅ Secure .env mounting (never copied into image)
- ✅ Optional: PostgreSQL + Redis (Level 2)

---

## 🏁 Method 1: Open in Cursor (Easiest)

### Step 1: Open Command Palette
```
⌘ + Shift + P (Mac)
Ctrl + Shift + P (Windows/Linux)
```

### Step 2: Type and Select
```
Dev Containers: Reopen in Container
```

### Step 3: Wait for Build
- First time: 2-5 minutes
- Subsequent times: 10-30 seconds (cached)

### Step 4: You're In!
Look at your terminal - it should say `trader@<container-id>:/workspace$`

---

## 🏁 Method 2: Open via CLI (What You Asked About)

### For Basic Container (Level 1)
```bash
# Navigate to project
cd /Volumes/LegacySafe/SovereignShadow

# Generate hex-encoded config
CONF='{"settingType":"config", "workspacePath": "/Volumes/LegacySafe/SovereignShadow", "devcontainerPath": "/Volumes/LegacySafe/SovereignShadow/.devcontainer/devcontainer.json"}'
HEX_CONF=$(printf "$CONF" | od -A n -t x1 | tr -d '[\n\t ]')

# Open in Cursor
cursor --folder-uri "vscode-remote://dev-container+${HEX_CONF}/workspace"
```

### Shortcut Version (Save this as an alias)
Add to your `~/.zshrc`:
```bash
alias shadow-dev='cd /Volumes/LegacySafe/SovereignShadow && \
  CONF='"'"'{"settingType":"config", "workspacePath": "/Volumes/LegacySafe/SovereignShadow", "devcontainerPath": "/Volumes/LegacySafe/SovereignShadow/.devcontainer/devcontainer.json"}'"'"' && \
  HEX_CONF=$(printf "$CONF" | od -A n -t x1 | tr -d '"'"'[\n\t ]'"'"') && \
  cursor --folder-uri "vscode-remote://dev-container+${HEX_CONF}/workspace"'
```

Then just run:
```bash
shadow-dev
```

---

## 🧪 Verify It's Working

Once inside the container, run these commands:

### 1. Check Python Environment
```bash
python --version
# Should show: Python 3.11.x
```

### 2. Check Dependencies
```bash
pip list | grep ccxt
pip list | grep coinbase
```

### 3. Check Your Custom Aliases
```bash
# Try these shortcuts:
ss          # Go to workspace
status      # Check API status
balance     # Get real balances
```

### 4. Verify .env Access
```bash
ls -la .env
# Should exist and show your API keys
```

### 5. Run a Test Script
```bash
python3 FINAL_API_STATUS.py
# Should connect to APIs without errors
```

---

## 📁 Understanding the File Structure

### In Container
```
/workspace/                    ← Your project (mounted from Mac)
├── .env                       ← Securely mounted (not in image)
├── scripts/                   ← All your scripts
├── shadow_sdk/                ← Shadow SDK
├── sovereign_legacy_loop/     ← Main system
└── logs/                      ← Logs (persisted)
```

### On Your Mac
```
/Volumes/LegacySafe/SovereignShadow/
└── .devcontainer/             ← Container config (new!)
    ├── devcontainer.json      ← Main config
    ├── Dockerfile             ← Image definition
    ├── postCreateCommand.sh   ← Setup script
    └── docker-compose.dev.yml ← Optional services
```

---

## 🎚️ Level 2: Add Database Services (Optional)

If you need PostgreSQL or Redis for testing:

### Step 1: Modify devcontainer.json
Uncomment this line in `.devcontainer/devcontainer.json`:
```json
// "dockerComposeFile": "docker-compose.dev.yml",
```

### Step 2: Rebuild Container
```
⌘ + Shift + P → Dev Containers: Rebuild Container
```

### Step 3: Access Services
```python
# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=trader
POSTGRES_PASSWORD=devpassword123
POSTGRES_DB=shadow_dev

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=devredis123
```

---

## 🔧 Common Commands Inside Container

### Trading Operations
```bash
# Check API status
python3 FINAL_API_STATUS.py

# Get real balances
python3 scripts/get_real_balances.py

# Live market snapshot
python3 instant_market_snapshot.py

# Start paper trading
./START_SOVEREIGN_SHADOW.sh paper

# Start live trading (careful!)
./START_SOVEREIGN_SHADOW.sh live
```

### Development
```bash
# Format code
black .

# Sort imports
isort .

# Run linter
pylint scripts/*.py

# Run tests (if you have them)
pytest tests/
```

### Container Management
```bash
# View running containers
docker ps

# Check container logs
docker logs <container-id>

# Restart container (from outside)
docker restart <container-id>
```

---

## 🐛 Troubleshooting

### Problem: Container won't build
**Solution:**
```bash
# Clean Docker cache
docker system prune -a

# Rebuild from scratch
⌘ + Shift + P → Dev Containers: Rebuild Container Without Cache
```

### Problem: Can't see .env file
**Solution:**
```bash
# On your Mac, check if .env exists
ls -la /Volumes/LegacySafe/SovereignShadow/.env

# Inside container
ls -la /workspace/.env

# If missing, create it on your Mac first
```

### Problem: Import errors
**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify PYTHONPATH
echo $PYTHONPATH
# Should include: /workspace
```

### Problem: Permission errors
**Solution:**
```bash
# Check ownership
ls -la /workspace

# Fix if needed (from container)
sudo chown -R trader:trader /workspace
```

### Problem: Slow performance on macOS
**Solution:**
This is normal for Docker on Mac. Optimizations already in place:
- Volume consistency set to `cached`
- Named volumes for venv and caches
- SSD recommended for best performance

---

## 🔄 Rebuilding the Container

### When to Rebuild:
- ✅ After adding new dependencies to requirements.txt
- ✅ After modifying Dockerfile or devcontainer.json
- ✅ When container becomes corrupted
- ✅ To get latest base image updates

### How to Rebuild:
```
⌘ + Shift + P → Dev Containers: Rebuild Container
```

Or force rebuild without cache:
```
⌘ + Shift + P → Dev Containers: Rebuild Container Without Cache
```

---

## 🚪 Exiting the Container

### Option 1: Close Cursor
Just close Cursor - container stops automatically (unless configured otherwise)

### Option 2: Reopen on Host
```
⌘ + Shift + P → Dev Containers: Reopen Folder Locally
```

### Option 3: Keep Container Running
Add to devcontainer.json:
```json
"shutdownAction": "stopContainer"
```

---

## 🎯 Next Steps

### 1. Validate Everything Works
```bash
# Inside container
python3 scripts/validate_api_connections.py
```

### 2. Start Developing
Your normal workflow, but inside container:
- Edit files (changes save to your Mac)
- Run scripts
- Debug with breakpoints
- All in isolated environment

### 3. Consider Level 2
If you need database testing:
- Uncomment docker-compose in devcontainer.json
- Rebuild container
- Access PostgreSQL and Redis locally

### 4. Customize Further
Edit `.devcontainer/devcontainer.json`:
- Add more VS Code extensions
- Change Python version
- Add system packages
- Configure settings

---

## 💡 Pro Tips

### Tip 1: Multiple Terminals
Open multiple terminals inside container (all share same environment):
```
⌘ + ` → New Terminal
```

### Tip 2: Port Forwarding
Container automatically forwards ports:
- 8000 (MCP Server)
- 3000 (Dashboard)
- 5432 (PostgreSQL, if Level 2)
- 6379 (Redis, if Level 2)

Access from browser: `http://localhost:<port>`

### Tip 3: Git from Container
Git operations work inside container:
```bash
git status
git add .
git commit -m "Trading improvements"
git push
```

### Tip 4: Use Host for Quick Checks
No need for container for simple tasks:
- Reading logs: Use host terminal
- Git operations: Use host terminal
- Quick file edits: Use host editor

### Tip 5: Persist Custom Configs
Add to postCreateCommand.sh for configs that persist across rebuilds

---

## 📚 Resources

- **Full Guide**: `/workspace/DEV_CONTAINERS_GUIDE.md`
- **Project README**: `/workspace/README.md`
- **Documentation**: `/workspace/Master_LOOP_Creation/`
- **Dev Container Docs**: https://containers.dev/

---

## ✅ Checklist

After first launch, verify:
- [ ] Python 3.11 installed
- [ ] Dependencies from requirements.txt installed
- [ ] .env file accessible
- [ ] Custom aliases work (try `ss`, `status`)
- [ ] Can run `python3 FINAL_API_STATUS.py`
- [ ] Logs directory exists and writable
- [ ] Git operations work
- [ ] VS Code extensions loaded

---

**You're ready to trade! 🏴**

Fearless. Bold. Smiling through chaos.

