#!/usr/bin/env python3
"""
SovereignShadow.Ai[LegacyLoop] Master System Analyzer
Analyzes the complete hierarchy of Raymond's most prized components
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class SovereignShadowAIAnalyzer:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.master_system = {
            'sovereign_shadow_ai': {
                'description': 'SovereignShadow.Ai[LegacyLoop] - Master system',
                'components': [],
                'status': 'active',
                'priority': 0
            }
        }
        
        self.component_hierarchy = {
            'omega_engines': {
                'description': 'Ω Engines - Core processing and automation',
                'subcomponents': ['processing', 'automation', 'core_engines'],
                'status': 'active',
                'priority': 1
            },
            'shepard_system': {
                'description': 'Shepard System - Navigation and guidance',
                'subcomponents': ['navigation', 'guidance', 'direction'],
                'status': 'active', 
                'priority': 2
            },
            'sigma_x': {
                'description': 'ΣIGMA-X - Signal detection and analysis',
                'subcomponents': ['signal_detection', 'analysis', 'patterns'],
                'status': 'active',
                'priority': 3
            },
            'crown_jewels': {
                'description': 'Crown Jewels - Most prized components',
                'subcomponents': ['toshi', 'ledgerghost90', 'sovßankingsystems'],
                'status': 'development',
                'priority': 4
            },
            'sovlegacyloop_shadow_ai_2': {
                'description': 'SOVlegacyloop: Shadow AI 2 - Core sovereign system',
                'subcomponents': ['shadow_ai_2', 'deep_agent', 'neural_network'],
                'status': 'production',
                'priority': 5
            },
            'nexus_protocol': {
                'description': 'Nexus Protocol - Bridge and connection systems',
                'subcomponents': ['bridges', 'connections', 'integration'],
                'status': 'active',
                'priority': 6
            },
            'keyblade_system': {
                'description': 'KeyBlade System - Ω Sigil, Toshi, Manus, Mennace, Ω Journey',
                'subcomponents': ['omega_sigil', 'toshi', 'manus', 'mennace', 'omega_journey'],
                'status': 'active',
                'priority': 7
            },
            'flipbot_system': {
                'description': 'FlipBot System - flipbot, flipbotphil automated trading',
                'subcomponents': ['flipbot', 'flipbotphil', 'automated_trading'],
                'status': 'production',
                'priority': 8
            },
            'whale_scanner': {
                'description': 'Whale Scanner - whalejackpotscanner, large trade detection',
                'subcomponents': ['whalejackpotscanner', 'large_trades', 'institutional', 'big_player'],
                'status': 'active',
                'priority': 9
            },
            'rebalancing_engine': {
                'description': 'Rebalancing Engine - Portfolio rebalancing automation',
                'subcomponents': ['rebalancing', 'rebal', 'portfolio_rebalancing', 'auto_rebalance'],
                'status': 'active',
                'priority': 10
            },
            'wallet_scanner': {
                'description': 'Wallet Scanner - Address monitoring and tracking',
                'subcomponents': ['wallet_scanner', 'wallet_watcher', 'address_monitor', 'wallet_tracker'],
                'status': 'active',
                'priority': 11
            },
            'data_agents': {
                'description': 'Data Agents - Market data collection and processing',
                'subcomponents': ['data_agent', 'data_collector', 'data_processor', 'market_data'],
                'status': 'production',
                'priority': 12
            }
        }
    
    def analyze_sovereign_shadow_ai(self):
        """Analyze the complete SovereignShadow.Ai[LegacyLoop] system"""
        print("👑 Analyzing SovereignShadow.Ai[LegacyLoop] Master System...")
        
        # Analyze each component
        for component_name, component_info in self.component_hierarchy.items():
            self.analyze_component(component_name, component_info)
        
        # Generate system hierarchy report
        return self.generate_hierarchy_report()
    
    def analyze_component(self, component_name, component_info):
        """Analyze individual component"""
        print(f"🔍 Analyzing {component_name}...")
        
        # Find files related to this component
        related_files = self.find_component_files(component_name, component_info)
        
        # Analyze component status
        status = self.determine_component_status(related_files)
        
        # Update component info
        self.component_hierarchy[component_name].update({
            'related_files': related_files,
            'file_count': len(related_files),
            'status': status,
            'last_analyzed': datetime.now().isoformat()
        })
    
    def find_component_files(self, component_name, component_info):
        """Find files related to a specific component"""
        related_files = []
        
        # Search for files containing component keywords
        keywords = [component_name.replace('_', ' '), component_name.replace('_', '-')]
        keywords.extend(component_info.get('subcomponents', []))
        
        for keyword in keywords:
            # Search Python files
            for py_file in self.root_path.rglob("*.py"):
                if self.file_contains_keyword(py_file, keyword):
                    related_files.append({
                        'path': str(py_file.relative_to(self.root_path)),
                        'type': 'python',
                        'keyword': keyword
                    })
            
            # Search JSON files
            for json_file in self.root_path.rglob("*.json"):
                if self.file_contains_keyword(json_file, keyword):
                    related_files.append({
                        'path': str(json_file.relative_to(self.root_path)),
                        'type': 'json',
                        'keyword': keyword
                    })
            
            # Search Markdown files
            for md_file in self.root_path.rglob("*.md"):
                if self.file_contains_keyword(md_file, keyword):
                    related_files.append({
                        'path': str(md_file.relative_to(self.root_path)),
                        'type': 'markdown',
                        'keyword': keyword
                    })
        
        return related_files
    
    def file_contains_keyword(self, file_path, keyword):
        """Check if file contains keyword"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                return keyword.lower() in content
        except:
            return False
    
    def determine_component_status(self, related_files):
        """Determine component status based on related files"""
        if len(related_files) == 0:
            return 'conceptual'
        elif len(related_files) < 3:
            return 'development'
        elif len(related_files) < 10:
            return 'active'
        else:
            return 'production'
    
    def generate_hierarchy_report(self):
        """Generate comprehensive hierarchy report"""
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'master_system': 'SovereignShadow.Ai[LegacyLoop]',
            'total_components': len(self.component_hierarchy),
            'component_hierarchy': self.component_hierarchy,
            'system_summary': self.generate_system_summary(),
            'development_roadmap': self.generate_development_roadmap()
        }
        
        return report
    
    def generate_system_summary(self):
        """Generate system summary"""
        summary = {
            'production_ready': [],
            'active_development': [],
            'conceptual_stage': [],
            'total_files': 0
        }
        
        for component_name, component_info in self.component_hierarchy.items():
            status = component_info.get('status', 'unknown')
            file_count = component_info.get('file_count', 0)
            
            summary['total_files'] += file_count
            
            if status == 'production':
                summary['production_ready'].append({
                    'component': component_name,
                    'files': file_count,
                    'description': component_info['description']
                })
            elif status == 'active':
                summary['active_development'].append({
                    'component': component_name,
                    'files': file_count,
                    'description': component_info['description']
                })
            elif status == 'conceptual':
                summary['conceptual_stage'].append({
                    'component': component_name,
                    'files': file_count,
                    'description': component_info['description']
                })
        
        return summary
    
    def generate_development_roadmap(self):
        """Generate development roadmap"""
        roadmap = {
            'phase_1_immediate': [],
            'phase_2_short_term': [],
            'phase_3_medium_term': [],
            'phase_4_long_term': []
        }
        
        # Sort components by priority
        sorted_components = sorted(
            self.component_hierarchy.items(),
            key=lambda x: x[1].get('priority', 99)
        )
        
        for component_name, component_info in sorted_components:
            status = component_info.get('status', 'unknown')
            priority = component_info.get('priority', 99)
            
            if status == 'production':
                roadmap['phase_1_immediate'].append({
                    'component': component_name,
                    'action': 'Deploy and monetize',
                    'description': component_info['description']
                })
            elif status == 'active':
                roadmap['phase_2_short_term'].append({
                    'component': component_name,
                    'action': 'Complete integration',
                    'description': component_info['description']
                })
            elif status == 'development':
                roadmap['phase_3_medium_term'].append({
                    'component': component_name,
                    'action': 'Continue development',
                    'description': component_info['description']
                })
            elif status == 'conceptual':
                roadmap['phase_4_long_term'].append({
                    'component': component_name,
                    'action': 'Begin architecture',
                    'description': component_info['description']
                })
        
        return roadmap
    
    def save_report(self, filename='sovereign_shadow_ai_hierarchy.json'):
        """Save hierarchy analysis report"""
        report = self.generate_hierarchy_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"👑 SovereignShadow.Ai[LegacyLoop] report saved to {filename}")
        return report

def main():
    """Main execution function"""
    print("👑 SovereignShadow.Ai[LegacyLoop] Master System Analyzer")
    print("=" * 70)
    
    root_path = Path(__file__).parent
    analyzer = SovereignShadowAIAnalyzer(root_path)
    
    report = analyzer.analyze_sovereign_shadow_ai()
    analyzer.save_report()
    
    # Print summary
    print("\n👑 SOVEREIGNSHADOW.AI[LEGACYLOOP] HIERARCHY")
    print("=" * 70)
    
    summary = report['system_summary']
    print(f"Total Components: {report['total_components']}")
    print(f"Total Files: {summary['total_files']}")
    
    if summary['production_ready']:
        print(f"\n🚀 PRODUCTION READY ({len(summary['production_ready'])} components):")
        for component in summary['production_ready']:
            print(f"  • {component['component']}: {component['files']} files")
    
    if summary['active_development']:
        print(f"\n⚡ ACTIVE DEVELOPMENT ({len(summary['active_development'])} components):")
        for component in summary['active_development']:
            print(f"  • {component['component']}: {component['files']} files")
    
    if summary['conceptual_stage']:
        print(f"\n💡 CONCEPTUAL STAGE ({len(summary['conceptual_stage'])} components):")
        for component in summary['conceptual_stage']:
            print(f"  • {component['component']}: {component['files']} files")
    
    roadmap = report['development_roadmap']
    print(f"\n📋 DEVELOPMENT ROADMAP:")
    print(f"  Phase 1 (Immediate): {len(roadmap['phase_1_immediate'])} components")
    print(f"  Phase 2 (Short-term): {len(roadmap['phase_2_short_term'])} components") 
    print(f"  Phase 3 (Medium-term): {len(roadmap['phase_3_medium_term'])} components")
    print(f"  Phase 4 (Long-term): {len(roadmap['phase_4_long_term'])} components")
    
    print(f"\n✅ Hierarchy analysis complete! Check sovereign_shadow_ai_hierarchy.json for details")

if __name__ == "__main__":
    main()
