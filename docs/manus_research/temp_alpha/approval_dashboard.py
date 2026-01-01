#!/usr/bin/env python3
"""
Human Approval Dashboard - Sovereign Shadow III
Provides a simple interface for humans to review and approve AI proposals.

Run with: python approval_dashboard.py
Then open: http://localhost:8080
"""

import json
from datetime import datetime

from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

BASE_DIR = Path(__file__).parent.parent
AI_DIR = BASE_DIR / ".ai"
PROPOSALS_DIR = AI_DIR / "proposals"
STATE_FILE = AI_DIR / "state.json"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>SS3 - AI Approval Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0d1117; color: #c9d1d9; padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #58a6ff; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
        h1::before { content: "♟️"; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 30px; }
        .stat-card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; color: #58a6ff; }
        .stat-label { color: #8b949e; font-size: 0.9em; }
        .proposals { display: flex; flex-direction: column; gap: 15px; }
        .proposal { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; }
        .proposal.pending { border-left: 4px solid #f0883e; }
        .proposal.approved { border-left: 4px solid #3fb950; }
        .proposal.rejected { border-left: 4px solid #f85149; }
        .proposal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .proposal-id { font-family: monospace; color: #8b949e; font-size: 0.85em; }
        .priority { padding: 2px 8px; border-radius: 12px; font-size: 0.75em; font-weight: bold; }
        .priority.critical { background: #f85149; color: white; }
        .priority.high { background: #f0883e; color: white; }
        .priority.medium { background: #58a6ff; color: white; }
        .priority.low { background: #8b949e; color: white; }
        .proposal-title { font-size: 1.1em; color: #f0f6fc; margin-bottom: 8px; }
        .proposal-meta { color: #8b949e; font-size: 0.9em; margin-bottom: 10px; }
        .proposal-meta span { margin-right: 15px; }
        .proposal-rationale { background: #0d1117; padding: 10px; border-radius: 4px; margin-bottom: 15px; font-size: 0.9em; }
        .files { margin-bottom: 15px; }
        .file { font-family: monospace; font-size: 0.85em; color: #58a6ff; padding: 5px 0; }
        .actions { display: flex; gap: 10px; }
        .btn { padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; font-weight: 500; }
        .btn-approve { background: #238636; color: white; }
        .btn-approve:hover { background: #2ea043; }
        .btn-reject { background: #da3633; color: white; }
        .btn-reject:hover { background: #f85149; }
        .btn-view { background: #30363d; color: #c9d1d9; }
        .btn-view:hover { background: #484f58; }
        .empty { text-align: center; padding: 40px; color: #8b949e; }
        .ai-badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; font-weight: 500; }
        .ai-badge.manus { background: #238636; color: white; }
        .ai-badge.claude_code { background: #a371f7; color: white; }
        .ai-badge.chatgpt { background: #10a37f; color: white; }
        .ai-badge.grok { background: #1da1f2; color: white; }
        .ai-badge.cursor { background: #f0883e; color: white; }
        .refresh { position: fixed; bottom: 20px; right: 20px; }
        .status-indicator { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 5px; }
        .status-indicator.active { background: #3fb950; }
        .status-indicator.idle { background: #8b949e; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Sovereign Shadow III - Approval Dashboard</h1>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{pending_count}</div>
                <div class="stat-label">Pending</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{approved_count}</div>
                <div class="stat-label">Approved</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{rejected_count}</div>
                <div class="stat-label">Rejected</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{active_ais}</div>
                <div class="stat-label">Active AIs</div>
            </div>
        </div>
        
        <h2 style="margin-bottom: 15px; color: #f0883e;">⏳ Pending Approval</h2>
        <div class="proposals">
            {pending_proposals}
        </div>
        
        <h2 style="margin: 30px 0 15px; color: #8b949e;">📋 Recent Activity</h2>
        <div class="proposals">
            {recent_proposals}
        </div>
        
        <button class="btn btn-view refresh" onclick="location.reload()">🔄 Refresh</button>
    </div>
    
    <script>
        function approve(id) {{
            if (confirm('Approve this proposal?')) {{
                fetch('/approve?id=' + id, {{ method: 'POST' }})
                    .then(() => location.reload());
            }}
        }}
        function reject(id) {{
            if (confirm('Reject this proposal?')) {{
                fetch('/reject?id=' + id, {{ method: 'POST' }})
                    .then(() => location.reload());
            }}
        }}
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
"""

PROPOSAL_TEMPLATE = """
<div class="proposal {status}">
    <div class="proposal-header">
        <span class="proposal-id">{id}</span>
        <span class="priority {priority}">{priority_upper}</span>
    </div>
    <div class="proposal-title">{description}</div>
    <div class="proposal-meta">
        <span class="ai-badge {ai}">{ai}</span>
        <span>📁 {type}</span>
        <span>🕐 {created_at}</span>
    </div>
    <div class="proposal-rationale">{rationale}</div>
    <div class="files">
        {files_html}
    </div>
    {actions}
</div>
"""


class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            self.send_dashboard()
        else:
            self.send_error(404)
    
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        
        if parsed.path == "/approve" and "id" in params:
            self.handle_review(params["id"][0], True)
        elif parsed.path == "/reject" and "id" in params:
            self.handle_review(params["id"][0], False)
        else:
            self.send_error(400)
    
    def handle_review(self, proposal_id, approved):
        proposal_file = PROPOSALS_DIR / f"{proposal_id}.json"
        if proposal_file.exists():
            proposal = json.loads(proposal_file.read_text())
            proposal["status"] = "approved" if approved else "rejected"
            proposal["reviewed_at"] = datetime.utcnow().isoformat() + "Z"
            proposal["reviewed_by"] = "human_dashboard"
            proposal_file.write_text(json.dumps(proposal, indent=2))
        
        self.send_response(200)
        self.end_headers()
    
    def send_dashboard(self):
        # Load proposals
        proposals = []
        for f in PROPOSALS_DIR.glob("*.json"):
            proposals.append(json.loads(f.read_text()))
        
        # Sort by status and time
        pending = [p for p in proposals if p.get("status") == "pending"]
        recent = [p for p in proposals if p.get("status") != "pending"][-10:]
        
        # Load state for active AIs
        state = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}
        active_ais = sum(1 for ai in state.get("ai_agents", {}).values() 
                        if ai.get("status") == "active")
        
        # Generate HTML
        pending_html = ""
        for p in sorted(pending, key=lambda x: (
            {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x.get("priority", "medium"), 2),
            x.get("created_at", "")
        )):
            files_html = "".join(f'<div class="file">📄 {f.get("path")} ({f.get("action")})</div>' 
                                for f in p.get("files", []))
            actions = f'''
                <div class="actions">
                    <button class="btn btn-approve" onclick="approve('{p["id"]}')">✓ Approve</button>
                    <button class="btn btn-reject" onclick="reject('{p["id"]}')">✗ Reject</button>
                </div>
            '''
            pending_html += PROPOSAL_TEMPLATE.format(
                id=p["id"],
                status="pending",
                priority=p.get("priority", "medium"),
                priority_upper=p.get("priority", "medium").upper(),
                description=p.get("description", "No description"),
                ai=p.get("ai", "unknown"),
                type=p.get("type", "unknown"),
                created_at=p.get("created_at", "")[:16].replace("T", " "),
                rationale=p.get("rationale", "No rationale provided"),
                files_html=files_html or "<em>No files</em>",
                actions=actions
            )
        
        if not pending_html:
            pending_html = '<div class="empty">✨ No pending proposals</div>'
        
        recent_html = ""
        for p in sorted(recent, key=lambda x: x.get("reviewed_at", x.get("created_at", "")), reverse=True):
            files_html = "".join(f'<div class="file">📄 {f.get("path")}</div>' 
                                for f in p.get("files", []))
            recent_html += PROPOSAL_TEMPLATE.format(
                id=p["id"],
                status=p.get("status", "pending"),
                priority=p.get("priority", "medium"),
                priority_upper=p.get("priority", "medium").upper(),
                description=p.get("description", "No description"),
                ai=p.get("ai", "unknown"),
                type=p.get("type", "unknown"),
                created_at=p.get("created_at", "")[:16].replace("T", " "),
                rationale=p.get("rationale", ""),
                files_html=files_html,
                actions=f'<span style="color: #8b949e;">Status: {p.get("status", "unknown")}</span>'
            )
        
        if not recent_html:
            recent_html = '<div class="empty">No recent activity</div>'
        
        html = HTML_TEMPLATE.format(
            pending_count=len(pending),
            approved_count=len([p for p in proposals if p.get("status") == "approved"]),
            rejected_count=len([p for p in proposals if p.get("status") == "rejected"]),
            active_ais=active_ais,
            pending_proposals=pending_html,
            recent_proposals=recent_html
        )
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        pass  # Suppress logging


def main():
    port = 8080
    server = HTTPServer(("0.0.0.0", port), DashboardHandler)
    print(f"\n{'='*60}")
    print(f"  SS3 Approval Dashboard")
    print(f"  http://localhost:{port}")
    print(f"{'='*60}\n")
    print("Press Ctrl+C to stop\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
