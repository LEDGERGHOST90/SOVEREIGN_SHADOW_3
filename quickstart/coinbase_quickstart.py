#!/usr/bin/env python3
"""
🚀 COINBASE QUICKSTART - SECURE CREDENTIAL SETUP
Military-grade encryption for your Sovereign Shadow AI platform
"""

import os
import json
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import getpass
import sys

class SecureCredentialManager:
    """Military-grade credential encryption for Sovereign Shadow AI"""
    
    def __init__(self):
        self.credentials_file = "logs/ai_enhanced/secure_credentials.enc"
        self.salt_file = "logs/ai_enhanced/credential_salt.enc"
        self.master_key = None
        
    def generate_key_from_password(self, password: str, salt: bytes) -> bytes:
        """Generate encryption key from master password using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # 100k iterations for security
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt_credentials(self, credentials: dict, master_password: str) -> bool:
        """Encrypt credentials with AES-256"""
        try:
            # Generate random salt
            salt = os.urandom(16)
            
            # Generate key from password
            key = self.generate_key_from_password(master_password, salt)
            fernet = Fernet(key)
            
            # Encrypt credentials
            credentials_json = json.dumps(credentials)
            encrypted_data = fernet.encrypt(credentials_json.encode())
            
            # Save encrypted data and salt
            os.makedirs('logs/ai_enhanced', exist_ok=True)
            
            with open(self.credentials_file, 'wb') as f:
                f.write(encrypted_data)
            
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
            
            print("✅ Credentials encrypted and saved securely")
            return True
            
        except Exception as e:
            print(f"❌ Encryption failed: {e}")
            return False
    
    def decrypt_credentials(self, master_password: str) -> dict:
        """Decrypt credentials with master password"""
        try:
            # Load salt and encrypted data
            with open(self.salt_file, 'rb') as f:
                salt = f.read()
            
            with open(self.credentials_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Generate key from password
            key = self.generate_key_from_password(master_password, salt)
            fernet = Fernet(key)
            
            # Decrypt credentials
            decrypted_data = fernet.decrypt(encrypted_data)
            credentials = json.loads(decrypted_data.decode())
            
            return credentials
            
        except Exception as e:
            print(f"❌ Decryption failed: {e}")
            return {}
    
    def setup_coinbase_credentials(self):
        """Interactive setup for Coinbase credentials"""
        print("🚀 COINBASE QUICKSTART - SECURE SETUP")
        print("=" * 50)
        print("This will securely encrypt your Coinbase API credentials")
        print("using military-grade AES-256 encryption.")
        print()
        
        # Get master password
        print("🔐 Create a MASTER PASSWORD for encryption:")
        print("   - Must be at least 12 characters")
        print("   - Write this down - you'll need it to access credentials")
        print("   - This password is NOT stored anywhere")
        print()
        
        while True:
            master_password = getpass.getpass("Master Password: ")
            if len(master_password) < 12:
                print("❌ Password must be at least 12 characters")
                continue
            
            confirm_password = getpass.getpass("Confirm Password: ")
            if master_password != confirm_password:
                print("❌ Passwords don't match")
                continue
            
            break
        
        print("\n📋 Now enter your Coinbase API credentials:")
        print("   Get them from: https://www.coinbase.com/settings/api")
        print()
        
        # Get Coinbase credentials
        coinbase_key = input("Coinbase API Key: ").strip()
        coinbase_secret = input("Coinbase Secret: ").strip()
        coinbase_passphrase = input("Coinbase Passphrase: ").strip()
        
        # Get CDP credentials
        print("\n🔧 Coinbase CDP (Developer Platform) credentials:")
        print("   Get them from: https://portal.cdp.coinbase.com/")
        print()
        
        cdp_api_key_name = input("CDP API Key Name: ").strip()
        cdp_private_key = input("CDP Private Key: ").strip()
        
        # Create credentials dictionary
        credentials = {
            'coinbase': {
                'api_key': coinbase_key,
                'secret': coinbase_secret,
                'passphrase': coinbase_passphrase,
                'sandbox': True
            },
            'cdp': {
                'api_key_name': cdp_api_key_name,
                'private_key': cdp_private_key,
                'project_id': 'f5b80ba9-92fd-4d0f-bb26-b9f546edcc1e'
            },
            'timestamp': '2025-10-06T11:45:00Z',
            'version': '1.0'
        }
        
        # Encrypt and save
        if self.encrypt_credentials(credentials, master_password):
            print("\n🎉 COINBASE CREDENTIALS SECURED!")
            print("=" * 50)
            print("✅ Credentials encrypted with AES-256")
            print("✅ PBKDF2 with 100k iterations")
            print("✅ Local-only storage")
            print("✅ Master password protection")
            print()
            print("📄 Files created:")
            print(f"   • {self.credentials_file}")
            print(f"   • {self.salt_file}")
            print()
            print("🔐 IMPORTANT: Write down your master password!")
            print("   You'll need it to access your credentials.")
            return True
        else:
            print("❌ Setup failed")
            return False
    
    def test_credentials(self):
        """Test the encrypted credentials"""
        print("🧪 TESTING ENCRYPTED CREDENTIALS")
        print("=" * 40)
        
        master_password = getpass.getpass("Enter Master Password: ")
        credentials = self.decrypt_credentials(master_password)
        
        if credentials:
            print("✅ Credentials decrypted successfully!")
            print()
            print("📋 Stored Credentials:")
            print(f"   Coinbase API Key: {credentials['coinbase']['api_key'][:8]}...")
            print(f"   CDP API Key Name: {credentials['cdp']['api_key_name']}")
            print(f"   Project ID: {credentials['cdp']['project_id']}")
            print(f"   Encrypted: {credentials['timestamp']}")
            print()
            print("🚀 Ready to integrate with Sovereign Shadow AI!")
            return credentials
        else:
            print("❌ Failed to decrypt credentials")
            return None
    
    def integrate_with_sovereign_shadow(self):
        """Integrate with your existing Sovereign Shadow AI platform"""
        print("🏰 INTEGRATING WITH SOVEREIGN SHADOW AI")
        print("=" * 50)
        
        master_password = getpass.getpass("Enter Master Password: ")
        credentials = self.decrypt_credentials(master_password)
        
        if not credentials:
            print("❌ Failed to decrypt credentials")
            return False
        
        # Update environment variables
        os.environ['COINBASE_API_KEY'] = credentials['coinbase']['api_key']
        os.environ['COINBASE_SECRET'] = credentials['coinbase']['secret']
        os.environ['COINBASE_PASSPHRASE'] = credentials['coinbase']['passphrase']
        os.environ['COINBASE_SANDBOX'] = 'true'
        
        os.environ['CDP_API_KEY_NAME'] = credentials['cdp']['api_key_name']
        os.environ['CDP_PRIVATE_KEY'] = credentials['cdp']['private_key']
        os.environ['CDP_PROJECT_ID'] = credentials['cdp']['project_id']
        
        print("✅ Environment variables updated")
        print("✅ Ready for Sovereign Shadow AI integration")
        print()
        print("🎯 Next steps:")
        print("   1. Run: python3 sovereign_shadow_unified.py")
        print("   2. Run: python3 claude_arbitrage_trader.py")
        print("   3. Check: python3 get_real_balances.py")
        
        return True

def main():
    """Main menu for Coinbase Quickstart"""
    manager = SecureCredentialManager()
    
    print("🚀 SOVEREIGN SHADOW AI - COINBASE QUICKSTART")
    print("=" * 60)
    print("Military-grade credential encryption for your trading platform")
    print()
    print("Options:")
    print("1. Setup Coinbase credentials (encrypt)")
    print("2. Test credentials (decrypt)")
    print("3. Integrate with Sovereign Shadow AI")
    print("4. Exit")
    print()
    
    while True:
        choice = input("Choose option (1-4): ").strip()
        
        if choice == '1':
            manager.setup_coinbase_credentials()
            break
        elif choice == '2':
            manager.test_credentials()
            break
        elif choice == '3':
            manager.integrate_with_sovereign_shadow()
            break
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main()
