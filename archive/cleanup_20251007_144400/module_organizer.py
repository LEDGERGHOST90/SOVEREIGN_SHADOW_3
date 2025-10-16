#!/usr/bin/env python3
"""
Legacy Loop Module Organizer
Automatically organizes modules into structured directories based on analysis
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

class ModuleOrganizer:
    def __init__(self, analysis_file='legacy_loop_analysis.json'):
        """Initialize organizer with analysis results"""
        if not Path(analysis_file).exists():
            raise FileNotFoundError(f"Analysis file {analysis_file} not found. Run module_analyzer.py first.")
        
        with open(analysis_file, 'r') as f:
            self.analysis = json.load(f)
        
        self.target_structure = {
            'sovereign_shadow_ai': {
                'description': 'SovereignShadow.Ai[LegacyLoop] - Master system encompassing all components',
                'priority': 0
            },
            'omega_engines': {
                'description': 'Ω Engines - Core processing and automation engines',
                'priority': 1
            },
            'shepard_system': {
                'description': 'Shepard System - Navigation and guidance system',
                'priority': 2
            },
            'sigma_x': {
                'description': 'ΣIGMA-X - Signal detection and analysis system',
                'priority': 3
            },
            'crown_jewels': {
                'description': 'Crown Jewels - toshi, ledgerghost90, SovßankingSystems (MOST PRIZED)',
                'priority': 4
            },
            'legacy_loop': {
                'description': 'SOVlegacyloop: Shadow AI 2 - Core sovereign system (NOT Kevin O\'Leary\'s sovereignty)',
                'priority': 5
            },
            'nexus_protocol': {
                'description': 'Nexus Protocol - Bridge and connection systems',
                'priority': 6
            },
            'keyblade_system': {
                'description': 'KeyBlade System - Ω Sigil, Toshi, Manus, Mennace, Ω Journey',
                'priority': 7
            },
            'flipbot_system': {
                'description': 'FlipBot System - flipbot, flipbotphil automated trading',
                'priority': 8
            },
            'rays_rules': {
                'description': 'Rays Rules - Proprietary trading rules',
                'priority': 9
            },
            'mcp_servers': {
                'description': 'MCP Servers - Claude SDK, Anthropic integration',
                'priority': 10
            },
            'automation_engine': {
                'description': 'Automation Engine - Bot and scheduler systems',
                'priority': 11
            },
            'core_engine': {
                'description': 'Core Engine - Trading algorithms and strategies',
                'priority': 12
            },
            'data_ingestion': {
                'description': 'Data Ingestion - Market data and API feeds',
                'priority': 13
            },
            'exchange_connectors': {
                'description': 'Exchange Connectors - Binance, Coinbase, Kraken',
                'priority': 14
            },
            'risk_management': {
                'description': 'Risk Management - Position sizing and safety',
                'priority': 15
            },
            'analytics': {
                'description': 'Analytics - Performance tracking and reporting',
                'priority': 16
            },
            'shadow_ai': {
                'description': 'Shadow AI - AI agents and brain systems',
                'priority': 17
            },
            'vault_system': {
                'description': 'Vault System - Siphon and graduation logic',
                'priority': 18
            },
            'rwa_assets': {
                'description': 'RWA Assets - Real world asset integration',
                'priority': 19
            },
            'utilities': {
                'description': 'Utilities - Helper functions and common tools',
                'priority': 20
            },
            'config': {
                'description': 'Configuration - Settings and credentials',
                'priority': 21
            },
            'docker_infrastructure': {
                'description': 'Docker Infrastructure - Containers, compose, orchestration',
                'priority': 22
            },
            'platform_bridges': {
                'description': 'Platform Bridges - Cross-platform integrations and connectors',
                'priority': 23
            },
            'notion_integration': {
                'description': 'Notion Integration - Workspaces, databases, pages, blocks',
                'priority': 24
            },
            'replit_repositories': {
                'description': 'Replit Repositories - Personal aarch, workspaces, repls',
                'priority': 25
            },
            'github_integration': {
                'description': 'GitHub Integration - Repositories, workflows, actions, version control',
                'priority': 26
            },
            'whale_scanner': {
                'description': 'Whale Scanner - whalejackpotscanner, large trade detection, institutional monitoring',
                'priority': 27
            },
            'rebalancing_engine': {
                'description': 'Rebalancing Engine - Portfolio rebalancing, automated allocation management',
                'priority': 28
            },
            'wallet_scanner': {
                'description': 'Wallet Scanner - Address monitoring, wallet watchers, transaction tracking',
                'priority': 29
            },
            'data_agents': {
                'description': 'Data Agents - Market data collection, processing, and pipeline management',
                'priority': 30
            },
            'experimental': {
                'description': 'Experimental - Prototype and test modules',
                'priority': 99
            }
        }
        
    def create_directory_structure(self):
        """Create organized directory structure"""
        base_path = Path('./legacy_loop_organized')
        base_path.mkdir(exist_ok=True)
        
        print(f"📁 Creating directory structure in {base_path}")
        
        # Create directories for each category
        for category, info in self.target_structure.items():
            category_path = base_path / category
            category_path.mkdir(exist_ok=True)
            
            # Create README for each category
            readme_content = f"""# {category.replace('_', ' ').title()}

{info['description']}

**Priority Level**: {info['priority']}

## Modules in this category:
<!-- Auto-generated by Legacy Loop Module Organizer -->

## Integration Notes:
<!-- Add integration instructions here -->
"""
            readme_file = category_path / 'README.md'
            readme_file.write_text(readme_content)
            
            # Create __init__.py for Python imports
            init_file = category_path / '__init__.py'
            init_file.write_text(f'"""Legacy Loop {category.replace("_", " ").title()} Module"""\n\n# Auto-generated by Legacy Loop Module Organizer\n')
        
        # Create master README
        master_readme = self._generate_master_readme()
        (base_path / 'README.md').write_text(master_readme)
        
        print(f"✅ Directory structure created with {len(self.target_structure)} categories")
    
    def _generate_master_readme(self):
        """Generate master README for organized structure"""
        total_modules = self.analysis['total_modules']
        total_lines = self.analysis['total_lines']
        
        readme = f"""# 🚀 Legacy Loop - Organized Module Architecture

**Total Modules**: {total_modules}  
**Total Lines**: {total_lines:,}  
**Organization Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Module Distribution

"""
        
        # Add category breakdown
        for category, info in sorted(self.target_structure.items(), key=lambda x: x[1]['priority']):
            module_count = len(self.analysis['category_breakdown'].get(category, {}).get('modules', []))
            readme += f"### {category.replace('_', ' ').title()} ({module_count} modules)\n"
            readme += f"{info['description']}\n\n"
        
        readme += """## 🏗️ Architecture Overview

This organized structure follows Raymond's proprietary terminology and system design:

- **SovereignShadow.Ai[LegacyLoop]**: Master system encompassing all components
- **Ω Engines**: Core processing and automation engines
- **Shepard System**: Navigation and guidance system
- **ΣIGMA-X**: Signal detection and analysis system
- **Crown Jewels**: toshi, ledgerghost90, SovßankingSystems (MOST PRIZED)
- **SOVlegacyloop**: Shadow AI 2 - Core sovereign system (NOT Kevin O'Leary's sovereignty)
- **Nexus Protocol**: Bridge and connection systems  
- **KeyBlade System**: Ω Sigil, Toshi, Manus, Mennace, Ω Journey components
- **FlipBot System**: flipbot, flipbotphil automated trading systems
- **Rays Rules**: Proprietary trading rules and logic
- **MCP Servers**: Claude SDK and Anthropic integrations
- **Automation Engine**: Bot and scheduler systems
- **Docker Infrastructure**: Container orchestration and deployment
- **Platform Bridges**: Cross-platform integrations and connectors
- **Notion Integration**: Workspaces, databases, and page management
- **Replit Repositories**: Personal aarch and workspace management
- **GitHub Integration**: Repositories, workflows, actions, and version control

## 🔧 Integration Priority

Modules are organized by integration priority (1 = highest priority):

0. SovereignShadow.Ai[LegacyLoop] - Master system encompassing all components
1. Ω Engines - Core processing and automation engines
2. Shepard System - Navigation and guidance system  
3. ΣIGMA-X - Signal detection and analysis system
4. Crown Jewels - toshi, ledgerghost90, SovßankingSystems (MOST PRIZED)
5. SOVlegacyloop: Shadow AI 2 - Core sovereign system (NOT Kevin O'Leary's)
6. Nexus Protocol - Foundation systems
7. KeyBlade System - Ω Sigil, Toshi, Manus, Mennace, Ω Journey
8. FlipBot System - flipbot, flipbotphil automated trading
9. Rays Rules - Trading logic
10. MCP Servers - AI integration
11. Automation Engine - Automated systems
12. Core Engine - Trading algorithms
13. Data Ingestion - Market data
14. Exchange Connectors - API integrations
15. Risk Management - Safety systems
16. Analytics - Performance tracking
17. Shadow AI - AI agents
18. Vault System - Wealth management
19. RWA Assets - Real world assets
20. Utilities - Helper functions
21. Configuration - Settings
22. Docker Infrastructure - Containers and orchestration
23. Platform Bridges - Cross-platform integrations
24. Notion Integration - Workspaces and databases
25. Replit Repositories - Personal aarch and workspaces
26. GitHub Integration - Repositories, workflows, and version control
27. Whale Scanner - whalejackpotscanner, large trade detection
28. Rebalancing Engine - Portfolio rebalancing, automated allocation
29. Wallet Scanner - Address monitoring, wallet watchers
30. Data Agents - Market data collection, processing pipelines
99. Experimental - Prototypes

## 🚀 Next Steps

1. Review module assignments
2. Update import statements
3. Test integration points
4. Deploy MCP servers
5. Build master orchestrator

---
*Auto-generated by Legacy Loop Module Organizer*
"""
        return readme
    
    def move_modules(self, dry_run=True):
        """Move modules to organized structure"""
        moves = []
        conflicts = []
        
        print(f"📦 {'Analyzing' if dry_run else 'Moving'} modules...")
        
        for category, modules in self.analysis['category_breakdown'].items():
            if not modules.get('modules'):
                continue
                
            target_dir = Path('./legacy_loop_organized') / category
            
            for module_name in modules['modules']:
                # Find the actual file in module details
                module_info = None
                for name, info in self.analysis.get('module_details', {}).items():
                    if name == module_name:
                        module_info = info
                        break
                
                if module_info:
                    source_path = Path(module_info['full_path'])
                    target_path = target_dir / source_path.name
                    
                    move_info = {
                        'source': str(source_path),
                        'target': str(target_path),
                        'category': category,
                        'module': module_name,
                        'size': module_info.get('size', 0),
                        'type': module_info.get('type', 'unknown')
                    }
                    
                    # Check for conflicts
                    if target_path.exists() and source_path != target_path:
                        conflicts.append({
                            'module': module_name,
                            'existing': str(target_path),
                            'source': str(source_path)
                        })
                    
                    moves.append(move_info)
                    
                    if not dry_run and source_path.exists():
                        try:
                            shutil.copy2(source_path, target_path)
                            print(f"  ✅ Moved {module_name} to {category}/")
                        except Exception as e:
                            print(f"  ❌ Failed to move {module_name}: {e}")
        
        if dry_run:
            print(f"📊 Would move {len(moves)} modules")
            if conflicts:
                print(f"⚠️  Found {len(conflicts)} potential conflicts:")
                for conflict in conflicts[:5]:  # Show first 5 conflicts
                    print(f"    {conflict['module']}: {conflict['existing']}")
        else:
            print(f"✅ Moved {len(moves)} modules successfully")
        
        return moves, conflicts
    
    def generate_integration_config(self):
        """Generate module integration configuration"""
        config = {
            'organization_timestamp': datetime.now().isoformat(),
            'total_modules': self.analysis['total_modules'],
            'module_registry': {},
            'load_order': [],
            'dependencies': self.analysis.get('dependency_graph', {}),
            'categories': {cat: info['description'] for cat, info in self.target_structure.items()},
            'integration_priority': {}
        }
        
        # Build integration priority based on category priority
        for category, info in sorted(self.target_structure.items(), key=lambda x: x[1]['priority']):
            config['integration_priority'][category] = info['priority']
            
            # Add modules to load order
            if category in self.analysis['category_breakdown']:
                modules = self.analysis['category_breakdown'][category].get('modules', [])
                config['load_order'].extend(modules)
        
        # Module registry with enhanced info
        for name, info in self.analysis.get('module_details', {}).items():
            config['module_registry'][name] = {
                'category': info.get('category', 'experimental'),
                'complexity': info.get('complexity_score', 0),
                'functions': len(info.get('functions', [])),
                'classes': len(info.get('classes', [])),
                'dependencies': info.get('imports', []),
                'patterns': info.get('patterns', {}),
                'priority': self.target_structure.get(info.get('category', 'experimental'), {}).get('priority', 99),
                'size': info.get('size', 0),
                'type': info.get('type', 'unknown')
            }
        
        # Save config
        with open('legacy_loop_integration_config.json', 'w') as f:
            json.dump(config, f, indent=2, default=str)
        
        print("⚙️  Integration config generated: legacy_loop_integration_config.json")
        return config
    
    def generate_migration_script(self):
        """Generate Python script to update imports after organization"""
        script_content = '''#!/usr/bin/env python3
"""
Legacy Loop Import Migration Script
Updates import statements after module reorganization
"""

import os
import re
from pathlib import Path

def update_imports_in_file(file_path, import_mapping):
    """Update imports in a single file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Update imports
        for old_import, new_import in import_mapping.items():
            # Pattern to match various import styles
            patterns = [
                f"from {old_import} import",
                f"import {old_import}",
                f"from {old_import}\\.",
            ]
            
            for pattern in patterns:
                content = re.sub(
                    pattern, 
                    pattern.replace(old_import, new_import), 
                    content
                )
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"  Updated imports in {file_path}")
            return True
        
    except Exception as e:
        print(f"  Error updating {file_path}: {e}")
        return False

def main():
    """Main migration function"""
    print("🔄 Starting import migration...")
    
    # Load integration config
    import json
    with open('legacy_loop_integration_config.json', 'r') as f:
        config = json.load(f)
    
    # Build import mapping
    import_mapping = {}
    for module_name, module_info in config['module_registry'].items():
        category = module_info['category']
        new_path = f"legacy_loop_organized.{category}.{module_name}"
        import_mapping[module_name] = new_path
    
    # Update all Python files
    organized_path = Path('./legacy_loop_organized')
    updated_count = 0
    
    for py_file in organized_path.rglob("*.py"):
        if py_file.name != '__init__.py':
            if update_imports_in_file(py_file, import_mapping):
                updated_count += 1
    
    print(f"✅ Migration complete! Updated {updated_count} files")

if __name__ == "__main__":
    main()
'''
        
        with open('migrate_imports.py', 'w') as f:
            f.write(script_content)
        
        print("📝 Migration script generated: migrate_imports.py")
    
    def run_organization(self, dry_run=True):
        """Run complete organization process"""
        print("🚀 Legacy Loop Module Organization")
        print("=" * 50)
        
        # Step 1: Create directory structure
        self.create_directory_structure()
        
        # Step 2: Move modules
        moves, conflicts = self.move_modules(dry_run=dry_run)
        
        # Step 3: Generate integration config
        config = self.generate_integration_config()
        
        # Step 4: Generate migration script
        self.generate_migration_script()
        
        # Summary
        print("\n📊 ORGANIZATION SUMMARY")
        print("=" * 50)
        print(f"Total modules to organize: {len(moves)}")
        print(f"Categories created: {len(self.target_structure)}")
        print(f"Potential conflicts: {len(conflicts)}")
        
        if dry_run:
            print("\n🔍 This was a DRY RUN - no files were moved")
            print("Run with dry_run=False to actually organize modules")
        else:
            print("\n✅ Modules organized successfully!")
        
        return {
            'moves': moves,
            'conflicts': conflicts,
            'config': config
        }

def main():
    """Main execution function"""
    try:
        organizer = ModuleOrganizer()
        result = organizer.run_organization(dry_run=True)
        
        print(f"\n🎯 Next steps:")
        print("1. Review the organization plan above")
        print("2. Run with dry_run=False to execute")
        print("3. Run migrate_imports.py to update imports")
        print("4. Test integration points")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Run module_analyzer.py first to generate analysis")

if __name__ == "__main__":
    main()
