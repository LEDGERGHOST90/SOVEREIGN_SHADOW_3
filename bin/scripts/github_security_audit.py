#!/usr/bin/env python3
"""
🔐 GITHUB SECURITY AUDIT - Pre-Deployment Scanner
Scans entire codebase for sensitive data before GitHub push
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

class SecurityAuditor:
    """Comprehensive security scanner for sensitive data"""

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.findings = defaultdict(list)

        # Sensitive patterns to search for
        self.patterns = {
            'api_key': [
                r'[A-Za-z0-9]{32,}',  # Generic 32+ char keys
                r'AKIA[0-9A-Z]{16}',  # AWS access key
                r'sk-[A-Za-z0-9]{40,}',  # OpenAI key
                r'[a-f0-9]{64}',  # 64-char hex keys
            ],
            'private_key': [
                r'-----BEGIN [A-Z ]+ PRIVATE KEY-----',
                r'BEGIN RSA PRIVATE KEY',
                r'BEGIN EC PRIVATE KEY',
            ],
            'ethereum_address': [
                r'0x[a-fA-F0-9]{40}',
            ],
            'database_url': [
                r'postgresql://[^\s]+',
                r'postgres://[^\s]+',
                r'mysql://[^\s]+',
                r'mongodb://[^\s]+',
            ],
            'secret': [
                r'["\']?secret["\']?\s*[:=]\s*["\'][^"\']{8,}["\']',
                r'["\']?password["\']?\s*[:=]\s*["\'][^"\']{8,}["\']',
                r'["\']?token["\']?\s*[:=]\s*["\'][^"\']{8,}["\']',
            ]
        }

        # Files/dirs to skip
        self.skip_patterns = {
            '__pycache__',
            'node_modules',
            '.next',
            '.git',
            'venv',
            'env',
            '.DS_Store',
            '*.pyc',
            '*.log',
            'package-lock.json',
        }

        # Known safe files (documentation, examples)
        self.safe_files = {
            'github_security_audit.py',  # This script
            'DEPLOYMENT_GUIDE.md',
            '.env.example',
        }

    def should_skip(self, path: Path) -> bool:
        """Check if path should be skipped"""
        path_str = str(path)

        # Skip by pattern
        for pattern in self.skip_patterns:
            if pattern in path_str:
                return True

        # Skip binary files
        if path.is_file():
            try:
                with open(path, 'rb') as f:
                    chunk = f.read(1024)
                    if b'\x00' in chunk:  # Binary file
                        return True
            except:
                return True

        return False

    def scan_file(self, file_path: Path) -> Dict[str, List[Dict]]:
        """Scan a single file for sensitive data"""
        findings = defaultdict(list)

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            for category, patterns in self.patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)

                    for match in matches:
                        # Get line number
                        line_num = content[:match.start()].count('\n') + 1

                        # Get context (50 chars before/after)
                        start = max(0, match.start() - 50)
                        end = min(len(content), match.end() + 50)
                        context = content[start:end].replace('\n', ' ')

                        findings[category].append({
                            'file': str(file_path.relative_to(self.root_dir)),
                            'line': line_num,
                            'match': match.group(),
                            'context': context,
                            'pattern': pattern
                        })

        except Exception as e:
            pass  # Skip files that can't be read

        return findings

    def scan_directory(self):
        """Scan entire directory tree"""
        print(f"🔍 Scanning: {self.root_dir}")
        print(f"{'='*70}\n")

        total_files = 0
        scanned_files = 0

        for root, dirs, files in os.walk(self.root_dir):
            root_path = Path(root)

            # Skip directories
            dirs[:] = [d for d in dirs if not self.should_skip(root_path / d)]

            for filename in files:
                file_path = root_path / filename
                total_files += 1

                # Skip files
                if self.should_skip(file_path) or filename in self.safe_files:
                    continue

                scanned_files += 1

                # Scan file
                file_findings = self.scan_file(file_path)

                for category, findings in file_findings.items():
                    self.findings[category].extend(findings)

        print(f"📊 Stats:")
        print(f"   Total files: {total_files:,}")
        print(f"   Scanned: {scanned_files:,}")
        print(f"   Skipped: {total_files - scanned_files:,}\n")

    def generate_report(self) -> dict:
        """Generate comprehensive security report"""
        report = {
            'timestamp': str(Path.cwd()),
            'total_findings': sum(len(v) for v in self.findings.values()),
            'categories': {},
            'critical_files': [],
            'summary': {}
        }

        # Group findings by category
        for category, findings in self.findings.items():
            unique_files = set(f['file'] for f in findings)

            report['categories'][category] = {
                'count': len(findings),
                'files_affected': len(unique_files),
                'findings': findings
            }

            report['summary'][category] = len(findings)

        # Identify critical files (most findings)
        file_counts = defaultdict(int)
        for findings in self.findings.values():
            for finding in findings:
                file_counts[finding['file']] += 1

        report['critical_files'] = [
            {'file': f, 'finding_count': c}
            for f, c in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        ]

        return report

    def print_report(self, report: dict):
        """Print human-readable report"""
        print(f"\n{'='*70}")
        print(f"🔐 SECURITY AUDIT REPORT")
        print(f"{'='*70}\n")

        print(f"⚠️  TOTAL FINDINGS: {report['total_findings']}\n")

        if report['total_findings'] == 0:
            print("✅ No sensitive data found! Safe to push to GitHub.\n")
            return

        print(f"📋 FINDINGS BY CATEGORY:\n")
        for category, data in report['categories'].items():
            print(f"   {category.upper().replace('_', ' ')}:")
            print(f"   ├─ Total matches: {data['count']}")
            print(f"   └─ Files affected: {data['files_affected']}\n")

        print(f"🚨 TOP 20 FILES WITH MOST SECRETS:\n")
        for item in report['critical_files'][:20]:
            print(f"   {item['finding_count']:3d} findings → {item['file']}")

        print(f"\n{'='*70}")
        print(f"⚠️  ACTION REQUIRED:")
        print(f"{'='*70}\n")
        print(f"1. Review detailed findings in: logs/security_audit_detailed.json")
        print(f"2. Remove/replace ALL sensitive data before GitHub push")
        print(f"3. Create .env.example with placeholder values")
        print(f"4. Update .gitignore to block sensitive files")
        print(f"5. Run this audit again before pushing")
        print(f"\n{'='*70}\n")


def main():
    """Run security audit"""
    root_dir = Path(__file__).parent.parent

    auditor = SecurityAuditor(root_dir)
    auditor.scan_directory()

    report = auditor.generate_report()
    auditor.print_report(report)

    # Save detailed report
    output_dir = root_dir / 'logs'
    output_dir.mkdir(exist_ok=True)

    with open(output_dir / 'security_audit_summary.json', 'w') as f:
        json.dump({
            'total_findings': report['total_findings'],
            'summary': report['summary'],
            'critical_files': report['critical_files']
        }, f, indent=2)

    with open(output_dir / 'security_audit_detailed.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"💾 Reports saved to:")
    print(f"   - logs/security_audit_summary.json")
    print(f"   - logs/security_audit_detailed.json\n")

    # Return exit code based on findings
    return 1 if report['total_findings'] > 0 else 0


if __name__ == '__main__':
    exit(main())
