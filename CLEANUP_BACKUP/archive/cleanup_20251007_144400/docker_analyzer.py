#!/usr/bin/env python3
"""
Docker Infrastructure Analyzer for Legacy Loop
Specialized analyzer for Docker compose files and infrastructure
"""

import yaml
import json
from pathlib import Path
from datetime import datetime

class DockerInfrastructureAnalyzer:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.docker_files = {}
        self.services = {}
        self.networks = {}
        self.volumes = {}
        
    def analyze_docker_infrastructure(self):
        """Analyze all Docker-related files"""
        print("🐳 Analyzing Docker Infrastructure...")
        
        # Find Docker files
        docker_files = list(self.root_path.rglob("docker-compose*.yml")) + \
                      list(self.root_path.rglob("docker-compose*.yaml")) + \
                      list(self.root_path.rglob("Dockerfile*"))
        
        for docker_file in docker_files:
            self.analyze_docker_file(docker_file)
        
        print(f"✅ Found {len(self.docker_files)} Docker files")
        return self.generate_docker_report()
    
    def analyze_docker_file(self, file_path):
        """Analyze individual Docker file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_info = {
                'path': str(file_path.relative_to(self.root_path)),
                'full_path': str(file_path),
                'size': len(content),
                'type': 'dockerfile' if file_path.name.lower() == 'dockerfile' else 'docker-compose',
                'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                'services': [],
                'networks': [],
                'volumes': [],
                'environment_vars': [],
                'ports': [],
                'depends_on': []
            }
            
            if file_info['type'] == 'docker-compose':
                self.analyze_compose_file(content, file_info)
            else:
                self.analyze_dockerfile(content, file_info)
            
            self.docker_files[file_path.stem] = file_info
            
        except Exception as e:
            print(f"❌ Error analyzing {file_path}: {e}")
    
    def analyze_compose_file(self, content, file_info):
        """Analyze docker-compose.yml content"""
        try:
            compose_data = yaml.safe_load(content)
            
            # Extract services
            if 'services' in compose_data:
                for service_name, service_config in compose_data['services'].items():
                    service_info = {
                        'name': service_name,
                        'image': service_config.get('image', ''),
                        'build': service_config.get('build', ''),
                        'ports': service_config.get('ports', []),
                        'environment': service_config.get('environment', []),
                        'volumes': service_config.get('volumes', []),
                        'depends_on': service_config.get('depends_on', []),
                        'networks': service_config.get('networks', []),
                        'restart': service_config.get('restart', ''),
                        'command': service_config.get('command', '')
                    }
                    
                    file_info['services'].append(service_info)
                    self.services[service_name] = service_info
            
            # Extract networks
            if 'networks' in compose_data:
                for network_name, network_config in compose_data['networks'].items():
                    network_info = {
                        'name': network_name,
                        'driver': network_config.get('driver', 'bridge'),
                        'external': network_config.get('external', False)
                    }
                    
                    file_info['networks'].append(network_info)
                    self.networks[network_name] = network_info
            
            # Extract volumes
            if 'volumes' in compose_data:
                for volume_name, volume_config in compose_data['volumes'].items():
                    volume_info = {
                        'name': volume_name,
                        'driver': volume_config.get('driver', 'local'),
                        'external': volume_config.get('external', False)
                    }
                    
                    file_info['volumes'].append(volume_info)
                    self.volumes[volume_name] = volume_info
            
        except yaml.YAMLError as e:
            print(f"⚠️  YAML parsing error: {e}")
    
    def analyze_dockerfile(self, content, file_info):
        """Analyze Dockerfile content"""
        lines = content.splitlines()
        
        file_info['base_image'] = ''
        file_info['exposed_ports'] = []
        file_info['environment_vars'] = []
        file_info['commands'] = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('FROM'):
                file_info['base_image'] = line.split()[1]
            elif line.startswith('EXPOSE'):
                ports = line.split()[1:]
                file_info['exposed_ports'].extend(ports)
            elif line.startswith('ENV'):
                env_var = line.split(' ', 1)[1]
                file_info['environment_vars'].append(env_var)
            elif line.startswith(('RUN', 'COPY', 'ADD', 'WORKDIR', 'CMD', 'ENTRYPOINT')):
                file_info['commands'].append(line)
    
    def generate_docker_report(self):
        """Generate comprehensive Docker infrastructure report"""
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'total_docker_files': len(self.docker_files),
            'total_services': len(self.services),
            'total_networks': len(self.networks),
            'total_volumes': len(self.volumes),
            'docker_files': self.docker_files,
            'services': self.services,
            'networks': self.networks,
            'volumes': self.volumes,
            'infrastructure_summary': self.generate_infrastructure_summary()
        }
        
        return report
    
    def generate_infrastructure_summary(self):
        """Generate infrastructure summary"""
        summary = {
            'high_priority_services': [],
            'external_dependencies': [],
            'potential_issues': [],
            'recommendations': []
        }
        
        # Analyze services
        for service_name, service_info in self.services.items():
            # High priority services (databases, APIs)
            if any(keyword in service_name.lower() for keyword in ['api', 'server', 'db', 'database', 'redis', 'postgres']):
                summary['high_priority_services'].append(service_name)
            
            # External dependencies
            if service_info.get('external', False):
                summary['external_dependencies'].append(service_name)
            
            # Potential issues
            if not service_info.get('restart'):
                summary['potential_issues'].append(f"Service '{service_name}' missing restart policy")
            
            if not service_info.get('networks'):
                summary['potential_issues'].append(f"Service '{service_name}' not connected to any network")
        
        # Recommendations
        if len(self.services) > 5:
            summary['recommendations'].append("Consider breaking down into smaller compose files for better maintainability")
        
        if any('latest' in service.get('image', '') for service in self.services.values()):
            summary['recommendations'].append("Avoid using 'latest' tags in production - use specific versions")
        
        return summary
    
    def save_report(self, filename='docker_infrastructure_analysis.json'):
        """Save Docker analysis report"""
        report = self.generate_docker_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"🐳 Docker report saved to {filename}")
        return report

def main():
    """Main execution function"""
    print("🐳 Legacy Loop Docker Infrastructure Analyzer")
    print("=" * 60)
    
    root_path = Path(__file__).parent
    analyzer = DockerInfrastructureAnalyzer(root_path)
    
    report = analyzer.analyze_docker_infrastructure()
    analyzer.save_report()
    
    # Print summary
    print("\n🐳 DOCKER INFRASTRUCTURE SUMMARY")
    print("=" * 60)
    print(f"Docker Files: {report['total_docker_files']}")
    print(f"Services: {report['total_services']}")
    print(f"Networks: {report['total_networks']}")
    print(f"Volumes: {report['total_volumes']}")
    
    if report['infrastructure_summary']['high_priority_services']:
        print(f"\n🎯 High Priority Services:")
        for service in report['infrastructure_summary']['high_priority_services']:
            print(f"  • {service}")
    
    if report['infrastructure_summary']['potential_issues']:
        print(f"\n⚠️  Potential Issues:")
        for issue in report['infrastructure_summary']['potential_issues'][:3]:
            print(f"  • {issue}")
    
    if report['infrastructure_summary']['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in report['infrastructure_summary']['recommendations']:
            print(f"  • {rec}")
    
    print(f"\n✅ Docker analysis complete! Check docker_infrastructure_analysis.json for details")

if __name__ == "__main__":
    main()
