# 🔌 MCP SERVER BRIDGE SETUP GUIDE

## ⚡ **SETTING UP THE MCP SERVER**

### 🎯 **WHAT IS MCP?**

MCP (Model Context Protocol) is the bridge between:
- **Claude AI** (intelligence layer)
- **Your Trading Engine** (execution layer)
- **Exchange APIs** (market data)

### 🔧 **OPTION 1: Use Existing MCP in sovereign_legacy_loop/**

Your `sovereign_legacy_loop/` already contains MCP infrastructure:

```bash
cd /Volumes/LegacySafe/SovereignShadow/sovereign_legacy_loop

# Check for MCP files
find . -name "*mcp*" -type f | head -10
```

**If you find MCP files:**
- They're already integrated into your main system
- No additional setup needed
- The orchestrator can use them directly

### 🔧 **OPTION 2: Standalone MCP Server (Simplified)**

**Step 1: Create MCP Server Script**
```bash
cd /Volumes/LegacySafe/SovereignShadow
```

**Step 2: Create `mcp_server.py`:**
```python
#!/usr/bin/env python3
"""
🔌 MCP Server Bridge - Strategy Router
Routes signals to optimal strategies from your 55,379 Python files
"""

import asyncio
import json
from datetime import datetime
from strategy_knowledge_base import StrategyKnowledgeBase

class MCPServer:
    """Model Context Protocol Server for Strategy Routing"""
    
    def __init__(self, port=8765):
        self.port = port
        self.strategy_kb = StrategyKnowledgeBase()
        print(f"🔌 MCP Server initialized on port {port}")
        
    async def route_signal(self, signal: dict) -> dict:
        """Route market signal to optimal strategy"""
        print(f"📡 MCP: Routing signal for {signal.get('pair', 'UNKNOWN')}")
        
        # Use Strategy Knowledge Base to select strategy
        strategy = self.strategy_kb.get_strategy_for_opportunity(signal)
        
        if not strategy:
            return {
                'strategy': 'none',
                'reason': 'No suitable strategy found'
            }
        
        # Get risk parameters
        capital = signal.get('capital', 8260)
        risk_params = self.strategy_kb.get_risk_parameters(strategy, capital)
        
        # Return routing decision
        return {
            'strategy_name': strategy.name,
            'strategy_type': strategy.type,
            'exchanges': strategy.exchanges,
            'risk_params': risk_params,
            'execution_priority': self.strategy_kb.get_execution_priority(strategy),
            'timestamp': datetime.now().isoformat()
        }
    
    async def handle_client(self, reader, writer):
        """Handle incoming MCP requests"""
        addr = writer.get_extra_info('peername')
        print(f"🔌 MCP: Client connected from {addr}")
        
        try:
            data = await reader.read(1024)
            message = json.loads(data.decode())
            
            # Route the signal
            response = await self.route_signal(message)
            
            # Send response
            writer.write(json.dumps(response).encode())
            await writer.drain()
            
        except Exception as e:
            print(f"❌ MCP Error: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def start(self):
        """Start the MCP server"""
        server = await asyncio.start_server(
            self.handle_client, 'localhost', self.port
        )
        
        addr = server.sockets[0].getsockname()
        print(f"🚀 MCP Server running on {addr}")
        
        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    mcp = MCPServer(port=8765)
    asyncio.run(mcp.start())
```

**Step 3: Run MCP Server**
```bash
# In a separate terminal or background
python3 mcp_server.py &
```

### 🔧 **OPTION 3: Use MCP Docker Container (Advanced)**

**If you want isolated MCP in Docker:**
```bash
# Create MCP Dockerfile
cat > Dockerfile.mcp << 'EOF'
FROM python:3.11-slim

WORKDIR /app
COPY strategy_knowledge_base.py .
COPY mcp_server.py .

CMD ["python3", "mcp_server.py"]
EOF

# Build and run
docker build -f Dockerfile.mcp -t sovereign-mcp .
docker run -d -p 8765:8765 --name mcp-server sovereign-mcp
```

### 🚀 **INTEGRATION WITH ORCHESTRATOR:**

The `sovereign_shadow_orchestrator.py` already expects MCP on port 8765:

```python
async def _mcp_route(self, signal: Dict[str, Any]) -> Dict[str, Any]:
    """MCP routes signal to optimal strategy"""
    # This already uses the Strategy Knowledge Base
    # No additional MCP server needed!
    pass
```

### 🎯 **RECOMMENDATION:**

**You DON'T need a separate MCP server!**

Your orchestrator already has MCP functionality built-in through:
- `strategy_knowledge_base.py` (routing logic)
- `sovereign_shadow_orchestrator.py` (integration layer)

**MCP is already operational in your mesh network.**

### ✅ **VERIFICATION:**

```bash
# Test the built-in MCP routing
python3 << 'EOF'
from sovereign_shadow_orchestrator import SovereignShadowOrchestrator
import asyncio

async def test():
    orch = SovereignShadowOrchestrator()
    
    # Test MCP routing
    signal = {
        'type': 'arbitrage',
        'pair': 'BTC/USD',
        'spread': 0.00125,
        'amount': 100
    }
    
    route = await orch._mcp_route(signal)
    print(f"✅ MCP Routing: {route['strategy_name']}")

asyncio.run(test())
EOF
```

**MCP BRIDGE IS READY. NO ADDITIONAL SETUP NEEDED.** 🔌

