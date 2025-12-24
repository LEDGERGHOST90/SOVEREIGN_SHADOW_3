#!/bin/bash
# =============================================================================
# 🔒 LOAD ENCRYPTED ENVIRONMENT FROM OBSIDIAN VAULT
# =============================================================================
# This script loads encrypted API keys from Obsidian vault into environment
# variables for use by applications

set -euo pipefail

# Configuration
VAULT_ROOT="$HOME/Obsidian/Sovereign-Shadow-Vault"
ENCRYPTED_DIR="$VAULT_ROOT/Encrypted"
TEMP_DIR=$(mktemp -d)
PASSPHRASE="SovereignShadow2024!UltraSecure"

# Cleanup function
cleanup() {
    echo "🧹 Cleaning up temporary files..."
    if command -v shred >/dev/null 2>&1; then
        find "$TEMP_DIR" -type f -exec shred -u {} \; 2>/dev/null || true
    fi
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

echo "🔓 Loading encrypted environment from Obsidian vault..."

# Check if vault exists
if [ ! -d "$VAULT_ROOT" ]; then
    echo "❌ Obsidian vault not found at: $VAULT_ROOT"
    echo "Run: ./scripts/create-obsidian-encrypted-vault.sh"
    exit 1
fi

# Decrypt secrets to temporary directory
find "$ENCRYPTED_DIR" -name "*.gpg" -type f | while read -r file; do
    filename=$(basename "$file" .gpg)
    temp_file="$TEMP_DIR/${filename}.md"
    
    echo "Decrypting: $filename"
    if echo "$PASSPHRASE" | gpg -d --quiet --batch --yes --passphrase-fd 0 -o "$temp_file" "$file"; then
        echo "✅ Decrypted: $filename"
    else
        echo "❌ Failed to decrypt: $filename"
        exit 1
    fi
done

# Create environment file
ENV_FILE="$TEMP_DIR/loaded.env"
echo "# =============================================================================" > "$ENV_FILE"
echo "# ENCRYPTED ENVIRONMENT VARIABLES FROM OBSIDIAN VAULT" >> "$ENV_FILE"
echo "# Generated: $(date)" >> "$ENV_FILE"
echo "# =============================================================================" >> "$ENV_FILE"
echo "" >> "$ENV_FILE"

# Extract environment variables from decrypted files
find "$TEMP_DIR" -name "*.md" -type f | while read -r file; do
    echo "Processing: $(basename "$file")"
    
    # Extract key-value pairs and convert to env format
    grep -E '^[A-Z_]+: ' "$file" | while IFS=': ' read -r key value; do
        # Clean up the value (remove brackets and extra spaces)
        clean_value=$(echo "$value" | sed 's/\[//g' | sed 's/\]//g' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
        
        # Handle multi-line values (like EC private keys)
        if echo "$clean_value" | grep -q "BEGIN"; then
            echo "# $key (multi-line value)" >> "$ENV_FILE"
            # Extract the entire key block
            awk "/^$key:/,/^-----END/" "$file" | grep -v "^$key:" | sed 's/^/    /' >> "$ENV_FILE"
            echo "export ${key}=\"\$(${key}_CONTENT)\"" >> "$ENV_FILE"
            echo "" >> "$ENV_FILE"
        else
            echo "export $key=\"$clean_value\"" >> "$ENV_FILE"
        fi
    done
done

# Source the environment file
echo "📋 Loading environment variables..."
source "$ENV_FILE"

# Export key variables for immediate use
export OBSIDIAN_VAULT_LOADED="true"
export VAULT_LOAD_TIME="$(date)"

echo "✅ Environment variables loaded from encrypted Obsidian vault"
echo "🔒 All temporary files will be securely deleted"
echo ""
echo "📊 Loaded variables:"
echo "  - Exchange API Keys: Binance, OKX, Kraken, Coinbase"
echo "  - AI Services: Claude, OpenAI"
echo "  - Infrastructure: Database, Redis, NextAuth"
echo "  - Security Keys: Encryption, JWT"
echo ""
echo "⚠️  Security: All decrypted data will be cleaned up automatically"
