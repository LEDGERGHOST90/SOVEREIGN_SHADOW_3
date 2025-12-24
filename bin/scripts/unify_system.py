#!/usr/bin/env python3
"""
SOVEREIGN_SHADOW_3 (SS_III) System Unification Script
Automatically scans, analyzes, and consolidates the entire system
"""

import os
import json
from pathlib import Path
from collections import defaultdict
import hashlib

class SystemUnifier:
    def __init__(self, root_path):
        self.root = Path(root_path)
        self.duplicates = []
        self.archives = []
        self.active_files = []
        self.obsolete = []
        self.file_map = defaultdict(list)

    def scan_system(self):
        """Scan entire directory structure"""
        print("🔍 SCANNING SYSTEM...")
        print("=" * 70)

        # Directories to skip
        skip_dirs = {
            '.git', 'node_modules', '__pycache__',
            '.next', 'venv', '.venv', 'env'
        }

        total_files = 0
        total_size = 0

        for root, dirs, files in os.walk(self.root):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in skip_dirs]

            rel_path = Path(root).relative_to(self.root)

            for file in files:
                file_path = Path(root) / file

                if file_path.is_file():
                    try:
                        size = file_path.stat().st_size
                        total_files += 1
                        total_size += size

                        # Categorize files
                        if 'archive' in str(rel_path).lower() or 'backup' in str(rel_path).lower():
                            self.archives.append(file_path)
                        elif file.endswith(('.log', '.tmp', '.cache')):
                            self.obsolete.append(file_path)
                        else:
                            self.active_files.append(file_path)

                        # Track by name for duplicate detection
                        self.file_map[file].append(file_path)
                    except:
                        pass

        print(f"✅ Scanned: {total_files:,} files")
        print(f"📦 Total Size: {total_size / 1024 / 1024:.1f} MB")
        print(f"📁 Active Files: {len(self.active_files):,}")
        print(f"🗄️  Archive Files: {len(self.archives):,}")
        print(f"🗑️  Obsolete Files: {len(self.obsolete):,}")
        print()

    def find_duplicates(self):
        """Find duplicate files by content hash"""
        print("🔍 FINDING DUPLICATES...")
        print("=" * 70)

        hash_map = defaultdict(list)

        for file_path in self.active_files:
            if file_path.stat().st_size > 0:
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    hash_map[file_hash].append(file_path)
                except:
                    pass

        # Find actual duplicates (same hash, multiple files)
        for file_hash, paths in hash_map.items():
            if len(paths) > 1:
                self.duplicates.append(paths)

        print(f"✅ Found {len(self.duplicates)} groups of duplicate files")

        if self.duplicates:
            print("\nDuplicate Groups:")
            for i, group in enumerate(self.duplicates[:10], 1):
                print(f"\n{i}. {group[0].name} ({len(group)} copies):")
                for path in group:
                    rel_path = path.relative_to(self.root)
                    print(f"   - {rel_path}")

            if len(self.duplicates) > 10:
                print(f"\n   ... and {len(self.duplicates) - 10} more groups")
        print()

    def analyze_structure(self):
        """Analyze directory structure and purpose"""
        print("📊 ANALYZING STRUCTURE...")
        print("=" * 70)

        structure = {}

        for item in self.root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                file_count = sum(1 for _ in item.rglob('*') if _.is_file())
                total_size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())

                structure[item.name] = {
                    'files': file_count,
                    'size_mb': total_size / 1024 / 1024,
                    'purpose': self._detect_purpose(item)
                }

        # Sort by size
        sorted_dirs = sorted(structure.items(), key=lambda x: x[1]['size_mb'], reverse=True)

        print(f"{'Directory':<30} {'Files':<10} {'Size (MB)':<12} {'Purpose':<30}")
        print("-" * 90)

        for dir_name, info in sorted_dirs:
            print(f"{dir_name:<30} {info['files']:<10} {info['size_mb']:<12.1f} {info['purpose']:<30}")

        print()
        return structure

    def _detect_purpose(self, dir_path):
        """Detect directory purpose"""
        name = dir_path.name.lower()

        if 'archive' in name or 'backup' in name:
            return '🗄️  Archive/Backup'
        elif 'log' in name:
            return '📝 Logs'
        elif 'test' in name:
            return '🧪 Tests'
        elif 'doc' in name:
            return '📚 Documentation'
        elif name in ['agents', 'core', 'modules']:
            return '⚙️  Core System'
        elif name in ['scripts', 'tools', 'bin']:
            return '🔧 Utilities'
        elif name in ['app', 'frontend']:
            return '🎨 Frontend'
        elif name in ['venv', 'node_modules', '.next']:
            return '📦 Dependencies'
        else:
            return '❓ Unknown'

    def create_unification_plan(self, structure):
        """Create automated unification plan"""
        print("📋 UNIFICATION PLAN...")
        print("=" * 70)

        plan = {
            'keep': [],
            'archive': [],
            'delete': []
        }

        # Rules for unification
        for dir_name, info in structure.items():
            if info['purpose'] == '🗄️  Archive/Backup':
                if info['size_mb'] > 100:
                    plan['archive'].append(f"Compress {dir_name}/ (large archive)")
                else:
                    plan['keep'].append(f"Keep {dir_name}/ (archive)")

            elif info['purpose'] == '📝 Logs':
                if info['size_mb'] > 50:
                    plan['delete'].append(f"Clean old logs in {dir_name}/")
                else:
                    plan['keep'].append(f"Keep {dir_name}/ (manageable)")

            elif info['purpose'] == '⚙️  Core System':
                plan['keep'].append(f"Keep {dir_name}/ (CORE)")

            elif info['purpose'] == '🔧 Utilities':
                plan['keep'].append(f"Keep {dir_name}/ (utilities)")

            elif info['purpose'] == '📚 Documentation':
                plan['keep'].append(f"Keep {dir_name}/ (docs)")

            elif info['files'] == 0:
                plan['delete'].append(f"Remove empty {dir_name}/")

        # Duplicates
        for group in self.duplicates:
            # Keep first, mark rest for review
            plan['archive'].append(f"Review duplicates of {group[0].name}")

        # Obsolete files
        if len(self.obsolete) > 100:
            plan['delete'].append(f"Clean {len(self.obsolete)} obsolete files (.log, .tmp, .cache)")

        print("\n✅ KEEP (Core System):")
        for item in plan['keep'][:10]:
            print(f"  • {item}")

        print("\n🗄️  ARCHIVE/REVIEW:")
        for item in plan['archive'][:10]:
            print(f"  • {item}")

        print("\n🗑️  DELETE/CLEAN:")
        for item in plan['delete'][:10]:
            print(f"  • {item}")

        return plan

    def generate_report(self, structure, plan):
        """Generate unification report"""
        report = {
            'scan_date': str(Path.cwd()),
            'total_files': len(self.active_files) + len(self.archives) + len(self.obsolete),
            'active_files': len(self.active_files),
            'archive_files': len(self.archives),
            'obsolete_files': len(self.obsolete),
            'duplicate_groups': len(self.duplicates),
            'structure': structure,
            'plan': plan
        }

        report_file = self.root / 'SYSTEM_UNIFICATION_REPORT.json'
        report_file.write_text(json.dumps(report, indent=2, default=str))

        print(f"\n📄 Report saved: {report_file}")

        return report


if __name__ == "__main__":
    root_path = Path(__file__).parent.parent

    unifier = SystemUnifier(root_path)

    # Run analysis
    unifier.scan_system()
    unifier.find_duplicates()
    structure = unifier.analyze_structure()
    plan = unifier.create_unification_plan(structure)
    report = unifier.generate_report(structure, plan)

    print("\n" + "=" * 70)
    print("✅ SYSTEM ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"\nNext: Review SYSTEM_UNIFICATION_REPORT.json")
    print("Then I can execute the automated consolidation")
