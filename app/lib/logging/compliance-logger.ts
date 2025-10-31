import fs from 'fs';
import path from 'path';
import { EventEmitter } from 'events';

export interface LoggingConfig {
  enabled: boolean;
  level: 'detailed' | 'standard' | 'minimal';
  includeTimestamps: boolean;
  regulatoryCompliance: boolean;
  retentionDays: number;
  systemHealth: {
    enabled: boolean;
    metricsInterval: number;
    alertThresholds: {
      responseTime: number;
      memoryUsage: number;
      cpuUsage: number;
    };
  };
}

export interface LogEntry {
  id: string;
  timestamp: string;
  level: 'INFO' | 'WARN' | 'ERROR' | 'CRITICAL';
  category: 'trading' | 'system' | 'security' | 'performance' | 'user_action';
  message: string;
  data?: any;
  userId?: string;
  sessionId?: string;
  ipAddress?: string;
  userAgent?: string;
  regulatoryFlags?: string[];
}

export interface TradingDecisionLog {
  id: string;
  timestamp: string;
  decision: 'BUY' | 'SELL' | 'HOLD' | 'REBALANCE';
  symbol: string;
  quantity: number;
  price: number;
  totalValue: number;
  reasoning: string;
  confidence: number;
  riskAssessment: string;
  userId: string;
  sessionId: string;
  regulatoryFlags: string[];
  complianceNotes: string;
}

export class ComplianceLogger extends EventEmitter {
  private config: LoggingConfig;
  private logBuffer: LogEntry[] = [];
  private tradingDecisions: TradingDecisionLog[] = [];
  private systemMetrics: any[] = [];
  private logDirectory: string;

  constructor() {
    super();
    
    this.config = {
      enabled: true,
      level: 'detailed',
      includeTimestamps: true,
      regulatoryCompliance: true,
      retentionDays: 365,
      systemHealth: {
        enabled: true,
        metricsInterval: 60000, // 1 minute
        alertThresholds: {
          responseTime: 200, // ms
          memoryUsage: 80, // %
          cpuUsage: 70 // %
        }
      }
    };

    this.logDirectory = path.join(process.cwd(), 'logs');
    this.ensureLogDirectory();
    this.startSystemMonitoring();
    this.startLogFlush();
  }

  // Main logging method
  log(level: LogEntry['level'], category: LogEntry['category'], message: string, data?: any, context?: {
    userId?: string;
    sessionId?: string;
    ipAddress?: string;
    userAgent?: string;
  }): void {
    if (!this.config.enabled) return;

    const entry: LogEntry = {
      id: this.generateLogId(),
      timestamp: new Date().toISOString(),
      level,
      category,
      message,
      data,
      userId: context?.userId,
      sessionId: context?.sessionId,
      ipAddress: context?.ipAddress,
      userAgent: context?.userAgent,
      regulatoryFlags: this.generateRegulatoryFlags(category, level, data)
    };

    this.logBuffer.push(entry);
    this.emit('log', entry);

    // Immediate write for critical logs
    if (level === 'CRITICAL') {
      this.writeLogImmediately(entry);
    }
  }

  // Trading decision logging (regulatory compliance)
  logTradingDecision(decision: {
    decision: 'BUY' | 'SELL' | 'HOLD' | 'REBALANCE';
    symbol: string;
    quantity: number;
    price: number;
    reasoning: string;
    confidence: number;
    riskAssessment: string;
    userId: string;
    sessionId: string;
  }): void {
    const totalValue = decision.quantity * decision.price;
    
    const tradingLog: TradingDecisionLog = {
      id: this.generateLogId(),
      timestamp: new Date().toISOString(),
      decision: decision.decision,
      symbol: decision.symbol,
      quantity: decision.quantity,
      price: decision.price,
      totalValue,
      reasoning: decision.reasoning,
      confidence: decision.confidence,
      riskAssessment: decision.riskAssessment,
      userId: decision.userId,
      sessionId: decision.sessionId,
      regulatoryFlags: this.generateTradingRegulatoryFlags(decision),
      complianceNotes: this.generateComplianceNotes(decision)
    };

    this.tradingDecisions.push(tradingLog);
    
    // Also create a regular log entry
    this.log('INFO', 'trading', `Trading decision: ${decision.decision} ${decision.quantity} ${decision.symbol} at $${decision.price}`, {
      decision: tradingLog
    }, {
      userId: decision.userId,
      sessionId: decision.sessionId
    });

    this.emit('tradingDecision', tradingLog);
  }

  // System health logging
  logSystemHealth(metrics: {
    responseTime: number;
    memoryUsage: number;
    cpuUsage: number;
    activeConnections: number;
    errorRate: number;
  }): void {
    if (!this.config.systemHealth.enabled) return;

    const healthLog = {
      id: this.generateLogId(),
      timestamp: new Date().toISOString(),
      metrics,
      alerts: this.generateHealthAlerts(metrics)
    };

    this.systemMetrics.push(healthLog);

    // Check alert thresholds
    const alerts = this.checkAlertThresholds(metrics);
    if (alerts.length > 0) {
      this.log('WARN', 'performance', `System health alerts: ${alerts.join(', ')}`, {
        metrics,
        alerts
      });
    }

    this.emit('systemHealth', healthLog);
  }

  // Security event logging
  logSecurityEvent(event: {
    type: 'login' | 'logout' | 'failed_auth' | 'suspicious_activity' | 'permission_denied';
    userId?: string;
    ipAddress?: string;
    details: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
  }): void {
    const level = event.severity === 'critical' ? 'CRITICAL' : 
                 event.severity === 'high' ? 'ERROR' :
                 event.severity === 'medium' ? 'WARN' : 'INFO';

    this.log(level, 'security', `Security event: ${event.type} - ${event.details}`, {
      event
    }, {
      userId: event.userId,
      ipAddress: event.ipAddress
    });
  }

  // User action logging
  logUserAction(action: {
    action: string;
    resource: string;
    userId: string;
    sessionId: string;
    ipAddress?: string;
    details?: any;
  }): void {
    this.log('INFO', 'user_action', `User action: ${action.action} on ${action.resource}`, {
      action
    }, {
      userId: action.userId,
      sessionId: action.sessionId,
      ipAddress: action.ipAddress
    });
  }

  // Query logs for compliance reporting
  queryLogs(filters: {
    startDate?: string;
    endDate?: string;
    level?: string;
    category?: string;
    userId?: string;
    limit?: number;
  }): LogEntry[] {
    let filteredLogs = [...this.logBuffer];

    if (filters.startDate) {
      filteredLogs = filteredLogs.filter(log => log.timestamp >= filters.startDate!);
    }

    if (filters.endDate) {
      filteredLogs = filteredLogs.filter(log => log.timestamp <= filters.endDate!);
    }

    if (filters.level) {
      filteredLogs = filteredLogs.filter(log => log.level === filters.level);
    }

    if (filters.category) {
      filteredLogs = filteredLogs.filter(log => log.category === filters.category);
    }

    if (filters.userId) {
      filteredLogs = filteredLogs.filter(log => log.userId === filters.userId);
    }

    if (filters.limit) {
      filteredLogs = filteredLogs.slice(-filters.limit);
    }

    return filteredLogs;
  }

  // Get trading decisions for compliance
  getTradingDecisions(filters: {
    startDate?: string;
    endDate?: string;
    userId?: string;
    symbol?: string;
    decision?: string;
  }): TradingDecisionLog[] {
    let filtered = [...this.tradingDecisions];

    if (filters.startDate) {
      filtered = filtered.filter(log => log.timestamp >= filters.startDate!);
    }

    if (filters.endDate) {
      filtered = filtered.filter(log => log.timestamp <= filters.endDate!);
    }

    if (filters.userId) {
      filtered = filtered.filter(log => log.userId === filters.userId);
    }

    if (filters.symbol) {
      filtered = filtered.filter(log => log.symbol === filters.symbol);
    }

    if (filters.decision) {
      filtered = filtered.filter(log => log.decision === filters.decision);
    }

    return filtered;
  }

  // Generate compliance report
  generateComplianceReport(startDate: string, endDate: string): {
    summary: any;
    tradingDecisions: TradingDecisionLog[];
    securityEvents: LogEntry[];
    systemHealth: any;
    regulatoryFlags: string[];
  } {
    const tradingDecisions = this.getTradingDecisions({ startDate, endDate });
    const securityEvents = this.queryLogs({ 
      startDate, 
      endDate, 
      category: 'security',
      limit: 1000 
    });

    const allRegulatoryFlags = new Set<string>();
    tradingDecisions.forEach(decision => {
      decision.regulatoryFlags.forEach(flag => allRegulatoryFlags.add(flag));
    });

    const summary = {
      period: { startDate, endDate },
      totalTradingDecisions: tradingDecisions.length,
      totalSecurityEvents: securityEvents.length,
      uniqueUsers: new Set(tradingDecisions.map(d => d.userId)).size,
      totalValueTraded: tradingDecisions.reduce((sum, d) => sum + d.totalValue, 0),
      averageConfidence: tradingDecisions.length > 0 
        ? tradingDecisions.reduce((sum, d) => sum + d.confidence, 0) / tradingDecisions.length 
        : 0
    };

    return {
      summary,
      tradingDecisions,
      securityEvents,
      systemHealth: this.systemMetrics.filter(m => 
        m.timestamp >= startDate && m.timestamp <= endDate
      ),
      regulatoryFlags: Array.from(allRegulatoryFlags)
    };
  }

  private generateLogId(): string {
    return `log_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
  }

  private generateRegulatoryFlags(category: string, level: string, data?: any): string[] {
    const flags: string[] = [];

    if (category === 'trading') {
      flags.push('TRADING_ACTIVITY');
      if (level === 'ERROR' || level === 'CRITICAL') {
        flags.push('TRADING_ERROR');
      }
    }

    if (category === 'security') {
      flags.push('SECURITY_EVENT');
      if (level === 'ERROR' || level === 'CRITICAL') {
        flags.push('SECURITY_ALERT');
      }
    }

    if (data?.totalValue && data.totalValue > 10000) {
      flags.push('HIGH_VALUE_TRANSACTION');
    }

    return flags;
  }

  private generateTradingRegulatoryFlags(decision: any): string[] {
    const flags = ['TRADING_DECISION'];

    if (decision.totalValue > 10000) {
      flags.push('HIGH_VALUE_TRADE');
    }

    if (decision.confidence < 70) {
      flags.push('LOW_CONFIDENCE_TRADE');
    }

    if (decision.riskAssessment === 'HIGH' || decision.riskAssessment === 'CRITICAL') {
      flags.push('HIGH_RISK_TRADE');
    }

    return flags;
  }

  private generateComplianceNotes(decision: any): string {
    const notes: string[] = [];

    if (decision.totalValue > 10000) {
      notes.push('High-value transaction requires additional monitoring');
    }

    if (decision.confidence < 70) {
      notes.push('Low confidence trade - review recommended');
    }

    if (decision.riskAssessment === 'HIGH' || decision.riskAssessment === 'CRITICAL') {
      notes.push('High-risk trade - compliance review required');
    }

    return notes.join('; ');
  }

  private generateHealthAlerts(metrics: any): string[] {
    const alerts: string[] = [];

    if (metrics.responseTime > this.config.systemHealth.alertThresholds.responseTime) {
      alerts.push('High response time');
    }

    if (metrics.memoryUsage > this.config.systemHealth.alertThresholds.memoryUsage) {
      alerts.push('High memory usage');
    }

    if (metrics.cpuUsage > this.config.systemHealth.alertThresholds.cpuUsage) {
      alerts.push('High CPU usage');
    }

    return alerts;
  }

  private checkAlertThresholds(metrics: any): string[] {
    return this.generateHealthAlerts(metrics);
  }

  private ensureLogDirectory(): void {
    if (!fs.existsSync(this.logDirectory)) {
      fs.mkdirSync(this.logDirectory, { recursive: true });
    }
  }

  private startSystemMonitoring(): void {
    if (!this.config.systemHealth.enabled) return;

    setInterval(() => {
      // Simulate system metrics collection
      const metrics = {
        responseTime: Math.floor(Math.random() * 200) + 50, // 50-250ms
        memoryUsage: Math.floor(Math.random() * 30) + 50, // 50-80%
        cpuUsage: Math.floor(Math.random() * 20) + 40, // 40-60%
        activeConnections: Math.floor(Math.random() * 50) + 10,
        errorRate: Math.floor(Math.random() * 5) // 0-5%
      };

      this.logSystemHealth(metrics);
    }, this.config.systemHealth.metricsInterval);
  }

  private startLogFlush(): void {
    // Flush logs to disk every 5 minutes
    setInterval(() => {
      this.flushLogsToDisk();
    }, 5 * 60 * 1000);
  }

  private flushLogsToDisk(): void {
    if (this.logBuffer.length === 0) return;

    const timestamp = new Date().toISOString().split('T')[0];
    const logFile = path.join(this.logDirectory, `compliance-${timestamp}.json`);

    try {
      const logsToWrite = [...this.logBuffer];
      this.logBuffer = []; // Clear buffer

      // Append to file
      const logData = logsToWrite.map(log => JSON.stringify(log)).join('\n') + '\n';
      fs.appendFileSync(logFile, logData);

      console.log(`📝 Flushed ${logsToWrite.length} logs to disk`);
    } catch (error) {
      console.error('Failed to flush logs to disk:', error);
    }
  }

  private writeLogImmediately(entry: LogEntry): void {
    const timestamp = new Date().toISOString().split('T')[0];
    const logFile = path.join(this.logDirectory, `critical-${timestamp}.json`);

    try {
      const logData = JSON.stringify(entry) + '\n';
      fs.appendFileSync(logFile, logData);
    } catch (error) {
      console.error('Failed to write critical log:', error);
    }
  }

  // Update configuration
  updateConfig(newConfig: Partial<LoggingConfig>): void {
    this.config = { ...this.config, ...newConfig };
    console.log('⚙️ Logging configuration updated:', newConfig);
  }

  // Get current configuration
  getConfig(): LoggingConfig {
    return { ...this.config };
  }

  // Get statistics
  getStats(): {
    totalLogs: number;
    tradingDecisions: number;
    systemMetrics: number;
    logBufferSize: number;
    oldestLog: string;
    newestLog: string;
  } {
    const allLogs = [...this.logBuffer, ...this.tradingDecisions, ...this.systemMetrics];
    const timestamps = allLogs.map(log => log.timestamp).sort();

    return {
      totalLogs: this.logBuffer.length,
      tradingDecisions: this.tradingDecisions.length,
      systemMetrics: this.systemMetrics.length,
      logBufferSize: this.logBuffer.length,
      oldestLog: timestamps[0] || 'N/A',
      newestLog: timestamps[timestamps.length - 1] || 'N/A'
    };
  }
}

// Export singleton instance
export const complianceLogger = new ComplianceLogger();
