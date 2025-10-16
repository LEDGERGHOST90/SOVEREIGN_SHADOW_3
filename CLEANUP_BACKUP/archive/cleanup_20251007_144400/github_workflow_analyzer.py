#!/usr/bin/env python3
"""
GitHub Workflow Analyzer for Legacy Loop
Analyzes GitHub Actions, workflows, and repository configurations
"""

import yaml
import json
from pathlib import Path
from datetime import datetime
import re

class GitHubWorkflowAnalyzer:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.workflows = {}
        self.actions = {}
        self.repositories = {}
        
    def analyze_github_integration(self):
        """Analyze all GitHub-related files"""
        print("🐙 Analyzing GitHub Integration...")
        
        # Find GitHub workflow files
        workflow_files = list(self.root_path.rglob(".github/workflows/*.yml")) + \
                        list(self.root_path.rglob(".github/workflows/*.yaml"))
        
        # Find other GitHub config files
        github_files = list(self.root_path.rglob(".github/*.yml")) + \
                      list(self.root_path.rglob(".github/*.yaml")) + \
                      list(self.root_path.rglob(".github/*.json")) + \
                      list(self.root_path.rglob(".gitignore")) + \
                      list(self.root_path.rglob(".gitattributes"))
        
        for workflow_file in workflow_files:
            self.analyze_workflow_file(workflow_file)
        
        for github_file in github_files:
            self.analyze_github_config_file(github_file)
        
        print(f"✅ Found {len(self.workflows)} workflows and {len(github_files)} GitHub config files")
        return self.generate_github_report()
    
    def analyze_workflow_file(self, file_path):
        """Analyze GitHub Actions workflow file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            workflow_info = {
                'path': str(file_path.relative_to(self.root_path)),
                'full_path': str(file_path),
                'size': len(content),
                'type': 'github-workflow',
                'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                'jobs': [],
                'triggers': [],
                'actions_used': [],
                'environments': [],
                'secrets_used': []
            }
            
            try:
                workflow_data = yaml.safe_load(content)
                
                # Extract workflow metadata
                if 'name' in workflow_data:
                    workflow_info['name'] = workflow_data['name']
                
                # Extract triggers
                if 'on' in workflow_data:
                    triggers = workflow_data['on']
                    if isinstance(triggers, dict):
                        workflow_info['triggers'] = list(triggers.keys())
                    elif isinstance(triggers, list):
                        workflow_info['triggers'] = triggers
                    else:
                        workflow_info['triggers'] = [triggers]
                
                # Extract jobs
                if 'jobs' in workflow_data:
                    for job_name, job_config in workflow_data['jobs'].items():
                        job_info = {
                            'name': job_name,
                            'runs_on': job_config.get('runs-on', ''),
                            'steps': len(job_config.get('steps', [])),
                            'uses_actions': [],
                            'environment': job_config.get('environment', ''),
                            'secrets': []
                        }
                        
                        # Extract actions used
                        for step in job_config.get('steps', []):
                            if 'uses' in step:
                                action = step['uses']
                                job_info['uses_actions'].append(action)
                                workflow_info['actions_used'].append(action)
                        
                        # Extract secrets
                        if 'secrets' in job_config:
                            job_info['secrets'] = list(job_config['secrets'].keys())
                            workflow_info['secrets_used'].extend(job_config['secrets'].keys())
                        
                        workflow_info['jobs'].append(job_info)
                
                # Extract environments
                for job in workflow_info['jobs']:
                    if job['environment']:
                        workflow_info['environments'].append(job['environment'])
                
                workflow_info['environments'] = list(set(workflow_info['environments']))
                workflow_info['secrets_used'] = list(set(workflow_info['secrets_used']))
                
            except yaml.YAMLError as e:
                print(f"⚠️  YAML parsing error in {file_path}: {e}")
            
            self.workflows[file_path.stem] = workflow_info
            
        except Exception as e:
            print(f"❌ Error analyzing workflow {file_path}: {e}")
    
    def analyze_github_config_file(self, file_path):
        """Analyze other GitHub configuration files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            config_info = {
                'path': str(file_path.relative_to(self.root_path)),
                'full_path': str(file_path),
                'size': len(content),
                'type': file_path.name,
                'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                'content_analysis': self.analyze_config_content(content, file_path.name)
            }
            
            self.repositories[file_path.stem] = config_info
            
        except Exception as e:
            print(f"❌ Error analyzing config {file_path}: {e}")
    
    def analyze_config_content(self, content, filename):
        """Analyze content of GitHub config files"""
        analysis = {}
        
        if filename == '.gitignore':
            analysis['ignored_patterns'] = [line.strip() for line in content.splitlines() 
                                          if line.strip() and not line.startswith('#')]
            analysis['total_patterns'] = len(analysis['ignored_patterns'])
        
        elif filename == '.gitattributes':
            analysis['attributes'] = [line.strip() for line in content.splitlines() 
                                    if line.strip() and not line.startswith('#')]
            analysis['total_attributes'] = len(analysis['attributes'])
        
        elif filename.endswith('.yml') or filename.endswith('.yaml'):
            try:
                yaml_data = yaml.safe_load(content)
                analysis['yaml_keys'] = list(yaml_data.keys()) if isinstance(yaml_data, dict) else []
            except yaml.YAMLError:
                analysis['yaml_keys'] = []
        
        elif filename.endswith('.json'):
            try:
                json_data = json.loads(content)
                analysis['json_keys'] = list(json_data.keys()) if isinstance(json_data, dict) else []
            except json.JSONDecodeError:
                analysis['json_keys'] = []
        
        return analysis
    
    def generate_github_report(self):
        """Generate comprehensive GitHub integration report"""
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'total_workflows': len(self.workflows),
            'total_config_files': len(self.repositories),
            'workflows': self.workflows,
            'repository_configs': self.repositories,
            'integration_summary': self.generate_integration_summary()
        }
        
        return report
    
    def generate_integration_summary(self):
        """Generate GitHub integration summary"""
        summary = {
            'workflow_triggers': [],
            'common_actions': [],
            'environments_used': [],
            'secrets_required': [],
            'potential_issues': [],
            'recommendations': []
        }
        
        # Analyze workflows
        all_triggers = []
        all_actions = []
        all_environments = []
        all_secrets = []
        
        for workflow_name, workflow_info in self.workflows.items():
            all_triggers.extend(workflow_info.get('triggers', []))
            all_actions.extend(workflow_info.get('actions_used', []))
            all_environments.extend(workflow_info.get('environments', []))
            all_secrets.extend(workflow_info.get('secrets_used', []))
        
        # Count occurrences
        from collections import Counter
        
        summary['workflow_triggers'] = dict(Counter(all_triggers))
        summary['common_actions'] = dict(Counter(all_actions))
        summary['environments_used'] = list(set(all_environments))
        summary['secrets_required'] = list(set(all_secrets))
        
        # Potential issues
        if not self.workflows:
            summary['potential_issues'].append("No GitHub Actions workflows found")
        
        if 'push' not in all_triggers and 'pull_request' not in all_triggers:
            summary['potential_issues'].append("No CI/CD triggers found (push/pull_request)")
        
        if not all_environments:
            summary['potential_issues'].append("No deployment environments configured")
        
        # Recommendations
        if len(self.workflows) > 5:
            summary['recommendations'].append("Consider consolidating workflows for better maintainability")
        
        if not any('test' in action.lower() for action in all_actions):
            summary['recommendations'].append("Add automated testing workflows")
        
        if not any('deploy' in action.lower() for action in all_actions):
            summary['recommendations'].append("Add deployment automation workflows")
        
        return summary
    
    def save_report(self, filename='github_integration_analysis.json'):
        """Save GitHub analysis report"""
        report = self.generate_github_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"🐙 GitHub report saved to {filename}")
        return report

def main():
    """Main execution function"""
    print("🐙 Legacy Loop GitHub Integration Analyzer")
    print("=" * 60)
    
    root_path = Path(__file__).parent
    analyzer = GitHubWorkflowAnalyzer(root_path)
    
    report = analyzer.analyze_github_integration()
    analyzer.save_report()
    
    # Print summary
    print("\n🐙 GITHUB INTEGRATION SUMMARY")
    print("=" * 60)
    print(f"Workflows: {report['total_workflows']}")
    print(f"Config Files: {report['total_config_files']}")
    
    if report['integration_summary']['workflow_triggers']:
        print(f"\n🎯 Workflow Triggers:")
        for trigger, count in report['integration_summary']['workflow_triggers'].items():
            print(f"  • {trigger}: {count} workflows")
    
    if report['integration_summary']['environments_used']:
        print(f"\n🌍 Environments:")
        for env in report['integration_summary']['environments_used']:
            print(f"  • {env}")
    
    if report['integration_summary']['potential_issues']:
        print(f"\n⚠️  Potential Issues:")
        for issue in report['integration_summary']['potential_issues']:
            print(f"  • {issue}")
    
    if report['integration_summary']['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in report['integration_summary']['recommendations']:
            print(f"  • {rec}")
    
    print(f"\n✅ GitHub analysis complete! Check github_integration_analysis.json for details")

if __name__ == "__main__":
    main()
