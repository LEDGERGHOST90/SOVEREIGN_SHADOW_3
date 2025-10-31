/**
 * 👁️ ADVANCED MONITORING - Better Visibility
 * Phase 1: Enhanced monitoring and visibility for all systems
 */

import { EventEmitter } from 'events';

interface SystemHealth {
  id: string;
  name: string;
  status: 'healthy' | 'warning' | 'critical' | 'offline';
  uptime: number;
  lastCheck: Date;
  metrics: Record<string, any>;
  alerts: Alert[];
}

interface Alert {
  id: string;
  type: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  timestamp: Date;
  resolved: boolean;
  system: string;
}

interface PerformanceMetrics {
  system: string;
  responseTime: number;
  throughput: number;
  errorRate: number;
  cpuUsage: number;
  memoryUsage: number;
  timestamp: Date;
}

interface TradingMetrics {
  totalTrades: number;
  successfulTrades: number;
  totalProfit: number;
  dailyPnL: number;
  winRate: number;
  avgTradeSize: number;
  timestamp: Date;
}

export class AdvancedMonitoring extends EventEmitter {
  private systemHealth: Map<string, SystemHealth> = new Map();
  private alerts: Alert[] = [];
  private performanceMetrics: PerformanceMetrics[] = [];
  private tradingMetrics: TradingMetrics[] = [];
  private isMonitoring: boolean = false;
  
  constructor() {
    super();
    this.initializeSystems();
    this.startMonitoring();
  }

  /**
   * Initialize Systems to Monitor
   */
  private initializeSystems(): void {
    const systems = [
      'shadow-ai',
      'trading-engine',
      'siphon-engine',
      'vault-system',
      'rwa-integration',
      'binance-api',
      'database',
      'chatllm-interface'
    ];

    for (const system of systems) {
      this.systemHealth.set(system, {
        id: system,
        name: this.getSystemDisplayName(system),
        status: 'healthy',
        uptime: 0,
        lastCheck: new Date(),
        metrics: {},
        alerts: []
      });
    }

    console.log(`👁️ Advanced Monitoring initialized for ${systems.length} systems`);
  }

  /**
   * Start Monitoring
   */
  private startMonitoring(): void {
    this.isMonitoring = true;

    // System health check every 30 seconds
    setInterval(() => {
      this.checkSystemHealth();
    }, 30000);

    // Performance metrics every minute
    setInterval(() => {
      this.collectPerformanceMetrics();
    }, 60000);

    // Trading metrics every 5 minutes
    setInterval(() => {
      this.collectTradingMetrics();
    }, 300000);

    // Alert processing every 10 seconds
    setInterval(() => {
      this.processAlerts();
    }, 10000);

    console.log('🔄 Advanced monitoring started');
  }

  /**
   * Check System Health
   */
  private async checkSystemHealth(): Promise<void> {
    for (const [systemId, health] of this.systemHealth) {
      try {
        const metrics = await this.getSystemMetrics(systemId);
        const status = this.determineSystemStatus(metrics);
        
        // Update health
        health.status = status;
        health.metrics = metrics;
        health.lastCheck = new Date();
        health.uptime = Date.now() - (health.uptime || Date.now());

        // Check for status changes
        if (status !== 'healthy') {
          this.createAlert(systemId, status, `System ${health.name} is ${status}`);
        }

        // Emit health update
        this.emit('systemHealthUpdate', { systemId, health });

      } catch (error) {
        console.error(`Health check failed for ${systemId}:`, error);
        health.status = 'offline';
        this.createAlert(systemId, 'critical', `System ${health.name} is offline`);
      }
    }
  }

  /**
   * Collect Performance Metrics
   */
  private async collectPerformanceMetrics(): Promise<void> {
    const metrics: PerformanceMetrics = {
      system: 'overall',
      responseTime: await this.getAverageResponseTime(),
      throughput: await this.getThroughput(),
      errorRate: await this.getErrorRate(),
      cpuUsage: await this.getCPUUsage(),
      memoryUsage: await this.getMemoryUsage(),
      timestamp: new Date()
    };

    this.performanceMetrics.push(metrics);

    // Keep only recent metrics
    if (this.performanceMetrics.length > 1000) {
      this.performanceMetrics = this.performanceMetrics.slice(-1000);
    }

    // Check for performance issues
    if (metrics.responseTime > 2000) {
      this.createAlert('performance', 'warning', `High response time: ${metrics.responseTime}ms`);
    }

    if (metrics.errorRate > 0.05) {
      this.createAlert('performance', 'error', `High error rate: ${(metrics.errorRate * 100).toFixed(2)}%`);
    }

    this.emit('performanceUpdate', metrics);
  }

  /**
   * Collect Trading Metrics
   */
  private async collectTradingMetrics(): Promise<void> {
    const metrics: TradingMetrics = {
      totalTrades: await this.getTotalTrades(),
      successfulTrades: await this.getSuccessfulTrades(),
      totalProfit: await this.getTotalProfit(),
      dailyPnL: await this.getDailyPnL(),
      winRate: 0,
      avgTradeSize: await this.getAverageTradeSize(),
      timestamp: new Date()
    };

    // Calculate win rate
    metrics.winRate = metrics.totalTrades > 0 ? metrics.successfulTrades / metrics.totalTrades : 0;

    this.tradingMetrics.push(metrics);

    // Keep only recent metrics
    if (this.tradingMetrics.length > 100) {
      this.tradingMetrics = this.tradingMetrics.slice(-100);
    }

    // Check for trading issues
    if (metrics.winRate < 0.5) {
      this.createAlert('trading', 'warning', `Low win rate: ${(metrics.winRate * 100).toFixed(1)}%`);
    }

    if (metrics.dailyPnL < -1000) {
      this.createAlert('trading', 'critical', `Daily loss: $${Math.abs(metrics.dailyPnL).toLocaleString()}`);
    }

    this.emit('tradingUpdate', metrics);
  }

  /**
   * Create Alert
   */
  private createAlert(system: string, type: Alert['type'], message: string): void {
    const alert: Alert = {
      id: `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type,
      message,
      timestamp: new Date(),
      resolved: false,
      system
    };

    this.alerts.push(alert);

    // Keep only recent alerts
    if (this.alerts.length > 1000) {
      this.alerts = this.alerts.slice(-1000);
    }

    console.log(`🚨 ${type.toUpperCase()}: ${message}`);
    this.emit('alertCreated', alert);
  }

  /**
   * Process Alerts
   */
  private processAlerts(): void {
    const unresolvedAlerts = this.alerts.filter(alert => !alert.resolved);
    
    for (const alert of unresolvedAlerts) {
      // Auto-resolve certain alerts after time
      if (alert.type === 'info' && Date.now() - alert.timestamp.getTime() > 300000) {
        alert.resolved = true;
        this.emit('alertResolved', alert);
      }
    }
  }

  /**
   * Get System Metrics
   */
  private async getSystemMetrics(systemId: string): Promise<Record<string, any>> {
    // Mock implementation - in real system, this would call actual APIs
    switch (systemId) {
      case 'shadow-ai':
        return {
          activeConnections: Math.floor(Math.random() * 10),
          processingQueue: Math.floor(Math.random() * 5),
          memoryUsage: Math.random() * 100,
          lastActivity: new Date()
        };
      
      case 'trading-engine':
        return {
          activeOrders: Math.floor(Math.random() * 3),
          pendingOrders: Math.floor(Math.random() * 2),
          lastTrade: new Date(),
          balance: Math.random() * 10000
        };
      
      case 'binance-api':
        return {
          connectionStatus: 'connected',
          lastPriceUpdate: new Date(),
          rateLimitRemaining: Math.floor(Math.random() * 1000),
          latency: Math.random() * 100
        };
      
      default:
        return {
          status: 'unknown',
          lastCheck: new Date()
        };
    }
  }

  /**
   * Determine System Status
   */
  private determineSystemStatus(metrics: Record<string, any>): SystemHealth['status'] {
    // Simple status determination logic
    if (metrics.status === 'offline') return 'offline';
    if (metrics.errorRate > 0.1) return 'critical';
    if (metrics.errorRate > 0.05) return 'warning';
    if (metrics.memoryUsage > 90) return 'warning';
    return 'healthy';
  }

  /**
   * Get System Display Name
   */
  private getSystemDisplayName(systemId: string): string {
    const names: Record<string, string> = {
      'shadow-ai': 'Shadow AI',
      'trading-engine': 'Trading Engine',
      'siphon-engine': 'Siphon Engine',
      'vault-system': 'Vault System',
      'rwa-integration': 'RWA Integration',
      'binance-api': 'Binance API',
      'database': 'Database',
      'chatllm-interface': 'ChatLLM Interface'
    };
    return names[systemId] || systemId;
  }

  /**
   * Get Dashboard Data
   */
  public getDashboardData(): any {
    const systemHealthArray = Array.from(this.systemHealth.values());
    const recentAlerts = this.alerts.slice(-10);
    const recentPerformance = this.performanceMetrics.slice(-10);
    const recentTrading = this.tradingMetrics.slice(-10);

    return {
      overview: {
        totalSystems: systemHealthArray.length,
        healthySystems: systemHealthArray.filter(s => s.status === 'healthy').length,
        warningSystems: systemHealthArray.filter(s => s.status === 'warning').length,
        criticalSystems: systemHealthArray.filter(s => s.status === 'critical').length,
        offlineSystems: systemHealthArray.filter(s => s.status === 'offline').length
      },
      systemHealth: systemHealthArray,
      alerts: recentAlerts,
      performance: recentPerformance,
      trading: recentTrading,
      timestamp: new Date()
    };
  }

  /**
   * Get System Status
   */
  public getSystemStatus(systemId: string): SystemHealth | undefined {
    return this.systemHealth.get(systemId);
  }

  /**
   * Get All Alerts
   */
  public getAllAlerts(): Alert[] {
    return [...this.alerts];
  }

  /**
   * Get Performance Metrics
   */
  public getPerformanceMetrics(): PerformanceMetrics[] {
    return [...this.performanceMetrics];
  }

  /**
   * Get Trading Metrics
   */
  public getTradingMetrics(): TradingMetrics[] {
    return [...this.tradingMetrics];
  }

  /**
   * Helper Methods (Mock implementations)
   */
  private async getAverageResponseTime(): Promise<number> {
    return Math.random() * 1000 + 100;
  }

  private async getThroughput(): Promise<number> {
    return Math.random() * 100 + 10;
  }

  private async getErrorRate(): Promise<number> {
    return Math.random() * 0.1;
  }

  private async getCPUUsage(): Promise<number> {
    return Math.random() * 100;
  }

  private async getMemoryUsage(): Promise<number> {
    return Math.random() * 100;
  }

  private async getTotalTrades(): Promise<number> {
    return Math.floor(Math.random() * 100) + 50;
  }

  private async getSuccessfulTrades(): Promise<number> {
    return Math.floor(Math.random() * 80) + 30;
  }

  private async getTotalProfit(): Promise<number> {
    return Math.random() * 10000 - 1000;
  }

  private async getDailyPnL(): Promise<number> {
    return Math.random() * 2000 - 500;
  }

  private async getAverageTradeSize(): Promise<number> {
    return Math.random() * 1000 + 100;
  }
}

export default AdvancedMonitoring;
