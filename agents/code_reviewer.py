#!/usr/bin/env python3
"""
🔍 Code Reviewer Agent - Sovereign Shadow II
Reviews code quality, finds bugs, suggests improvements
"""

import ast
import json
from datetime import datetime
from pathlib import Path


class CodeReviewerAgent:
    """Code quality analysis and review"""

    def __init__(self):
        self.name = "Code Reviewer Agent"
        self.issues = []
        print(f"✅ {self.name} initialized")

    def review_python_file(self, file_path):
        """Review a Python file for issues"""
        file_path = Path(file_path)
        if not file_path.exists():
            return {'error': 'File not found'}

        issues = []

        try:
            with open(file_path, 'r') as f:
                code = f.read()

            # Parse AST
            tree = ast.parse(code)

            # Check for common issues
            for node in ast.walk(tree):
                # Bare except clauses
                if isinstance(node, ast.ExceptHandler):
                    if node.type is None:
                        issues.append({
                            'type': 'BAD_PRACTICE',
                            'line': node.lineno,
                            'message': 'Bare except clause - specify exception type',
                            'severity': 'MEDIUM'
                        })

                # Print statements (should use logging)
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == 'print':
                        issues.append({
                            'type': 'SUGGESTION',
                            'line': node.lineno,
                            'message': 'Consider using logging instead of print',
                            'severity': 'LOW'
                        })

                # TODO comments
                if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                    if isinstance(node.value.value, str) and 'TODO' in node.value.value:
                        issues.append({
                            'type': 'TODO',
                            'line': node.lineno,
                            'message': f"TODO found: {node.value.value}",
                            'severity': 'INFO'
                        })

            # Check for missing docstrings
            if not ast.get_docstring(tree):
                issues.append({
                    'type': 'MISSING_DOC',
                    'line': 1,
                    'message': 'Module missing docstring',
                    'severity': 'LOW'
                })

            return {
                'file': str(file_path),
                'issues': issues,
                'total_issues': len(issues),
                'lines_of_code': len(code.splitlines())
            }

        except SyntaxError as e:
            return {
                'file': str(file_path),
                'error': f'Syntax error: {e}',
                'issues': [{
                    'type': 'SYNTAX_ERROR',
                    'line': e.lineno,
                    'message': e.msg,
                    'severity': 'CRITICAL'
                }]
            }

    def review_directory(self, directory):
        """Review all Python files in a directory"""
        directory = Path(directory)
        if not directory.exists():
            return {'error': 'Directory not found'}

        results = []
        python_files = list(directory.rglob('*.py'))

        for file_path in python_files:
            if '__pycache__' not in str(file_path):
                result = self.review_python_file(file_path)
                if result.get('total_issues', 0) > 0:
                    results.append(result)

        return results

    def check_for_security_issues(self, file_path):
        """Check for common security issues"""
        file_path = Path(file_path)
        security_issues = []

        try:
            with open(file_path, 'r') as f:
                code = f.read()

            # Check for hardcoded secrets
            if any(keyword in code for keyword in ['password =', 'api_key =', 'secret =']):
                security_issues.append({
                    'type': 'SECURITY',
                    'message': 'Possible hardcoded credentials detected',
                    'severity': 'HIGH',
                    'recommendation': 'Use environment variables'
                })

            # Check for SQL injection risks
            if 'execute(' in code and 'f"' in code:
                security_issues.append({
                    'type': 'SECURITY',
                    'message': 'Possible SQL injection risk with f-strings',
                    'severity': 'HIGH',
                    'recommendation': 'Use parameterized queries'
                })

            # Check for unsafe eval/exec
            if 'eval(' in code or 'exec(' in code:
                security_issues.append({
                    'type': 'SECURITY',
                    'message': 'Use of eval() or exec() detected',
                    'severity': 'CRITICAL',
                    'recommendation': 'Avoid eval/exec - major security risk'
                })

        except Exception as e:
            security_issues.append({
                'type': 'ERROR',
                'message': f'Security scan error: {e}',
                'severity': 'INFO'
            })

        return security_issues

    def generate_report(self, target_dir='agents'):
        """Generate code review report"""
        print(f"\n{'='*70}")
        print(f"🔍 {self.name.upper()} - CODE REVIEW")
        print(f"{'='*70}\n")

        # Review agents directory
        target_path = Path(__file__).parent.parent / target_dir
        print(f"📁 Reviewing: {target_path}")

        results = self.review_directory(target_path)

        # Count issues by severity
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}

        for result in results:
            for issue in result.get('issues', []):
                severity = issue.get('severity', 'INFO')
                severity_counts[severity] += 1

        # Display summary
        print(f"\n📊 REVIEW SUMMARY:")
        print(f"  Files reviewed: {len(results)}")
        print(f"  Total issues: {sum(severity_counts.values())}")
        print(f"\n  By severity:")
        for severity, count in severity_counts.items():
            if count > 0:
                emoji = {'CRITICAL': '🚨', 'HIGH': '🔴', 'MEDIUM': '🟠', 'LOW': '🟡', 'INFO': 'ℹ️'}
                print(f"    {emoji[severity]} {severity}: {count}")

        # Display top issues
        print(f"\n🔴 TOP ISSUES:")
        all_issues = []
        for result in results:
            for issue in result.get('issues', []):
                all_issues.append({
                    'file': result['file'],
                    **issue
                })

        # Sort by severity
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'INFO': 4}
        all_issues.sort(key=lambda x: severity_order.get(x['severity'], 5))

        for i, issue in enumerate(all_issues[:10], 1):
            print(f"\n  {i}. [{issue['severity']}] {Path(issue['file']).name}:{issue['line']}")
            print(f"     {issue['message']}")

        print(f"\n{'='*70}")

        return {
            'results': results,
            'summary': {
                'files_reviewed': len(results),
                'total_issues': sum(severity_counts.values()),
                'by_severity': severity_counts
            },
            'timestamp': datetime.now().isoformat()
        }


if __name__ == '__main__':
    agent = CodeReviewerAgent()
    report = agent.generate_report()

    # Save report
    output_file = Path(__file__).parent.parent / 'logs' / 'code_review_report.json'
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n📄 Report saved to: {output_file}")
