#!/usr/bin/env python3
"""
Legacy Loop Module Analyzer
Automatically scans and categorizes 100+ modules for organization
"""

import os
import ast
import json
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

class LegacyLoopAnalyzer:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.modules = {}
        self.dependencies = defaultdict(list)
        self.categories = {
            'nexus_protocol': ['nexus', 'protocol', 'bridge', 'connection'],
            'legacy_loop': ['legacy', 'loop', 'sovereign', 'legacy_loop', 'sovlegacyloop', 'shadow ai 2', 'shadow ai ii'],
            'sovereign_shadow_ai': ['sovereignshadow.ai', 'legacy loop', 'sovereign shadow ai', 'master system'],
            'omega_engines': ['omega', 'ω', 'omega engines', 'engine'],
            'shepard_system': ['shepard', 'shepherd', 'shepard system'],
            'sigma_x': ['sigma', 'σ', 'sigma-x', 'sigmax', 'sigma x'],
            'crown_jewels': ['toshi', 'ledgerghost90', 'sovßankingsystems', 'sovereign banking systems'],
            'keyblade_system': ['keyblade', 'sigil', 'omega', 'ω', 'toshi', 'manus', 'mennace', 'journey'],
            'flipbot_system': ['flipbot', 'flipbotphil', 'flip', 'bot'],
            'rays_rules': ['rays', 'rules', 'ray', 'rule'],
            'mcp_servers': ['mcp', 'server', 'protocol', 'anthropic', 'claude', 'sdk'],
            'automation_engine': ['automation', 'automate', 'auto', 'bot', 'scheduler'],
            'core_engine': ['arbitrage', 'trading', 'engine', 'strategy', 'algorithm'],
            'data_ingestion': ['data', 'feed', 'api', 'scraper', 'collector', 'market'],
            'exchange_connectors': ['binance', 'coinbase', 'kraken', 'exchange', 'connector', 'cex'],
            'risk_management': ['risk', 'position', 'stop', 'limit', 'safety', 'hedge'],
            'analytics': ['analytics', 'report', 'performance', 'metrics', 'chart', 'stats'],
            'utilities': ['util', 'helper', 'format', 'common', 'tool', 'base'],
            'config': ['config', 'settings', 'env', 'credentials', 'auth'],
            'crypto_empire': ['empire', 'automation', 'sovereign'],
            'shadow_ai': ['shadow', 'ai', 'claude', 'agent', 'brain'],
            'vault_system': ['vault', 'siphon', 'graduation', 'ondes'],
            'rwa_assets': ['rwa', 'ondo', 'treasury', 'bond', 'real_world'],
            'chatgpt_integration': ['chatgpt', 'gpt', 'openai', 'chat'],
            'claude_integration': ['claude', 'anthropic', 'sonnet'],
            'docker_infrastructure': ['docker', 'compose', 'container', 'orchestration', 'deployment'],
            'platform_bridges': ['bridge', 'notion', 'workspace', 'replit', 'github', 'platform', 'integration'],
            'notion_integration': ['notion', 'workspace', 'database', 'page', 'block', 'api'],
            'replit_repositories': ['replit', 'repl', 'repository', 'workspace', 'aarch'],
            'github_integration': ['github', 'git', 'repository', 'workflow', 'action', 'commit', 'push', 'pull', 'branch'],
            'whale_scanner': ['whale', 'whalejackpotscanner', 'whale scanner', 'big player', 'institutional', 'large trade'],
            'rebalancing_engine': ['rebalancing', 'rebal', 'rebalance', 'portfolio rebalancing', 'auto rebalance'],
            'wallet_scanner': ['wallet', 'scanner', 'watcher', 'monitor', 'tracker', 'address scanner', 'wallet tracker'],
            'data_agents': ['data agent', 'data collector', 'data processor', 'market data', 'data feed', 'data pipeline'],
            'reinforcement_learning': ['reinforcement learning', 'rl', 'deep agent', 'neural network', 'backpropagation', 'q-learning', 'policy gradient', 'reward function', 'shadow brain', 'recursive neural', 'neural brain', 'learning rate', 'weight optimization', 'memory management', 'snapshot', 'rollback'],
            'shadow_ai_systems': ['shadow ai', 'deep agent core', 'shadow brain', 'multi-ai orchestration', 'claude sdk', 'gpt-5 pro', 'manus ai', 'abacus ai', 'neural network', 'recursive processing', 'safety guards', 'circuit breakers'],
            'btc_breakout_mission': ['btc breakout', 'oco ladder', 'profit siphon', 'graduation threshold', 'dry powder', 'stop loss', 'breakout mission', 'trading mission'],
            'legacy_rl_systems': ['r2', 'r2 system', 'older rl', 'legacy rl', 'previous rl', 'old reinforcement', 'r2 reinforcement', 'r2 learning']
        }
        
    def scan_modules(self):
        """Scan all Python files and JSON configs"""
        print(f"🔍 Scanning modules in {self.root_path}")
        
        # Scan Python files
        for py_file in self.root_path.rglob("*.py"):
            if self._should_analyze_file(py_file):
                self.analyze_python_file(py_file)
        
        # Scan JSON files
        for json_file in self.root_path.rglob("*.json"):
            if self._should_analyze_file(json_file):
                self.analyze_json_file(json_file)
        
        # Scan YAML files (Docker, configs)
        for yaml_file in self.root_path.rglob("*.yaml"):
            if self._should_analyze_file(yaml_file):
                self.analyze_yaml_file(yaml_file)
        
        for yml_file in self.root_path.rglob("*.yml"):
            if self._should_analyze_file(yml_file):
                self.analyze_yaml_file(yml_file)
        
        # Scan other config files
        for config_file in self.root_path.rglob("*.toml"):
            if self._should_analyze_file(config_file):
                self.analyze_config_file(config_file)
        
        for env_file in self.root_path.rglob(".env*"):
            if self._should_analyze_file(env_file):
                self.analyze_env_file(env_file)
        
        # Scan GitHub workflow files
        for workflow_file in self.root_path.rglob(".github/workflows/*.yml"):
            if self._should_analyze_file(workflow_file):
                self.analyze_yaml_file(workflow_file)
        
        for workflow_file in self.root_path.rglob(".github/workflows/*.yaml"):
            if self._should_analyze_file(workflow_file):
                self.analyze_yaml_file(workflow_file)
        
        print(f"✅ Scanned {len(self.modules)} modules")
    
    def _should_analyze_file(self, file_path):
        """Skip certain directories and files"""
        skip_dirs = {'node_modules', '.git', '__pycache__', '.venv', 'venv', '.next'}
        skip_files = {'package-lock.json', 'yarn.lock', 'node_modules', '.gitignore', '.DS_Store'}
        
        # Skip if in excluded directory
        for part in file_path.parts:
            if part in skip_dirs:
                return False
        
        # Skip specific files
        if file_path.name in skip_files:
            return False
            
        return True
    
    def analyze_python_file(self, file_path):
        """Analyze individual Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError:
                tree = None
            
            # Extract file info
            module_info = {
                'path': str(file_path.relative_to(self.root_path)),
                'full_path': str(file_path),
                'size': len(content),
                'lines': len(content.splitlines()),
                'type': 'python',
                'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                'category': self.categorize_module(file_path.name, content),
                'complexity_score': 0,
                'functions': [],
                'classes': [],
                'imports': [],
                'docstring': self.extract_docstring(content)
            }
            
            if tree:
                module_info.update({
                    'functions': self.extract_functions(tree),
                    'classes': self.extract_classes(tree),
                    'imports': self.extract_imports(tree),
                    'complexity_score': self.calculate_complexity(tree)
                })
            
            # Check for specific patterns
            module_info.update(self.detect_patterns(content))
            
            self.modules[file_path.stem] = module_info
            
        except Exception as e:
            print(f"❌ Error analyzing {file_path}: {e}")
    
    def analyze_json_file(self, file_path):
        """Analyze JSON configuration files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to parse JSON
            try:
                json_data = json.loads(content)
            except json.JSONDecodeError:
                json_data = None
            
            module_info = {
                'path': str(file_path.relative_to(self.root_path)),
                'full_path': str(file_path),
                'size': len(content),
                'lines': len(content.splitlines()),
                'type': 'json',
                'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                'category': self.categorize_module(file_path.name, content),
                'complexity_score': 0,
                'functions': [],
                'classes': [],
                'imports': [],
                'json_keys': list(json_data.keys()) if json_data else [],
                'is_config': 'config' in file_path.name.lower() or 'settings' in file_path.name.lower()
            }
            
            self.modules[file_path.stem] = module_info
            
        except Exception as e:
            print(f"❌ Error analyzing JSON {file_path}: {e}")
    
    def analyze_yaml_file(self, file_path):
        """Analyze YAML configuration files (Docker, etc.)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            module_info = {
                'path': str(file_path.relative_to(self.root_path)),
                'full_path': str(file_path),
                'size': len(content),
                'lines': len(content.splitlines()),
                'type': 'yaml',
                'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                'category': self.categorize_module(file_path.name, content),
                'complexity_score': 0,
                'functions': [],
                'classes': [],
                'imports': [],
                'is_docker_compose': 'docker-compose' in file_path.name.lower() or 'compose' in content.lower(),
                'is_dockerfile': file_path.name.lower() == 'dockerfile',
                'is_deployment_config': any(deploy in content.lower() for deploy in ['deploy', 'production', 'staging']),
                'has_services': 'services:' in content.lower(),
                'has_networks': 'networks:' in content.lower(),
                'has_volumes': 'volumes:' in content.lower()
            }
            
            # Extract service names from docker-compose
            if module_info['is_docker_compose']:
                import re
                services = re.findall(r'^\s*(\w+):\s*$', content, re.MULTILINE)
                module_info['docker_services'] = services
            
            # Check for specific patterns
            module_info.update(self.detect_patterns(content))
            
            self.modules[file_path.stem] = module_info
            
        except Exception as e:
            print(f"❌ Error analyzing YAML {file_path}: {e}")
    
    def analyze_config_file(self, file_path):
        """Analyze TOML and other config files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            module_info = {
                'path': str(file_path.relative_to(self.root_path)),
                'full_path': str(file_path),
                'size': len(content),
                'lines': len(content.splitlines()),
                'type': 'config',
                'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                'category': self.categorize_module(file_path.name, content),
                'complexity_score': 0,
                'functions': [],
                'classes': [],
                'imports': [],
                'is_toml': file_path.suffix == '.toml',
                'has_platform_config': any(platform in content.lower() for platform in ['platform', 'bridge', 'integration']),
                'has_workspace_config': 'workspace' in content.lower()
            }
            
            # Check for specific patterns
            module_info.update(self.detect_patterns(content))
            
            self.modules[file_path.stem] = module_info
            
        except Exception as e:
            print(f"❌ Error analyzing config {file_path}: {e}")
    
    def analyze_env_file(self, file_path):
        """Analyze environment files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract environment variables
            env_vars = []
            for line in content.splitlines():
                if '=' in line and not line.strip().startswith('#'):
                    key = line.split('=')[0].strip()
                    env_vars.append(key)
            
            module_info = {
                'path': str(file_path.relative_to(self.root_path)),
                'full_path': str(file_path),
                'size': len(content),
                'lines': len(content.splitlines()),
                'type': 'env',
                'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                'category': self.categorize_module(file_path.name, content),
                'complexity_score': 0,
                'functions': [],
                'classes': [],
                'imports': [],
                'environment_variables': env_vars,
                'has_api_keys': any(key in content.lower() for key in ['api_key', 'secret', 'token', 'password']),
                'has_platform_keys': any(platform in content.lower() for platform in ['notion', 'replit', 'github', 'docker']),
            'has_github_keys': any(git_key in content.lower() for git_key in ['github_token', 'git_token', 'repo_token', 'gh_token'])
            }
            
            # Check for specific patterns
            module_info.update(self.detect_patterns(content))
            
            self.modules[file_path.stem] = module_info
            
        except Exception as e:
            print(f"❌ Error analyzing env {file_path}: {e}")
    
    def extract_functions(self, tree):
        """Extract function definitions"""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'args': len(node.args.args),
                    'line': node.lineno,
                    'is_async': isinstance(node, ast.AsyncFunctionDef),
                    'docstring': ast.get_docstring(node)
                })
        return functions
    
    def extract_classes(self, tree):
        """Extract class definitions"""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                classes.append({
                    'name': node.name,
                    'methods': len(methods),
                    'method_names': methods,
                    'line': node.lineno,
                    'docstring': ast.get_docstring(node)
                })
        return classes
    
    def extract_imports(self, tree):
        """Extract import statements"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return list(set(imports))  # Remove duplicates
    
    def categorize_module(self, filename, content):
        """Auto-categorize module based on name and content"""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        scores = defaultdict(int)
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in filename_lower:
                    scores[category] += 3  # Higher weight for filename matches
                if keyword in content_lower:
                    scores[category] += 1
        
        return max(scores, key=scores.get) if scores else 'experimental'
    
    def calculate_complexity(self, tree):
        """Calculate module complexity score"""
        complexity = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                complexity += 1
            elif isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(node, ast.Call):
                complexity += 0.5
        return complexity
    
    def detect_patterns(self, content):
        """Detect specific patterns in code"""
        content_lower = content.lower()
        patterns = {
            'has_binance_api': 'binance' in content_lower and ('api' in content_lower or 'client' in content_lower),
            'has_async_functions': 'async def' in content,
            'has_database_queries': any(db in content_lower for db in ['sql', 'query', 'select', 'insert', 'update']),
            'has_websockets': 'websocket' in content_lower or 'ws' in content_lower,
            'has_mcp_server': 'mcp' in content_lower and 'server' in content_lower,
            'has_ai_integration': any(ai in content_lower for ai in ['claude', 'openai', 'anthropic', 'ai']),
            'has_encryption': any(crypto in content_lower for crypto in ['encrypt', 'decrypt', 'hash', 'crypto']),
            'has_trading_logic': any(trade in content_lower for trade in ['buy', 'sell', 'trade', 'order', 'position']),
            'has_risk_management': any(risk in content_lower for risk in ['risk', 'stop', 'limit', 'hedge', 'position']),
            'has_nexus_protocol': any(nexus in content_lower for nexus in ['nexus', 'protocol', 'bridge']),
            'has_keyblade_system': any(key in content_lower for key in ['keyblade', 'sigil', 'omega', 'ω', 'toshi', 'manus', 'journey']),
            'has_flipbot_system': any(flip in content_lower for flip in ['flipbot', 'flipbotphil', 'flip']),
            'has_legacy_loop': 'legacy' in content_lower and 'loop' in content_lower,
            'has_rays_rules': 'rays' in content_lower and 'rules' in content_lower,
            'has_automation': 'automation' in content_lower or 'automate' in content_lower,
            'has_chatgpt': any(gpt in content_lower for gpt in ['chatgpt', 'gpt', 'openai']),
            'has_claude_sdk': any(claude in content_lower for claude in ['claude', 'anthropic', 'sonnet']),
            'has_docker_infrastructure': any(docker in content_lower for docker in ['docker', 'compose', 'container', 'orchestration']),
            'has_deployment_config': any(deploy in content_lower for deploy in ['deploy', 'production', 'staging', 'environment']),
            'has_platform_bridge': any(bridge in content_lower for bridge in ['bridge', 'platform', 'integration', 'connector']),
            'has_notion_integration': any(notion in content_lower for notion in ['notion', 'workspace', 'database', 'page', 'block']),
            'has_replit_repo': any(replit in content_lower for replit in ['replit', 'repl', 'repository', 'aarch']),
            'has_cross_platform': any(cross in content_lower for cross in ['cross-platform', 'multi-platform', 'universal', 'bridge']),
            'has_github_integration': any(git in content_lower for git in ['github', 'git', 'repository', 'workflow', 'action', 'commit']),
            'has_version_control': any(vc in content_lower for vc in ['version', 'control', 'git', 'commit', 'branch', 'merge']),
            'has_sovereign_shadow_ai': any(sovereign in content_lower for sovereign in ['sovereignshadow.ai', 'legacy loop', 'sovereign shadow ai', 'master system']),
            'has_omega_engines': any(omega in content_lower for omega in ['omega', 'ω', 'omega engines', 'engine']),
            'has_shepard_system': any(shepard in content_lower for shepard in ['shepard', 'shepherd', 'shepard system']),
            'has_sigma_x': any(sigma in content_lower for sigma in ['sigma', 'σ', 'sigma-x', 'sigmax', 'sigma x']),
            'has_crown_jewels': any(jewel in content_lower for jewel in ['toshi', 'ledgerghost90', 'sovßankingsystems', 'sovereign banking systems']),
            'has_shadow_ai_2': any(shadow in content_lower for shadow in ['shadow ai 2', 'shadow ai ii', 'sovlegacyloop']),
            'is_prized_component': any(prized in content_lower for prized in ['toshi', 'ledgerghost90', 'shadow ai 2', 'sovlegacyloop', 'crown jewel', 'omega engines', 'shepard system', 'sigma x']),
            'has_whale_scanner': any(whale in content_lower for whale in ['whale', 'whalejackpotscanner', 'whale scanner', 'big player', 'institutional']),
            'has_rebalancing': any(rebal in content_lower for rebal in ['rebalancing', 'rebal', 'rebalance', 'portfolio rebalancing']),
            'has_wallet_scanner': any(wallet in content_lower for wallet in ['wallet scanner', 'wallet watcher', 'wallet monitor', 'address scanner', 'wallet tracker']),
            'has_data_agents': any(data in content_lower for data in ['data agent', 'data collector', 'data processor', 'data pipeline', 'market data']),
            'has_reinforcement_learning': any(rl in content_lower for rl in ['reinforcement learning', 'rl', 'deep agent', 'neural network', 'backpropagation', 'q-learning', 'policy gradient', 'reward function']),
            'has_shadow_ai_systems': any(shadow in content_lower for shadow in ['shadow ai', 'deep agent core', 'shadow brain', 'multi-ai orchestration', 'claude sdk', 'gpt-5 pro', 'manus ai', 'abacus ai']),
            'has_btc_breakout_mission': any(btc in content_lower for btc in ['btc breakout', 'oco ladder', 'profit siphon', 'graduation threshold', 'dry powder', 'stop loss']),
            'has_legacy_rl_systems': any(r2 in content_lower for r2 in ['r2', 'r2 system', 'older rl', 'legacy rl', 'previous rl', 'old reinforcement', 'r2 reinforcement']),
            'has_neural_networks': any(nn in content_lower for nn in ['neural network', 'recursive neural', 'neural brain', 'neuron', 'synapse', 'activation function', 'forward propagation', 'backpropagation']),
            'has_machine_learning': any(ml in content_lower for ml in ['machine learning', 'deep learning', 'supervised learning', 'unsupervised learning', 'reinforcement learning', 'model training', 'feature engineering']),
            'has_ai_orchestration': any(ai in content_lower for ai in ['multi-ai', 'ai orchestration', 'claude sdk', 'gpt-5 pro', 'manus ai', 'abacus ai', 'ai consensus', 'ai decision'])
        }
        return patterns
    
    def extract_docstring(self, content):
        """Extract module docstring"""
        lines = content.splitlines()
        if lines and lines[0].strip().startswith('"""'):
            docstring_lines = []
            for line in lines[1:]:
                if line.strip().endswith('"""'):
                    break
                docstring_lines.append(line.strip())
            return ' '.join(docstring_lines)
        return None
    
    def build_dependency_graph(self):
        """Build module dependency relationships"""
        graph = defaultdict(list)
        
        for name, info in self.modules.items():
            if info['type'] == 'python':
                for imp in info['imports']:
                    # Check if import matches any of our modules
                    for module_name in self.modules.keys():
                        if (module_name in imp or 
                            imp.split('.')[0] == module_name or 
                            any(keyword in imp for keyword in module_name.split('_'))):
                            if module_name != name:  # Don't self-reference
                                graph[name].append(module_name)
        
        return dict(graph)
    
    def generate_recommendations(self):
        """Generate optimization recommendations"""
        recommendations = []
        
        # Find orphaned modules
        all_references = set()
        dependency_graph = self.build_dependency_graph()
        
        for deps in dependency_graph.values():
            all_references.update(deps)
        
        orphaned = [name for name in self.modules.keys() if name not in all_references and len(self.modules[name].get('functions', [])) == 0]
        
        for module in orphaned[:5]:  # Top 5 orphaned
            recommendations.append(f"Module '{module}' appears unused - consider archiving")
        
        # Find overly complex modules
        complex_modules = [(name, info) for name, info in self.modules.items() 
                          if info['complexity_score'] > 50]
        complex_modules.sort(key=lambda x: x[1]['complexity_score'], reverse=True)
        
        for name, info in complex_modules[:3]:
            recommendations.append(f"Module '{name}' is highly complex ({info['complexity_score']} score) - consider refactoring")
        
        # Find high-value modules
        high_value = [(name, info) for name, info in self.modules.items() 
                     if info['complexity_score'] > 20 and len(info.get('functions', [])) > 5]
        high_value.sort(key=lambda x: x[1]['complexity_score'], reverse=True)
        
        recommendations.append(f"High-value modules identified: {[name for name, _ in high_value[:5]]}")
        
        return recommendations
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        dependency_graph = self.build_dependency_graph()
        recommendations = self.generate_recommendations()
        
        # Category breakdown
        category_stats = defaultdict(lambda: {'count': 0, 'total_complexity': 0, 'total_functions': 0})
        
        for name, info in self.modules.items():
            category = info['category']
            category_stats[category]['count'] += 1
            category_stats[category]['total_complexity'] += info['complexity_score']
            category_stats[category]['total_functions'] += len(info.get('functions', []))
        
        # Calculate averages
        for category in category_stats:
            count = category_stats[category]['count']
            if count > 0:
                category_stats[category]['avg_complexity'] = category_stats[category]['total_complexity'] / count
                category_stats[category]['avg_functions'] = category_stats[category]['total_functions'] / count
        
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'total_modules': len(self.modules),
            'total_lines': sum(info['lines'] for info in self.modules.values()),
            'category_breakdown': dict(category_stats),
            'complexity_ranking': sorted(
                [(name, info['complexity_score']) for name, info in self.modules.items()], 
                key=lambda x: x[1], 
                reverse=True
            )[:20],
            'dependency_graph': dependency_graph,
            'recommendations': recommendations,
            'module_details': self.modules
        }
        
        return report
    
    def save_report(self, filename='legacy_loop_analysis.json'):
        """Save analysis report to file"""
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📊 Report saved to {filename}")
        return report

def main():
    """Main execution function"""
    print("🚀 Legacy Loop Module Analyzer")
    print("=" * 50)
    
    # Initialize analyzer
    root_path = Path(__file__).parent
    analyzer = LegacyLoopAnalyzer(root_path)
    
    # Run analysis
    analyzer.scan_modules()
    report = analyzer.save_report()
    
    # Print summary
    print("\n📈 ANALYSIS SUMMARY")
    print("=" * 50)
    print(f"Total Modules: {report['total_modules']}")
    print(f"Total Lines: {report['total_lines']:,}")
    
    print("\n📁 CATEGORY BREAKDOWN")
    for category, stats in report['category_breakdown'].items():
        print(f"  {category}: {stats['count']} modules ({stats['avg_complexity']:.1f} avg complexity)")
    
    print("\n🏆 TOP COMPLEX MODULES")
    for i, (name, complexity) in enumerate(report['complexity_ranking'][:5], 1):
        print(f"  {i}. {name}: {complexity} complexity")
    
    print("\n💡 RECOMMENDATIONS")
    for rec in report['recommendations'][:3]:
        print(f"  • {rec}")
    
    print(f"\n✅ Analysis complete! Check legacy_loop_analysis.json for full details")

if __name__ == "__main__":
    main()
