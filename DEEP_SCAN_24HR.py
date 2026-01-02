#!/usr/bin/env python3
"""
24-HOUR DEEP SCAN - Find EVERY system across the entire computer
Scans all accessible directories, catalogs all code, reports to WHAT_IS_IN_MY_COMPUTER.json
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

OUTPUT_FILE = "/Volumes/LegacySafe/SS_III/WHAT_IS_IN_MY_COMPUTER.json"
SCAN_DURATION = 24 * 60 * 60  # 24 hours in seconds

class DeepScanner:
    def __init__(self):
        self.findings = {
            "scan_started": datetime.now().isoformat(),
            "scan_duration_hours": 24,
            "total_directories_scanned": 0,
            "total_files_found": 0,
            "systems_found": {},
            "python_projects": {},
            "trading_systems": {},
            "gpt_prompts": [],
            "documentation": [],
            "config_files": [],
            "credentials": [],
            "excluded_dirs": []
        }

        self.skip_dirs = {
            'node_modules', '__pycache__', '.git', '.venv', 'venv',
            'Library/Caches', 'Library/Logs', '.Trash',
            'System', 'private/var', '.DocumentRevisions-V100'
        }

        self.interesting_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.md',
            '.env', '.yaml', '.yml', '.toml', '.txt', '.sh', '.bash'
        }

    def should_skip(self, path):
        """Check if directory should be skipped"""
        parts = Path(path).parts
        return any(skip in parts for skip in self.skip_dirs)

    def categorize_file(self, filepath):
        """Determine what category a file belongs to"""
        path = Path(filepath)
        name = path.name.lower()
        content_keywords = ['trading', 'crypto', 'wallet', 'exchange', 'coinbase',
                          'binance', 'aave', 'defi', 'portfolio', 'agent', 'strategy']

        # Check if it's a trading/crypto file
        if any(kw in str(path).lower() for kw in content_keywords):
            return 'trading_system'

        # Check for GPT prompts
        if 'prompt' in name or 'gpt' in name or 'custom_instructions' in name:
            return 'gpt_prompt'

        # Check for config
        if path.suffix in ['.env', '.yaml', '.yml', '.toml', '.json']:
            return 'config'

        # Check for documentation
        if path.suffix == '.md':
            return 'documentation'

        return 'code'

    def scan_directory(self, root_path):
        """Recursively scan a directory"""
        try:
            for dirpath, dirnames, filenames in os.walk(root_path):
                # Filter out directories to skip
                dirnames[:] = [d for d in dirnames if not self.should_skip(os.path.join(dirpath, d))]

                self.findings['total_directories_scanned'] += 1

                # Scan files in this directory
                py_files = []
                other_files = []

                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    ext = Path(filename).suffix

                    if ext not in self.interesting_extensions:
                        continue

                    self.findings['total_files_found'] += 1

                    try:
                        category = self.categorize_file(filepath)

                        if ext == '.py':
                            py_files.append(filename)

                        if category == 'trading_system':
                            rel_path = os.path.relpath(filepath, root_path)
                            if dirpath not in self.findings['trading_systems']:
                                self.findings['trading_systems'][dirpath] = []
                            self.findings['trading_systems'][dirpath].append(filename)

                        elif category == 'gpt_prompt':
                            self.findings['gpt_prompts'].append(filepath)

                        elif category == 'documentation' and 'README' in filename:
                            self.findings['documentation'].append(filepath)

                        elif category == 'config' and 'env' in filename:
                            self.findings['config_files'].append(filepath)

                    except Exception as e:
                        pass

                # If this directory has Python files, catalog it
                if py_files:
                    rel_path = os.path.relpath(dirpath, root_path)
                    self.findings['python_projects'][rel_path] = {
                        'file_count': len(py_files),
                        'files': py_files[:20]  # Store first 20 files
                    }

                # Progress report every 1000 directories
                if self.findings['total_directories_scanned'] % 1000 == 0:
                    self.save_progress()
                    print(f"[SCAN] {self.findings['total_directories_scanned']} dirs, "
                          f"{self.findings['total_files_found']} files, "
                          f"{len(self.findings['trading_systems'])} trading systems found")

        except PermissionError:
            self.findings['excluded_dirs'].append(f"{root_path} (permission denied)")
        except Exception as e:
            self.findings['excluded_dirs'].append(f"{root_path} (error: {str(e)})")

    def save_progress(self):
        """Save current findings to JSON file"""
        try:
            # Load existing data
            if os.path.exists(OUTPUT_FILE):
                with open(OUTPUT_FILE, 'r') as f:
                    existing = json.load(f)
            else:
                existing = {}

            # Add scan results to existing data
            existing['DEEP_SCAN_24HR'] = self.findings
            existing['last_scan_update'] = datetime.now().isoformat()

            # Write back
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(existing, f, indent=2)

        except Exception as e:
            print(f"Error saving progress: {e}")

    def run_scan(self):
        """Run the 24-hour deep scan"""
        start_time = time.time()
        end_time = start_time + SCAN_DURATION

        print(f"[DEEP SCAN] Starting 24-hour scan at {datetime.now()}")
        print(f"[DEEP SCAN] Will complete at {datetime.fromtimestamp(end_time)}")

        # Scan locations in priority order
        scan_paths = [
            "/Volumes/LegacySafe",
            "/Users/memphis/Downloads",
            "/Users/memphis/Documents",
            "/Users/memphis/Desktop",
            "/Users/memphis",
            "/"
        ]

        for path in scan_paths:
            if not os.path.exists(path):
                continue

            print(f"\n[SCAN] Starting scan of: {path}")
            self.scan_directory(path)

            # Check if we've exceeded 24 hours
            if time.time() > end_time:
                print(f"[SCAN] 24-hour limit reached")
                break

        # Final save
        self.findings['scan_completed'] = datetime.now().isoformat()
        self.findings['scan_duration_actual_hours'] = (time.time() - start_time) / 3600
        self.save_progress()

        print(f"\n[DEEP SCAN] COMPLETE")
        print(f"  Directories scanned: {self.findings['total_directories_scanned']}")
        print(f"  Files found: {self.findings['total_files_found']}")
        print(f"  Trading systems: {len(self.findings['trading_systems'])}")
        print(f"  Python projects: {len(self.findings['python_projects'])}")
        print(f"  GPT prompts: {len(self.findings['gpt_prompts'])}")
        print(f"\nResults saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    scanner = DeepScanner()
    scanner.run_scan()
