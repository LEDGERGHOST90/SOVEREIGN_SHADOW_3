import jwt from 'jsonwebtoken';
import { NextRequest } from 'next/server';

export interface SessionConfig {
  jwtTokens: boolean;
  refreshInterval: number; // in hours
  autoRefresh: boolean;
  securityLevel: 'high' | 'medium' | 'low';
  multiFactor: boolean;
}

export interface UserSession {
  userId: string;
  email: string;
  role: 'admin' | 'trader' | 'viewer';
  permissions: string[];
  lastLogin: string;
  sessionId: string;
  mfaVerified: boolean;
  securityLevel: string;
}

export interface TokenPair {
  accessToken: string;
  refreshToken: string;
  expiresAt: string;
  refreshExpiresAt: string;
}

export class SessionManager {
  private config: SessionConfig;
  private activeSessions: Map<string, UserSession> = new Map();
  private refreshTokens: Map<string, { userId: string; expiresAt: number }> = new Map();
  private jwtSecret: string;

  constructor() {
    this.jwtSecret = process.env.JWT_SECRET || 'sovereign-shadow-ai-secret-key-2024';
    
    this.config = {
      jwtTokens: true,
      refreshInterval: 24, // 24 hours
      autoRefresh: true,
      securityLevel: 'high',
      multiFactor: true
    };

    // Start cleanup process for expired sessions
    this.startSessionCleanup();
  }

  // Create new session with JWT tokens
  createSession(userData: {
    userId: string;
    email: string;
    role: 'admin' | 'trader' | 'viewer';
    permissions?: string[];
    mfaVerified?: boolean;
  }): TokenPair {
    const sessionId = this.generateSessionId();
    const now = Date.now();
    const accessExpires = now + (this.config.refreshInterval * 60 * 60 * 1000); // 24 hours
    const refreshExpires = now + (7 * 24 * 60 * 60 * 1000); // 7 days

    const session: UserSession = {
      userId: userData.userId,
      email: userData.email,
      role: userData.role,
      permissions: userData.permissions || this.getDefaultPermissions(userData.role),
      lastLogin: new Date().toISOString(),
      sessionId,
      mfaVerified: userData.mfaVerified || false,
      securityLevel: this.config.securityLevel
    };

    // Create JWT tokens
    const accessToken = jwt.sign(
      {
        userId: userData.userId,
        email: userData.email,
        role: userData.role,
        sessionId,
        permissions: session.permissions,
        mfaVerified: session.mfaVerified,
        type: 'access'
      },
      this.jwtSecret,
      { expiresIn: `${this.config.refreshInterval}h` }
    );

    const refreshToken = jwt.sign(
      {
        userId: userData.userId,
        sessionId,
        type: 'refresh'
      },
      this.jwtSecret,
      { expiresIn: '7d' }
    );

    // Store session and refresh token
    this.activeSessions.set(sessionId, session);
    this.refreshTokens.set(refreshToken, {
      userId: userData.userId,
      expiresAt: refreshExpires
    });

    console.log(`✅ New session created for ${userData.email} (${userData.role})`);

    return {
      accessToken,
      refreshToken,
      expiresAt: new Date(accessExpires).toISOString(),
      refreshExpiresAt: new Date(refreshExpires).toISOString()
    };
  }

  // Validate access token
  validateToken(token: string): {
    valid: boolean;
    session?: UserSession;
    error?: string;
  } {
    try {
      const decoded = jwt.verify(token, this.jwtSecret) as any;
      
      if (decoded.type !== 'access') {
        return { valid: false, error: 'Invalid token type' };
      }

      const session = this.activeSessions.get(decoded.sessionId);
      if (!session) {
        return { valid: false, error: 'Session not found' };
      }

      // Check if session is still valid
      if (Date.now() > new Date(decoded.exp * 1000).getTime()) {
        return { valid: false, error: 'Token expired' };
      }

      // Update last activity
      session.lastLogin = new Date().toISOString();

      return { valid: true, session };
    } catch (error) {
      return { valid: false, error: 'Invalid token' };
    }
  }

  // Refresh access token using refresh token
  refreshAccessToken(refreshToken: string): {
    success: boolean;
    tokens?: TokenPair;
    error?: string;
  } {
    try {
      const decoded = jwt.verify(refreshToken, this.jwtSecret) as any;
      
      if (decoded.type !== 'refresh') {
        return { success: false, error: 'Invalid refresh token type' };
      }

      const storedRefresh = this.refreshTokens.get(refreshToken);
      if (!storedRefresh) {
        return { success: false, error: 'Refresh token not found' };
      }

      if (Date.now() > storedRefresh.expiresAt) {
        this.refreshTokens.delete(refreshToken);
        return { success: false, error: 'Refresh token expired' };
      }

      const session = this.activeSessions.get(decoded.sessionId);
      if (!session) {
        return { success: false, error: 'Session not found' };
      }

      // Create new access token
      const now = Date.now();
      const accessExpires = now + (this.config.refreshInterval * 60 * 60 * 1000);

      const newAccessToken = jwt.sign(
        {
          userId: session.userId,
          email: session.email,
          role: session.role,
          sessionId: session.sessionId,
          permissions: session.permissions,
          mfaVerified: session.mfaVerified,
          type: 'access'
        },
        this.jwtSecret,
        { expiresIn: `${this.config.refreshInterval}h` }
      );

      console.log(`🔄 Access token refreshed for ${session.email}`);

      return {
        success: true,
        tokens: {
          accessToken: newAccessToken,
          refreshToken, // Keep the same refresh token
          expiresAt: new Date(accessExpires).toISOString(),
          refreshExpiresAt: new Date(storedRefresh.expiresAt).toISOString()
        }
      };

    } catch (error) {
      return { success: false, error: 'Invalid refresh token' };
    }
  }

  // Extract token from request
  extractTokenFromRequest(request: NextRequest): string | null {
    // Try Authorization header first
    const authHeader = request.headers.get('authorization');
    if (authHeader && authHeader.startsWith('Bearer ')) {
      return authHeader.substring(7);
    }

    // Try cookie
    const tokenCookie = request.cookies.get('access_token')?.value;
    if (tokenCookie) {
      return tokenCookie;
    }

    return null;
  }

  // Middleware function for API routes
  async authenticateRequest(request: NextRequest): Promise<{
    authenticated: boolean;
    session?: UserSession;
    error?: string;
  }> {
    const token = this.extractTokenFromRequest(request);
    
    if (!token) {
      return { authenticated: false, error: 'No token provided' };
    }

    const validation = this.validateToken(token);
    
    if (!validation.valid) {
      return { authenticated: false, error: validation.error };
    }

    return {
      authenticated: true,
      session: validation.session
    };
  }

  // Check permissions
  hasPermission(session: UserSession, requiredPermission: string): boolean {
    if (session.role === 'admin') {
      return true; // Admin has all permissions
    }

    return session.permissions.includes(requiredPermission);
  }

  // Logout session
  logout(sessionId: string): boolean {
    const session = this.activeSessions.get(sessionId);
    if (!session) {
      return false;
    }

    // Remove session and all associated refresh tokens
    this.activeSessions.delete(sessionId);
    
    // Remove all refresh tokens for this session
    for (const [token, data] of this.refreshTokens.entries()) {
      if (data.userId === session.userId) {
        this.refreshTokens.delete(token);
      }
    }

    console.log(`🚪 Session ended for ${session.email}`);
    return true;
  }

  // Get session statistics
  getSessionStats(): {
    activeSessions: number;
    totalRefreshTokens: number;
    sessionsByRole: { [key: string]: number };
    averageSessionAge: number;
  } {
    const sessions = Array.from(this.activeSessions.values());
    const sessionsByRole = sessions.reduce((acc, session) => {
      acc[session.role] = (acc[session.role] || 0) + 1;
      return acc;
    }, {} as { [key: string]: number });

    const now = Date.now();
    const averageSessionAge = sessions.length > 0 
      ? sessions.reduce((sum, session) => {
          return sum + (now - new Date(session.lastLogin).getTime());
        }, 0) / sessions.length / (1000 * 60 * 60) // in hours
      : 0;

    return {
      activeSessions: this.activeSessions.size,
      totalRefreshTokens: this.refreshTokens.size,
      sessionsByRole,
      averageSessionAge: Math.round(averageSessionAge * 100) / 100
    };
  }

  private generateSessionId(): string {
    return `sess_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
  }

  private getDefaultPermissions(role: string): string[] {
    const permissions: { [key: string]: string[] } = {
      admin: ['read', 'write', 'delete', 'trade', 'manage_users', 'system_config'],
      trader: ['read', 'write', 'trade', 'view_portfolio'],
      viewer: ['read', 'view_portfolio']
    };

    return permissions[role] || ['read'];
  }

  private startSessionCleanup(): void {
    // Clean up expired sessions every hour
    setInterval(() => {
      const now = Date.now();
      let cleanedSessions = 0;
      let cleanedTokens = 0;

      // Clean expired refresh tokens
      for (const [token, data] of this.refreshTokens.entries()) {
        if (now > data.expiresAt) {
          this.refreshTokens.delete(token);
          cleanedTokens++;
        }
      }

      // Clean inactive sessions (older than 7 days)
      const sevenDaysAgo = now - (7 * 24 * 60 * 60 * 1000);
      for (const [sessionId, session] of this.activeSessions.entries()) {
        if (new Date(session.lastLogin).getTime() < sevenDaysAgo) {
          this.activeSessions.delete(sessionId);
          cleanedSessions++;
        }
      }

      if (cleanedSessions > 0 || cleanedTokens > 0) {
        console.log(`🧹 Cleaned up ${cleanedSessions} expired sessions and ${cleanedTokens} expired tokens`);
      }
    }, 60 * 60 * 1000); // 1 hour
  }

  // Update configuration
  updateConfig(newConfig: Partial<SessionConfig>): void {
    this.config = { ...this.config, ...newConfig };
    console.log('⚙️ Session configuration updated:', newConfig);
  }

  // Get current configuration
  getConfig(): SessionConfig {
    return { ...this.config };
  }
}

// Export singleton instance
export const sessionManager = new SessionManager();
