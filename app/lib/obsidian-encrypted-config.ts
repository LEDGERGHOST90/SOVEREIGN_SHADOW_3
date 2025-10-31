/**
 * 🔒 OBSIDIAN ENCRYPTED CONFIG LOADER
 * =============================================================================
 * Loads encrypted API keys from Obsidian vault for secure application use
 */

import { execSync } from 'child_process';
import { existsSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

export interface EncryptedConfig {
  // Exchange APIs
  BINANCE_US_API_KEY?: string;
  BINANCE_US_SECRET?: string;
  OKX_API_KEY?: string;
  OKX_SECRET?: string;
  OKX_PASSPHRASE?: string;
  KRAKEN_API_KEY?: string;
  KRAKEN_SECRET?: string;
  COINBASE_ORGANIZATION_ID?: string;
  COINBASE_API_KEY?: string;
  COINBASE_API_SECRET?: string;
  
  // AI Services
  CLAUDE_API_KEY?: string;
  OPENAI_API_KEY?: string;
  OPENAI_API_BASE?: string;
  OPENAI_MODEL?: string;
  
  // Infrastructure
  DATABASE_URL?: string;
  REDIS_URL?: string;
  NEXTAUTH_URL?: string;
  NEXTAUTH_SECRET?: string;
  
  // Security
  ENCRYPTION_KEY?: string;
  JWT_SECRET?: string;
  JWT_EXPIRATION?: string;
}

export class ObsidianEncryptedConfig {
  private vaultRoot: string;
  private config: EncryptedConfig = {};
  private loaded = false;

  constructor(vaultPath?: string) {
    this.vaultRoot = vaultPath || join(homedir(), 'Obsidian', 'Sovereign-Shadow-Vault');
  }

  /**
   * Load encrypted configuration from Obsidian vault
   */
  async load(): Promise<EncryptedConfig> {
    if (this.loaded) {
      return this.config;
    }

    try {
      // Check if vault exists
      if (!existsSync(this.vaultRoot)) {
        throw new Error(`Obsidian vault not found at: ${this.vaultRoot}`);
      }

      // Check if encryption script exists
      const encryptScript = join(this.vaultRoot, 'decrypt-with-passphrase.sh');
      if (!existsSync(encryptScript)) {
        throw new Error(`Encryption script not found at: ${encryptScript}`);
      }

      console.log('🔓 Loading encrypted configuration from Obsidian vault...');

      // Execute the decryption script and capture output
      const result = execSync(encryptScript, { 
        cwd: this.vaultRoot,
        encoding: 'utf8',
        timeout: 30000 // 30 second timeout
      });

      console.log('✅ Configuration decrypted successfully');

      // Load the configuration
      await this.parseDecryptedFiles();
      
      this.loaded = true;
      console.log('📊 Loaded encrypted configuration variables');
      
      return this.config;

    } catch (error) {
      console.error('❌ Failed to load encrypted configuration:', error);
      throw error;
    }
  }

  /**
   * Parse decrypted files and extract configuration
   */
  private async parseDecryptedFiles(): Promise<void> {
    const secretsDir = join(this.vaultRoot, 'API-Secrets');
    
    // Parse Exchange APIs
    const exchangeFile = join(secretsDir, 'Exchange-APIs.md');
    if (existsSync(exchangeFile)) {
      this.parseMarkdownFile(exchangeFile);
    }

    // Parse AI Services
    const aiFile = join(secretsDir, 'AI-Services.md');
    if (existsSync(aiFile)) {
      this.parseMarkdownFile(aiFile);
    }

    // Parse Infrastructure
    const infraFile = join(secretsDir, 'Infrastructure.md');
    if (existsSync(infraFile)) {
      this.parseMarkdownFile(infraFile);
    }
  }

  /**
   * Parse markdown file and extract key-value pairs
   */
  private parseMarkdownFile(filePath: string): void {
    const fs = require('fs');
    const content = fs.readFileSync(filePath, 'utf8');
    
    // Extract key-value pairs from markdown
    const lines = content.split('\n');
    let currentKey = '';
    let currentValue = '';
    let inCodeBlock = false;

    for (const line of lines) {
      // Check for code blocks
      if (line.trim().startsWith('```')) {
        inCodeBlock = !inCodeBlock;
        continue;
      }

      // Skip non-code block lines
      if (!inCodeBlock) continue;

      // Parse key-value pairs
      const keyValueMatch = line.match(/^([A-Z_]+):\s*(.*)$/);
      if (keyValueMatch) {
        // Save previous key-value if exists
        if (currentKey && currentValue) {
          this.config[currentKey as keyof EncryptedConfig] = currentValue.trim();
        }
        
        currentKey = keyValueMatch[1];
        currentValue = keyValueMatch[2];
      } else if (line.trim() && currentKey) {
        // Multi-line value (like EC private keys)
        currentValue += '\n' + line;
      }
    }

    // Save last key-value
    if (currentKey && currentValue) {
      this.config[currentKey as keyof EncryptedConfig] = currentValue.trim();
    }
  }

  /**
   * Get specific configuration value
   */
  get(key: keyof EncryptedConfig): string | undefined {
    if (!this.loaded) {
      throw new Error('Configuration not loaded. Call load() first.');
    }
    return this.config[key];
  }

  /**
   * Get all configuration
   */
  getAll(): EncryptedConfig {
    if (!this.loaded) {
      throw new Error('Configuration not loaded. Call load() first.');
    }
    return { ...this.config };
  }

  /**
   * Re-encrypt the vault (clean up decrypted files)
   */
  async reEncrypt(): Promise<void> {
    try {
      const encryptScript = join(this.vaultRoot, 'encrypt-with-passphrase.sh');
      execSync(encryptScript, { 
        cwd: this.vaultRoot,
        timeout: 30000
      });
      console.log('🔒 Vault re-encrypted successfully');
    } catch (error) {
      console.error('❌ Failed to re-encrypt vault:', error);
      throw error;
    }
  }

  /**
   * Check if vault is properly configured
   */
  static async validateVault(vaultPath?: string): Promise<boolean> {
    const vaultRoot = vaultPath || join(homedir(), 'Obsidian', 'Sovereign-Shadow-Vault');
    
    const requiredPaths = [
      vaultRoot,
      join(vaultRoot, 'Encrypted'),
      join(vaultRoot, 'encrypt-with-passphrase.sh'),
      join(vaultRoot, 'decrypt-with-passphrase.sh')
    ];

    return requiredPaths.every(path => existsSync(path));
  }
}

// Export singleton instance
export const obsidianConfig = new ObsidianEncryptedConfig();

// Helper function to load configuration
export async function loadEncryptedConfig(): Promise<EncryptedConfig> {
  return await obsidianConfig.load();
}

// Helper function to validate vault
export async function validateObsidianVault(): Promise<boolean> {
  return await ObsidianEncryptedConfig.validateVault();
}
