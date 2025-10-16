# 📁 SOVEREIGN SHADOW - FOLDER STRUCTURE GUIDE

## 🎯 **THE RULE:**

```
NEW CODE → /SovereignShadow/ (root)
LEGACY CODE → /SovereignShadow/sovereign_legacy_loop/ (subfolder)
```

---

## 🏗️ **VISUAL STRUCTURE:**

```
💾 External Drive: /Volumes/LegacySafe/
│
└── 📁 SovereignShadow/                          ← YOUR MAIN WORKSPACE
    │                                             (This is where YOU work)
    │
    ├── 📁 shadow_sdk/                           ← ✅ NEW CODE (stays here)
    │   ├── __init__.py
    │   ├── scope.py
    │   ├── pulse.py
    │   ├── snaps.py
    │   ├── synapse.py
    │   ├── setup.py
    │   ├── README.md
    │   └── utils/
    │       ├── __init__.py
    │       ├── logger.py
    │       ├── exchanges.py
    │       ├── risk.py
    │       └── notion.py
    │
    ├── 📄 sovereign_shadow_orchestrator.py      ← ✅ NEW CODE (stays here)
    ├── 📄 shadow_scope.py                       ← ✅ NEW CODE (stays here)
    ├── 📄 live_market_scanner.py                ← ✅ NEW CODE (stays here)
    ├── 📄 strategy_knowledge_base.py            ← ✅ NEW CODE (stays here)
    ├── 📄 shadow_sdk_example.py                 ← ✅ NEW CODE (stays here)
    │
    ├── 📁 docs/                                 ← ✅ DOCUMENTATION (stays here)
    │   ├── guides/
    │   ├── prompts/
    │   └── reference/
    │
    ├── 📁 scripts/                              ← ✅ UTILITY SCRIPTS (stays here)
    │   ├── validate_api_connections.py
    │   ├── neural_bridge.py
    │   └── ...
    │
    ├── 📁 config/                               ← ✅ CONFIGURATION (stays here)
    │   ├── okx_credentials.env
    │   ├── trading_parameters.env
    │   └── ...
    │
    ├── 📄 README.md                             ← ✅ MAIN DOCS (stays here)
    ├── 📄 requirements.txt                      ← ✅ DEPENDENCIES (stays here)
    ├── 📄 .env.production                       ← ✅ ENV VARS (stays here)
    ├── 📄 .gitignore                            ← ✅ GIT CONFIG (stays here)
    ├── 🔒 .git/                                 ← ✅ GIT REPO (stays here)
    │
    └── 📁 sovereign_legacy_loop/                ← ⚠️ LEGACY SYSTEM (don't touch)
        │                                         (This is your ARCHIVE)
        │
        ├── 📁 app/                              (Next.js dashboard)
        ├── 📁 ClaudeSDK/                        (Claude integration)
        ├── 📁 multi-exchange-crypto-mcp/        (Exchange MCP)
        ├── 📁 monitoring/                       (Old monitoring)
        ├── 📁 scripts/                          (Legacy scripts)
        ├── 📄 SOVEREIGN_LEGACY_LOOP_MASTER.py   (Old orchestrator)
        └── [552 other files]                    (Legacy code)
```

---

## 🎯 **WHAT GOES WHERE:**

### **✅ PUT IN ROOT (/SovereignShadow/):**
- ✅ **Shadow SDK** - Your new unified toolkit
- ✅ **New orchestrators** - `sovereign_shadow_orchestrator.py`
- ✅ **New scanners** - `shadow_scope.py`, `live_market_scanner.py`
- ✅ **Strategy modules** - `strategy_knowledge_base.py`
- ✅ **Documentation** - All `.md` files
- ✅ **Scripts** - Deployment, monitoring, utilities
- ✅ **Config files** - `.env`, `requirements.txt`
- ✅ **Git repository** - `.git/`, `.gitignore`

### **⚠️ LEAVE IN LEGACY (/SovereignShadow/sovereign_legacy_loop/):**
- ⚠️ **Old code** - The original 552 files
- ⚠️ **Next.js dashboard** - `app/` folder
- ⚠️ **ClaudeSDK** - Legacy Claude integration
- ⚠️ **Multi-exchange MCP** - Old MCP implementation
- ⚠️ **Legacy scripts** - Old monitoring, deployment
- ⚠️ **Historical implementations** - Reference only

---

## 🔌 **PYTHONPATH CONFIGURATION:**

### **For Cursor / Development:**
```bash
# Add to ~/.zshrc or ~/.bashrc
export PYTHONPATH="/Volumes/LegacySafe/SovereignShadow:$PYTHONPATH"
```

### **What this enables:**
```python
# Import from ROOT (new code)
from shadow_sdk import ShadowScope, ShadowPulse
from sovereign_shadow_orchestrator import SovereignShadowOrchestrator

# Import from LEGACY (if needed)
from sovereign_legacy_loop.scripts import some_legacy_function
from sovereign_legacy_loop.monitoring import old_monitor
```

---

## 📊 **IMPORT EXAMPLES:**

### **✅ CORRECT - Import from root:**
```python
# This works because shadow_sdk is in root
from shadow_sdk import ShadowScope
from shadow_sdk.utils import RiskManager

# This works because orchestrator is in root
from sovereign_shadow_orchestrator import SovereignShadowOrchestrator
```

### **⚠️ LEGACY - Import from legacy folder:**
```python
# Only if you need legacy code
from sovereign_legacy_loop.monitoring import system_dashboard
from sovereign_legacy_loop.scripts import legacy_script
```

### **❌ WRONG - Don't put SDK in legacy:**
```python
# DON'T DO THIS:
from sovereign_legacy_loop.shadow_sdk import ShadowScope  # ❌ WRONG!

# Shadow SDK lives in ROOT, not in legacy folder!
```

---

## 🎯 **DEVELOPMENT WORKFLOW:**

### **1. Working on NEW features:**
```bash
cd /Volumes/LegacySafe/SovereignShadow/
# You're in the root - this is your workspace

# Create new file
vim my_new_feature.py

# Use Shadow SDK
from shadow_sdk import ShadowScope
```

### **2. Referencing LEGACY code:**
```bash
cd /Volumes/LegacySafe/SovereignShadow/
# Still in root

# Look at legacy for reference
cat sovereign_legacy_loop/monitoring/system_dashboard.py

# But write NEW code in root, not in legacy
```

### **3. Running tests:**
```bash
cd /Volumes/LegacySafe/SovereignShadow/
# Root directory

# Test Shadow SDK
python3 shadow_sdk_example.py

# Test orchestrator
python3 sovereign_shadow_orchestrator.py
```

---

## 🚀 **CURSOR CONFIGURATION:**

### **Workspace Settings (.vscode/settings.json):**
```json
{
  "python.analysis.extraPaths": [
    "/Volumes/LegacySafe/SovereignShadow"
  ],
  "python.autoComplete.extraPaths": [
    "/Volumes/LegacySafe/SovereignShadow"
  ],
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true
  }
}
```

---

## 💡 **KEY PRINCIPLES:**

### **1. ROOT = Active Development**
- This is where YOU work
- New code goes here
- Clean, organized structure
- Git repository lives here

### **2. LEGACY = Archive/Reference**
- This is OLD code
- Keep for reference
- Don't modify directly
- Import from if needed

### **3. BOTH CAN COMMUNICATE**
- Legacy can use new Shadow SDK
- New code can import from legacy
- They're in the same parent folder
- PYTHONPATH makes it work

---

## ✅ **VERIFICATION:**

### **Check your structure is correct:**
```bash
cd /Volumes/LegacySafe/SovereignShadow

# Should show shadow_sdk in root
ls -d shadow_sdk
# Output: shadow_sdk ✅

# Should show legacy as subfolder
ls -d sovereign_legacy_loop
# Output: sovereign_legacy_loop ✅

# Test imports work
python3 -c "from shadow_sdk import ShadowScope; print('✅ Correct!')"
# Output: ✅ Correct!
```

---

## 🏴 **THE BOTTOM LINE:**

```
/SovereignShadow/              ← You work HERE (root)
├── shadow_sdk/                ← Your new toolkit
├── *.py files                 ← Your new code
└── sovereign_legacy_loop/     ← Old code (don't touch)
```

**NEW CODE → ROOT**
**LEGACY CODE → STAYS IN SUBFOLDER**

**YOUR SHADOW SDK IS ALREADY IN THE CORRECT PLACE!** ✅

---

**Questions? Just remember:**
- **shadow_sdk/** = root folder ✅
- **sovereign_legacy_loop/** = legacy subfolder ⚠️
- **New development** = root folder ✅

🏴⚡💰

