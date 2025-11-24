#!/usr/bin/env python3
"""
Dual System Comprehensive Unification Analysis
Scans ClaudeSDK + SovereignShadow_II and creates unified architecture
"""

import os
import json
from pathlib import Path
from collections import defaultdict
import hashlib

class DualSystemAnalyzer:
    def __init__(self, sdk_path, shadow_path):
        self.sdk_root = Path(sdk_path)
        self.shadow_root = Path(shadow_path)
        self.sdk_files = {}
        self.shadow_files = {}
        self.shared_files = []
        self.duplicates = []
        self.unified_structure = {}

    def scan_directory(self, root_path, name):
        """Deep scan of directory"""
        print(f"\n🔍 SCANNING: {name}")
        print("=" * 70)

        skip_dirs = {'.git', 'node_modules', '__pycache__', '.next', 'venv', '.venv', 'env'}

        files = {}
        total_files = 0
        total_size = 0
        file_types = defaultdict(int)
        code_files = []

        for root, dirs, filenames in os.walk(root_path):
            dirs[:] = [d for d in dirs if d not in skip_dirs]

            for filename in filenames:
                file_path = Path(root) / filename

                if file_path.is_file():
                    try:
                        size = file_path.stat().st_size
                        rel_path = file_path.relative_to(root_path)

                        total_files += 1
                        total_size += size

                        ext = file_path.suffix.lower()
                        file_types[ext if ext else 'no_ext'] += 1

                        # Categorize code files
                        if ext in ['.py', '.js', '.ts', '.tsx', '.json', '.yaml', '.yml', '.sh']:
                            code_files.append(file_path)

                        files[str(rel_path)] = {
                            'path': file_path,
                            'size': size,
                            'type': ext,
                            'rel_path': str(rel_path)
                        }
                    except:
                        pass

        print(f"✅ Files: {total_files:,}")
        print(f"📦 Size: {total_size / 1024 / 1024:.1f} MB")
        print(f"💻 Code Files: {len(code_files):,}")
        print(f"\nFile Types:")
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {ext:15s} {count:>6,}")

        return files

    def find_shared_files(self):
        """Find files that exist in both projects"""
        print(f"\n🔗 FINDING SHARED/DUPLICATE FILES...")
        print("=" * 70)

        sdk_names = {Path(f['rel_path']).name: f for f in self.sdk_files.values()}
        shadow_names = {Path(f['rel_path']).name: f for f in self.shadow_files.values()}

        shared_names = set(sdk_names.keys()) & set(shadow_names.keys())

        print(f"✅ Found {len(shared_names)} files with same name in both projects")

        # Check if they're actually the same content
        for name in list(shared_names)[:20]:
            sdk_file = sdk_names[name]
            shadow_file = shadow_names[name]

            try:
                sdk_hash = hashlib.md5(sdk_file['path'].read_bytes()).hexdigest()
                shadow_hash = hashlib.md5(shadow_file['path'].read_bytes()).hexdigest()

                if sdk_hash == shadow_hash:
                    status = "✅ IDENTICAL"
                else:
                    status = "⚠️  DIFFERENT"

                print(f"  {status} {name}")
                print(f"     ClaudeSDK: {sdk_file['rel_path']}")
                print(f"     ShadowII:  {shadow_file['rel_path']}")

                self.shared_files.append({
                    'name': name,
                    'sdk': sdk_file,
                    'shadow': shadow_file,
                    'identical': sdk_hash == shadow_hash
                })
            except:
                pass

        if len(shared_names) > 20:
            print(f"\n  ... and {len(shared_names) - 20} more shared files")

    def analyze_purpose(self):
        """Understand the purpose of each system"""
        print(f"\n📊 ANALYZING SYSTEM PURPOSES...")
        print("=" * 70)

        # ClaudeSDK analysis
        print("\n📦 ClaudeSDK Purpose:")
        sdk_indicators = {
            'mcp': 0,
            'claude': 0,
            'sdk': 0,
            'agent': 0,
            'tool': 0
        }

        for file_info in self.sdk_files.values():
            path_str = str(file_info['rel_path']).lower()
            for keyword in sdk_indicators:
                if keyword in path_str:
                    sdk_indicators[keyword] += 1

        for keyword, count in sorted(sdk_indicators.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                print(f"  {keyword.upper():15s} {count:>4} references")

        # SovereignShadow analysis
        print("\n💰 SovereignShadow_II Purpose:")
        shadow_indicators = {
            'trading': 0,
            'portfolio': 0,
            'exchange': 0,
            'aave': 0,
            'ledger': 0,
            'agent': 0,
            'shadow': 0
        }

        for file_info in self.shadow_files.values():
            path_str = str(file_info['rel_path']).lower()
            for keyword in shadow_indicators:
                if keyword in path_str:
                    shadow_indicators[keyword] += 1

        for keyword, count in sorted(shadow_indicators.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                print(f"  {keyword.upper():15s} {count:>4} references")

    def create_unified_plan(self):
        """Create plan to unify both systems"""
        print(f"\n🎯 UNIFIED ARCHITECTURE PLAN...")
        print("=" * 70)

        plan = {
            'verdict': '',
            'approach': '',
            'actions': []
        }

        # Determine relationship
        identical_count = sum(1 for f in self.shared_files if f.get('identical'))
        different_count = len(self.shared_files) - identical_count

        print(f"\nShared Files Analysis:")
        print(f"  Identical: {identical_count}")
        print(f"  Different: {different_count}")

        if len(self.shared_files) > 50 and identical_count > len(self.shared_files) * 0.5:
            plan['verdict'] = "SIGNIFICANT OVERLAP - Likely duplicated project"
            plan['approach'] = "MERGE: Consolidate into single unified system"
            plan['actions'] = [
                "Keep SovereignShadow_II as main project",
                "Merge unique ClaudeSDK features into SovereignShadow_II",
                "Archive ClaudeSDK after merge",
                "Remove duplicates"
            ]
        elif len(self.shared_files) > 20:
            plan['verdict'] = "MODERATE OVERLAP - Shared utilities/libraries"
            plan['approach'] = "EXTRACT: Create shared library"
            plan['actions'] = [
                "Extract common code to shared/ directory",
                "Both projects import from shared/",
                "Keep both projects separate",
                "Eliminate duplicate implementations"
            ]
        else:
            plan['verdict'] = "MINIMAL OVERLAP - Independent projects"
            plan['approach'] = "KEEP SEPARATE: Different purposes"
            plan['actions'] = [
                "Keep ClaudeSDK separate (SDK/MCP tools)",
                "Keep SovereignShadow_II separate (Trading system)",
                "Link if needed via import/module system"
            ]

        print(f"\n✅ VERDICT: {plan['verdict']}")
        print(f"📋 APPROACH: {plan['approach']}")
        print(f"\nRecommended Actions:")
        for i, action in enumerate(plan['actions'], 1):
            print(f"  {i}. {action}")

        return plan

    def generate_comprehensive_report(self, plan):
        """Generate final comprehensive report"""
        report = {
            'analysis_date': str(Path.cwd()),
            'systems': {
                'ClaudeSDK': {
                    'path': str(self.sdk_root),
                    'files': len(self.sdk_files),
                    'size_mb': sum(f['size'] for f in self.sdk_files.values()) / 1024 / 1024
                },
                'SovereignShadow_II': {
                    'path': str(self.shadow_root),
                    'files': len(self.shadow_files),
                    'size_mb': sum(f['size'] for f in self.shadow_files.values()) / 1024 / 1024
                }
            },
            'shared_files': {
                'total': len(self.shared_files),
                'identical': sum(1 for f in self.shared_files if f.get('identical')),
                'different': sum(1 for f in self.shared_files if not f.get('identical'))
            },
            'plan': plan
        }

        report_file = Path('/Volumes/LegacySafe/DUAL_SYSTEM_UNIFICATION_REPORT.json')
        report_file.write_text(json.dumps(report, indent=2, default=str))

        print(f"\n📄 Report saved: {report_file}")

        return report


if __name__ == "__main__":
    sdk_path = "/Volumes/LegacySafe/ClaudeSDK"
    shadow_path = "/Volumes/LegacySafe/SovereignShadow_II"

    analyzer = DualSystemAnalyzer(sdk_path, shadow_path)

    # Scan both systems
    analyzer.sdk_files = analyzer.scan_directory(analyzer.sdk_root, "ClaudeSDK")
    analyzer.shadow_files = analyzer.scan_directory(analyzer.shadow_root, "SovereignShadow_II")

    # Find relationships
    analyzer.find_shared_files()
    analyzer.analyze_purpose()

    # Create unification plan
    plan = analyzer.create_unified_plan()

    # Generate report
    report = analyzer.generate_comprehensive_report(plan)

    print("\n" + "=" * 70)
    print("✅ DUAL SYSTEM ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"\nReview: /Volumes/LegacySafe/DUAL_SYSTEM_UNIFICATION_REPORT.json")
    print("Ready to execute unification plan on your command")
