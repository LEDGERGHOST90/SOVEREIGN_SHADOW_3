#!/bin/bash
# =============================================================================
# 🔒 OBSIDIAN ENCRYPTED VAULT CREATOR
# =============================================================================
# Creates encrypted storage for all API keys using Obsidian + GPG
# This ensures maximum security for your sensitive credentials

set -euo pipefail

# Configuration
VAULT_ROOT="$HOME/Obsidian/Sovereign-Shadow-Vault"
SECRETS_DIR="$VAULT_ROOT/API-Secrets"
ENCRYPTED_DIR="$VAULT_ROOT/Encrypted"
TEMPLATES_DIR="$VAULT_ROOT/Templates"

echo "🔒 CREATING OBSIDIAN ENCRYPTED VAULT FOR API KEYS"
echo "=================================================="

# Create directory structure
mkdir -p "$VAULT_ROOT"
mkdir -p "$SECRETS_DIR"
mkdir -p "$ENCRYPTED_DIR"
mkdir -p "$TEMPLATES_DIR"
mkdir -p "$VAULT_ROOT/.obsidian"

echo "✅ Created vault structure at: $VAULT_ROOT"

# Create Obsidian vault configuration
cat > "$VAULT_ROOT/.obsidian/app.json" << 'EOF'
{
  "legacyEditor": false,
  "livePreview": true
}
EOF

cat > "$VAULT_ROOT/.obsidian/core-plugins.json" << 'EOF'
{
  "file-explorer": true,
  "global-search": true,
  "switcher": true,
  "graph": true,
  "backlink": true,
  "canvas": true,
  "outgoing-link": true,
  "tag-pane": true,
  "page-preview": true,
  "daily-notes": true,
  "templates": true,
  "note-composer": true,
  "command-palette": true,
  "slash-command": true,
  "editor-status": true,
  "markdown-importer": true,
  "zk-prefixer": true,
  "random-note": true,
  "outline": true,
  "word-count": true,
  "slides": true,
  "audio-recorder": true,
  "workspaces": true,
  "file-recovery": true,
  "publish": false,
  "sync": false
}
EOF

echo "✅ Configured Obsidian vault"

# Create API key templates (these will be encrypted)
cat > "$TEMPLATES_DIR/API-Keys-Template.md" << 'EOF'
# 🔑 API Keys Template

## Exchange APIs

### Binance US
```
API_KEY: [YOUR_BINANCE_US_API_KEY]
SECRET: [YOUR_BINANCE_US_SECRET]
```

### OKX
```
API_KEY: [YOUR_OKX_API_KEY]
SECRET: [YOUR_OKX_SECRET]
PASSPHRASE: [YOUR_OKX_PASSPHRASE]
```

### Kraken
```
API_KEY: [YOUR_KRAKEN_API_KEY]
SECRET: [YOUR_KRAKEN_SECRET]
```

### Coinbase
```
ORGANIZATION_ID: [YOUR_COINBASE_ORG_ID]
API_KEY: [YOUR_COINBASE_API_KEY]
SECRET: [YOUR_COINBASE_API_SECRET]
```

## AI Services

### Claude
```
API_KEY: [YOUR_CLAUDE_API_KEY]
```

### OpenAI
```
API_KEY: [YOUR_OPENAI_API_KEY]
```

## Database & Infrastructure

### PostgreSQL
```
HOST: [YOUR_DB_HOST]
PORT: [YOUR_DB_PORT]
DATABASE: [YOUR_DB_NAME]
USERNAME: [YOUR_DB_USER]
PASSWORD: [YOUR_DB_PASSWORD]
```

### Redis
```
HOST: [YOUR_REDIS_HOST]
PORT: [YOUR_REDIS_PORT]
PASSWORD: [YOUR_REDIS_PASSWORD]
```

## Security Keys

### Encryption
```
MASTER_KEY: [YOUR_MASTER_ENCRYPTION_KEY]
SALT: [YOUR_ENCRYPTION_SALT]
JWT_SECRET: [YOUR_JWT_SECRET]
```

---

⚠️ **SECURITY NOTICE**: This file contains sensitive information. 
It should be encrypted using GPG before storage.
EOF

echo "✅ Created API keys template"

# Create encryption script
cat > "$VAULT_ROOT/encrypt-secrets.sh" << 'EOF'
#!/bin/bash
# Encrypt all API key files in the vault

set -euo pipefail

VAULT_ROOT="$(dirname "$0")"
SECRETS_DIR="$VAULT_ROOT/API-Secrets"
ENCRYPTED_DIR="$VAULT_ROOT/Encrypted"

echo "🔒 ENCRYPTING API SECRETS IN OBSIDIAN VAULT"

# Create encrypted directory if it doesn't exist
mkdir -p "$ENCRYPTED_DIR"

# Find all markdown files in secrets directory
find "$SECRETS_DIR" -name "*.md" -type f | while read -r file; do
    filename=$(basename "$file" .md)
    encrypted_file="$ENCRYPTED_DIR/${filename}.gpg"
    
    echo "Encrypting: $filename"
    
    # Encrypt with GPG (symmetric encryption)
    if gpg -c --cipher-algo AES256 --symmetric --armor -o "$encrypted_file" "$file"; then
        # Securely delete original
        if command -v shred >/dev/null 2>&1; then
            shred -u "$file"
        else
            rm -f "$file"
        fi
        echo "✅ Encrypted and secured: $filename"
    else
        echo "❌ Failed to encrypt: $filename"
        exit 1
    fi
done

echo "🔒 All secrets encrypted successfully!"
echo "📁 Encrypted files stored in: $ENCRYPTED_DIR"
EOF

chmod +x "$VAULT_ROOT/encrypt-secrets.sh"

# Create decryption script
cat > "$VAULT_ROOT/decrypt-secrets.sh" << 'EOF'
#!/bin/bash
# Decrypt API key files for temporary access

set -euo pipefail

VAULT_ROOT="$(dirname "$0")"
SECRETS_DIR="$VAULT_ROOT/API-Secrets"
ENCRYPTED_DIR="$VAULT_ROOT/Encrypted"

echo "🔓 DECRYPTING API SECRETS (TEMPORARY ACCESS)"

# Create secrets directory if it doesn't exist
mkdir -p "$SECRETS_DIR"

# Find all encrypted files
find "$ENCRYPTED_DIR" -name "*.gpg" -type f | while read -r file; do
    filename=$(basename "$file" .gpg)
    decrypted_file="$SECRETS_DIR/${filename}.md"
    
    echo "Decrypting: $filename"
    
    # Decrypt with GPG
    if gpg -d --quiet -o "$decrypted_file" "$file"; then
        echo "✅ Decrypted: $filename"
    else
        echo "❌ Failed to decrypt: $filename"
        exit 1
    fi
done

echo "🔓 All secrets decrypted for temporary access!"
echo "⚠️  Remember to re-encrypt when done: ./encrypt-secrets.sh"
EOF

chmod +x "$VAULT_ROOT/decrypt-secrets.sh"

# Create vault index
cat > "$VAULT_ROOT/README.md" << 'EOF'
# 🔒 Sovereign Shadow AI - Encrypted Vault

This Obsidian vault contains encrypted API keys and sensitive configuration data for the Sovereign Shadow AI system.

## 🔐 Security Features

- **GPG Encryption**: All API keys encrypted with AES-256
- **Obsidian Integration**: Secure note-taking and organization
- **Temporary Access**: Decrypt only when needed, re-encrypt immediately
- **Secure Deletion**: Original files securely deleted after encryption

## 📁 Directory Structure

```
Sovereign-Shadow-Vault/
├── API-Secrets/          # Temporary decrypted files (use only when needed)
├── Encrypted/           # Permanently encrypted .gpg files
├── Templates/           # Templates for new API keys
├── encrypt-secrets.sh   # Script to encrypt all secrets
├── decrypt-secrets.sh   # Script to decrypt secrets (temporary)
└── README.md           # This file
```

## 🚀 Usage

### To Decrypt API Keys (Temporary Access):
```bash
cd "$HOME/Obsidian/Sovereign-Shadow-Vault"
./decrypt-secrets.sh
```

### To Re-encrypt API Keys (After Use):
```bash
cd "$HOME/Obsidian/Sovereign-Shadow-Vault"
./encrypt-secrets.sh
```

### To Add New API Keys:
1. Copy template from `Templates/API-Keys-Template.md`
2. Create new file in `API-Secrets/` with your keys
3. Run `./encrypt-secrets.sh` to encrypt

## ⚠️ Security Warnings

- **NEVER** commit decrypted files to git
- **ALWAYS** re-encrypt after use
- **KEEP** your GPG passphrase secure
- **BACKUP** encrypted files only

## 🔑 GPG Setup

If you haven't set up GPG yet:

```bash
# Generate GPG key
gpg --full-generate-key

# Or use existing key
gpg --list-keys
```

## 📝 Integration with Applications

Applications should:
1. Decrypt secrets temporarily when starting
2. Load environment variables from decrypted files
3. Re-encrypt secrets after loading
4. Never store decrypted data permanently
EOF

echo "✅ Created vault documentation"

# Create environment loader script
cat > "$VAULT_ROOT/load-env.sh" << 'EOF'
#!/bin/bash
# Load environment variables from encrypted Obsidian vault

set -euo pipefail

VAULT_ROOT="$(dirname "$0")"
TEMP_DIR=$(mktemp -d)

# Cleanup function
cleanup() {
    echo "🧹 Cleaning up temporary files..."
    if command -v shred >/dev/null 2>&1; then
        find "$TEMP_DIR" -type f -exec shred -u {} \;
    else
        rm -rf "$TEMP_DIR"
    fi
}
trap cleanup EXIT

echo "🔓 Loading environment from encrypted vault..."

# Decrypt secrets to temporary directory
find "$VAULT_ROOT/Encrypted" -name "*.gpg" -type f | while read -r file; do
    filename=$(basename "$file" .gpg)
    temp_file="$TEMP_DIR/${filename}.md"
    
    echo "Decrypting: $filename"
    gpg -d --quiet -o "$temp_file" "$file"
done

# Extract environment variables and export them
find "$TEMP_DIR" -name "*.md" -type f | while read -r file; do
    echo "Loading variables from: $(basename "$file")"
    
    # Extract key-value pairs and export them
    grep -E '^[A-Z_]+: ' "$file" | while IFS=': ' read -r key value; do
        # Remove brackets and export
        clean_value=$(echo "$value" | sed 's/\[//g' | sed 's/\]//g')
        export "$key"="$clean_value"
        echo "  Exported: $key"
    done
done

echo "✅ Environment variables loaded from encrypted vault"
echo "⚠️  Remember: These are temporary and will be cleaned up on exit"
EOF

chmod +x "$VAULT_ROOT/load-env.sh"

echo ""
echo "🎉 OBSIDIAN ENCRYPTED VAULT CREATED SUCCESSFULLY!"
echo "=================================================="
echo "📍 Vault Location: $VAULT_ROOT"
echo ""
echo "🚀 Next Steps:"
echo "1. Copy your API keys to: $SECRETS_DIR/"
echo "2. Run: $VAULT_ROOT/encrypt-secrets.sh"
echo "3. Open vault in Obsidian: $VAULT_ROOT"
echo ""
echo "🔒 Security: All API keys will be encrypted with GPG AES-256"
