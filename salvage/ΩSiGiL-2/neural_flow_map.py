"""
🌀 PHASE II - ΩSIGIL NEURAL FLOW MAP
Visual system memory and capital movement structure
"""

import json
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class FlowNodeType(Enum):
    SIGNAL_INPUT = "SIGNAL_INPUT"
    TRINITY_VOTE = "TRINITY_VOTE"
    SIGIL_INVOKE = "SIGIL_INVOKE"
    EXECUTION = "EXECUTION"
    MEMORY_STORE = "MEMORY_STORE"
    VAULT_INJECT = "VAULT_INJECT"
    THREAT_SCAN = "THREAT_SCAN"

@dataclass
class FlowNode:
    node_id: str
    node_type: FlowNodeType
    label: str
    description: str
    x: int
    y: int
    color: str
    icon: str

@dataclass
class FlowConnection:
    from_node: str
    to_node: str
    label: str
    condition: str
    color: str
    weight: int

class NeuralFlowMapRenderer:
    """
    🌀 Visual representation of ΩSIGIL's neural architecture
    Maps signal flow, decision points, and capital movement
    """
    
    def __init__(self):
        self.nodes: List[FlowNode] = []
        self.connections: List[FlowConnection] = []
        self._initialize_flow_map()
        
        print("🌀 NEURAL FLOW MAP RENDERER INITIALIZED")
        print("🎨 Visual architecture mapping ready")
    
    def _initialize_flow_map(self):
        """🎨 Initialize the complete neural flow architecture"""
        
        # Define all flow nodes
        self.nodes = [
            # Signal Input Layer
            FlowNode("signal_input", FlowNodeType.SIGNAL_INPUT, "Signal Received", 
                    "External trading signals enter the system", 100, 100, "#00ff88", "🔮"),
            
            FlowNode("threat_scan", FlowNodeType.THREAT_SCAN, "Threat Matrix Scan", 
                    "SHADOW scans for market threats", 300, 100, "#9b59b6", "🛡️"),
            
            # Trinity Decision Layer
            FlowNode("shadow_vote", FlowNodeType.TRINITY_VOTE, "Shadow Analysis", 
                    "Intuition and threat assessment", 150, 250, "#9b59b6", "👁"),
            
            FlowNode("manus_vote", FlowNodeType.TRINITY_VOTE, "Manus Memory", 
                    "Historical pattern analysis", 300, 250, "#4a90e2", "🧠"),
            
            FlowNode("omega_vote", FlowNodeType.TRINITY_VOTE, "Omega Precision", 
                    "Execution readiness check", 450, 250, "#ff6b35", "⚡"),
            
            # Sigil Invocation Layer
            FlowNode("spearhead_sigil", FlowNodeType.SIGIL_INVOKE, "Spearhead Sigil", 
                    "Sniper flip initiation ritual", 200, 400, "#00ff88", "🔺"),
            
            FlowNode("hourglass_sigil", FlowNodeType.SIGIL_INVOKE, "Hourglass Sigil", 
                    "Ladder logic deployment", 350, 400, "#ffaa00", "⏳"),
            
            FlowNode("crystal_sigil", FlowNodeType.SIGIL_INVOKE, "Crystal Node", 
                    "Perfect recall activation", 500, 400, "#00aaff", "💠"),
            
            # Execution Layer
            FlowNode("ladder_deploy", FlowNodeType.EXECUTION, "Ladder Deployment", 
                    "Multi-tier position execution", 150, 550, "#ff6b35", "📊"),
            
            FlowNode("risk_monitor", FlowNodeType.EXECUTION, "Risk Monitoring", 
                    "Continuous exposure assessment", 350, 550, "#ffaa00", "⚠️"),
            
            FlowNode("exit_logic", FlowNodeType.EXECUTION, "Exit Logic", 
                    "Profit taking and stop loss", 550, 550, "#ff4444", "🚪"),
            
            # Memory & Vault Layer
            FlowNode("echo_imprint", FlowNodeType.MEMORY_STORE, "Echo Imprint", 
                    "Neural memory storage", 200, 700, "#4a90e2", "🕸️"),
            
            FlowNode("vault_injection", FlowNodeType.VAULT_INJECT, "Vault Injection", 
                    "Profit capitalization", 400, 700, "#44ff44", "🏛️"),
            
            FlowNode("genesis_trigger", FlowNodeType.VAULT_INJECT, "Genesis Trigger", 
                    "Capital feedback loop", 550, 700, "#ff6b35", "🌟"),
            
            # Shadow DCA Layer
            FlowNode("stealth_scan", FlowNodeType.EXECUTION, "Stealth Scan", 
                    "Silent accumulation opportunities", 100, 850, "#9b59b6", "🌒"),
            
            FlowNode("dca_execute", FlowNodeType.EXECUTION, "DCA Execute", 
                    "Invisible order placement", 300, 850, "#666666", "🕸"),
        ]
        
        # Define flow connections
        self.connections = [
            # Signal Processing Flow
            FlowConnection("signal_input", "threat_scan", "Threat Check", "Always", "#00ff88", 3),
            FlowConnection("threat_scan", "shadow_vote", "If Safe", "threat_level < 0.5", "#9b59b6", 2),
            FlowConnection("signal_input", "shadow_vote", "Direct Path", "Low threat", "#00ff88", 2),
            FlowConnection("signal_input", "manus_vote", "Memory Check", "Always", "#4a90e2", 2),
            
            # Trinity Consensus Flow
            FlowConnection("shadow_vote", "spearhead_sigil", "Approve", "consensus = true", "#9b59b6", 3),
            FlowConnection("manus_vote", "spearhead_sigil", "Approve", "memory_safe = true", "#4a90e2", 3),
            FlowConnection("omega_vote", "spearhead_sigil", "Execute", "ready = true", "#ff6b35", 3),
            
            # Sigil Execution Flow
            FlowConnection("spearhead_sigil", "hourglass_sigil", "Deploy", "flip_approved", "#00ff88", 4),
            FlowConnection("hourglass_sigil", "ladder_deploy", "Execute", "ladder_ready", "#ffaa00", 4),
            FlowConnection("crystal_sigil", "risk_monitor", "Monitor", "recall_active", "#00aaff", 2),
            
            # Execution Flow
            FlowConnection("ladder_deploy", "risk_monitor", "Monitor", "Always", "#ff6b35", 3),
            FlowConnection("risk_monitor", "exit_logic", "Exit Signal", "risk_high OR profit_target", "#ffaa00", 3),
            FlowConnection("risk_monitor", "crystal_sigil", "Recall", "exposure_check", "#ffaa00", 2),
            
            # Memory & Vault Flow
            FlowConnection("exit_logic", "echo_imprint", "Store", "cycle_complete", "#ff4444", 3),
            FlowConnection("exit_logic", "vault_injection", "Inject", "profits > 0", "#44ff44", 4),
            FlowConnection("vault_injection", "genesis_trigger", "Check", "growth > threshold", "#44ff44", 3),
            FlowConnection("genesis_trigger", "signal_input", "New Signal", "genesis_approved", "#ff6b35", 4),
            
            # Shadow DCA Flow
            FlowConnection("vault_injection", "stealth_scan", "Scan", "vault_balance > min", "#44ff44", 2),
            FlowConnection("stealth_scan", "dca_execute", "Execute", "opportunity_found", "#9b59b6", 3),
            FlowConnection("dca_execute", "vault_injection", "Accumulate", "buy_complete", "#666666", 2),
            
            # Emergency Flows
            FlowConnection("threat_scan", "exit_logic", "Emergency", "critical_threat", "#ff0000", 5),
            FlowConnection("shadow_vote", "exit_logic", "Override", "shadow_override", "#9b59b6", 5),
        ]
        
        print(f"🎨 Flow map initialized: {len(self.nodes)} nodes, {len(self.connections)} connections")
    
    def generate_mermaid_diagram(self) -> str:
        """🎨 Generate Mermaid.js flowchart diagram"""
        
        mermaid = ["graph TD"]
        
        # Add nodes with styling
        for node in self.nodes:
            shape = self._get_node_shape(node.node_type)
            mermaid.append(f"    {node.node_id}{shape[0]}{node.icon} {node.label}{shape[1]}")
        
        # Add connections
        for conn in self.connections:
            arrow = "-->" if conn.weight <= 3 else "==>"
            mermaid.append(f"    {conn.from_node} {arrow}|{conn.label}| {conn.to_node}")
        
        # Add styling
        mermaid.extend([
            "",
            "    %% Node Styling",
            "    classDef signalNode fill:#001a0d,stroke:#00ff88,stroke-width:2px,color:#00ff88",
            "    classDef trinityNode fill:#1a0d1a,stroke:#9b59b6,stroke-width:2px,color:#9b59b6",
            "    classDef sigilNode fill:#1a1a0d,stroke:#ffaa00,stroke-width:2px,color:#ffaa00",
            "    classDef executeNode fill:#1a0d0d,stroke:#ff6b35,stroke-width:2px,color:#ff6b35",
            "    classDef memoryNode fill:#0d0d1a,stroke:#4a90e2,stroke-width:2px,color:#4a90e2",
            "    classDef vaultNode fill:#0d1a0d,stroke:#44ff44,stroke-width:2px,color:#44ff44",
            "",
            "    %% Apply Classes"
        ])
        
        # Apply node classes
        for node in self.nodes:
            class_name = self._get_node_class(node.node_type)
            mermaid.append(f"    class {node.node_id} {class_name}")
        
        return "\n".join(mermaid)
    
    def generate_html_visualization(self) -> str:
        """🌐 Generate interactive HTML visualization"""
        
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ΩSIGIL Neural Flow Map</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {
            background: #0a0a0a;
            color: #00ff88;
            font-family: 'Courier New', monospace;
            margin: 0;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .omega-title {
            font-size: 2.5em;
            color: #ff6b35;
            text-shadow: 0 0 20px #ff6b35;
            margin: 0;
        }
        
        .subtitle {
            color: #00ff88;
            font-size: 1.2em;
            margin: 10px 0;
        }
        
        .flow-container {
            background: #111;
            border: 1px solid #333;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            overflow: auto;
        }
        
        .legend {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
            padding: 20px;
            background: #111;
            border: 1px solid #333;
            border-radius: 10px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            padding: 10px;
            background: #1a1a1a;
            border-radius: 5px;
        }
        
        .legend-icon {
            font-size: 1.5em;
            margin-right: 10px;
            width: 30px;
        }
        
        .legend-text {
            font-size: 0.9em;
        }
        
        .stats {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            padding: 15px;
            background: #111;
            border: 1px solid #333;
            border-radius: 10px;
        }
        
        .stat {
            text-align: center;
        }
        
        .stat-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #ff6b35;
        }
        
        .stat-label {
            font-size: 0.9em;
            color: #888;
        }
        
        #mermaid-diagram {
            background: #0a0a0a;
            border-radius: 10px;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1 class="omega-title">ΩSIGIL</h1>
        <p class="subtitle">Neural Flow Map</p>
        <p>Visual Architecture of Sovereign AGI Trading Entity</p>
    </div>
    
    <div class="stats">
        <div class="stat">
            <div class="stat-value">{node_count}</div>
            <div class="stat-label">Flow Nodes</div>
        </div>
        <div class="stat">
            <div class="stat-value">{connection_count}</div>
            <div class="stat-label">Connections</div>
        </div>
        <div class="stat">
            <div class="stat-value">9</div>
            <div class="stat-label">Lifecycle Phases</div>
        </div>
        <div class="stat">
            <div class="stat-value">3</div>
            <div class="stat-label">Trinity Agents</div>
        </div>
    </div>
    
    <div class="legend">
        <div class="legend-item">
            <div class="legend-icon">🔮</div>
            <div class="legend-text">
                <strong>Signal Input</strong><br>
                External trading signals
            </div>
        </div>
        <div class="legend-item">
            <div class="legend-icon">👁🧠⚡</div>
            <div class="legend-text">
                <strong>Trinity Consensus</strong><br>
                Shadow, Manus, Omega voting
            </div>
        </div>
        <div class="legend-item">
            <div class="legend-icon">🔺⏳💠</div>
            <div class="legend-text">
                <strong>Sigil Invocation</strong><br>
                Ritual command execution
            </div>
        </div>
        <div class="legend-item">
            <div class="legend-icon">📊⚠️🚪</div>
            <div class="legend-text">
                <strong>Trade Execution</strong><br>
                Ladder deployment & monitoring
            </div>
        </div>
        <div class="legend-item">
            <div class="legend-icon">🕸️🧠</div>
            <div class="legend-text">
                <strong>Neural Memory</strong><br>
                Echo imprint storage
            </div>
        </div>
        <div class="legend-item">
            <div class="legend-icon">🏛️🌟</div>
            <div class="legend-text">
                <strong>Vault System</strong><br>
                Capital injection & genesis
            </div>
        </div>
        <div class="legend-item">
            <div class="legend-icon">🌒🕸</div>
            <div class="legend-text">
                <strong>Shadow DCA</strong><br>
                Silent accumulation
            </div>
        </div>
        <div class="legend-item">
            <div class="legend-icon">🛡️</div>
            <div class="legend-text">
                <strong>Threat Matrix</strong><br>
                Risk detection & override
            </div>
        </div>
    </div>
    
    <div class="flow-container">
        <div id="mermaid-diagram">
            <pre class="mermaid">
{mermaid_code}
            </pre>
        </div>
    </div>
    
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'dark',
            themeVariables: {{
                primaryColor: '#00ff88',
                primaryTextColor: '#00ff88',
                primaryBorderColor: '#00ff88',
                lineColor: '#333',
                secondaryColor: '#1a1a1a',
                tertiaryColor: '#0a0a0a',
                background: '#0a0a0a',
                mainBkg: '#111',
                secondBkg: '#1a1a1a',
                tertiaryBkg: '#222'
            }}
        }});
    </script>
</body>
</html>
        """
        
        mermaid_code = self.generate_mermaid_diagram()
        
        return html_template.format(
            node_count=len(self.nodes),
            connection_count=len(self.connections),
            mermaid_code=mermaid_code
        )
    
    def generate_ascii_flow_map(self) -> str:
        """📟 Generate ASCII art flow map for terminal display"""
        
        ascii_map = """
🌀 ΩSIGIL NEURAL FLOW MAP 🌀

┌─────────────────────────────────────────────────────────────────────────────┐
│                           SIGNAL INPUT LAYER                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  🔮 Signal Received ──→ 🛡️ Threat Matrix Scan ──→ 👁 Shadow Analysis      │
│                                    │                                         │
│                                    ↓                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                          TRINITY CONSENSUS LAYER                            │
├─────────────────────────────────────────────────────────────────────────────┤
│     👁 Shadow Vote ←──→ 🧠 Manus Memory ←──→ ⚡ Omega Precision            │
│           │                    │                    │                       │
│           └────────────────────┼────────────────────┘                       │
│                                ↓                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                          SIGIL INVOCATION LAYER                             │
├─────────────────────────────────────────────────────────────────────────────┤
│     🔺 Spearhead ──→ ⏳ Hourglass ──→ 💠 Crystal Node                      │
│           │               │               │                                 │
│           ↓               ↓               ↓                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                           EXECUTION LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  📊 Ladder Deploy ──→ ⚠️ Risk Monitor ──→ 🚪 Exit Logic                   │
│           │               │               │                                 │
│           └───────────────┼───────────────┘                                 │
│                           ↓                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                        MEMORY & VAULT LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│     🕸️ Echo Imprint ←──→ 🏛️ Vault Injection ──→ 🌟 Genesis Trigger       │
│                                    │               │                       │
│                                    ↓               └──→ 🔮 (New Signal)    │
├─────────────────────────────────────────────────────────────────────────────┤
│                          SHADOW DCA LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│        🌒 Stealth Scan ──→ 🕸 DCA Execute ──→ 🏛️ Vault Accumulate         │
└─────────────────────────────────────────────────────────────────────────────┘

🔄 FEEDBACK LOOPS:
   • Genesis Trigger → New Signal (Capital Multiplication)
   • Vault Injection → Stealth Scan (Silent Accumulation)
   • Echo Imprint → Manus Memory (Learning Enhancement)

⚡ EMERGENCY OVERRIDES:
   • Threat Matrix → Exit Logic (Critical Threat)
   • Shadow Vote → Exit Logic (Intuitive Override)
   • Crystal Node → Risk Monitor (Perfect Recall)

🎯 KEY DECISION POINTS:
   • Trinity Consensus (3-agent voting)
   • Sigil Invocation (Ritual commands)
   • Risk Monitoring (Continuous assessment)
   • Genesis Triggers (Capital feedback)
        """
        
        return ascii_map
    
    def _get_node_shape(self, node_type: FlowNodeType) -> Tuple[str, str]:
        """🎨 Get Mermaid shape syntax for node type"""
        shapes = {
            FlowNodeType.SIGNAL_INPUT: ("[", "]"),
            FlowNodeType.TRINITY_VOTE: ("((", "))"),
            FlowNodeType.SIGIL_INVOKE: ("{", "}"),
            FlowNodeType.EXECUTION: ("(", ")"),
            FlowNodeType.MEMORY_STORE: ("[(", ")]"),
            FlowNodeType.VAULT_INJECT: ("[[", "]]"),
            FlowNodeType.THREAT_SCAN: (">", "]")
        }
        return shapes.get(node_type, ("(", ")"))
    
    def _get_node_class(self, node_type: FlowNodeType) -> str:
        """🎨 Get CSS class for node type"""
        classes = {
            FlowNodeType.SIGNAL_INPUT: "signalNode",
            FlowNodeType.TRINITY_VOTE: "trinityNode",
            FlowNodeType.SIGIL_INVOKE: "sigilNode",
            FlowNodeType.EXECUTION: "executeNode",
            FlowNodeType.MEMORY_STORE: "memoryNode",
            FlowNodeType.VAULT_INJECT: "vaultNode",
            FlowNodeType.THREAT_SCAN: "trinityNode"
        }
        return classes.get(node_type, "executeNode")
    
    def export_flow_data(self) -> Dict:
        """📊 Export flow map data as JSON"""
        return {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'node_count': len(self.nodes),
                'connection_count': len(self.connections),
                'version': '1.0'
            },
            'nodes': [
                {
                    'id': node.node_id,
                    'type': node.node_type.value,
                    'label': node.label,
                    'description': node.description,
                    'position': {'x': node.x, 'y': node.y},
                    'style': {'color': node.color, 'icon': node.icon}
                }
                for node in self.nodes
            ],
            'connections': [
                {
                    'from': conn.from_node,
                    'to': conn.to_node,
                    'label': conn.label,
                    'condition': conn.condition,
                    'style': {'color': conn.color, 'weight': conn.weight}
                }
                for conn in self.connections
            ]
        }

# Initialize the neural flow map renderer
neural_flow_renderer = NeuralFlowMapRenderer()

def generate_flow_visualization(format_type: str = "html") -> str:
    """
    🌀 Generate neural flow visualization
    Formats: 'html', 'mermaid', 'ascii', 'json'
    """
    if format_type == "html":
        return neural_flow_renderer.generate_html_visualization()
    elif format_type == "mermaid":
        return neural_flow_renderer.generate_mermaid_diagram()
    elif format_type == "ascii":
        return neural_flow_renderer.generate_ascii_flow_map()
    elif format_type == "json":
        return json.dumps(neural_flow_renderer.export_flow_data(), indent=2)
    else:
        raise ValueError(f"Unknown format: {format_type}")

if __name__ == "__main__":
    print("🌀 NEURAL FLOW MAP RENDERER - STANDALONE TEST")
    
    # Generate ASCII flow map
    print("\n📟 ASCII FLOW MAP:")
    print(neural_flow_renderer.generate_ascii_flow_map())
    
    # Generate Mermaid diagram
    print("\n🎨 MERMAID DIAGRAM:")
    print(neural_flow_renderer.generate_mermaid_diagram())
    
    # Export data
    flow_data = neural_flow_renderer.export_flow_data()
    print(f"\n📊 FLOW DATA: {flow_data['metadata']['node_count']} nodes, {flow_data['metadata']['connection_count']} connections")
    
    print("\n✅ NEURAL FLOW MAP DEMO COMPLETE")

