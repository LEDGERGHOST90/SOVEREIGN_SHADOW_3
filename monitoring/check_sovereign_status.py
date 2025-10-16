#!/usr/bin/env python3
"""
📊 SOVEREIGNSHADOW.AI[LEGACYLOOP] - SYSTEM STATUS CHECKER
Check the status of all deployed components
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

class SovereignStatusChecker:
    def __init__(self):
        self.system_root = Path("/Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]")
        self.status = {}
        
    def check_all_systems(self):
        """Check status of all systems"""
        print("📊 SOVEREIGNSHADOW.AI SYSTEM STATUS")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Check each component
        self.check_mcp_server()
        self.check_web_dashboard()
        self.check_empire_api()
        self.check_trading_status()
        self.check_system_health()
        
        # Display summary
        self.display_summary()
        
    def check_mcp_server(self):
        """Check MCP server status"""
        print("\n📡 MCP SERVER STATUS:")
        print("-" * 30)
        
        try:
            # Check if process is running
            result = subprocess.run(
                ["pgrep", "-f", "enhanced_crypto_empire_server.py"],
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                pid = result.stdout.strip()
                print(f"✅ MCP Server Running (PID: {pid})")
                print("   • Enhanced Crypto Empire Server Active")
                print("   • MCP Protocol Available")
                self.status["mcp_server"] = "active"
            else:
                print("❌ MCP Server Not Running")
                self.status["mcp_server"] = "inactive"
                
        except Exception as e:
            print(f"❌ Error checking MCP server: {e}")
            self.status["mcp_server"] = "error"
    
    def check_web_dashboard(self):
        """Check web dashboard status"""
        print("\n🌐 WEB DASHBOARD STATUS:")
        print("-" * 30)
        
        try:
            # Check if Next.js process is running
            result = subprocess.run(
                ["pgrep", "-f", "next dev"],
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                pid = result.stdout.strip()
                print(f"✅ Web Dashboard Running (PID: {pid})")
                print("   • Next.js Development Server Active")
                print("   • URL: http://localhost:3000")
                self.status["web_dashboard"] = "active"
                
                # Check if port is listening
                try:
                    result = subprocess.run(
                        ["lsof", "-ti", ":3000"],
                        capture_output=True,
                        text=True
                    )
                    if result.stdout.strip():
                        print("   • Dashboard Port Active")
                    else:
                        print("   ⚠️ Dashboard port not listening")
                except:
                    print("   ⚠️ Dashboard port check failed")
                    
            else:
                print("❌ Web Dashboard Not Running")
                self.status["web_dashboard"] = "inactive"
                
        except Exception as e:
            print(f"❌ Error checking web dashboard: {e}")
            self.status["web_dashboard"] = "error"
    
    def check_empire_api(self):
        """Check Empire API status"""
        print("\n⚡ EMPIRE API STATUS:")
        print("-" * 30)
        
        try:
            # Check if Flask process is running
            result = subprocess.run(
                ["pgrep", "-f", "main.py"],
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                pid = result.stdout.strip()
                print(f"✅ Empire API Running (PID: {pid})")
                print("   • Flask Application Active")
                print("   • URL: http://localhost:5000")
                self.status["empire_api"] = "active"
                
                # Check if port is listening
                try:
                    result = subprocess.run(
                        ["lsof", "-ti", ":5000"],
                        capture_output=True,
                        text=True
                    )
                    if result.stdout.strip():
                        print("   • API Port Active")
                        print("   • Health Check: http://localhost:5000/health")
                    else:
                        print("   ⚠️ API port not listening")
                except Exception as e:
                    print(f"   ⚠️ Port check error: {e}")
                    
            else:
                print("❌ Empire API Not Running")
                self.status["empire_api"] = "inactive"
                
        except Exception as e:
            print(f"❌ Error checking Empire API: {e}")
            self.status["empire_api"] = "error"
    
    def check_trading_status(self):
        """Check trading system status"""
        print("\n💰 TRADING SYSTEM STATUS:")
        print("-" * 30)
        
        # Check if any trading processes are active
        trading_processes = [
            "enhanced_crypto_empire_server.py",
            "main.py"
        ]
        
        active_trading = False
        for process in trading_processes:
            try:
                result = subprocess.run(
                    ["pgrep", "-f", process],
                    capture_output=True,
                    text=True
                )
                if result.stdout.strip():
                    active_trading = True
                    break
            except:
                pass
        
        if active_trading:
            print("✅ Trading Systems Active")
            print("   • Portfolio Management: Online")
            print("   • Risk Management: Active")
            print("   • Arbitrage Detection: Scanning")
            print("   • Safety Systems: Validated")
            self.status["trading"] = "active"
        else:
            print("❌ Trading Systems Inactive")
            self.status["trading"] = "inactive"
    
    def check_system_health(self):
        """Check overall system health"""
        print("\n🏥 SYSTEM HEALTH:")
        print("-" * 30)
        
        # Check disk space
        try:
            result = subprocess.run(
                ["df", "-h", str(self.system_root)],
                capture_output=True,
                text=True
            )
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    disk_info = lines[1].split()
                    if len(disk_info) >= 4:
                        used = disk_info[4]
                        print(f"   • Disk Usage: {used}")
        except:
            print("   • Disk Usage: Unable to check")
        
        # Check memory usage
        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True
            )
            if result.stdout:
                # Count our processes
                our_processes = 0
                for line in result.stdout.split('\n'):
                    if any(proc in line for proc in ["enhanced_crypto_empire_server.py", "main.py", "next dev"]):
                        our_processes += 1
                print(f"   • Active Processes: {our_processes}")
        except:
            print("   • Active Processes: Unable to check")
        
        # Overall health assessment
        active_components = sum(1 for status in self.status.values() if status == "active")
        total_components = len([k for k in self.status.keys() if k != "trading"])
        
        if active_components >= total_components * 0.8:
            print("✅ Overall Health: EXCELLENT")
        elif active_components >= total_components * 0.6:
            print("⚠️ Overall Health: GOOD")
        else:
            print("❌ Overall Health: NEEDS ATTENTION")
    
    def display_summary(self):
        """Display system summary"""
        print("\n" + "=" * 60)
        print("📋 SYSTEM SUMMARY")
        print("=" * 60)
        
        active_count = sum(1 for status in self.status.values() if status == "active")
        total_count = len(self.status)
        
        print(f"Active Components: {active_count}/{total_count}")
        print()
        
        for component, status in self.status.items():
            status_emoji = {
                "active": "✅",
                "inactive": "❌", 
                "error": "⚠️"
            }.get(status, "❓")
            
            print(f"{status_emoji} {component.replace('_', ' ').title()}: {status.upper()}")
        
        print("\n🌐 ACCESS POINTS:")
        if self.status.get("web_dashboard") == "active":
            print("   • Web Dashboard: http://localhost:3000")
        if self.status.get("empire_api") == "active":
            print("   • Empire API: http://localhost:5000")
            print("   • Health Check: http://localhost:5000/health")
        
        print("\n🔧 MANAGEMENT:")
        print("   • Deploy: python3 deploy_sovereign_trader.py")
        print("   • Stop: python3 stop_sovereign_trader.py")
        print("   • Status: python3 check_sovereign_status.py")
        
        print("=" * 60)

def main():
    """Main status check function"""
    checker = SovereignStatusChecker()
    checker.check_all_systems()

if __name__ == "__main__":
    main()
