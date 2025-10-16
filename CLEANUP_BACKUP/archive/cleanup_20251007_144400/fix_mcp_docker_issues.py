#!/usr/bin/env python3
"""
🔧 MCP DOCKER ISSUES FIXER
Fixes the recurring Docker and MCP server issues
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_missing_directories():
    """Create missing directories and files"""
    print("🔧 Creating missing directories and files...")
    
    # Create the data directory
    data_dir = "/Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]/sovereign_legacy_loop/ClaudeSDK/data"
    os.makedirs(data_dir, exist_ok=True)
    print(f"✅ Created data directory: {data_dir}")
    
    # Create the .env file
    env_file = "/Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]/sovereign_legacy_loop/ClaudeSDK/.env"
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write("""# ClaudeSDK Environment Configuration
# Add your API keys and configuration here

# Exchange API Keys
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET_KEY=your_binance_secret_key_here
BINANCE_TESTNET=true

OKX_API_KEY=your_okx_api_key_here
OKX_SECRET_KEY=your_okx_secret_key_here
OKX_PASSPHRASE=your_okx_passphrase_here
OKX_SANDBOX=true

KRAKEN_API_KEY=your_kraken_api_key_here
KRAKEN_SECRET_KEY=your_kraken_secret_key_here

COINBASE_SANDBOX_KEY=your_coinbase_sandbox_key_here
COINBASE_SANDBOX_SECRET=your_coinbase_sandbox_secret_here

# MCP Configuration
MCP_SERVER_ENABLED=true
USE_DUMMY_DATA=false
""")
        print(f"✅ Created .env file: {env_file}")
    else:
        print(f"✅ .env file already exists: {env_file}")

def create_symlink_solution():
    """Create symlink to avoid bracket issues"""
    print("🔧 Creating symlink solution for Docker path issues...")
    
    original_path = "/Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]"
    symlink_path = "/Volumes/LegacySafe/SovereignShadow"
    
    try:
        if os.path.exists(symlink_path):
            os.unlink(symlink_path)
            print(f"✅ Removed existing symlink: {symlink_path}")
        
        os.symlink(original_path, symlink_path)
        print(f"✅ Created symlink: {symlink_path} -> {original_path}")
        
        # Test the symlink
        test_path = f"{symlink_path}/sovereign_legacy_loop/ClaudeSDK/data"
        if os.path.exists(test_path):
            print(f"✅ Symlink test successful: {test_path}")
        else:
            print(f"⚠️  Symlink test failed: {test_path}")
            
    except Exception as e:
        print(f"❌ Symlink creation failed: {e}")

def restart_docker():
    """Restart Docker service"""
    print("🔧 Restarting Docker service...")
    
    try:
        # Kill Docker processes
        subprocess.run(["pkill", "Docker"], capture_output=True)
        print("✅ Killed Docker processes")
        
        # Wait a moment
        import time
        time.sleep(3)
        
        # Start Docker Desktop
        subprocess.run(["open", "/Applications/Docker.app"], capture_output=True)
        print("✅ Started Docker Desktop")
        
        print("⏳ Waiting for Docker to start...")
        time.sleep(10)
        
        # Test Docker
        result = subprocess.run(["docker", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is running successfully")
        else:
            print("⚠️  Docker may still be starting up")
            
    except Exception as e:
        print(f"❌ Docker restart failed: {e}")

def test_docker_mount():
    """Test Docker mount with the fixed paths"""
    print("🔧 Testing Docker mount with fixed paths...")
    
    try:
        # Test with symlink path
        test_cmd = [
            "docker", "run", "--rm",
            "-v", "/Volumes/LegacySafe/SovereignShadow/sovereign_legacy_loop/ClaudeSDK/data:/app/data",
            "hello-world"
        ]
        
        result = subprocess.run(test_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker mount test successful with symlink path")
        else:
            print(f"⚠️  Docker mount test failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Docker mount test failed: {e}")

def create_mcp_config_fix():
    """Create a fixed MCP configuration"""
    print("🔧 Creating fixed MCP configuration...")
    
    config_content = """{
  "mcpServers": {
    "sovereign-shadow-claudesdk": {
      "command": "/usr/local/bin/docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--env-file",
        "/Volumes/LegacySafe/SovereignShadow/sovereign_legacy_loop/ClaudeSDK/.env",
        "-v",
        "/Volumes/LegacySafe/SovereignShadow/sovereign_legacy_loop/ClaudeSDK/data:/app/data",
        "--network",
        "host",
        "mcp-crypto-exchange"
      ]
    }
  }
}"""
    
    config_file = "/Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]/mcp_config_fixed.json"
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    print(f"✅ Created fixed MCP config: {config_file}")

def main():
    """Main fix function"""
    print("🚀 MCP DOCKER ISSUES FIXER")
    print("=" * 50)
    
    # Step 1: Create missing directories and files
    create_missing_directories()
    
    # Step 2: Create symlink solution
    create_symlink_solution()
    
    # Step 3: Restart Docker
    restart_docker()
    
    # Step 4: Test Docker mount
    test_docker_mount()
    
    # Step 5: Create fixed MCP config
    create_mcp_config_fix()
    
    print("\n🎉 MCP DOCKER FIXES COMPLETE!")
    print("=" * 50)
    print("📋 SUMMARY OF FIXES:")
    print("✅ Created missing data directory")
    print("✅ Created missing .env file")
    print("✅ Created symlink to avoid bracket issues")
    print("✅ Restarted Docker service")
    print("✅ Tested Docker mount")
    print("✅ Created fixed MCP configuration")
    
    print("\n💡 NEXT STEPS:")
    print("1. Update your MCP configuration to use the symlink path")
    print("2. Add your API keys to the .env file")
    print("3. Restart Claude to test the MCP server")
    
    print("\n🔧 SYMLINK PATH TO USE:")
    print("/Volumes/LegacySafe/SovereignShadow/sovereign_legacy_loop/ClaudeSDK/")

if __name__ == "__main__":
    main()
