#!/usr/bin/env python3
"""
🧹 WORKSPACE ORGANIZER
Clean up and organize the SovereignShadow.Ai workspace
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

class WorkspaceOrganizer:
    """Organize the workspace into a clean structure"""
    
    def __init__(self):
        self.root = Path.cwd()
        self.backup_dir = self.root / f"archive/cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Define clean structure
        self.structure = {
            'scripts': {
                'desc': 'Core trading and automation scripts',
                'patterns': ['*arbitrage*.py', '*trading*.py', '*portfolio*.py', 'sovereign_shadow_unified.py']
            },
            'config': {
                'desc': 'Configuration and setup files',
                'patterns': ['configure_*.py', '*_config.py', 'setup_*.py', '*integration*.py']
            },
            'monitoring': {
                'desc': 'Monitoring and status checking',
                'patterns': ['check_*.py', '*monitor*.py', '*status*.py', 'live_trading_monitor.py']
            },
            'deployment': {
                'desc': 'Deployment scripts and configs',
                'patterns': ['deploy_*.py', '*.sh', 'start_*.py', 'stop_*.py']
            },
            'docs': {
                'desc': 'Documentation and reports',
                'patterns': ['*.md', '*REPORT*.md', '*STATUS*.md', '*GUIDE*.md']
            },
            'tests': {
                'desc': 'Test and verification scripts',
                'patterns': ['test_*.py', 'verify_*.py', '*_test.py', 'final_*.py']
            },
            'quickstart': {
                'desc': 'Quick start and example scripts',
                'patterns': ['*quickstart*.py', '*example*.py', 'quick_*.py']
            }
        }
    
    def analyze_workspace(self):
        """Analyze current workspace state"""
        print("\n🔍 ANALYZING WORKSPACE...")
        print("=" * 80)
        
        loose_files = {
            'python': list(self.root.glob('*.py')),
            'shell': list(self.root.glob('*.sh')),
            'markdown': list(self.root.glob('*.md')),
            'json': list(self.root.glob('*.json')),
            'other': []
        }
        
        total_files = sum(len(files) for files in loose_files.values())
        
        print(f"\n📊 LOOSE FILES IN ROOT:")
        print(f"   Python scripts: {len(loose_files['python'])}")
        print(f"   Shell scripts: {len(loose_files['shell'])}")
        print(f"   Markdown docs: {len(loose_files['markdown'])}")
        print(f"   JSON files: {len(loose_files['json'])}")
        print(f"   TOTAL: {total_files} files")
        
        return loose_files, total_files
    
    def create_structure(self):
        """Create organized directory structure"""
        print("\n📁 CREATING CLEAN STRUCTURE...")
        
        for folder, info in self.structure.items():
            folder_path = self.root / folder
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
                print(f"   ✅ Created: {folder}/ - {info['desc']}")
            else:
                print(f"   ✓ Exists: {folder}/ - {info['desc']}")
    
    def organize_files(self, dry_run=True):
        """Organize files into proper directories"""
        print("\n🗂️  ORGANIZING FILES...")
        print(f"   Mode: {'DRY RUN (preview only)' if dry_run else 'LIVE (moving files)'}")
        print()
        
        moves = []
        
        # Get all loose files
        all_files = [f for f in self.root.iterdir() if f.is_file() and not f.name.startswith('.')]
        
        for file in all_files:
            # Skip essential files
            if file.name in ['sovereign_shadow_unified.py', 'organize_workspace.py', 'README.md']:
                continue
            
            # Find matching category
            moved = False
            for category, info in self.structure.items():
                for pattern in info['patterns']:
                    if file.match(pattern):
                        dest = self.root / category / file.name
                        moves.append((file, dest, category))
                        moved = True
                        break
                if moved:
                    break
            
            # If no category found, move to archive
            if not moved and file.suffix in ['.py', '.sh', '.md', '.json']:
                dest = self.backup_dir / file.name
                moves.append((file, dest, 'archive'))
        
        # Display planned moves
        by_category = {}
        for src, dest, category in moves:
            if category not in by_category:
                by_category[category] = []
            by_category[category].append((src, dest))
        
        for category, files in sorted(by_category.items()):
            print(f"\n📦 {category.upper()}:")
            for src, dest in files[:5]:  # Show first 5
                print(f"   {src.name} → {dest.relative_to(self.root)}")
            if len(files) > 5:
                print(f"   ... and {len(files) - 5} more files")
        
        print(f"\n📊 SUMMARY: {len(moves)} files to organize")
        
        # Execute moves if not dry run
        if not dry_run:
            print("\n🚀 EXECUTING MOVES...")
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            for src, dest, category in moves:
                try:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(src), str(dest))
                    print(f"   ✅ Moved: {src.name}")
                except Exception as e:
                    print(f"   ❌ Error moving {src.name}: {e}")
            
            print(f"\n✅ ORGANIZATION COMPLETE!")
            print(f"   Backup created at: {self.backup_dir.relative_to(self.root)}")
    
    def create_readme(self):
        """Create main README with structure explanation"""
        readme_content = """# 🏰 SovereignShadow.Ai - Trading Platform

## 📁 Directory Structure

```
SovereignShadow.Ai[LegacyLoop]/
├── scripts/           # Core trading and automation scripts
├── config/            # Configuration and setup files
├── monitoring/        # System monitoring and status checking
├── deployment/        # Deployment scripts and automation
├── docs/              # Documentation and reports
├── tests/             # Test and verification scripts
├── quickstart/        # Quick start examples and tutorials
├── environments/      # Dev, Staging, Production configs
│   ├── dev/          # Development environment
│   ├── staging/      # Paper trading environment
│   └── production/   # Live trading environment
├── logs/              # System and trading logs
├── data/              # Trading data and exports
└── archive/           # Historical files and backups
```

## 🚀 Quick Start

### 1. Run Unified Platform
```bash
python3 sovereign_shadow_unified.py
```

### 2. Configure APIs
```bash
python3 config/configure_all_apis.py
```

### 3. Check System Status
```bash
python3 monitoring/check_sovereign_status.py
```

### 4. Deploy Trading System
```bash
./deployment/AI_ENHANCED_DEPLOYMENT.sh
```

## 🎯 Core Components

- **sovereign_shadow_unified.py** - Main unified trading platform
- **scripts/** - Trading automation and arbitrage
- **config/** - API and system configuration
- **monitoring/** - Real-time monitoring and alerts
- **environments/** - Multi-tier deployment (Dev/Staging/Prod)

## 📊 System Status

Check current status: `python3 sovereign_shadow_unified.py`

---
*Last organized: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "*"
        
        readme_path = self.root / 'README.md'
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        print(f"\n📄 Created: README.md with directory structure")

def main():
    """Main execution"""
    import sys
    
    print("🧹 SOVEREIGNSHADOW.AI WORKSPACE ORGANIZER")
    print("=" * 80)
    
    organizer = WorkspaceOrganizer()
    
    # Analyze workspace
    loose_files, total = organizer.analyze_workspace()
    
    if total == 0:
        print("\n✅ Workspace is already clean!")
        return
    
    # Create structure
    organizer.create_structure()
    
    # Preview organization
    organizer.organize_files(dry_run=True)
    
    # Ask for confirmation
    if '--execute' in sys.argv or '--yes' in sys.argv:
        confirm = 'y'
    else:
        print("\n" + "=" * 80)
        print("⚠️  This will move files to organize the workspace.")
        print("   A backup will be created in archive/")
        confirm = input("\n🔹 Proceed with organization? (y/n): ").lower()
    
    if confirm == 'y':
        organizer.organize_files(dry_run=False)
        organizer.create_readme()
        
        print("\n" + "=" * 80)
        print("✅ WORKSPACE ORGANIZATION COMPLETE!")
        print("=" * 80)
        print("\n📁 Your workspace is now clean and organized!")
        print("📄 See README.md for the new structure")
        print("🗂️  All files backed up to archive/")
    else:
        print("\n❌ Organization cancelled")

if __name__ == "__main__":
    main()

