import { EventEmitter } from 'events';

export interface MCPEnhancedConfig {
  keepAlive: boolean;
  maxConnections: number;
  connectionTimeout: number;
  retryAttempts: number;
  healthCheckInterval: number;
  circuitBreaker: {
    enabled: boolean;
    failureThreshold: number;
    resetTimeout: number;
  };
}

export interface CircuitBreakerState {
  state: 'CLOSED' | 'OPEN' | 'HALF_OPEN';
  failureCount: number;
  lastFailureTime: number;
  nextAttemptTime: number;
}

export class EnhancedMCPClient extends EventEmitter {
  private config: MCPEnhancedConfig;
  private circuitBreaker: CircuitBreakerState;
  private connectionPool: Array<any> = [];
  private healthStatus: 'healthy' | 'degraded' | 'critical' = 'healthy';
  private lastHealthCheck: number = Date.now();
  private retryQueue: Array<{ request: any; resolve: Function; reject: Function; attempts: number }> = [];

  constructor() {
    super();
    
    this.config = {
      keepAlive: true,
      maxConnections: 10,
      connectionTimeout: 5000,
      retryAttempts: 3,
      healthCheckInterval: 30000,
      circuitBreaker: {
        enabled: true,
        failureThreshold: 5,
        resetTimeout: 60000 // 60 seconds
      }
    };

    this.circuitBreaker = {
      state: 'CLOSED',
      failureCount: 0,
      lastFailureTime: 0,
      nextAttemptTime: 0
    };

    this.initializeConnectionPool();
    this.startHealthMonitoring();
    this.processRetryQueue();
  }

  private initializeConnectionPool(): void {
    for (let i = 0; i < this.config.maxConnections; i++) {
      // Simulate connection pool initialization
      this.connectionPool.push({
        id: i,
        active: true,
        lastUsed: Date.now(),
        requestCount: 0
      });
    }
  }

  private getAvailableConnection(): any {
    // Find least recently used connection
    const available = this.connectionPool
      .filter(conn => conn.active)
      .sort((a, b) => a.lastUsed - b.lastUsed);
    
    return available[0] || null;
  }

  // Enhanced request with circuit breaker and retry logic
  async makeRequest(endpoint: string, data: any = {}): Promise<any> {
    // Check circuit breaker state
    if (this.circuitBreaker.state === 'OPEN') {
      if (Date.now() < this.circuitBreaker.nextAttemptTime) {
        throw new Error('Circuit breaker is OPEN - request rejected');
      } else {
        this.circuitBreaker.state = 'HALF_OPEN';
      }
    }

    const connection = this.getAvailableConnection();
    if (!connection) {
      throw new Error('No available connections in pool');
    }

    const startTime = Date.now();
    let lastError: Error | null = null;

    // Retry logic with exponential backoff
    for (let attempt = 1; attempt <= this.config.retryAttempts; attempt++) {
      try {
        const response = await this.executeRequest(connection, endpoint, data);
        const responseTime = Date.now() - startTime;

        // Update connection stats
        connection.lastUsed = Date.now();
        connection.requestCount++;

        // Success - reset circuit breaker
        this.resetCircuitBreaker();

        // Update health status
        this.updateHealthStatus(responseTime);

        return {
          success: true,
          data: response,
          responseTime,
          attempt,
          connectionId: connection.id,
          circuitBreakerState: this.circuitBreaker.state
        };

      } catch (error) {
        lastError = error as Error;
        console.warn(`MCP request attempt ${attempt} failed:`, error);

        // Record failure
        this.recordFailure();

        // Exponential backoff
        if (attempt < this.config.retryAttempts) {
          const backoffDelay = Math.pow(2, attempt) * 100;
          await this.delay(backoffDelay);
        }
      }
    }

    // All attempts failed
    const responseTime = Date.now() - startTime;
    this.updateHealthStatus(responseTime, true);

    return {
      success: false,
      error: lastError?.toString(),
      responseTime,
      attempts: this.config.retryAttempts,
      circuitBreakerState: this.circuitBreaker.state,
      connectionId: connection?.id
    };
  }

  private async executeRequest(connection: any, endpoint: string, data: any): Promise<any> {
    const url = `http://localhost:8000${endpoint}`;
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.connectionTimeout);

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Connection': this.config.keepAlive ? 'keep-alive' : 'close',
          'Keep-Alive': 'timeout=30, max=100'
        },
        body: JSON.stringify(data),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();

    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }

  private recordFailure(): void {
    this.circuitBreaker.failureCount++;
    this.circuitBreaker.lastFailureTime = Date.now();

    if (this.circuitBreaker.failureCount >= this.config.circuitBreaker.failureThreshold) {
      this.circuitBreaker.state = 'OPEN';
      this.circuitBreaker.nextAttemptTime = Date.now() + this.config.circuitBreaker.resetTimeout;
      
      console.log(`🚨 Circuit breaker triggered for mcpServer`);
      console.log(`   Failures: ${this.circuitBreaker.failureCount}/${this.config.circuitBreaker.failureThreshold}`);
      console.log(`   Next attempt: ${new Date(this.circuitBreaker.nextAttemptTime).toISOString()}`);
      
      this.emit('circuitBreakerOpen', this.circuitBreaker);
    }
  }

  private resetCircuitBreaker(): void {
    if (this.circuitBreaker.state === 'HALF_OPEN') {
      this.circuitBreaker.state = 'CLOSED';
      this.circuitBreaker.failureCount = 0;
      this.emit('circuitBreakerClosed');
    }
  }

  private updateHealthStatus(responseTime: number, isError: boolean = false): void {
    if (isError || responseTime > 3000) {
      this.healthStatus = 'critical';
    } else if (responseTime > 1000) {
      this.healthStatus = 'degraded';
    } else {
      this.healthStatus = 'healthy';
    }
    this.lastHealthCheck = Date.now();
  }

  private startHealthMonitoring(): void {
    setInterval(async () => {
      try {
        const healthCheck = await this.makeRequest('/health');
        if (healthCheck.success) {
          console.log(`✅ MCP Server health check passed: ${healthCheck.responseTime}ms`);
        } else {
          console.warn(`⚠️ MCP Server health check failed: ${healthCheck.error}`);
        }
      } catch (error) {
        console.error(`❌ MCP Server health check error:`, error);
      }
    }, this.config.healthCheckInterval);
  }

  private processRetryQueue(): void {
    setInterval(() => {
      if (this.retryQueue.length > 0 && this.circuitBreaker.state !== 'OPEN') {
        const queuedRequest = this.retryQueue.shift();
        if (queuedRequest) {
          this.makeRequest(queuedRequest.request.endpoint, queuedRequest.request.data)
            .then(queuedRequest.resolve)
            .catch(queuedRequest.reject);
        }
      }
    }, 1000);
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Health and metrics
  getHealthStatus(): {
    status: string;
    circuitBreaker: CircuitBreakerState;
    connectionPool: any;
    lastHealthCheck: string;
  } {
    return {
      status: this.healthStatus,
      circuitBreaker: { ...this.circuitBreaker },
      connectionPool: {
        total: this.connectionPool.length,
        active: this.connectionPool.filter(c => c.active).length,
        averageRequests: this.connectionPool.reduce((sum, c) => sum + c.requestCount, 0) / this.connectionPool.length
      },
      lastHealthCheck: new Date(this.lastHealthCheck).toISOString()
    };
  }

  // Force circuit breaker reset (for testing)
  resetCircuitBreakerForced(): void {
    this.circuitBreaker = {
      state: 'CLOSED',
      failureCount: 0,
      lastFailureTime: 0,
      nextAttemptTime: 0
    };
    console.log('🔄 Circuit breaker manually reset');
  }

  // Get configuration
  getConfig(): MCPEnhancedConfig {
    return { ...this.config };
  }

  // Update configuration
  updateConfig(newConfig: Partial<MCPEnhancedConfig>): void {
    this.config = { ...this.config, ...newConfig };
    console.log('⚙️ MCP configuration updated:', newConfig);
  }
}

// Export singleton instance
export const enhancedMCPClient = new EnhancedMCPClient();
