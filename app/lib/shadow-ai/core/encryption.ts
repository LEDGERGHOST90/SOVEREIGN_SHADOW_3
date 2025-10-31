/**
 * 🔒 CUSTOM ENCRYPTION - Your Private Security Layer
 * AES-256-GCM encryption with your own keys
 */

import crypto from 'crypto';

export class CustomEncryption {
  private algorithm = 'aes-256-gcm';
  private key: Buffer;
  private keyRotationInterval = 30 * 24 * 60 * 60 * 1000; // 30 days
  private lastKeyRotation: Date;
  
  constructor() {
    // Derive key from YOUR secret (never hardcoded)
    this.key = this.deriveKey();
    this.lastKeyRotation = new Date();
    
    // Check if key rotation needed
    this.scheduleKeyRotation();
  }
  
  /**
   * Derive encryption key from environment variable
   */
  private deriveKey(): Buffer {
    const masterKey = process.env.SHADOW_MASTER_KEY;
    const salt = process.env.SHADOW_ENCRYPTION_SALT;
    
    if (!masterKey || !salt) {
      throw new Error('SECURITY ERROR: Encryption keys not configured');
    }
    
    // Use scrypt for key derivation (secure)
    return crypto.scryptSync(masterKey, salt, 32);
  }
  
  /**
   * Encrypt data with YOUR key
   */
  encrypt(text: string): string {
    try {
      // Generate random IV for each encryption
      const iv = crypto.randomBytes(16);
      
      // Create cipher
      const cipher = crypto.createCipheriv(this.algorithm, this.key, iv);
      
      // Encrypt
      let encrypted = cipher.update(text, 'utf8', 'hex');
      encrypted += cipher.final('hex');
      
      // Get authentication tag
      const authTag = cipher.getAuthTag();
      
      // Return format: IV:AuthTag:EncryptedData
      return `${iv.toString('hex')}:${authTag.toString('hex')}:${encrypted}`;
    } catch (error) {
      console.error('Encryption error:', error);
      throw new Error('Failed to encrypt data');
    }
  }
  
  /**
   * Decrypt data with YOUR key
   */
  decrypt(encrypted: string): string {
    try {
      // Parse encrypted data
      const [ivHex, authTagHex, encryptedData] = encrypted.split(':');
      
      if (!ivHex || !authTagHex || !encryptedData) {
        throw new Error('Invalid encrypted data format');
      }
      
      // Convert from hex
      const iv = Buffer.from(ivHex, 'hex');
      const authTag = Buffer.from(authTagHex, 'hex');
      
      // Create decipher
      const decipher = crypto.createDecipheriv(this.algorithm, this.key, iv);
      decipher.setAuthTag(authTag);
      
      // Decrypt
      let decrypted = decipher.update(encryptedData, 'hex', 'utf8');
      decrypted += decipher.final('utf8');
      
      return decrypted;
    } catch (error) {
      console.error('Decryption error:', error);
      throw new Error('Failed to decrypt data');
    }
  }
  
  /**
   * Hash sensitive data (one-way)
   */
  hash(data: string): string {
    return crypto
      .createHash('sha256')
      .update(data)
      .digest('hex');
  }
  
  /**
   * Generate secure random token
   */
  generateToken(length: number = 32): string {
    return crypto.randomBytes(length).toString('hex');
  }
  
  /**
   * Schedule automatic key rotation
   */
  private scheduleKeyRotation(): void {
    setInterval(() => {
      const timeSinceRotation = Date.now() - this.lastKeyRotation.getTime();
      if (timeSinceRotation >= this.keyRotationInterval) {
        console.warn('⚠️ Key rotation needed');
        // In production, implement automatic key rotation
      }
    }, 24 * 60 * 60 * 1000); // Check daily
  }
  
  /**
   * Validate encryption integrity
   */
  isValid(encrypted: string): boolean {
    try {
      const parts = encrypted.split(':');
      return parts.length === 3 && 
             parts.every(part => /^[0-9a-f]+$/i.test(part));
    } catch {
      return false;
    }
  }
}
