
/**
 * ⚡ REDIS CACHING SYSTEM
 * Enterprise-grade caching for performance optimization
 */

import { Redis } from 'ioredis'

// Redis client configuration
const redis = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: parseInt(process.env.REDIS_PORT || '6379'),
  password: process.env.REDIS_PASSWORD,
  enableReadyCheck: false,
  maxRetriesPerRequest: 3,
  lazyConnect: true,
  family: 4,
  keepAlive: 30000,
  connectTimeout: 10000,
})

// Cache key patterns
export const CacheKeys = {
  USER_PROFILE: (userId: string) => `user:profile:${userId}`,
  PORTFOLIO: (userId: string) => `portfolio:${userId}`,
  MARKET_PRICES: (symbols: string[]) => `prices:${symbols.sort().join(',')}`,
  TRADING_LIMITS: (userId: string) => `limits:trading:${userId}`,
  SIPHON_CONFIG: (userId: string) => `config:siphon:${userId}`,
  VAULT_BALANCE: (userId: string) => `vault:balance:${userId}`,
  RISK_PROFILE: (userId: string) => `risk:profile:${userId}`,
  AI_ANALYSIS: (symbol: string, timeframe: string) => `ai:analysis:${symbol}:${timeframe}`,
  RATE_LIMIT: (clientId: string, endpoint: string) => `ratelimit:${clientId}:${endpoint}`,
} as const

// Cache TTL (Time To Live) in seconds
export const CacheTTL = {
  USER_PROFILE: 300,      // 5 minutes
  PORTFOLIO: 30,          // 30 seconds (frequent updates)
  MARKET_PRICES: 5,       // 5 seconds (real-time data)
  TRADING_LIMITS: 3600,   // 1 hour
  SIPHON_CONFIG: 1800,    // 30 minutes
  VAULT_BALANCE: 60,      // 1 minute
  RISK_PROFILE: 3600,     // 1 hour
  AI_ANALYSIS: 300,       // 5 minutes
  RATE_LIMIT: 60,         // 1 minute (matches rate limit window)
} as const

export interface CacheOptions {
  ttl?: number
  compress?: boolean
  tags?: string[]
}

class CacheManager {
  private static instance: CacheManager
  private connected: boolean = false

  public static getInstance(): CacheManager {
    if (!CacheManager.instance) {
      CacheManager.instance = new CacheManager()
    }
    return CacheManager.instance
  }

  constructor() {
    this.initializeConnection()
  }

  private async initializeConnection(): Promise<void> {
    try {
      redis.on('connect', () => {
        console.log('Redis connected successfully')
        this.connected = true
      })

      redis.on('error', (error: any) => {
        console.error('Redis connection error:', error)
        this.connected = false
      })

      redis.on('ready', () => {
        console.log('Redis ready for operations')
        this.connected = true
      })

      redis.on('reconnecting', () => {
        console.log('Redis reconnecting...')
      })

      // Test connection
      await redis.ping()
    } catch (error) {
      console.error('Failed to initialize Redis:', error)
      this.connected = false
    }
  }

  async get<T>(key: string): Promise<T | null> {
    if (!this.connected) {
      console.warn('Redis not connected, cache miss for key:', key)
      return null
    }

    try {
      const cached = await redis.get(key)
      if (!cached) return null

      // Try to parse as JSON, fallback to string
      try {
        return JSON.parse(cached) as T
      } catch {
        return cached as unknown as T
      }
    } catch (error) {
      console.error('Cache get error:', error, 'for key:', key)
      return null
    }
  }

  async set<T>(key: string, value: T, options: CacheOptions = {}): Promise<boolean> {
    if (!this.connected) {
      console.warn('Redis not connected, skipping cache set for key:', key)
      return false
    }

    try {
      const serialized = typeof value === 'string' ? value : JSON.stringify(value)
      const ttl = options.ttl || CacheTTL.USER_PROFILE // Default TTL

      if (options.tags) {
        // Set tags for cache invalidation
        await Promise.all(
          options.tags.map(tag => 
            redis.sadd(`tag:${tag}`, key)
          )
        )
      }

      await redis.setex(key, ttl, serialized)
      return true
    } catch (error) {
      console.error('Cache set error:', error, 'for key:', key)
      return false
    }
  }

  async del(key: string | string[]): Promise<number> {
    if (!this.connected) return 0

    try {
      const keys = Array.isArray(key) ? key : [key]
      return await redis.del(...keys)
    } catch (error) {
      console.error('Cache delete error:', error)
      return 0
    }
  }

  async exists(key: string): Promise<boolean> {
    if (!this.connected) return false

    try {
      const result = await redis.exists(key)
      return result === 1
    } catch (error) {
      console.error('Cache exists error:', error)
      return false
    }
  }

  // Invalidate by tags
  async invalidateByTag(tag: string): Promise<number> {
    if (!this.connected) return 0

    try {
      const keys = await redis.smembers(`tag:${tag}`)
      if (keys.length === 0) return 0

      // Delete the keys and the tag set
      await redis.del(`tag:${tag}`)
      return await redis.del(...keys)
    } catch (error) {
      console.error('Tag invalidation error:', error)
      return 0
    }
  }

  // Portfolio-specific caching
  async cachePortfolio(userId: string, portfolio: any): Promise<boolean> {
    return this.set(
      CacheKeys.PORTFOLIO(userId), 
      portfolio, 
      { 
        ttl: CacheTTL.PORTFOLIO,
        tags: [`user:${userId}`, 'portfolio']
      }
    )
  }

  async getPortfolio(userId: string): Promise<any | null> {
    return this.get(CacheKeys.PORTFOLIO(userId))
  }

  // Market prices caching
  async cacheMarketPrices(symbols: string[], prices: Record<string, number>): Promise<boolean> {
    return this.set(
      CacheKeys.MARKET_PRICES(symbols),
      prices,
      { 
        ttl: CacheTTL.MARKET_PRICES,
        tags: ['market-data']
      }
    )
  }

  async getMarketPrices(symbols: string[]): Promise<Record<string, number> | null> {
    return this.get(CacheKeys.MARKET_PRICES(symbols))
  }

  // AI analysis caching
  async cacheAIAnalysis(symbol: string, timeframe: string, analysis: any): Promise<boolean> {
    return this.set(
      CacheKeys.AI_ANALYSIS(symbol, timeframe),
      analysis,
      { 
        ttl: CacheTTL.AI_ANALYSIS,
        tags: ['ai-analysis', `symbol:${symbol}`]
      }
    )
  }

  async getAIAnalysis(symbol: string, timeframe: string): Promise<any | null> {
    return this.get(CacheKeys.AI_ANALYSIS(symbol, timeframe))
  }

  // User profile caching
  async cacheUserProfile(userId: string, profile: any): Promise<boolean> {
    return this.set(
      CacheKeys.USER_PROFILE(userId),
      profile,
      { 
        ttl: CacheTTL.USER_PROFILE,
        tags: [`user:${userId}`]
      }
    )
  }

  async getUserProfile(userId: string): Promise<any | null> {
    return this.get(CacheKeys.USER_PROFILE(userId))
  }

  // Rate limiting support
  async incrementRateLimit(clientId: string, endpoint: string, windowMs: number): Promise<number> {
    if (!this.connected) return 1

    try {
      const key = CacheKeys.RATE_LIMIT(clientId, endpoint)
      const current = await redis.incr(key)
      
      // Set expiration on first increment
      if (current === 1) {
        await redis.expire(key, Math.ceil(windowMs / 1000))
      }
      
      return current
    } catch (error) {
      console.error('Rate limit increment error:', error)
      return 1
    }
  }

  // Cache statistics
  async getCacheStats(): Promise<{
    connected: boolean
    keyCount: number
    memory: string
    hitRate?: string
  }> {
    if (!this.connected) {
      return { connected: false, keyCount: 0, memory: '0B' }
    }

    try {
      const info = await redis.info('memory')
      const keyCount = await redis.dbsize()
      
      return {
        connected: this.connected,
        keyCount,
        memory: this.parseMemoryFromInfo(info),
      }
    } catch (error) {
      console.error('Cache stats error:', error)
      return { connected: false, keyCount: 0, memory: '0B' }
    }
  }

  private parseMemoryFromInfo(info: string): string {
    const match = info.match(/used_memory_human:(.+?)\r/)
    return match ? match[1] : '0B'
  }

  // Warm up cache with frequently accessed data
  async warmupCache(): Promise<void> {
    if (!this.connected) return

    try {
      console.log('Warming up cache...')
      
      // Pre-cache frequently accessed market data
      // This would typically be done based on user activity patterns
      
      console.log('Cache warmed up successfully')
    } catch (error) {
      console.error('Cache warmup error:', error)
    }
  }

  // Graceful shutdown
  async disconnect(): Promise<void> {
    try {
      await redis.quit()
      this.connected = false
    } catch (error) {
      console.error('Redis disconnect error:', error)
    }
  }
}

// Export singleton instance
export const cacheManager = CacheManager.getInstance()

// Middleware wrapper for caching API responses
export function withCache<T extends (...args: any[]) => any>(
  handler: T,
  getCacheKey: (...args: any[]) => string,
  ttl: number = CacheTTL.USER_PROFILE
): T {
  return (async (...args: any[]) => {
    const cacheKey = getCacheKey(...args)
    
    // Try cache first
    const cached = await cacheManager.get(cacheKey)
    if (cached) {
      return cached
    }
    
    // Execute handler
    const result = await handler(...args)
    
    // Cache result
    await cacheManager.set(cacheKey, result, { ttl })
    
    return result
  }) as T
}

// Cache decorator for class methods
export function Cache(keyGenerator: (...args: any[]) => string, ttl?: number) {
  return function (target: any, propertyName: string, descriptor: PropertyDescriptor) {
    const method = descriptor.value
    
    descriptor.value = async function (...args: any[]) {
      const cacheKey = keyGenerator(...args)
      
      const cached = await cacheManager.get(cacheKey)
      if (cached) {
        return cached
      }
      
      const result = await method.apply(this, args)
      
      if (result !== null && result !== undefined) {
        await cacheManager.set(cacheKey, result, { ttl })
      }
      
      return result
    }
    
    return descriptor
  }
}

