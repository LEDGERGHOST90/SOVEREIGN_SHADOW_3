#!/usr/bin/env python3
"""
AI System Monitor - Sovereign Legacy Loop
Comprehensive health check for all MCP modules and system components
"""

import os
import sys
import asyncio
import logging
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the sovereign legacy loop root to Python path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "multi-exchange-crypto-mcp"))
sys.path.insert(0, str(ROOT_DIR / "ClaudeSDK"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ai_system_monitor")

class SystemHealthMonitor:
    """Comprehensive system health monitoring for Sovereign Legacy Loop"""
    
    def __init__(self):
        self.root_dir = ROOT_DIR
        self.health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "components": {}
        }
        
    async def check_all_components(self) -> Dict[str, Any]:
        """Run comprehensive health checks on all system components"""
        logger.info("🔍 Starting comprehensive system health check...")
        
        # Check MCP modules
        await self._check_mcp_modules()
        
        # Check Docker services
        await self._check_docker_services()
        
        # Check Python dependencies
        await self._check_python_dependencies()
        
        # Check file system integrity
        await self._check_file_system()
        
        # Check network connectivity
        await self._check_network_connectivity()
        
        # Determine overall status
        self._determine_overall_status()
        
        return self.health_status
    
    async def _check_mcp_modules(self):
        """Check MCP module health and dependencies"""
        logger.info("📦 Checking MCP modules...")
        
        mcp_status = {
            "status": "healthy",
            "modules": {},
            "errors": []
        }
        
        # Check multi-exchange-crypto-mcp
        try:
            mcp_path = self.root_dir / "multi-exchange-crypto-mcp"
            if mcp_path.exists():
                # Test import
                sys.path.insert(0, str(mcp_path))
                try:
                    import empire_automation
                    mcp_status["modules"]["empire_automation"] = "✅ Import successful"
                except ImportError as e:
                    mcp_status["modules"]["empire_automation"] = f"❌ Import failed: {e}"
                    mcp_status["errors"].append(f"empire_automation import: {e}")
                
                # Check requirements
                req_file = mcp_path / "requirements.txt"
                if req_file.exists():
                    mcp_status["modules"]["requirements"] = "✅ Requirements file found"
                else:
                    mcp_status["modules"]["requirements"] = "❌ Requirements file missing"
                    mcp_status["errors"].append("requirements.txt missing")
            else:
                mcp_status["modules"]["multi_exchange_mcp"] = "❌ Directory not found"
                mcp_status["errors"].append("multi-exchange-crypto-mcp directory missing")
        except Exception as e:
            mcp_status["status"] = "unhealthy"
            mcp_status["errors"].append(f"MCP module check failed: {e}")
        
        self.health_status["components"]["mcp_modules"] = mcp_status
    
    async def _check_docker_services(self):
        """Check Docker services health"""
        logger.info("🐳 Checking Docker services...")
        
        docker_status = {
            "status": "healthy",
            "services": {},
            "errors": []
        }
        
        try:
            # Check if Docker is running
            result = subprocess.run(
                ["docker", "ps"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                docker_status["services"]["docker_daemon"] = "✅ Docker daemon running"
                
                # Check for our specific containers
                output = result.stdout.lower()
                if "mcp-crypto-exchange" in output:
                    docker_status["services"]["mcp_exchange"] = "✅ MCP Exchange container running"
                else:
                    docker_status["services"]["mcp_exchange"] = "⚠️ MCP Exchange container not running"
                
                if "mcp-redis-cache" in output:
                    docker_status["services"]["redis"] = "✅ Redis container running"
                else:
                    docker_status["services"]["redis"] = "⚠️ Redis container not running"
            else:
                docker_status["services"]["docker_daemon"] = "❌ Docker daemon not accessible"
                docker_status["errors"].append("Docker daemon not running")
                docker_status["status"] = "unhealthy"
                
        except subprocess.TimeoutExpired:
            docker_status["services"]["docker_daemon"] = "❌ Docker timeout"
            docker_status["errors"].append("Docker command timeout")
            docker_status["status"] = "unhealthy"
        except FileNotFoundError:
            docker_status["services"]["docker_daemon"] = "❌ Docker not installed"
            docker_status["errors"].append("Docker not found")
            docker_status["status"] = "unhealthy"
        except Exception as e:
            docker_status["status"] = "unhealthy"
            docker_status["errors"].append(f"Docker check failed: {e}")
        
        self.health_status["components"]["docker_services"] = docker_status
    
    async def _check_python_dependencies(self):
        """Check Python dependencies and environment"""
        logger.info("🐍 Checking Python dependencies...")
        
        deps_status = {
            "status": "healthy",
            "packages": {},
            "errors": []
        }
        
        # Check critical packages
        critical_packages = [
            "mcp", "ccxt", "pandas", "numpy", "aiohttp", 
            "websockets", "requests", "python-dotenv"
        ]
        
        for package in critical_packages:
            try:
                __import__(package)
                deps_status["packages"][package] = "✅ Available"
            except ImportError:
                deps_status["packages"][package] = "❌ Missing"
                deps_status["errors"].append(f"Missing package: {package}")
        
        # Check Python version
        python_version = sys.version_info
        if python_version >= (3, 11):
            deps_status["packages"]["python_version"] = f"✅ Python {python_version.major}.{python_version.minor}"
        else:
            deps_status["packages"]["python_version"] = f"❌ Python {python_version.major}.{python_version.minor} (need 3.11+)"
            deps_status["errors"].append(f"Python version too old: {python_version.major}.{python_version.minor}")
        
        if deps_status["errors"]:
            deps_status["status"] = "unhealthy"
        
        self.health_status["components"]["python_dependencies"] = deps_status
    
    async def _check_file_system(self):
        """Check critical file system components"""
        logger.info("📁 Checking file system...")
        
        fs_status = {
            "status": "healthy",
            "files": {},
            "errors": []
        }
        
        # Critical files to check
        critical_files = [
            "multi-exchange-crypto-mcp/empire_automation.py",
            "multi-exchange-crypto-mcp/requirements.txt",
            "ClaudeSDK/mcp_exchange_server.py",
            "ClaudeSDK/docker-compose.yml",
            "app/package.json",
            "app/prisma/schema.prisma"
        ]
        
        for file_path in critical_files:
            full_path = self.root_dir / file_path
            if full_path.exists():
                fs_status["files"][file_path] = "✅ Found"
            else:
                fs_status["files"][file_path] = "❌ Missing"
                fs_status["errors"].append(f"Missing file: {file_path}")
        
        # Check directories
        critical_dirs = [
            "multi-exchange-crypto-mcp",
            "ClaudeSDK", 
            "app",
            "monitoring"
        ]
        
        for dir_path in critical_dirs:
            full_path = self.root_dir / dir_path
            if full_path.exists() and full_path.is_dir():
                fs_status["files"][f"{dir_path}/"] = "✅ Directory found"
            else:
                fs_status["files"][f"{dir_path}/"] = "❌ Directory missing"
                fs_status["errors"].append(f"Missing directory: {dir_path}")
        
        if fs_status["errors"]:
            fs_status["status"] = "unhealthy"
        
        self.health_status["components"]["file_system"] = fs_status
    
    async def _check_network_connectivity(self):
        """Check network connectivity for external services"""
        logger.info("🌐 Checking network connectivity...")
        
        net_status = {
            "status": "healthy",
            "endpoints": {},
            "errors": []
        }
        
        # Test endpoints (non-blocking)
        test_endpoints = [
            "https://api.binance.us",
            "https://www.okx.com",
            "https://api.kraken.com"
        ]
        
        for endpoint in test_endpoints:
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(endpoint, timeout=5) as response:
                        if response.status < 500:
                            net_status["endpoints"][endpoint] = "✅ Reachable"
                        else:
                            net_status["endpoints"][endpoint] = f"⚠️ Server error: {response.status}"
            except asyncio.TimeoutError:
                net_status["endpoints"][endpoint] = "⚠️ Timeout"
            except Exception as e:
                net_status["endpoints"][endpoint] = f"❌ Error: {str(e)[:50]}"
                net_status["errors"].append(f"Network error for {endpoint}: {e}")
        
        if len(net_status["errors"]) > 2:  # Allow some network issues
            net_status["status"] = "unhealthy"
        
        self.health_status["components"]["network"] = net_status
    
    def _determine_overall_status(self):
        """Determine overall system health status"""
        component_statuses = [
            comp.get("status", "unknown") 
            for comp in self.health_status["components"].values()
        ]
        
        if all(status == "healthy" for status in component_statuses):
            self.health_status["overall_status"] = "healthy"
        elif any(status == "unhealthy" for status in component_statuses):
            self.health_status["overall_status"] = "unhealthy"
        else:
            self.health_status["overall_status"] = "degraded"
    
    def print_health_report(self):
        """Print a formatted health report"""
        print("\n" + "="*80)
        print("🏥 SOVEREIGN LEGACY LOOP - SYSTEM HEALTH REPORT")
        print("="*80)
        print(f"📅 Timestamp: {self.health_status['timestamp']}")
        print(f"🎯 Overall Status: {self.health_status['overall_status'].upper()}")
        print()
        
        for component_name, component_data in self.health_status["components"].items():
            print(f"📦 {component_name.upper().replace('_', ' ')}")
            print(f"   Status: {component_data.get('status', 'unknown')}")
            
            # Print sub-items
            for key, value in component_data.items():
                if key not in ['status', 'errors']:
                    print(f"   {value}")
            
            # Print errors if any
            if component_data.get('errors'):
                print("   🚨 Errors:")
                for error in component_data['errors']:
                    print(f"      • {error}")
            print()
        
        print("="*80)

async def main():
    """Main health check function"""
    monitor = SystemHealthMonitor()
    
    # Check if running with --once flag
    if "--once" in sys.argv:
        health_data = await monitor.check_all_components()
        monitor.print_health_report()
        
        # Exit with appropriate code
        if health_data["overall_status"] == "healthy":
            sys.exit(0)
        elif health_data["overall_status"] == "degraded":
            sys.exit(1)
        else:
            sys.exit(2)
    else:
        print("Usage: python ai_system_monitor.py --once")
        print("For continuous monitoring, implement a scheduler or use systemd")

if __name__ == "__main__":
    asyncio.run(main())

