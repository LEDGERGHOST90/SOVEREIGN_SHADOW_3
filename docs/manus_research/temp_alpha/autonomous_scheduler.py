#!/usr/bin/env python3
"""
Autonomous Scheduler - Sovereign Shadow III
24/7 execution framework with human consent gates.

This scheduler:
1. Runs scheduled tasks from all AIs
2. Enforces human approval for sensitive operations
3. Maintains execution logs
4. Handles failures gracefully
"""

import json
import time
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable
import signal
import sys

BASE_DIR = Path(__file__).parent.parent
AI_DIR = BASE_DIR / ".ai"
STATE_FILE = AI_DIR / "state.json"
LOGS_DIR = AI_DIR / "logs"
SCHEDULE_FILE = AI_DIR / "schedule.json"

LOGS_DIR.mkdir(parents=True, exist_ok=True)


class AutonomousScheduler:
    """
    24/7 Autonomous Execution Framework
    
    Runs scheduled tasks while respecting human consent gates.
    """
    
    # Tasks that can run without approval (safe operations)
    AUTO_APPROVE_TASKS = [
        "health_check",
        "price_sync",
        "data_backup",
        "log_rotation",
        "status_report"
    ]
    
    # Tasks that ALWAYS require human approval
    REQUIRE_APPROVAL_TASKS = [
        "trade_execution",
        "strategy_change",
        "config_update",
        "code_deployment",
        "vault_operation"
    ]
    
    def __init__(self):
        self.running = False
        self.tasks: Dict[str, Dict] = {}
        self.execution_log: List[Dict] = []
        self._load_schedule()
    
    def _load_schedule(self):
        """Load scheduled tasks from file"""
        if SCHEDULE_FILE.exists():
            data = json.loads(SCHEDULE_FILE.read_text())
            self.tasks = data.get("tasks", {})
        else:
            # Default schedule
            self.tasks = {
                "manus_opportunity_scan": {
                    "ai": "manus",
                    "description": "Scan for trading opportunities",
                    "command": "python scripts/manus_sync.py sync",
                    "cron": "0 */4 * * *",  # Every 4 hours
                    "requires_approval": False,
                    "enabled": True,
                    "last_run": None,
                    "next_run": None
                },
                "manus_daily_report": {
                    "ai": "manus",
                    "description": "Generate daily analysis report",
                    "command": "python scripts/manus_sync.py full",
                    "cron": "0 0 * * *",  # Daily at midnight
                    "requires_approval": False,
                    "enabled": True,
                    "last_run": None,
                    "next_run": None
                },
                "health_check": {
                    "ai": "system",
                    "description": "Check system health",
                    "command": "python scripts/health_check.py",
                    "cron": "*/30 * * * *",  # Every 30 minutes
                    "requires_approval": False,
                    "enabled": True,
                    "last_run": None,
                    "next_run": None
                },
                "proposal_reminder": {
                    "ai": "system",
                    "description": "Remind about pending proposals",
                    "command": "python scripts/ai_proposal_handler.py list --status pending",
                    "cron": "0 */2 * * *",  # Every 2 hours
                    "requires_approval": False,
                    "enabled": True,
                    "last_run": None,
                    "next_run": None
                }
            }
            self._save_schedule()
    
    def _save_schedule(self):
        """Save schedule to file"""
        SCHEDULE_FILE.write_text(json.dumps({
            "tasks": self.tasks,
            "last_updated": datetime.utcnow().isoformat() + "Z"
        }, indent=2))
    
    def _parse_cron(self, cron_expr: str) -> Optional[datetime]:
        """
        Simple cron parser - returns next run time.
        Supports: minute hour day month weekday
        """
        # Simplified implementation - for production use croniter
        parts = cron_expr.split()
        if len(parts) != 5:
            return None
        
        now = datetime.utcnow()
        minute, hour, day, month, weekday = parts
        
        # Handle */N patterns
        if minute.startswith("*/"):
            interval = int(minute[2:])
            next_minute = ((now.minute // interval) + 1) * interval
            if next_minute >= 60:
                return now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            return now.replace(minute=next_minute, second=0, microsecond=0)
        
        if hour.startswith("*/"):
            interval = int(hour[2:])
            next_hour = ((now.hour // interval) + 1) * interval
            if next_hour >= 24:
                return now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            return now.replace(hour=next_hour, minute=0, second=0, microsecond=0)
        
        # Fixed time
        target_minute = int(minute) if minute != "*" else now.minute
        target_hour = int(hour) if hour != "*" else now.hour
        
        target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        
        return target
    
    def _should_run(self, task_id: str, task: Dict) -> bool:
        """Check if a task should run now"""
        if not task.get("enabled", True):
            return False
        
        next_run = task.get("next_run")
        if next_run:
            next_run_dt = datetime.fromisoformat(next_run.replace("Z", ""))
            return datetime.utcnow() >= next_run_dt
        
        return True
    
    def _execute_task(self, task_id: str, task: Dict) -> Dict:
        """Execute a scheduled task"""
        result = {
            "task_id": task_id,
            "started_at": datetime.utcnow().isoformat() + "Z",
            "success": False,
            "output": "",
            "error": None
        }
        
        try:
            # Check if approval is required
            if task.get("requires_approval", False):
                # Create a proposal instead of executing
                self._create_execution_proposal(task_id, task)
                result["output"] = "Proposal created - awaiting human approval"
                result["success"] = True
                return result
            
            # Execute the command
            proc = subprocess.run(
                task["command"],
                shell=True,
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            result["output"] = proc.stdout
            result["error"] = proc.stderr if proc.returncode != 0 else None
            result["success"] = proc.returncode == 0
            result["return_code"] = proc.returncode
            
        except subprocess.TimeoutExpired:
            result["error"] = "Task timed out after 5 minutes"
        except Exception as e:
            result["error"] = str(e)
        
        result["completed_at"] = datetime.utcnow().isoformat() + "Z"
        
        # Update task state
        task["last_run"] = result["started_at"]
        task["next_run"] = self._parse_cron(task["cron"]).isoformat() + "Z" if task.get("cron") else None
        self._save_schedule()
        
        # Log execution
        self._log_execution(result)
        
        return result
    
    def _create_execution_proposal(self, task_id: str, task: Dict):
        """Create a proposal for tasks requiring approval"""
        from ai_proposal_handler import ProposalHandler
        
        handler = ProposalHandler()
        handler.create_proposal(
            ai_source=task.get("ai", "system"),
            proposal_type="system_change",
            description=f"Scheduled task execution: {task.get('description', task_id)}",
            files=[],
            rationale=f"Scheduled task '{task_id}' requires human approval before execution. Command: {task['command']}",
            priority="high"
        )
    
    def _log_execution(self, result: Dict):
        """Log task execution"""
        log_file = LOGS_DIR / f"scheduler_{datetime.utcnow().strftime('%Y%m%d')}.log"
        
        with open(log_file, "a") as f:
            status = "✓" if result["success"] else "✗"
            f.write(f"[{result['started_at']}] {status} {result['task_id']}\n")
            if result.get("error"):
                f.write(f"    Error: {result['error']}\n")
        
        self.execution_log.append(result)
        # Keep only last 100 executions in memory
        self.execution_log = self.execution_log[-100:]
    
    def add_task(
        self,
        task_id: str,
        ai: str,
        description: str,
        command: str,
        cron: str,
        requires_approval: bool = False
    ):
        """Add a new scheduled task"""
        self.tasks[task_id] = {
            "ai": ai,
            "description": description,
            "command": command,
            "cron": cron,
            "requires_approval": requires_approval,
            "enabled": True,
            "last_run": None,
            "next_run": self._parse_cron(cron).isoformat() + "Z"
        }
        self._save_schedule()
    
    def remove_task(self, task_id: str):
        """Remove a scheduled task"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save_schedule()
    
    def enable_task(self, task_id: str, enabled: bool = True):
        """Enable or disable a task"""
        if task_id in self.tasks:
            self.tasks[task_id]["enabled"] = enabled
            self._save_schedule()
    
    def run_once(self):
        """Run all due tasks once"""
        for task_id, task in self.tasks.items():
            if self._should_run(task_id, task):
                print(f"[{datetime.utcnow().isoformat()}] Running: {task_id}")
                result = self._execute_task(task_id, task)
                status = "✓" if result["success"] else "✗"
                print(f"[{datetime.utcnow().isoformat()}] {status} {task_id}")
    
    def run_forever(self, check_interval: int = 60):
        """Run the scheduler continuously"""
        self.running = True
        
        def signal_handler(sig, frame):
            print("\nShutting down scheduler...")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        print(f"\n{'='*60}")
        print("  SS3 Autonomous Scheduler")
        print(f"  Started: {datetime.utcnow().isoformat()}Z")
        print(f"  Tasks: {len(self.tasks)}")
        print(f"  Check interval: {check_interval}s")
        print(f"{'='*60}\n")
        
        while self.running:
            self.run_once()
            time.sleep(check_interval)
        
        print("Scheduler stopped.")
    
    def get_status(self) -> Dict:
        """Get scheduler status"""
        return {
            "running": self.running,
            "tasks": {
                task_id: {
                    "description": task.get("description"),
                    "enabled": task.get("enabled"),
                    "last_run": task.get("last_run"),
                    "next_run": task.get("next_run"),
                    "requires_approval": task.get("requires_approval")
                }
                for task_id, task in self.tasks.items()
            },
            "recent_executions": self.execution_log[-10:]
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="SS3 Autonomous Scheduler")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start the scheduler")
    start_parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds")
    
    # Run once command
    subparsers.add_parser("run", help="Run all due tasks once")
    
    # Status command
    subparsers.add_parser("status", help="Show scheduler status")
    
    # List command
    subparsers.add_parser("list", help="List all tasks")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a task")
    add_parser.add_argument("--id", required=True, help="Task ID")
    add_parser.add_argument("--ai", required=True, help="AI source")
    add_parser.add_argument("--description", required=True, help="Description")
    add_parser.add_argument("--command", required=True, help="Command to run")
    add_parser.add_argument("--cron", required=True, help="Cron expression")
    add_parser.add_argument("--require-approval", action="store_true", help="Require human approval")
    
    args = parser.parse_args()
    scheduler = AutonomousScheduler()
    
    if args.command == "start":
        scheduler.run_forever(args.interval)
    
    elif args.command == "run":
        scheduler.run_once()
    
    elif args.command == "status":
        status = scheduler.get_status()
        print(json.dumps(status, indent=2))
    
    elif args.command == "list":
        print(f"\n{'='*60}")
        print("  SCHEDULED TASKS")
        print(f"{'='*60}\n")
        for task_id, task in scheduler.tasks.items():
            status = "✓" if task.get("enabled") else "○"
            approval = "🔒" if task.get("requires_approval") else ""
            print(f"{status} {task_id} {approval}")
            print(f"   AI: {task.get('ai')} | Cron: {task.get('cron')}")
            print(f"   {task.get('description')}")
            print(f"   Next: {task.get('next_run', 'Not scheduled')}\n")
    
    elif args.command == "add":
        scheduler.add_task(
            task_id=args.id,
            ai=args.ai,
            description=args.description,
            command=args.command,
            cron=args.cron,
            requires_approval=args.require_approval
        )
        print(f"✓ Task added: {args.id}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
