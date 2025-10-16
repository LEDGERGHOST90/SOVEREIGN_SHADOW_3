#!/usr/bin/env python3
"""
🛑 SOVEREIGNSHADOW.AI[LEGACYLOOP] - EMERGENCY SHUTDOWN
Safely stop all trading systems and components
"""

import os
import sys
import signal
import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("sovereign_stopper")

class SovereignTraderStopper:
    def __init__(self):
        self.system_root = Path("/Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]")
        
    def stop_all_systems(self):
        """Stop all SovereignShadow.Ai components"""
        logger.info("🛑 STOPPING SOVEREIGNSHADOW.AI SYSTEMS")
        logger.info("=" * 50)
        
        try:
            # Stop processes by name
            self.stop_processes_by_name()
            
            # Stop processes by port
            self.stop_processes_by_port()
            
            # Clean up any remaining processes
            self.cleanup_remaining_processes()
            
            logger.info("✅ ALL SYSTEMS STOPPED SAFELY")
            
        except Exception as e:
            logger.error(f"❌ Error stopping systems: {e}")
            raise
    
    def stop_processes_by_name(self):
        """Stop processes by name pattern"""
        process_patterns = [
            "enhanced_crypto_empire_server.py",
            "main.py",
            "npm run dev",
            "next dev"
        ]
        
        for pattern in process_patterns:
            try:
                # Find processes matching pattern
                result = subprocess.run(
                    ["pgrep", "-f", pattern],
                    capture_output=True,
                    text=True
                )
                
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid:
                            logger.info(f"🛑 Stopping process {pid} ({pattern})")
                            os.kill(int(pid), signal.SIGTERM)
                            
            except Exception as e:
                logger.warning(f"⚠️ Could not stop {pattern}: {e}")
    
    def stop_processes_by_port(self):
        """Stop processes by port"""
        ports = [3000, 5000, 8000]  # Next.js, Flask, MCP
        
        for port in ports:
            try:
                # Find process using port
                result = subprocess.run(
                    ["lsof", "-ti", f":{port}"],
                    capture_output=True,
                    text=True
                )
                
                if result.stdout.strip():
                    pid = result.stdout.strip()
                    logger.info(f"🛑 Stopping process {pid} on port {port}")
                    os.kill(int(pid), signal.SIGTERM)
                    
            except Exception as e:
                logger.warning(f"⚠️ Could not stop process on port {port}: {e}")
    
    def cleanup_remaining_processes(self):
        """Clean up any remaining processes"""
        logger.info("🧹 Cleaning up remaining processes...")
        
        # Kill any remaining Python processes related to our system
        try:
            subprocess.run(["pkill", "-f", "sovereign"], check=False)
            subprocess.run(["pkill", "-f", "empire"], check=False)
            subprocess.run(["pkill", "-f", "mcp"], check=False)
        except:
            pass

def main():
    """Main stop function"""
    print("🛑 SOVEREIGNSHADOW.AI EMERGENCY SHUTDOWN")
    print("=" * 50)
    
    stopper = SovereignTraderStopper()
    stopper.stop_all_systems()
    
    print("✅ All systems stopped safely")

if __name__ == "__main__":
    main()
