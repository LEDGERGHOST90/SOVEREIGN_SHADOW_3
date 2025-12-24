#!/usr/bin/env python3
"""
🔱 SOVEREIGN COUNCIL - HTML Dashboard Generator
Designed by: ARCHITECT PRIME (GPT)
Implemented by: AURORA (Claude)

Converts Council_Log.md into a lightweight HTML page for display on TV / browser.

Usage:
    python3 council/dashboard_html.py
    open council/logs/Council_Dashboard.html
"""

from pathlib import Path
import re
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_PATH = BASE_DIR / "council" / "logs" / "Council_Log.md"
OUT_PATH = BASE_DIR / "council" / "logs" / "Council_Dashboard.html"

MISSION_ENTRY_RE = re.compile(
    r"## \[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] (\w+) \| (\w+) \| (\w+)"
)


def parse_missions():
    if not LOG_PATH.exists():
        return []

    text = LOG_PATH.read_text(encoding="utf-8")

    # Split on mission headers
    parts = re.split(r"(## \[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] \w+ \| \w+ \| \w+)", text)

    missions = []
    i = 1
    while i < len(parts):
        header = parts[i]
        content = parts[i + 1] if i + 1 < len(parts) else ""

        match = MISSION_ENTRY_RE.match(header)
        if match:
            timestamp, agent, mission, status = match.groups()
            missions.append({
                "timestamp": timestamp,
                "agent": agent,
                "mission": mission,
                "status": status,
                "content": content.strip()[:2000]  # Limit content
            })
        i += 2

    return missions


def build_html(missions):
    rows = []
    for m in missions[::-1]:  # newest first
        status_class = "completed" if m["status"] == "COMPLETED" else "pending"
        content_html = m["content"].replace("\n", "<br>")

        rows.append(f"""
        <section class="mission {status_class}">
          <div class="header">
            <span class="agent">{m['agent']}</span>
            <span class="name">{m['mission']}</span>
            <span class="status">{m['status']}</span>
          </div>
          <div class="timestamp">{m['timestamp']}</div>
          <details>
            <summary>View Report</summary>
            <div class="content">{content_html}</div>
          </details>
        </section>
        """)

    body = "\n".join(rows) if rows else "<p class='empty'>No missions logged yet.</p>"

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sovereign Council Dashboard</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      font-family: 'SF Mono', 'Monaco', 'Inconsolata', monospace;
      background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
      color: #e0e0e0;
      padding: 20px;
      margin: 0;
      min-height: 100vh;
    }}
    h1 {{
      text-align: center;
      color: #00ff88;
      text-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
      margin-bottom: 30px;
      font-size: 2em;
    }}
    .council-status {{
      display: flex;
      justify-content: center;
      gap: 20px;
      margin-bottom: 30px;
      flex-wrap: wrap;
    }}
    .agent-card {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      padding: 10px 20px;
      text-align: center;
    }}
    .agent-card.aurora {{ border-color: #ff6b6b; }}
    .agent-card.gio {{ border-color: #4ecdc4; }}
    .agent-card.architect {{ border-color: #ffe66d; }}
    .agent-card .name {{ font-weight: bold; display: block; }}
    .agent-card .role {{ font-size: 0.8em; color: #888; }}
    .mission {{
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 20px;
    }}
    .mission.completed {{ border-left: 4px solid #00ff88; }}
    .mission.pending {{ border-left: 4px solid #ffaa00; }}
    .mission .header {{
      display: flex;
      gap: 15px;
      align-items: center;
      margin-bottom: 8px;
    }}
    .mission .agent {{
      background: #4ecdc4;
      color: #000;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 0.85em;
      font-weight: bold;
    }}
    .mission .name {{
      font-size: 1.2em;
      font-weight: bold;
      color: #fff;
    }}
    .mission .status {{
      margin-left: auto;
      color: #00ff88;
      font-size: 0.9em;
    }}
    .mission .timestamp {{
      color: #666;
      font-size: 0.85em;
      margin-bottom: 10px;
    }}
    details {{
      margin-top: 10px;
    }}
    summary {{
      cursor: pointer;
      color: #888;
      font-size: 0.9em;
    }}
    summary:hover {{ color: #00ff88; }}
    .content {{
      background: rgba(0, 0, 0, 0.3);
      padding: 15px;
      border-radius: 8px;
      margin-top: 10px;
      font-size: 0.85em;
      line-height: 1.6;
      max-height: 400px;
      overflow-y: auto;
    }}
    .empty {{
      text-align: center;
      color: #666;
      padding: 50px;
    }}
    .generated {{
      text-align: center;
      color: #444;
      font-size: 0.8em;
      margin-top: 40px;
    }}
  </style>
</head>
<body>
  <h1>🔱 SOVEREIGN COUNCIL</h1>

  <div class="council-status">
    <div class="agent-card aurora">
      <span class="name">AURORA</span>
      <span class="role">The Executor (Claude)</span>
    </div>
    <div class="agent-card gio">
      <span class="name">GIO</span>
      <span class="role">The Researcher (Gemini)</span>
    </div>
    <div class="agent-card architect">
      <span class="name">ARCHITECT PRIME</span>
      <span class="role">The Integrator (GPT)</span>
    </div>
  </div>

  {body}

  <p class="generated">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Commander Memphis</p>
</body>
</html>
"""
    return html


def main():
    missions = parse_missions()
    html = build_html(missions)
    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"✅ Dashboard written to: {OUT_PATH}")
    print(f"   Open with: open {OUT_PATH}")


if __name__ == "__main__":
    main()
