import { EventEmitter } from 'events';

export interface DataFeedConfig {
  name: string;
  enabled: boolean;
  failureThreshold: number;
  timeout: number;
  fallback: string;
  endpoint: string;
}

export interface CircuitBreakerState {
  state: 'CLOSED' | 'OPEN' | 'HALF_OPEN';
  failureCount: number;
  lastFailureTime: number;
  nextAttemptTime: number;
}

export class DataFeedCircuitBreakers extends EventEmitter {
  private feeds: Map<string, DataFeedConfig> = new Map();
  private circuitBreakers: Map<string, CircuitBreakerState> = new Map();
  private fallbackChain: string[] = ['binance', 'coingecko', 'defipulse'];

  constructor() {
    super();
    this.initializeDataFeeds();
  }

  private initializeDataFeeds(): void {
    const feedConfigs: DataFeedConfig[] = [
      {
        name: 'binance',
        enabled: true,
        failureThreshold: 3,
        timeout: 30000,
        fallback: 'coingecko',
        endpoint: 'https://api.binance.us/api/v3/ticker/price'
      },
      {
        name: 'coingecko',
        enabled: true,
        failureThreshold: 3,
        timeout: 30000,
        fallback: 'defipulse',
        endpoint: 'https://api.coingecko.com/api/v3/simple/price'
      },
      {
        name: 'defipulse',
        enabled: true,
        failureThreshold: 3,
        timeout: 30000,
        fallback: 'cached_data',
        endpoint: 'https://data-api.defipulse.com/api/v1/tvl'
      }
    ];

    feedConfigs.forEach(feed => {
      this.feeds.set(feed.name, feed);
      this.circuitBreakers.set(feed.name, {
        state: 'CLOSED',
        failureCount: 0,
        lastFailureTime: 0,
        nextAttemptTime: 0
      });
    });
  }

  async fetchData(symbol: string, feedName?: string): Promise<{
    success: boolean;
    data: any;
    source: string;
    responseTime: number;
    circuitBreakerState: string;
    fallbackUsed: boolean;
  }> {
    const startTime = Date.now();
    
    // Determine which feed to use
    const targetFeed = feedName || this.selectOptimalFeed();
    
    // Check circuit breaker state
    const circuitBreaker = this.circuitBreakers.get(targetFeed);
    if (!circuitBreaker) {
      throw new Error(`Unknown feed: ${targetFeed}`);
    }

    if (circuitBreaker.state === 'OPEN') {
      if (Date.now() < circuitBreaker.nextAttemptTime) {
        console.log(`🚨 Circuit breaker OPEN for ${targetFeed}, using fallback`);
        return await this.useFallback(symbol, targetFeed, startTime);
      } else {
        circuitBreaker.state = 'HALF_OPEN';
      }
    }

    try {
      const data = await this.executeFeedRequest(targetFeed, symbol);
      const responseTime = Date.now() - startTime;

      // Success - reset circuit breaker
      this.resetCircuitBreaker(targetFeed);

      return {
        success: true,
        data,
        source: targetFeed,
        responseTime,
        circuitBreakerState: circuitBreaker.state,
        fallbackUsed: false
      };

    } catch (error) {
      console.warn(`❌ ${targetFeed} request failed:`, error);
      
      // Record failure
      this.recordFailure(targetFeed);
      
      // Use fallback
      return await this.useFallback(symbol, targetFeed, startTime);
    }
  }

  private async executeFeedRequest(feedName: string, symbol: string): Promise<any> {
    const feed = this.feeds.get(feedName);
    if (!feed) {
      throw new Error(`Feed not configured: ${feedName}`);
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), feed.timeout);

    try {
      let url = feed.endpoint;
      
      // Add symbol-specific parameters
      if (feedName === 'binance') {
        url += `?symbol=${symbol.toUpperCase()}USDT`;
      } else if (feedName === 'coingecko') {
        const coinId = this.getCoinGeckoId(symbol);
        url += `?ids=${coinId}&vs_currencies=usd`;
      }

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'User-Agent': 'SovereignShadow.Ai/1.0'
        },
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

  private async useFallback(symbol: string, failedFeed: string, startTime: number): Promise<any> {
    const feed = this.feeds.get(failedFeed);
    if (!feed) {
      throw new Error(`Feed not configured: ${failedFeed}`);
    }

    let fallbackFeed = feed.fallback;
    
    // Try fallback chain
    while (fallbackFeed && fallbackFeed !== 'cached_data') {
      try {
        const data = await this.executeFeedRequest(fallbackFeed, symbol);
        const responseTime = Date.now() - startTime;

        console.log(`✅ Fallback successful: ${failedFeed} → ${fallbackFeed}`);

        return {
          success: true,
          data,
          source: fallbackFeed,
          responseTime,
          circuitBreakerState: this.circuitBreakers.get(fallbackFeed)?.state || 'CLOSED',
          fallbackUsed: true
        };

      } catch (error) {
        console.warn(`❌ Fallback ${fallbackFeed} also failed:`, error);
        
        // Record failure for fallback
        this.recordFailure(fallbackFeed);
        
        // Try next fallback
        const nextFeed = this.feeds.get(fallbackFeed);
        fallbackFeed = nextFeed?.fallback || 'cached_data';
      }
    }

    // All feeds failed, return cached data
    return this.getCachedData(symbol, startTime);
  }

  private getCachedData(symbol: string, startTime: number): any {
    console.log(`📦 Using cached data for ${symbol} (all feeds failed)`);
    
    // Return cached data structure
    const cachedData = {
      symbol: symbol.toUpperCase(),
      price: this.getCachedPrice(symbol),
      timestamp: new Date().toISOString(),
      source: 'cached_data'
    };

    return {
      success: true,
      data: cachedData,
      source: 'cached_data',
      responseTime: Date.now() - startTime,
      circuitBreakerState: 'CLOSED',
      fallbackUsed: true
    };
  }

  private getCachedPrice(symbol: string): number {
    // Simulate cached prices (in real system, these would come from a cache)
    const cachedPrices: { [key: string]: number } = {
      'BTC': 95000,
      'ETH': 3200,
      'XRP': 0.65,
      'ADA': 0.45,
      'SOL': 180
    };
    
    return cachedPrices[symbol.toUpperCase()] || 100;
  }

  private getCoinGeckoId(symbol: string): string {
    const coinIds: { [key: string]: string } = {
      'BTC': 'bitcoin',
      'ETH': 'ethereum',
      'XRP': 'ripple',
      'ADA': 'cardano',
      'SOL': 'solana'
    };
    
    return coinIds[symbol.toUpperCase()] || 'bitcoin';
  }

  private selectOptimalFeed(): string {
    // Select the first available feed in the chain
    for (const feedName of this.fallbackChain) {
      const circuitBreaker = this.circuitBreakers.get(feedName);
      if (circuitBreaker && circuitBreaker.state === 'CLOSED') {
        return feedName;
      }
    }
    
    // If all circuit breakers are open, return the first one
    return this.fallbackChain[0];
  }

  private recordFailure(feedName: string): void {
    const circuitBreaker = this.circuitBreakers.get(feedName);
    if (!circuitBreaker) return;

    circuitBreaker.failureCount++;
    circuitBreaker.lastFailureTime = Date.now();

    const feed = this.feeds.get(feedName);
    if (feed && circuitBreaker.failureCount >= feed.failureThreshold) {
      circuitBreaker.state = 'OPEN';
      circuitBreaker.nextAttemptTime = Date.now() + 60000; // 60 seconds
      
      console.log(`🚨 Circuit breaker OPEN for ${feedName}`);
      console.log(`   Failures: ${circuitBreaker.failureCount}/${feed.failureThreshold}`);
      console.log(`   Next attempt: ${new Date(circuitBreaker.nextAttemptTime).toISOString()}`);
      
      this.emit('circuitBreakerOpen', { feedName, circuitBreaker });
    }
  }

  private resetCircuitBreaker(feedName: string): void {
    const circuitBreaker = this.circuitBreakers.get(feedName);
    if (!circuitBreaker) return;

    if (circuitBreaker.state === 'HALF_OPEN') {
      circuitBreaker.state = 'CLOSED';
      circuitBreaker.failureCount = 0;
      console.log(`✅ Circuit breaker CLOSED for ${feedName}`);
      this.emit('circuitBreakerClosed', { feedName });
    }
  }

  // Health monitoring
  getHealthStatus(): {
    feeds: Array<{
      name: string;
      state: string;
      failureCount: number;
      lastFailure: string;
      nextAttempt: string;
    }>;
    overallHealth: 'healthy' | 'degraded' | 'critical';
  } {
    const feeds = Array.from(this.circuitBreakers.entries()).map(([name, state]) => ({
      name,
      state: state.state,
      failureCount: state.failureCount,
      lastFailure: state.lastFailureTime ? new Date(state.lastFailureTime).toISOString() : 'Never',
      nextAttempt: state.nextAttemptTime ? new Date(state.nextAttemptTime).toISOString() : 'N/A'
    }));

    const openBreakers = feeds.filter(f => f.state === 'OPEN').length;
    const halfOpenBreakers = feeds.filter(f => f.state === 'HALF_OPEN').length;

    let overallHealth: 'healthy' | 'degraded' | 'critical';
    if (openBreakers === 0 && halfOpenBreakers === 0) {
      overallHealth = 'healthy';
    } else if (openBreakers < 2) {
      overallHealth = 'degraded';
    } else {
      overallHealth = 'critical';
    }

    return { feeds, overallHealth };
  }

  // Force reset all circuit breakers (for testing)
  resetAllCircuitBreakers(): void {
    this.circuitBreakers.forEach((state, name) => {
      state.state = 'CLOSED';
      state.failureCount = 0;
      state.lastFailureTime = 0;
      state.nextAttemptTime = 0;
    });
    console.log('🔄 All circuit breakers reset');
  }
}

// Export singleton instance
export const dataFeedCircuitBreakers = new DataFeedCircuitBreakers();
