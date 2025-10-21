#!/usr/bin/env python3
"""
QUICK FIX - MONITORING STATUS ISSUES
===================================
Fixes common monitoring_status.json issues
"""

import json
import os
from pathlib import Path
from datetime import datetime

def fix_monitoring_status():
    """Fix monitoring status file issues"""
    
    # Get project root
    project_root = Path(__file__).resolve().parent
    state_dir = project_root / "state"
    
    # Ensure state directory exists
    state_dir.mkdir(parents=True, exist_ok=True)
    
    # Fix monitoring_status.json
    monitoring_file = state_dir / "monitoring_status.json"
    
    # Create proper monitoring status
    monitoring_status = {
        "timestamp": datetime.now().isoformat(),
        "monitoring_active": False,
        "positions_count": 0,
        "portfolio_snapshots": 0,
        "last_check": datetime.now().isoformat(),
        "system_status": "READY",
        "project_root": str(project_root),
        "state_directory": str(state_dir)
    }
    
    # Write with error handling
    try:
        with open(monitoring_file, 'w') as f:
            json.dump(monitoring_status, f, indent=2)
        
        print(f"✅ Fixed monitoring_status.json at: {monitoring_file}")
        print(f"📁 State directory: {state_dir}")
        print(f"🔍 File exists: {monitoring_file.exists()}")
        print(f"📊 File size: {monitoring_file.stat().st_size} bytes")
        
        # Verify file is readable
        with open(monitoring_file, 'r') as f:
            data = json.load(f)
            print(f"✅ File is readable and valid JSON")
            print(f"🕐 Timestamp: {data['timestamp']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing monitoring_status.json: {e}")
        return False

def check_all_state_files():
    """Check all state files"""
    
    project_root = Path(__file__).resolve().parent
    state_dir = project_root / "state"
    
    print(f"🔍 CHECKING STATE FILES")
    print(f"📁 Project root: {project_root}")
    print(f"📁 State directory: {state_dir}")
    print(f"📁 State dir exists: {state_dir.exists()}")
    print()
    
    if state_dir.exists():
        print("📄 STATE FILES:")
        for file_path in state_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                print(f"   ✅ {file_path.name} - Valid JSON ({file_path.stat().st_size} bytes)")
            except Exception as e:
                print(f"   ❌ {file_path.name} - Error: {e}")
    else:
        print("❌ State directory does not exist")

if __name__ == "__main__":
    print("🔧 MONITORING STATUS QUICK FIX")
    print("=" * 40)
    
    # Check current state
    check_all_state_files()
    print()
    
    # Fix monitoring status
    if fix_monitoring_status():
        print()
        print("🎉 MONITORING STATUS FIXED!")
        print()
        print("📋 VERIFICATION:")
        check_all_state_files()
    else:
        print("❌ FAILED TO FIX MONITORING STATUS")

