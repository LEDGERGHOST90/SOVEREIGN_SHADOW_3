#!/usr/bin/env python3
"""
🚀 DEPLOYMENT STATUS CHECKER
Comprehensive status check for AI trading platform
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

def check_ai_portfolio_protection():
    """Check AI Portfolio Protection status"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'ai_portfolio_protection' in line and 'grep' not in line:
                parts = line.split()
                if len(parts) > 1:
                    return {
                        'status': 'ACTIVE',
                        'pid': parts[1],
                        'cpu': parts[2],
                        'memory': parts[3]
                    }
        return {'status': 'INACTIVE'}
    except Exception as e:
        return {'status': 'ERROR', 'error': str(e)}

def check_dependencies():
    """Check Python dependencies"""
    dependencies = {}
    
    deps_to_check = ['websocket-client', 'pyyaml', 'pandas', 'numpy']
    
    for dep in deps_to_check:
        try:
            if dep == 'websocket-client':
                import websocket
            elif dep == 'pyyaml':
                import yaml
            elif dep == 'pandas':
                import pandas
            elif dep == 'numpy':
                import numpy
            dependencies[dep] = 'INSTALLED'
        except ImportError:
            dependencies[dep] = 'MISSING'
    
    return dependencies

def check_log_files():
    """Check log file status"""
    log_files = {}
    
    log_paths = [
        'logs/ai_enhanced/ai_portfolio_protection.log',
        'logs/ai_enhanced/ai_system_monitor.log',
        'logs/empire_automation.log'
    ]
    
    for log_path in log_paths:
        if os.path.exists(log_path):
            size = os.path.getsize(log_path)
            log_files[os.path.basename(log_path)] = f'EXISTS ({size} bytes)'
        else:
            log_files[os.path.basename(log_path)] = 'MISSING'
    
    return log_files

def check_environment_variables():
    """Check environment variables"""
    env_vars = {}
    
    vars_to_check = [
        'CLAUDE_SDK_ACTIVE',
        'MCP_FRAMEWORK_ACTIVE',
        'MULTI_AI_ORCHESTRATION'
    ]
    
    for var in vars_to_check:
        value = os.getenv(var, 'NOT_SET')
        env_vars[var] = value
    
    return env_vars

def check_staging_environment():
    """Check staging environment configuration"""
    staging_config = {
        'config_file': 'MISSING',
        'virtual_env': 'MISSING',
        'dependencies': 'MISSING'
    }
    
    # Check staging config
    if os.path.exists('environments/staging/config_staging.yaml'):
        staging_config['config_file'] = 'EXISTS'
    
    # Check virtual environment
    if os.path.exists('multi-exchange-crypto-mcp/crypto_empire_env'):
        staging_config['virtual_env'] = 'EXISTS'
    
    # Check if dependencies are installed in virtual env
    try:
        result = subprocess.run([
            'multi-exchange-crypto-mcp/crypto_empire_env/bin/pip', 'list'
        ], capture_output=True, text=True)
        
        if 'websocket-client' in result.stdout and 'pandas' in result.stdout:
            staging_config['dependencies'] = 'INSTALLED'
    except:
        pass
    
    return staging_config

def generate_deployment_report():
    """Generate comprehensive deployment report"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'deployment_status': 'SUCCESSFUL',
        'ai_systems': {
            'portfolio_protection': check_ai_portfolio_protection()
        },
        'dependencies': check_dependencies(),
        'log_files': check_log_files(),
        'environment_variables': check_environment_variables(),
        'staging_environment': check_staging_environment()
    }
    
    # Determine overall status
    all_deps_installed = all(status == 'INSTALLED' for status in report['dependencies'].values())
    ai_system_active = report['ai_systems']['portfolio_protection']['status'] == 'ACTIVE'
    
    if all_deps_installed and ai_system_active:
        report['deployment_status'] = 'FULLY_OPERATIONAL'
    elif ai_system_active:
        report['deployment_status'] = 'PARTIALLY_OPERATIONAL'
    else:
        report['deployment_status'] = 'NEEDS_ATTENTION'
    
    return report

def display_status():
    """Display deployment status"""
    report = generate_deployment_report()
    
    print("\n" + "="*80)
    print("🚀 AI-ENHANCED TRADING PLATFORM - DEPLOYMENT STATUS")
    print("="*80)
    print(f"📅 Timestamp: {report['timestamp']}")
    print(f"🎯 Overall Status: {report['deployment_status']}")
    
    print("\n🤖 AI SYSTEMS:")
    print("-" * 40)
    for system, status in report['ai_systems'].items():
        status_icon = "✅" if status['status'] == 'ACTIVE' else "❌"
        print(f"{status_icon} {system.replace('_', ' ').title()}: {status['status']}")
        if 'pid' in status:
            print(f"   PID: {status['pid']}, CPU: {status['cpu']}%, Memory: {status['memory']}%")
    
    print("\n📦 DEPENDENCIES:")
    print("-" * 40)
    for dep, status in report['dependencies'].items():
        status_icon = "✅" if status == 'INSTALLED' else "❌"
        print(f"{status_icon} {dep}: {status}")
    
    print("\n📋 LOG FILES:")
    print("-" * 40)
    for log, status in report['log_files'].items():
        status_icon = "✅" if 'EXISTS' in status else "❌"
        print(f"{status_icon} {log}: {status}")
    
    print("\n🔧 ENVIRONMENT VARIABLES:")
    print("-" * 40)
    for var, value in report['environment_variables'].items():
        status_icon = "✅" if value != 'NOT_SET' else "❌"
        print(f"{status_icon} {var}: {value}")
    
    print("\n🧪 STAGING ENVIRONMENT:")
    print("-" * 40)
    for item, status in report['staging_environment'].items():
        status_icon = "✅" if status in ['EXISTS', 'INSTALLED'] else "❌"
        print(f"{status_icon} {item.replace('_', ' ').title()}: {status}")
    
    print("="*80)
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    print("-" * 40)
    
    if report['deployment_status'] == 'FULLY_OPERATIONAL':
        print("🎉 Your AI trading platform is fully operational!")
        print("   • All systems are active and dependencies installed")
        print("   • Ready for live trading operations")
    elif report['deployment_status'] == 'PARTIALLY_OPERATIONAL':
        print("⚠️  Platform is partially operational")
        print("   • AI systems are active but some dependencies may be missing")
        print("   • Consider installing missing dependencies for full functionality")
    else:
        print("🔧 Platform needs attention")
        print("   • Check AI system status and restart if necessary")
        print("   • Install missing dependencies")
        print("   • Verify environment configuration")
    
    return report

def main():
    """Main function"""
    report = display_status()
    
    # Save report to file
    with open('logs/ai_enhanced/deployment_status.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Full report saved to: logs/ai_enhanced/deployment_status.json")

if __name__ == "__main__":
    main()
