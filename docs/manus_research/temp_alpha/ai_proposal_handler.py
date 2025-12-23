#!/usr/bin/env python3
"""
AI Proposal Handler - Sovereign Shadow III
Manages proposals from all AI agents in the unified collaboration framework.

This script:
1. Creates proposals from any AI
2. Lists pending proposals
3. Approves/rejects proposals (human only)
4. Executes approved proposals
5. Notifies relevant AIs
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

# Configuration
BASE_DIR = Path(__file__).parent.parent
AI_DIR = BASE_DIR / ".ai"
PROPOSALS_DIR = AI_DIR / "proposals"
STATE_FILE = AI_DIR / "state.json"
LOGS_DIR = AI_DIR / "logs"

# Ensure directories exist
PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


class ProposalHandler:
    """Handles AI proposals in the unified framework"""
    
    VALID_AIS = [
        "chatgpt", "claude_code", "claude_desktop", "claude_mobile",
        "cursor", "grok", "gemini", "manus"
    ]
    
    PROPOSAL_TYPES = [
        "code_change",      # Modify existing code
        "new_file",         # Create new file
        "delete_file",      # Remove file
        "config_update",    # Update configuration
        "analysis_update",  # New analysis/data
        "strategy_change",  # Trading strategy (requires Colonel approval)
        "system_change",    # System-level changes
    ]
    
    PRIORITY_LEVELS = ["low", "medium", "high", "critical"]
    
    def __init__(self):
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load current system state"""
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text())
        return {"pending_proposals": [], "ai_agents": {}}
    
    def _save_state(self):
        """Save system state"""
        self.state["last_updated"] = datetime.utcnow().isoformat() + "Z"
        STATE_FILE.write_text(json.dumps(self.state, indent=2))
    
    def create_proposal(
        self,
        ai_source: str,
        proposal_type: str,
        description: str,
        files: List[Dict],
        rationale: str,
        priority: str = "medium"
    ) -> Dict:
        """
        Create a new proposal from an AI agent.
        
        Args:
            ai_source: Which AI is proposing (e.g., "manus", "claude_code")
            proposal_type: Type of change (see PROPOSAL_TYPES)
            description: Brief description of the change
            files: List of file changes [{path, action, content}]
            rationale: Why this change is needed
            priority: low/medium/high/critical
        
        Returns:
            The created proposal dict
        """
        if ai_source not in self.VALID_AIS:
            raise ValueError(f"Invalid AI source: {ai_source}")
        if proposal_type not in self.PROPOSAL_TYPES:
            raise ValueError(f"Invalid proposal type: {proposal_type}")
        if priority not in self.PRIORITY_LEVELS:
            raise ValueError(f"Invalid priority: {priority}")
        
        # Determine if this requires special approval
        requires_colonel = proposal_type in ["strategy_change", "system_change"]
        requires_human = True  # All proposals require human approval
        
        timestamp = datetime.utcnow()
        proposal_id = f"{ai_source}_{timestamp.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        proposal = {
            "id": proposal_id,
            "ai": ai_source,
            "type": proposal_type,
            "priority": priority,
            "description": description,
            "files": files,
            "rationale": rationale,
            "requires_human_approval": requires_human,
            "requires_colonel_approval": requires_colonel,
            "status": "pending",
            "created_at": timestamp.isoformat() + "Z",
            "reviewed_at": None,
            "reviewed_by": None,
            "execution_result": None
        }
        
        # Save proposal file
        proposal_file = PROPOSALS_DIR / f"{proposal_id}.json"
        proposal_file.write_text(json.dumps(proposal, indent=2))
        
        # Update state
        self.state["pending_proposals"].append(proposal_id)
        if ai_source in self.state.get("ai_agents", {}):
            self.state["ai_agents"][ai_source]["last_active"] = proposal["created_at"]
        self._save_state()
        
        self._log(f"Proposal created: {proposal_id} by {ai_source}")
        
        return proposal
    
    def list_proposals(self, status: Optional[str] = None) -> List[Dict]:
        """List all proposals, optionally filtered by status"""
        proposals = []
        for f in PROPOSALS_DIR.glob("*.json"):
            proposal = json.loads(f.read_text())
            if status is None or proposal.get("status") == status:
                proposals.append(proposal)
        
        # Sort by priority and creation time
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        proposals.sort(key=lambda p: (
            priority_order.get(p.get("priority", "medium"), 2),
            p.get("created_at", "")
        ))
        
        return proposals
    
    def review_proposal(
        self,
        proposal_id: str,
        approved: bool,
        reviewer: str = "human",
        notes: Optional[str] = None
    ) -> Dict:
        """
        Review (approve/reject) a proposal.
        Only humans can approve proposals.
        """
        proposal_file = PROPOSALS_DIR / f"{proposal_id}.json"
        if not proposal_file.exists():
            raise ValueError(f"Proposal not found: {proposal_id}")
        
        proposal = json.loads(proposal_file.read_text())
        
        if proposal["status"] != "pending":
            raise ValueError(f"Proposal already reviewed: {proposal['status']}")
        
        proposal["status"] = "approved" if approved else "rejected"
        proposal["reviewed_at"] = datetime.utcnow().isoformat() + "Z"
        proposal["reviewed_by"] = reviewer
        proposal["review_notes"] = notes
        
        proposal_file.write_text(json.dumps(proposal, indent=2))
        
        # Update state
        if proposal_id in self.state["pending_proposals"]:
            self.state["pending_proposals"].remove(proposal_id)
        self._save_state()
        
        self._log(f"Proposal {proposal_id} {'approved' if approved else 'rejected'} by {reviewer}")
        
        # If approved, execute the proposal
        if approved:
            self.execute_proposal(proposal_id)
        
        return proposal
    
    def execute_proposal(self, proposal_id: str) -> Dict:
        """Execute an approved proposal"""
        proposal_file = PROPOSALS_DIR / f"{proposal_id}.json"
        proposal = json.loads(proposal_file.read_text())
        
        if proposal["status"] != "approved":
            raise ValueError(f"Proposal not approved: {proposal['status']}")
        
        results = []
        try:
            for file_change in proposal.get("files", []):
                path = BASE_DIR / file_change["path"]
                action = file_change["action"]
                
                if action == "create" or action == "update":
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(file_change.get("content", ""))
                    results.append(f"✓ {action}: {path}")
                
                elif action == "delete":
                    if path.exists():
                        path.unlink()
                    results.append(f"✓ deleted: {path}")
                
                elif action == "append":
                    with open(path, "a") as f:
                        f.write(file_change.get("content", ""))
                    results.append(f"✓ appended to: {path}")
            
            proposal["status"] = "executed"
            proposal["execution_result"] = {
                "success": True,
                "results": results,
                "executed_at": datetime.utcnow().isoformat() + "Z"
            }
            
        except Exception as e:
            proposal["status"] = "failed"
            proposal["execution_result"] = {
                "success": False,
                "error": str(e),
                "executed_at": datetime.utcnow().isoformat() + "Z"
            }
        
        proposal_file.write_text(json.dumps(proposal, indent=2))
        self._log(f"Proposal {proposal_id} execution: {proposal['status']}")
        
        return proposal
    
    def _log(self, message: str):
        """Log activity"""
        timestamp = datetime.utcnow().isoformat()
        log_file = LOGS_DIR / f"proposals_{datetime.utcnow().strftime('%Y%m%d')}.log"
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
        print(f"[{timestamp}] {message}")


def main():
    """CLI interface for proposal management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Proposal Handler")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List proposals")
    list_parser.add_argument("--status", choices=["pending", "approved", "rejected", "executed", "failed"])
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create proposal")
    create_parser.add_argument("--ai", required=True, help="AI source")
    create_parser.add_argument("--type", required=True, help="Proposal type")
    create_parser.add_argument("--description", required=True, help="Description")
    create_parser.add_argument("--rationale", required=True, help="Rationale")
    create_parser.add_argument("--priority", default="medium", help="Priority level")
    create_parser.add_argument("--file", action="append", help="File:action:content")
    
    # Review command
    review_parser = subparsers.add_parser("review", help="Review proposal")
    review_parser.add_argument("proposal_id", help="Proposal ID")
    review_parser.add_argument("--approve", action="store_true", help="Approve")
    review_parser.add_argument("--reject", action="store_true", help="Reject")
    review_parser.add_argument("--notes", help="Review notes")
    
    args = parser.parse_args()
    handler = ProposalHandler()
    
    if args.command == "list":
        proposals = handler.list_proposals(args.status)
        print(f"\n{'='*60}")
        print(f"  PROPOSALS ({len(proposals)} total)")
        print(f"{'='*60}")
        for p in proposals:
            status_icon = {"pending": "⏳", "approved": "✓", "rejected": "✗", "executed": "✓✓", "failed": "💥"}.get(p["status"], "?")
            print(f"\n{status_icon} [{p['priority'].upper()}] {p['id']}")
            print(f"   AI: {p['ai']} | Type: {p['type']}")
            print(f"   {p['description']}")
            print(f"   Created: {p['created_at']}")
    
    elif args.command == "create":
        files = []
        if args.file:
            for f in args.file:
                parts = f.split(":", 2)
                files.append({
                    "path": parts[0],
                    "action": parts[1] if len(parts) > 1 else "update",
                    "content": parts[2] if len(parts) > 2 else ""
                })
        
        proposal = handler.create_proposal(
            ai_source=args.ai,
            proposal_type=args.type,
            description=args.description,
            files=files,
            rationale=args.rationale,
            priority=args.priority
        )
        print(f"\n✓ Proposal created: {proposal['id']}")
    
    elif args.command == "review":
        if args.approve:
            proposal = handler.review_proposal(args.proposal_id, True, notes=args.notes)
            print(f"\n✓ Proposal approved and executed")
        elif args.reject:
            proposal = handler.review_proposal(args.proposal_id, False, notes=args.notes)
            print(f"\n✗ Proposal rejected")
        else:
            print("Specify --approve or --reject")


if __name__ == "__main__":
    main()
