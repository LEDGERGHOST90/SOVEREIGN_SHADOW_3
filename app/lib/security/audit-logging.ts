
/**
 * 📊 COMPREHENSIVE AUDIT LOGGING SYSTEM
 * Enterprise-grade logging for all financial operations
 * Edge Runtime Compatible
 */

import { NextRequest } from 'next/server'

// Simple logger for Edge runtime compatibility
const logger = {
  info: (message: string, meta?: any) => {
    console.log(`[INFO] ${new Date().toISOString()} - ${message}`, meta || '')
  },
  error: (message: string, meta?: any) => {
    console.error(`[ERROR] ${new Date().toISOString()} - ${message}`, meta || '')
  },
  warn: (message: string, meta?: any) => {
    console.warn(`[WARN] ${new Date().toISOString()} - ${message}`, meta || '')
  },
}

// Audit event types
export enum AuditAction {
  // Authentication
  USER_LOGIN = 'USER_LOGIN',
  USER_LOGOUT = 'USER_LOGOUT',
  LOGIN_FAILED = 'LOGIN_FAILED',
  USER_REGISTERED = 'USER_REGISTERED',
  PASSWORD_CHANGED = 'PASSWORD_CHANGED',
  
  // Trading
  TRADE_EXECUTED = 'TRADE_EXECUTED',
  TRADE_FAILED = 'TRADE_FAILED',
  TRADE_CANCELLED = 'TRADE_CANCELLED',
  ORDER_PLACED = 'ORDER_PLACED',
  ORDER_MODIFIED = 'ORDER_MODIFIED',
  
  // Siphon Operations
  SIPHON_EXECUTED = 'SIPHON_EXECUTED',
  SIPHON_FAILED = 'SIPHON_FAILED',
  EMERGENCY_SIPHON = 'EMERGENCY_SIPHON',
  SIPHON_CONFIG_CHANGED = 'SIPHON_CONFIG_CHANGED',
  
  // Vault Operations
  VAULT_TRANSFER = 'VAULT_TRANSFER',
  HOT_TO_COLD = 'HOT_TO_COLD',
  COLD_TO_HOT = 'COLD_TO_HOT',
  VAULT_ACCESS = 'VAULT_ACCESS',
  
  // Portfolio
  PORTFOLIO_SYNC = 'PORTFOLIO_SYNC',
  PORTFOLIO_UPDATED = 'PORTFOLIO_UPDATED',
  PNL_CALCULATED = 'PNL_CALCULATED',
  
  // Security Events
  RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED',
  SUSPICIOUS_ACTIVITY = 'SUSPICIOUS_ACTIVITY',
  INVALID_INPUT = 'INVALID_INPUT',
  UNAUTHORIZED_ACCESS = 'UNAUTHORIZED_ACCESS',
  
  // System Events
  API_ERROR = 'API_ERROR',
  DATABASE_ERROR = 'DATABASE_ERROR',
  EXTERNAL_SERVICE_ERROR = 'EXTERNAL_SERVICE_ERROR',
}

export enum AuditSeverity {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL',
}

interface AuditLogEntry {
  userId?: string
  action: AuditAction
  resource: string
  severity: AuditSeverity
  ipAddress?: string
  userAgent?: string
  timestamp: Date
  metadata: Record<string, any>
  success: boolean
  errorMessage?: string
  requestId?: string
}

class AuditLogger {
  private static instance: AuditLogger
  private requestId: string = ''
  
  public static getInstance(): AuditLogger {
    if (!AuditLogger.instance) {
      AuditLogger.instance = new AuditLogger()
    }
    return AuditLogger.instance
  }

  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  private getClientInfo(request?: NextRequest): { ipAddress: string; userAgent: string } {
    if (!request) {
      return { ipAddress: 'unknown', userAgent: 'unknown' }
    }
    
    const forwarded = request.headers.get('x-forwarded-for')
    const ipAddress = forwarded ? forwarded.split(',')[0] : 'unknown'
    const userAgent = request.headers.get('user-agent') || 'unknown'
    
    return { ipAddress, userAgent }
  }

  private getUserIdFromRequest(request?: NextRequest): string | undefined {
    if (!request) return undefined
    
    try {
      const authHeader = request.headers.get('authorization')
      if (!authHeader) return undefined
      
      const token = authHeader.replace('Bearer ', '')
      const payload = JSON.parse(atob(token.split('.')[1]))
      return payload.sub || payload.userId
    } catch (error) {
      return undefined
    }
  }

  async logAudit(entry: Partial<AuditLogEntry>, request?: NextRequest): Promise<void> {
    try {
      const clientInfo = this.getClientInfo(request)
      const userId = entry.userId || this.getUserIdFromRequest(request)
      
      const auditEntry: AuditLogEntry = {
        userId,
        action: entry.action!,
        resource: entry.resource!,
        severity: entry.severity || AuditSeverity.MEDIUM,
        ipAddress: clientInfo.ipAddress,
        userAgent: clientInfo.userAgent,
        timestamp: new Date(),
        metadata: entry.metadata || {},
        success: entry.success ?? true,
        errorMessage: entry.errorMessage,
        requestId: this.requestId || this.generateRequestId(),
        ...entry,
      }
      
      // Log to console
      const logMethod = auditEntry.severity === AuditSeverity.CRITICAL || auditEntry.severity === AuditSeverity.HIGH 
        ? logger.error 
        : auditEntry.severity === AuditSeverity.MEDIUM 
        ? logger.warn 
        : logger.info
      logMethod('Audit Event', auditEntry)
      
      // Save to database (TODO: Enable when audit log table is fully configured)
      // await prisma.auditLog.create({
      //   data: {
      //     userId: auditEntry.userId,
      //     action: auditEntry.action,
      //     resource: auditEntry.resource,
      //     severity: auditEntry.severity,
      //     ipAddress: auditEntry.ipAddress,
      //     userAgent: auditEntry.userAgent,
      //     metadata: auditEntry.metadata,
      //     success: auditEntry.success,
      //     errorMessage: auditEntry.errorMessage,
      //     requestId: auditEntry.requestId,
      //   },
      // })
      
      // Alert on critical events
      if (auditEntry.severity === AuditSeverity.CRITICAL) {
        await this.sendSecurityAlert(auditEntry)
      }
      
    } catch (error) {
      // Fallback logging if database fails
      logger.error('Failed to save audit log', { error: error, entry })
      console.error('Audit logging failed:', error)
    }
  }

  private async sendSecurityAlert(entry: AuditLogEntry): Promise<void> {
    // In production, this would send alerts to security team
    logger.error('CRITICAL SECURITY EVENT', entry)
    
    // Example: Send to Slack, PagerDuty, etc.
    // await notifySecurityTeam(entry)
  }

  // Convenience methods for common audit events
  async logTradeExecution(userId: string, tradeData: any, success: boolean, request?: NextRequest): Promise<void> {
    await this.logAudit({
      userId,
      action: success ? AuditAction.TRADE_EXECUTED : AuditAction.TRADE_FAILED,
      resource: 'trading/execute',
      severity: success ? AuditSeverity.MEDIUM : AuditSeverity.HIGH,
      metadata: {
        symbol: tradeData.symbol,
        side: tradeData.side,
        quantity: tradeData.quantity,
        orderId: tradeData.orderId,
        executedPrice: tradeData.executedPrice,
      },
      success,
    }, request)
  }

  async logSiphonExecution(userId: string, siphonData: any, success: boolean, request?: NextRequest): Promise<void> {
    await this.logAudit({
      userId,
      action: success ? AuditAction.SIPHON_EXECUTED : AuditAction.SIPHON_FAILED,
      resource: 'siphon/execute',
      severity: success ? AuditSeverity.MEDIUM : AuditSeverity.HIGH,
      metadata: {
        thresholdAmount: siphonData.thresholdAmount,
        siphonedAmount: siphonData.siphonedAmount,
        retainedAmount: siphonData.retainedAmount,
        triggered: siphonData.triggered,
      },
      success,
    }, request)
  }

  async logAuthentication(userId: string, success: boolean, request?: NextRequest): Promise<void> {
    await this.logAudit({
      userId,
      action: success ? AuditAction.USER_LOGIN : AuditAction.LOGIN_FAILED,
      resource: 'auth/login',
      severity: success ? AuditSeverity.LOW : AuditSeverity.MEDIUM,
      metadata: {},
      success,
    }, request)
  }

  async logSecurityEvent(action: AuditAction, severity: AuditSeverity, metadata: any, request?: NextRequest): Promise<void> {
    await this.logAudit({
      action,
      resource: 'security/event',
      severity,
      metadata,
      success: false,
    }, request)
  }

  async logVaultOperation(userId: string, operation: string, amount: number, success: boolean, request?: NextRequest): Promise<void> {
    await this.logAudit({
      userId,
      action: AuditAction.VAULT_TRANSFER,
      resource: 'vault/transfer',
      severity: AuditSeverity.HIGH, // Vault operations are always high severity
      metadata: {
        operation,
        amount,
        timestamp: new Date(),
      },
      success,
    }, request)
  }

  async logRateLimitExceeded(endpoint: string, clientId: string, request?: NextRequest): Promise<void> {
    await this.logAudit({
      action: AuditAction.RATE_LIMIT_EXCEEDED,
      resource: endpoint,
      severity: AuditSeverity.MEDIUM,
      metadata: {
        clientId,
        endpoint,
        timestamp: new Date(),
      },
      success: false,
    }, request)
  }

  setRequestId(requestId: string): void {
    this.requestId = requestId
  }

  // Query audit logs
  async getAuditLogs(filters: {
    userId?: string
    action?: AuditAction
    resource?: string
    startDate?: Date
    endDate?: Date
    severity?: AuditSeverity
    limit?: number
  } = {}): Promise<any[]> {
    const where: any = {}
    
    if (filters.userId) where.userId = filters.userId
    if (filters.action) where.action = filters.action
    if (filters.resource) where.resource = { contains: filters.resource }
    if (filters.severity) where.severity = filters.severity
    
    if (filters.startDate || filters.endDate) {
      where.createdAt = {}
      if (filters.startDate) where.createdAt.gte = filters.startDate
      if (filters.endDate) where.createdAt.lte = filters.endDate
    }
    
    // TODO: Enable when audit log table is configured
    // return prisma.auditLog.findMany({
    //   where,
    //   orderBy: { createdAt: 'desc' },
    //   take: filters.limit || 100,
    // })
    return []
  }

  // Security analytics
  async getSecurityMetrics(timeframe: 'hour' | 'day' | 'week' = 'day'): Promise<any> {
    const now = new Date()
    const startDate = new Date()
    
    switch (timeframe) {
      case 'hour':
        startDate.setHours(now.getHours() - 1)
        break
      case 'day':
        startDate.setDate(now.getDate() - 1)
        break
      case 'week':
        startDate.setDate(now.getDate() - 7)
        break
    }
    
    // TODO: Enable when audit log table is configured
    const totalEvents = 0
    const failedEvents = 0  
    const criticalEvents = 0
    const rateLimitEvents = 0
    
    return {
      timeframe,
      totalEvents,
      failedEvents,
      criticalEvents,
      rateLimitEvents,
      successRate: totalEvents > 0 ? ((totalEvents - failedEvents) / totalEvents * 100).toFixed(2) : 100,
    }
  }
}

// Export singleton instance
export const auditLogger = AuditLogger.getInstance()

// Middleware wrapper
export function createAuditMiddleware() {
  return {
    before: (request: NextRequest) => {
      const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      auditLogger.setRequestId(requestId)
      return { requestId }
    },
    after: async (request: NextRequest, response: Response, requestId: string) => {
      // Log the request completion
      await auditLogger.logAudit({
        action: AuditAction.API_ERROR,
        resource: request.nextUrl.pathname,
        severity: response.status >= 400 ? AuditSeverity.MEDIUM : AuditSeverity.LOW,
        metadata: {
          method: request.method,
          status: response.status,
          requestId,
        },
        success: response.status < 400,
      }, request)
    }
  }
}

