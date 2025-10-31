# 🔧 MCP SERVER TROUBLESHOOTING GUIDE

## ❌ **"Could not attach MCP servers, sovereign shadow"**

### ✅ **FIXED ISSUES:**

1. **Import Path Fixed**: Changed from `/app/shadow_sdk` to `os.path.dirname(__file__)`
2. **Simple Server Created**: `simple_mcp_server.py` - minimal working version
3. **Config Updated**: Points to the simple server now

---

## 🚀 **NEXT STEPS:**

### **1. Restart Claude Desktop**
```bash
# Quit Claude Desktop completely
# Then reopen it
```

### **2. Test Connection**
In Claude Desktop, ask:
```
What is my capital structure?
```

**Expected Response:**
```json
{
  "💰 Total Capital": "$10,811",
  "🔒 Ledger (Cold Storage)": "$6,600", 
  "🔥 Coinbase (Hot Wallet)": "$1,660",
  "🏦 AAVE Position": "$2,397 net",
  "📊 Health Factor": "2.49 (SAFE)"
}
```

---

## 🔍 **IF STILL NOT WORKING:**

### **Check 1: Server File Exists**
```bash
ls -la /Volumes/LegacySafe/SovereignShadow/shadow_sdk/simple_mcp_server.py
```

### **Check 2: Python Path**
```bash
cd /Volumes/LegacySafe/SovereignShadow
source .venv/bin/activate
python3 shadow_sdk/simple_mcp_server.py
```
Should start without errors.

### **Check 3: Claude Desktop Logs**
```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

### **Check 4: Config File**
```bash
cat "/Users/memphis/Library/Application Support/Claude/claude_desktop_config.json"
```

---

## 🛠️ **ALTERNATIVE: Manual Test**

If MCP still fails, test the server manually:

```bash
cd /Volumes/LegacySafe/SovereignShadow
source .venv/bin/activate
python3 shadow_sdk/simple_mcp_server.py
```

Then in another terminal:
```bash
# Test the server responds
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | python3 shadow_sdk/simple_mcp_server.py
```

---

## 📋 **CURRENT CONFIG:**

**Claude Desktop Config:**
```json
{
  "mcpServers": {
    "sovereign-shadow": {
      "command": "python3",
      "args": ["/Volumes/LegacySafe/SovereignShadow/shadow_sdk/simple_mcp_server.py"],
      "env": {
        "SHADOW_MODE": "production",
        "PORTFOLIO_ACTIVE": "1660",
        "PORTFOLIO_COLD": "6600",
        "AAVE_BORROWED": "1151",
        "HEALTH_FACTOR": "2.49",
        "PYTHONPATH": "/Volumes/LegacySafe/SovereignShadow"
      }
    }
  }
}
```

---

## ✅ **SUCCESS INDICATORS:**

1. **Claude Desktop starts without MCP errors**
2. **Can ask "What is my capital?" and get portfolio data**
3. **Can ask "What is my status?" and get system info**
4. **No error messages in Claude Desktop**

---

**Try restarting Claude Desktop now!** 🚀
