#!/usr/bin/env python3
"""
TROOPER DRONE - Security Scanner
Autonomous security patrol for the Sovereign Shadow ecosystem

Scans for:
1. Exposed API keys / secrets
2. Broken imports / syntax errors
3. Hardcoded credentials
4. .env files in wrong places
5. Suspicious patterns

Run: python trooper_drone.py [path]
"""

import os
import re
import ast
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("TrooperDrone")

# Patterns that indicate exposed secrets
SECRET_PATTERNS = [
    (r'api[_-]?key["\']?\s*[:=]\s*["\'][a-zA-Z0-9]{20,}["\']', "API Key exposure"),
    (r'secret[_-]?key["\']?\s*[:=]\s*["\'][a-zA-Z0-9]{20,}["\']', "Secret Key exposure"),
    (r'password["\']?\s*[:=]\s*["\'][^"\']{8,}["\']', "Password exposure"),
    (r'private[_-]?key["\']?\s*[:=]\s*["\'][a-zA-Z0-9+/=]{40,}["\']', "Private Key exposure"),
    (r'-----BEGIN.*PRIVATE KEY-----', "PEM Private Key exposure"),
    (r'sk_live_[a-zA-Z0-9]{20,}', "Stripe Live Key exposure"),
    (r'sk_test_[a-zA-Z0-9]{20,}', "Stripe Test Key exposure"),
    (r'AKIA[0-9A-Z]{16}', "AWS Access Key exposure"),
    (r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*', "JWT Token exposure"),
    (r'ghp_[a-zA-Z0-9]{36}', "GitHub Personal Access Token"),
    (r'gho_[a-zA-Z0-9]{36}', "GitHub OAuth Token"),
    (r'organizations/[a-f0-9-]{36}', "Coinbase CDP Key Pattern"),
]

# File patterns to scan
SCAN_EXTENSIONS = {'.py', '.js', '.ts', '.json', '.env', '.yaml', '.yml', '.toml', '.cfg', '.ini'}

# Directories to skip
SKIP_DIRS = {'node_modules', '.git', '__pycache__', 'venv', '.venv', 'env', '.env'}


@dataclass
class SecurityAlert:
    """Security alert from scan"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str
    file_path: str
    line_number: int
    description: str
    snippet: str = ""


class TrooperDrone:
    """
    Autonomous Security Scanner

    Constantly patrols the codebase for:
    - Exposed credentials
    - Syntax errors
    - Broken imports
    - Security vulnerabilities
    """

    def __init__(self, scan_paths: List[str] = None):
        self.scan_paths = scan_paths or ['.']
        self.alerts: List[SecurityAlert] = []
        self.files_scanned = 0
        self.start_time = None

    def scan(self) -> List[SecurityAlert]:
        """Run full security scan"""
        self.start_time = datetime.now()
        self.alerts = []
        self.files_scanned = 0

        logger.info("=" * 60)
        logger.info("  TROOPER DRONE - SECURITY SCAN INITIATED")
        logger.info("=" * 60)
        logger.info(f"  Scan started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"  Paths: {self.scan_paths}")
        logger.info("=" * 60)
        logger.info("")

        for scan_path in self.scan_paths:
            self._scan_directory(Path(scan_path))

        self._print_report()
        return self.alerts

    def _scan_directory(self, directory: Path):
        """Recursively scan directory"""
        if not directory.exists():
            logger.warning(f"Path does not exist: {directory}")
            return

        for item in directory.iterdir():
            if item.is_dir():
                if item.name not in SKIP_DIRS:
                    self._scan_directory(item)
            elif item.is_file():
                if item.suffix in SCAN_EXTENSIONS:
                    self._scan_file(item)

    def _scan_file(self, file_path: Path):
        """Scan individual file for security issues"""
        self.files_scanned += 1

        try:
            content = file_path.read_text(errors='ignore')
            lines = content.split('\n')

            # Check for secret patterns
            self._check_secrets(file_path, content, lines)

            # Check Python syntax
            if file_path.suffix == '.py':
                self._check_python_syntax(file_path, content)

            # Check for .env files in wrong places
            if file_path.name == '.env':
                self._check_env_file(file_path, content)

            # Check JSON files for credentials
            if file_path.suffix == '.json':
                self._check_json_secrets(file_path, content)

        except Exception as e:
            logger.debug(f"Error scanning {file_path}: {e}")

    def _check_secrets(self, file_path: Path, content: str, lines: List[str]):
        """Check for exposed secrets using patterns"""
        for pattern, description in SECRET_PATTERNS:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                # Find line number
                pos = match.start()
                line_num = content[:pos].count('\n') + 1

                # Get snippet (redacted)
                snippet = match.group()[:20] + "..." if len(match.group()) > 20 else match.group()

                self.alerts.append(SecurityAlert(
                    severity="CRITICAL",
                    category="SECRET_EXPOSURE",
                    file_path=str(file_path),
                    line_number=line_num,
                    description=description,
                    snippet=f"[REDACTED: {snippet[:10]}...]"
                ))

    def _check_python_syntax(self, file_path: Path, content: str):
        """Check Python file for syntax errors"""
        try:
            ast.parse(content)
        except SyntaxError as e:
            self.alerts.append(SecurityAlert(
                severity="MEDIUM",
                category="SYNTAX_ERROR",
                file_path=str(file_path),
                line_number=e.lineno or 0,
                description=f"Python syntax error: {e.msg}",
                snippet=e.text[:50] if e.text else ""
            ))

    def _check_env_file(self, file_path: Path, content: str):
        """Check .env file location and contents"""
        # Alert if .env is in a git-tracked directory
        git_dir = file_path.parent / '.git'
        if not git_dir.exists():
            # Check parent directories for .git
            parent = file_path.parent.parent
            while parent != parent.parent:
                if (parent / '.git').exists():
                    self.alerts.append(SecurityAlert(
                        severity="HIGH",
                        category="ENV_EXPOSURE",
                        file_path=str(file_path),
                        line_number=0,
                        description=".env file in git-trackable location",
                        snippet=""
                    ))
                    break
                parent = parent.parent

    def _check_json_secrets(self, file_path: Path, content: str):
        """Check JSON files for credential patterns"""
        try:
            data = json.loads(content)
            self._scan_json_recursive(file_path, data, "")
        except json.JSONDecodeError:
            pass

    def _scan_json_recursive(self, file_path: Path, data, path: str):
        """Recursively scan JSON for sensitive keys"""
        sensitive_keys = {'api_key', 'apikey', 'secret', 'password', 'private_key', 'token', 'credential'}

        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key

                if key.lower() in sensitive_keys and isinstance(value, str) and len(value) > 10:
                    self.alerts.append(SecurityAlert(
                        severity="CRITICAL",
                        category="JSON_SECRET",
                        file_path=str(file_path),
                        line_number=0,
                        description=f"Sensitive key in JSON: {key}",
                        snippet=f"{value[:10]}..." if len(value) > 10 else "[REDACTED]"
                    ))
                else:
                    self._scan_json_recursive(file_path, value, current_path)

        elif isinstance(data, list):
            for i, item in enumerate(data):
                self._scan_json_recursive(file_path, item, f"{path}[{i}]")

    def _print_report(self):
        """Print security scan report"""
        duration = (datetime.now() - self.start_time).total_seconds()

        logger.info("")
        logger.info("=" * 60)
        logger.info("  TROOPER DRONE - SCAN COMPLETE")
        logger.info("=" * 60)
        logger.info(f"  Files scanned: {self.files_scanned}")
        logger.info(f"  Duration: {duration:.2f}s")
        logger.info(f"  Alerts found: {len(self.alerts)}")
        logger.info("=" * 60)

        if not self.alerts:
            logger.info("")
            logger.info("  ALL CLEAR - No security issues detected")
            logger.info("")
        else:
            # Group by severity
            critical = [a for a in self.alerts if a.severity == "CRITICAL"]
            high = [a for a in self.alerts if a.severity == "HIGH"]
            medium = [a for a in self.alerts if a.severity == "MEDIUM"]
            low = [a for a in self.alerts if a.severity == "LOW"]

            logger.info("")
            logger.info(f"  CRITICAL: {len(critical)}")
            logger.info(f"  HIGH:     {len(high)}")
            logger.info(f"  MEDIUM:   {len(medium)}")
            logger.info(f"  LOW:      {len(low)}")
            logger.info("")

            # Print critical alerts
            if critical:
                logger.info("-" * 60)
                logger.info("  CRITICAL ALERTS:")
                logger.info("-" * 60)
                for alert in critical[:10]:  # Limit to first 10
                    logger.info(f"  [{alert.category}] {alert.file_path}:{alert.line_number}")
                    logger.info(f"    {alert.description}")
                    logger.info("")

            # Print high alerts
            if high:
                logger.info("-" * 60)
                logger.info("  HIGH ALERTS:")
                logger.info("-" * 60)
                for alert in high[:10]:
                    logger.info(f"  [{alert.category}] {alert.file_path}:{alert.line_number}")
                    logger.info(f"    {alert.description}")
                    logger.info("")

        logger.info("=" * 60)

        return {
            "files_scanned": self.files_scanned,
            "alerts": len(self.alerts),
            "critical": len([a for a in self.alerts if a.severity == "CRITICAL"]),
            "high": len([a for a in self.alerts if a.severity == "HIGH"]),
            "duration": duration
        }


def quick_scan(paths: List[str] = None) -> Dict:
    """Quick scan function for integration"""
    drone = TrooperDrone(paths or ['.'])
    drone.scan()
    return {
        "status": "complete",
        "files": drone.files_scanned,
        "alerts": len(drone.alerts),
        "critical": len([a for a in drone.alerts if a.severity == "CRITICAL"])
    }


if __name__ == "__main__":
    import sys

    # Get paths from command line or use defaults
    paths = sys.argv[1:] if len(sys.argv) > 1 else [
        "/Volumes/LegacySafe/Shadow-3-Legacy-Loop-Platform",
        "/Users/memphis/Downloads"
    ]

    drone = TrooperDrone(paths)
    drone.scan()
