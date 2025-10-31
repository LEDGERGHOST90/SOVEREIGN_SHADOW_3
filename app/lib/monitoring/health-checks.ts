import { EventEmitter } from 'events';

export interface HealthCheckConfig {
  primaryAI: {
    maxResponseTime: number; // ms
    expectedUptime: number; // percentage
  };
  secondaryNode: {
    activationTimeout: number; // ms
    expectedStatus: 'active' | 'standby' | 'offline';
  };
  mcpServer: {
    connectionTimeout: number; // ms
    expectedLatency: number; // ms
  };
  dataFeeds: {
    maxFailureRate: number; // percentage
    circuitBreakerThreshold: number; // failures
  };
}

export interface HealthStatus {
  component: string;
  status: 'healthy' | 'warning' | 'critical' | 'unknown';
  lastCheck: string;
  responseTime?: number;
  uptime?: number;
  errorCount?: number;
  details: string;
}

export class HealthCheckSystem extends EventEmitter {
  private config: HealthCheckConfig;
  private healthStatus: Map<string, HealthStatus> = new Map();
  private failureCounts: Map<string, number> = new Map();
  private circuitBreakers: Map<string, boolean> = new Map();

  constructor() {
    super();
    this.config = {
      primaryAI: {
        maxResponseTime: 5000, // 5 seconds
        expectedUptime: 99.5 // 99.5%
      },
      secondaryNode: {
        activationTimeout: 30000, // 30 seconds
        expectedStatus: 'active'
      },
      mcpServer: {
        connectionTimeout: 10000, // 10 seconds
        expectedLatency: 500 // 500ms
      },
      dataFeeds: {
        maxFailureRate: 5, // 5%
        circuitBreakerThreshold: 3 // 3 failures
      }
    };

    // Start continuous health monitoring
    this.startHealthMonitoring();
  }

  // Primary AI health check
  async checkPrimaryAI(): Promise<HealthStatus> {
    const startTime = Date.now();
    
    try {
      // Simulate AI response check
      const response = await fetch('http://localhost:3000/api/shadow-ai/core', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: 'health_check' }),
        signal: AbortSignal.timeout(this.config.primaryAI.maxResponseTime)
      });

      const responseTime = Date.now() - startTime;
      const isHealthy = response.ok && responseTime < this.config.primaryAI.maxResponseTime;

      const status: HealthStatus = {
        component: 'primaryAI',
        status: isHealthy ? 'healthy' : responseTime > this.config.primaryAI.maxResponseTime ? 'warning' : 'critical',
        lastCheck: new Date().toISOString(),
        responseTime: responseTime,
        uptime: isHealthy ? 99.8 : 95.0, // Simulated uptime
        details: isHealthy ? 'Primary AI responding normally' : 'Primary AI response time exceeded'
      };

      this.healthStatus.set('primaryAI', status);
      return status;
    } catch (error) {
      const status: HealthStatus = {
        component: 'primaryAI',
        status: 'critical',
        lastCheck: new Date().toISOString(),
        details: `Primary AI health check failed: ${error}`
      };
      
      this.healthStatus.set('primaryAI', status);
      this.incrementFailureCount('primaryAI');
      return status;
    }
  }

  // Secondary node health check
  async checkSecondaryNode(): Promise<HealthStatus> {
    try {
      // Check secondary node activation status
      const activationStartTime = Date.now();
      
      // Simulate secondary node check (in production, ping actual Lenovo Yoga)
      const isActivated = await this.checkSecondaryNodeActivation();
      const activationTime = Date.now() - activationStartTime;

      const status: HealthStatus = {
        component: 'secondaryNode',
        status: isActivated ? 'healthy' : activationTime > this.config.secondaryNode.activationTimeout ? 'critical' : 'warning',
        lastCheck: new Date().toISOString(),
        responseTime: activationTime,
        details: isActivated ? 'Secondary node active and responsive' : 'Secondary node activation pending'
      };

      this.healthStatus.set('secondaryNode', status);
      
      if (!isActivated) {
        this.triggerSecondaryNodeActivation();
      }
      
      return status;
    } catch (error) {
      const status: HealthStatus = {
        component: 'secondaryNode',
        status: 'critical',
        lastCheck: new Date().toISOString(),
        details: `Secondary node check failed: ${error}`
      };
      
      this.healthStatus.set('secondaryNode', status);
      this.incrementFailureCount('secondaryNode');
      return status;
    }
  }

  // MCP Server health check
  async checkMCPServer(): Promise<HealthStatus> {
    const startTime = Date.now();
    
    try {
      // Check MCP server connectivity
      const response = await fetch('http://localhost:8000/health', {
        signal: AbortSignal.timeout(this.config.mcpServer.connectionTimeout)
      });

      const responseTime = Date.now() - startTime;
      const isHealthy = response.ok && responseTime < this.config.mcpServer.expectedLatency;

      const status: HealthStatus = {
        component: 'mcpServer',
        status: isHealthy ? 'healthy' : responseTime > this.config.mcpServer.expectedLatency ? 'warning' : 'critical',
        lastCheck: new Date().toISOString(),
        responseTime: responseTime,
        details: isHealthy ? 'MCP Server responding normally' : 'MCP Server latency exceeded'
      };

      this.healthStatus.set('mcpServer', status);
      return status;
    } catch (error) {
      const status: HealthStatus = {
        component: 'mcpServer',
        status: 'critical',
        lastCheck: new Date().toISOString(),
        details: `MCP Server health check failed: ${error}`
      };
      
      this.healthStatus.set('mcpServer', status);
      this.incrementFailureCount('mcpServer');
      return status;
    }
  }

  // Data feeds health check
  async checkDataFeeds(): Promise<HealthStatus> {
    const feeds = ['binance', 'coingecko', 'defipulse'];
    const results = await Promise.allSettled(
      feeds.map(feed => this.checkDataFeed(feed))
    );

    const successfulFeeds = results.filter(r => r.status === 'fulfilled').length;
    const failureRate = (feeds.length - successfulFeeds) / feeds.length * 100;

    // Check circuit breakers
    feeds.forEach((feed, index) => {
      if (results[index].status === 'rejected') {
        this.incrementFailureCount(`dataFeed_${feed}`);
      }
    });

    const status: HealthStatus = {
      component: 'dataFeeds',
      status: failureRate < this.config.dataFeeds.maxFailureRate ? 'healthy' : 
              failureRate < this.config.dataFeeds.maxFailureRate * 2 ? 'warning' : 'critical',
      lastCheck: new Date().toISOString(),
      errorCount: feeds.length - successfulFeeds,
      details: `${successfulFeeds}/${feeds.length} data feeds operational (${failureRate.toFixed(1)}% failure rate)`
    };

    this.healthStatus.set('dataFeeds', status);
    return status;
  }

  private async checkDataFeed(feedName: string): Promise<boolean> {
    try {
      // Simulate data feed check
      const response = await fetch(`https://api.${feedName}.com/ping`, {
        signal: AbortSignal.timeout(5000)
      });
      return response.ok;
    } catch (error) {
      return false;
    }
  }

  private async checkSecondaryNodeActivation(): Promise<boolean> {
    // In production, this would ping the actual Lenovo Yoga
    // For now, simulate activation check
    return Math.random() > 0.3; // 70% chance of being "active"
  }

  private triggerSecondaryNodeActivation(): void {
    console.log('🔄 Triggering secondary node activation...');
    // In production, send activation command to Lenovo Yoga
    this.emit('secondaryNodeActivation', {
      timestamp: new Date().toISOString(),
      action: 'activation_triggered'
    });
  }

  private incrementFailureCount(component: string): void {
    const currentCount = this.failureCounts.get(component) || 0;
    const newCount = currentCount + 1;
    this.failureCounts.set(component, newCount);

    // Trigger circuit breaker if threshold exceeded
    if (newCount >= this.config.dataFeeds.circuitBreakerThreshold) {
      this.circuitBreakers.set(component, true);
      console.log(`🚨 Circuit breaker triggered for ${component}`);
      this.emit('circuitBreakerTriggered', { component, failureCount: newCount });
    }
  }

  private startHealthMonitoring(): void {
    // Check every 30 seconds
    setInterval(async () => {
      await Promise.all([
        this.checkPrimaryAI(),
        this.checkSecondaryNode(),
        this.checkMCPServer(),
        this.checkDataFeeds()
      ]);
    }, 30000);
  }

  // Get overall system health
  getSystemHealth(): {
    overallStatus: 'healthy' | 'warning' | 'critical';
    components: HealthStatus[];
    recommendations: string[];
  } {
    const components = Array.from(this.healthStatus.values());
    const criticalCount = components.filter(c => c.status === 'critical').length;
    const warningCount = components.filter(c => c.status === 'warning').length;

    let overallStatus: 'healthy' | 'warning' | 'critical';
    if (criticalCount > 0) {
      overallStatus = 'critical';
    } else if (warningCount > 1) {
      overallStatus = 'warning';
    } else {
      overallStatus = 'healthy';
    }

    const recommendations = [];
    if (criticalCount > 0) {
      recommendations.push('Immediate attention required for critical components');
    }
    if (warningCount > 0) {
      recommendations.push('Monitor warning components closely');
    }
    if (this.circuitBreakers.size > 0) {
      recommendations.push('Circuit breakers active - review failed components');
    }

    return {
      overallStatus,
      components,
      recommendations
    };
  }
}

// Export singleton instance
export const healthCheckSystem = new HealthCheckSystem();
