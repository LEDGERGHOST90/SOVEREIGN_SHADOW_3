# 🏗️ Dev Container Architecture

## 🎯 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  macOS Host Machine (LegacySafe Drive)                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                                                          │  │
│  │  🖥️  Cursor IDE (Native macOS Application)             │  │
│  │                                                          │  │
│  │  User Interface:                                        │  │
│  │  • Editor                                               │  │
│  │  • Terminal                                             │  │
│  │  • Extensions UI                                        │  │
│  │  • Debugger                                             │  │
│  │                                                          │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                         │
│                       │ VS Code Remote Protocol                │
│                       │ (Communicates with container)          │
│                       │                                         │
│  ┌────────────────────┴─────────────────────────────────────┐  │
│  │                                                          │  │
│  │  🐳 Docker Engine (Docker Desktop)                      │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │                                                    │ │  │
│  │  │  📦 Dev Container (Linux)                         │ │  │
│  │  │                                                    │ │  │
│  │  │  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │ │  │
│  │  │  ┃  🐍 Python 3.11 Environment              ┃ │ │  │
│  │  │  ┃                                           ┃ │ │  │
│  │  │  ┃  Installed:                              ┃ │ │  │
│  │  │  ┃  • ccxt (Exchange APIs)                  ┃ │ │  │
│  │  │  ┃  • coinbase-advanced-py                  ┃ │ │  │
│  │  │  ┃  • pandas, numpy (Data)                  ┃ │ │  │
│  │  │  ┃  • websockets (Real-time)                ┃ │ │  │
│  │  │  ┃  • pytest, black, pylint (Dev tools)     ┃ │ │  │
│  │  │  ┃                                           ┃ │ │  │
│  │  │  ┃  Development Tools:                      ┃ │ │  │
│  │  │  ┃  • VS Code Server                        ┃ │ │  │
│  │  │  ┃  • Python Language Server (Pylance)      ┃ │ │  │
│  │  │  ┃  • Debugger (debugpy)                    ┃ │ │  │
│  │  │  ┃  • Git                                   ┃ │ │  │
│  │  │  ┃                                           ┃ │ │  │
│  │  │  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │ │  │
│  │  │                                                    │ │  │
│  │  │  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │ │  │
│  │  │  ┃  📁 Mounted Volumes                       ┃ │ │  │
│  │  │  ┃                                           ┃ │ │  │
│  │  │  ┃  /workspace → Your project files         ┃ │ │  │
│  │  │  ┃    (Live sync with macOS)                ┃ │ │  │
│  │  │  ┃                                           ┃ │ │  │
│  │  │  ┃  /workspace/.env → API keys              ┃ │ │  │
│  │  │  ┃    (Secure mount, never in image)        ┃ │ │  │
│  │  │  ┃                                           ┃ │ │  │
│  │  │  ┃  /workspace/logs → Log files             ┃ │ │  │
│  │  │  ┃    (Persisted)                           ┃ │ │  │
│  │  │  ┃                                           ┃ │ │  │
│  │  │  ┃  venv (Named volume)                     ┃ │ │  │
│  │  │  ┃    (Optimized for speed)                 ┃ │ │  │
│  │  │  ┃                                           ┃ │ │  │
│  │  │  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │ │  │
│  │  │                                                    │ │  │
│  │  │  User: trader (non-root)                          │ │  │
│  │  │  Shell: zsh with Oh My Zsh                        │ │  │
│  │  │                                                    │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │  Optional: PostgreSQL Container (Level 2)         │ │  │
│  │  │  Port: 5432                                        │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │  Optional: Redis Container (Level 2)              │ │  │
│  │  │  Port: 6379                                        │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  │                                                          │  │
│  │  Docker Network: shadow-dev-network                     │  │
│  │  (All containers can communicate)                       │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow

### 1. Code Editing Flow
```
User types in Cursor
    ↓
Cursor (macOS) → VS Code Server (Container)
    ↓
File changes written to /workspace
    ↓
Mounted volume syncs to macOS filesystem
    ↓
Changes appear in /Volumes/LegacySafe/SovereignShadow
```

### 2. Script Execution Flow
```
User runs: python3 scripts/validate_api_connections.py
    ↓
Command sent to container shell
    ↓
Python interpreter in container executes
    ↓
Script reads .env from mounted volume
    ↓
Makes API calls to exchanges
    ↓
Writes logs to /workspace/logs
    ↓
Logs persist on macOS
```

### 3. Debugging Flow
```
User sets breakpoint in Cursor
    ↓
Cursor → debugpy (in container)
    ↓
Script pauses at breakpoint
    ↓
User inspects variables
    ↓
Step through code
    ↓
All in isolated container environment
```

---

## 📊 Component Breakdown

### Layer 1: macOS Host
```
┌─────────────────────────────────────┐
│  Your Physical Machine              │
│                                     │
│  • Cursor application runs here    │
│  • Docker Desktop runs here        │
│  • Your files stored here          │
│  • .env secrets stored here        │
│                                     │
└─────────────────────────────────────┘
```

**Responsibilities:**
- Run Cursor UI
- Manage Docker engine
- Store source code
- Secure API keys

### Layer 2: Docker Engine
```
┌─────────────────────────────────────┐
│  Docker Desktop (macOS)             │
│                                     │
│  • Manages containers              │
│  • Handles volume mounts           │
│  • Network isolation               │
│  • Resource allocation             │
│                                     │
└─────────────────────────────────────┘
```

**Responsibilities:**
- Container lifecycle
- Volume mapping
- Network creation
- Resource limits

### Layer 3: Dev Container
```
┌─────────────────────────────────────┐
│  Linux Container (Debian-based)     │
│                                     │
│  • Python environment              │
│  • VS Code Server                  │
│  • Development tools               │
│  • Your workspace files            │
│                                     │
└─────────────────────────────────────┘
```

**Responsibilities:**
- Code execution
- Dependency isolation
- Development environment
- Tool integration

---

## 🔌 Connection Mechanisms

### VS Code Remote Protocol
```
Cursor (macOS)  ←→  VS Code Server (Container)
     │                      │
     │  1. Command          │
     ├──────────────────────→
     │                      │
     │  2. Execute          │
     │                      ├─→ Python script
     │                      │
     │  3. Result           │
     ←──────────────────────┤
     │                      │
```

**What's transmitted:**
- Keystrokes
- File edits
- Terminal commands
- Debug commands
- Extension requests

**What's NOT transmitted:**
- Large file contents (cached locally in container)
- Binary data
- Already synced files

---

## 💾 Volume Mount Strategy

### Bind Mount (Live Sync)
```
macOS                          Container
─────────────────────────────────────────
/Volumes/.../SovereignShadow  →  /workspace
├── scripts/                  →  /workspace/scripts/
├── shadow_sdk/               →  /workspace/shadow_sdk/
├── .env (secure)             →  /workspace/.env
└── logs/                     →  /workspace/logs/
```

**Characteristics:**
- ✅ Changes instantly reflected both ways
- ✅ No data duplication
- ⚠️ Slight I/O performance overhead
- ✅ Safe - can't lose data

### Named Volume (Performance)
```
Docker Volume                 Container
─────────────────────────────────────────
sovereign-shadow-venv         →  /workspace/venv/
├── lib/                      →  (Isolated)
├── bin/                      →  (Optimized)
└── site-packages/            →  (Fast access)
```

**Characteristics:**
- ✅ Much faster than bind mounts
- ✅ Optimized for containers
- ⚠️ Not visible on macOS (that's OK)
- ✅ Persists across rebuilds

---

## 🔐 Security Architecture

### API Key Isolation
```
.env file on macOS
    ↓ (mounted at runtime)
Container /workspace/.env
    ↓ (read by scripts)
Environment variables in memory
    ↓ (used by CCXT, Coinbase SDK)
Exchange APIs
```

**Security Features:**
1. **Never in Docker Image**
   - .env in .dockerignore
   - Only mounted at runtime
   - Can't leak via image push

2. **Proper Permissions**
   - Read-only mount possible
   - Container user has limited access
   - Can't accidentally delete

3. **Network Isolation**
   - Private Docker network
   - No exposure to host network
   - Controlled port forwarding

---

## 🚀 Build & Launch Process

### First Time Build
```
1. Read devcontainer.json
   ↓
2. Build Docker image from Dockerfile
   • Pull base image (python:3.11-slim)
   • Install system packages
   • Create user 'trader'
   • Install Python tools
   ↓
3. Create container from image
   ↓
4. Mount volumes
   • Bind mount workspace
   • Bind mount .env
   • Create named volume for venv
   ↓
5. Run postCreateCommand.sh
   • Install requirements.txt
   • Configure shell
   • Set up aliases
   ↓
6. Install VS Code Server
   ↓
7. Install extensions
   ↓
8. Connect Cursor to VS Code Server
   ↓
9. Ready! 🎉
```

**Time:** 2-5 minutes

### Subsequent Launches
```
1. Read devcontainer.json
   ↓
2. Find existing container
   ↓
3. Start container
   ↓
4. Mount volumes
   ↓
5. Connect Cursor
   ↓
6. Ready! 🎉
```

**Time:** 10-30 seconds

---

## 🎚️ Progressive Complexity

### Level 1: Basic Container (Current)
```
┌────────────────────────┐
│  Dev Container         │
│  • Python 3.11        │
│  • Trading libraries  │
│  • Dev tools          │
│  • Your code          │
└────────────────────────┘
```

### Level 2: With Services
```
┌────────────────────────┐     ┌────────────────┐
│  Dev Container         │────→│  PostgreSQL    │
│  • Python 3.11        │     └────────────────┘
│  • Trading libraries  │
│  • Dev tools          │     ┌────────────────┐
│  • Your code          │────→│  Redis         │
└────────────────────────┘     └────────────────┘
```

### Level 3: Full Stack
```
┌────────────────────────┐     ┌────────────────┐
│  Dev Container         │────→│  PostgreSQL    │
│  • Python Backend     │     └────────────────┘
│  • Trading scripts    │
└────────────────────────┘     ┌────────────────┐
                              │  Redis         │
┌────────────────────────┐     └────────────────┘
│  Frontend Container    │
│  • Next.js            │     ┌────────────────┐
│  • Dashboard          │────→│  MCP Server    │
└────────────────────────┘     └────────────────┘
```

---

## 🔄 File Synchronization Details

### What Syncs Instantly
- ✅ Source code (.py, .ts, .tsx, etc.)
- ✅ Configuration files (.json, .yaml, .env)
- ✅ Scripts (.sh)
- ✅ Documentation (.md)

### What's Optimized
- ⚡ Python packages (in named volume)
- ⚡ Node modules (in named volume)
- ⚡ Cache directories (in named volume)

### What's Excluded
- 🚫 __pycache__/ (generated in container)
- 🚫 *.pyc (generated in container)
- 🚫 .DS_Store (macOS only)
- 🚫 Docker images (Docker layer)

---

## 🎯 Performance Characteristics

### Read Operations
```
Read file in container:
File on macOS → Docker volume driver → Container filesystem
                    ↓
               Cached in container
                    ↓
               Fast subsequent reads
```

**Speed:** First read ~10ms, cached reads ~1ms

### Write Operations
```
Write file in container:
Container filesystem → Docker volume driver → macOS filesystem
                                 ↓
                            Sync complete
```

**Speed:** ~10-50ms depending on file size

### Optimization
```
Frequently accessed files → Named volumes (venv, node_modules)
Source code → Bind mounts (need sync)
Static assets → Could use named volumes
Logs → Bind mounts (need to see on macOS)
```

---

## 🎨 Customization Points

### 1. Python Version
```dockerfile
# In Dockerfile
FROM python:3.11-slim-bullseye
# Change to: FROM python:3.12-slim-bullseye
```

### 2. System Packages
```dockerfile
# In Dockerfile
RUN apt-get install -y \
    your-package-here
```

### 3. VS Code Extensions
```json
// In devcontainer.json
"extensions": [
    "your-extension-id"
]
```

### 4. Environment Variables
```json
// In devcontainer.json
"containerEnv": {
    "YOUR_VAR": "value"
}
```

### 5. Port Forwarding
```json
// In devcontainer.json
"forwardPorts": [8080, 3000]
```

---

## 🔧 Maintenance

### Updating Dependencies
```bash
# 1. Add to requirements.txt on macOS
echo "new-package==1.0.0" >> requirements.txt

# 2. Rebuild container
⌘ + Shift + P → Dev Containers: Rebuild Container

# Or, install in running container:
pip install new-package
```

### Cleaning Up
```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Nuclear option (careful!)
docker system prune -a --volumes
```

### Backup Strategy
- ✅ Source code: On macOS (also in Git)
- ✅ .env file: On macOS (never in container)
- ✅ Logs: On macOS (mounted)
- ⚠️ Container state: Rebuild anytime from Dockerfile
- ⚠️ Named volumes: Backup if needed

---

## 🤔 FAQ

### How is this different from running Docker Compose?
**Docker Compose**: Runs your application in production-like setup  
**Dev Container**: Runs your development environment with IDE integration

### Can I use both?
**Yes!** Dev Container for coding, Docker Compose for testing deployment

### What if I break something?
**Just rebuild!** Your code is safe on macOS. Container is disposable.

### Performance on macOS?
**Good for most tasks.** File I/O has slight overhead, but optimizations help.

### Can others use my Dev Container?
**Yes!** They just need Docker and your .devcontainer config. They'll get identical environment.

---

**Next Steps:**
- Review `QUICK_START.md` for launch instructions
- Review `DEV_CONTAINERS_GUIDE.md` for detailed explanation
- Try launching with `./open-dev-container.sh`

🏴 Ready to build the empire!

