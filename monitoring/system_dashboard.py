#!/usr/bin/env python3
"""
📊 SYSTEM DASHBOARD
Shows all active services, how to access them, and system status
"""

import subprocess
import os
import json
from pathlib import Path
from datetime import datetime

class SystemDashboard:
    """Display comprehensive system dashboard"""
    
    def __init__(self):
        self.root = Path.cwd()
    
    def check_running_processes(self):
        """Check what's actually running"""
        print("\n🔍 CHECKING ACTIVE PROCESSES...")
        print("=" * 80)
        
        processes = {
            'AI Portfolio Protection': [],
            'Paper Trading System': [],
            'Docker MCP Servers': [],
            'Web Servers': [],
            'Other Trading Scripts': []
        }
        
        try:
            # Check for Python processes
            result = subprocess.run(
                ['ps', 'aux'], 
                capture_output=True, 
                text=True
            )
            
            for line in result.stdout.split('\n'):
                if 'ai_portfolio_protection' in line and 'grep' not in line:
                    processes['AI Portfolio Protection'].append(line)
                elif 'paper_trading' in line and 'grep' not in line:
                    processes['Paper Trading System'].append(line)
                elif 'docker' in line and 'mcp' in line and 'grep' not in line:
                    processes['Docker MCP Servers'].append(line)
                elif any(x in line for x in ['node', 'npm', 'next']) and 'grep' not in line:
                    processes['Web Servers'].append(line)
                elif any(x in line for x in ['sovereign', 'trading', 'arbitrage']) and 'python' in line and 'grep' not in line:
                    processes['Other Trading Scripts'].append(line)
        
        except Exception as e:
            print(f"   ⚠️  Error checking processes: {e}")
        
        # Display results
        for category, procs in processes.items():
            if procs:
                print(f"\n✅ {category}: {len(procs)} running")
                for proc in procs[:2]:  # Show first 2
                    pid = proc.split()[1]
                    print(f"   PID: {pid}")
            else:
                print(f"\n❌ {category}: Not running")
        
        return processes
    
    def check_web_interfaces(self):
        """Check for active web interfaces"""
        print("\n\n🌐 WEB INTERFACES")
        print("=" * 80)
        
        ports_to_check = {
            3000: 'Next.js Dashboard (Development)',
            3001: 'Staging Dashboard',
            5000: 'Flask API Server',
            8000: 'Alternative API Server'
        }
        
        active_ports = []
        
        for port, description in ports_to_check.items():
            try:
                result = subprocess.run(
                    ['lsof', '-i', f':{port}'],
                    capture_output=True,
                    text=True
                )
                
                if result.stdout:
                    print(f"   ✅ Port {port}: {description}")
                    print(f"      → http://localhost:{port}")
                    active_ports.append((port, description))
                else:
                    print(f"   ❌ Port {port}: {description} (Not active)")
            except Exception as e:
                print(f"   ⚠️  Error checking port {port}: {e}")
        
        if not active_ports:
            print("\n   ⚠️  No web interfaces currently running")
        
        return active_ports
    
    def check_logs(self):
        """Check recent logs"""
        print("\n\n📋 RECENT ACTIVITY (LOGS)")
        print("=" * 80)
        
        log_dirs = [
            self.root / 'logs' / 'ai_enhanced',
            self.root / 'environments' / 'staging' / 'logs',
            self.root / 'logs'
        ]
        
        recent_logs = []
        
        for log_dir in log_dirs:
            if log_dir.exists():
                for log_file in log_dir.glob('*.log'):
                    try:
                        stat = log_file.stat()
                        recent_logs.append((log_file, stat.st_mtime))
                    except:
                        pass
        
        # Sort by modification time
        recent_logs.sort(key=lambda x: x[1], reverse=True)
        
        if recent_logs:
            print("\n   Most Recent Logs:")
            for log_file, mtime in recent_logs[:5]:
                rel_path = log_file.relative_to(self.root)
                mod_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                print(f"   • {rel_path}")
                print(f"     Last updated: {mod_time}")
        else:
            print("\n   ⚠️  No recent logs found")
        
        return recent_logs
    
    def check_configuration(self):
        """Check configuration status"""
        print("\n\n⚙️  CONFIGURATION STATUS")
        print("=" * 80)
        
        config_files = {
            '.env': 'Main environment variables',
            'config/api_config.json': 'API configuration',
            'sovereign_legacy_loop/ClaudeSDK/.env': 'Claude SDK config',
            'environments/staging/config_staging.yaml': 'Staging config',
            'environments/production/config_prod.yaml': 'Production config'
        }
        
        for file_path, description in config_files.items():
            full_path = self.root / file_path
            if full_path.exists():
                print(f"   ✅ {description}")
                print(f"      → {file_path}")
            else:
                print(f"   ❌ {description}")
                print(f"      → {file_path} (Missing)")
    
    def show_access_instructions(self):
        """Show how to access everything"""
        print("\n\n🚀 HOW TO ACCESS YOUR SYSTEM")
        print("=" * 80)
        
        print("\n📊 VIEW SYSTEM STATUS:")
        print("   python3 sovereign_shadow_unified.py")
        
        print("\n🔧 CONFIGURE APIS:")
        print("   python3 config/configure_all_apis.py")
        
        print("\n🧪 START PAPER TRADING:")
        print("   ./deployment/AI_ENHANCED_DEPLOYMENT.sh")
        
        print("\n📈 MONITOR REAL-TIME:")
        print("   tail -f logs/ai_enhanced/ai_portfolio_protection.log")
        
        print("\n🌐 WEB DASHBOARD (if running):")
        print("   http://localhost:3000  (Main Dashboard)")
        print("   http://localhost:3001  (Staging Dashboard)")
        
        print("\n🛑 STOP SERVICES:")
        print("   pkill -f ai_portfolio_protection")
        print("   pkill -f paper_trading")
        
        print("\n📁 KEY DIRECTORIES:")
        print("   scripts/       - Trading automation")
        print("   config/        - Configuration files")
        print("   monitoring/    - System monitoring")
        print("   deployment/    - Deployment scripts")
        print("   logs/          - System logs")
    
    def generate_status_report(self):
        """Generate complete status report"""
        print("\n" + "="*80)
        print("🏰 SOVEREIGNSHADOW.AI - SYSTEM DASHBOARD")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check all components
        processes = self.check_running_processes()
        web_interfaces = self.check_web_interfaces()
        logs = self.check_logs()
        self.check_configuration()
        self.show_access_instructions()
        
        # Summary
        print("\n\n📊 SUMMARY")
        print("=" * 80)
        
        total_processes = sum(len(procs) for procs in processes.values())
        print(f"   Active Processes: {total_processes}")
        print(f"   Active Web Interfaces: {len(web_interfaces)}")
        print(f"   Recent Log Files: {len(logs)}")
        
        if total_processes > 0:
            print("\n   ✅ System Status: ACTIVE")
        else:
            print("\n   ⚠️  System Status: IDLE")
            print("      Run: ./deployment/AI_ENHANCED_DEPLOYMENT.sh to start")
        
        print("\n" + "="*80)

def main():
    """Main execution"""
    dashboard = SystemDashboard()
    dashboard.generate_status_report()

if __name__ == "__main__":
    main()

