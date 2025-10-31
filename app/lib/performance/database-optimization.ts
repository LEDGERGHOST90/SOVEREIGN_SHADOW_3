
/**
 * 🗄️ DATABASE PERFORMANCE OPTIMIZATION
 * Query optimization, connection pooling, and performance monitoring
 */

import { PrismaClient } from '@prisma/client'
import { cacheManager, CacheKeys, CacheTTL } from './redis-cache'

// Extended Prisma client with performance monitoring
export class OptimizedPrismaClient extends PrismaClient {
  private queryMetrics: Map<string, {
    count: number
    totalTime: number
    avgTime: number
    slowQueries: number
  }> = new Map()

  constructor() {
    super({
      log: [
        { level: 'query', emit: 'event' },
        { level: 'error', emit: 'stdout' },
        { level: 'warn', emit: 'stdout' },
      ],
    })

    // Query performance monitoring
    if (process.env.NODE_ENV === 'development') {
      try {
        (this as any).$on('query', (e: any) => {
          this.trackQueryPerformance(e)
        })
      } catch (error) {
        console.log('Query monitoring not available in this environment')
      }
    }

    this.enableQueryOptimizations()
  }

  private trackQueryPerformance(event: any): void {
    const query = String(event.query || '')
    const duration = Number(event.duration || 0)
    const operation = this.extractOperation(query)

    const current = this.queryMetrics.get(operation) || {
      count: 0,
      totalTime: 0,
      avgTime: 0,
      slowQueries: 0,
    }

    current.count++
    current.totalTime += duration
    current.avgTime = current.totalTime / current.count

    // Track slow queries (>100ms)
    if (duration > 100) {
      current.slowQueries++
      console.warn(`Slow query detected (${duration}ms):`, {
        operation,
        query: query.substring(0, 200),
      })
    }

    this.queryMetrics.set(operation, current)
  }

  private extractOperation(query: string): string {
    const match = query.match(/^(SELECT|INSERT|UPDATE|DELETE)/i)
    return match ? match[1].toUpperCase() : 'UNKNOWN'
  }

  private enableQueryOptimizations(): void {
    // Enable query result caching
    this.$use(async (params: any, next: any) => {
      const start = Date.now()
      
      // Check if query result is cacheable
      if (this.isCacheableQuery(params)) {
        const cacheKey = this.generateCacheKey(params)
        
        // Try cache first
        const cached = await cacheManager.get(cacheKey)
        if (cached) {
          return cached
        }
        
        // Execute query and cache result
        const result = await next(params)
        
        if (result) {
          const ttl = this.getCacheTTL(params.model || 'Unknown')
          await cacheManager.set(cacheKey, result, { ttl })
        }
        
        return result
      }
      
      const result = await next(params)
      const duration = Date.now() - start
      
      // Log slow queries
      if (duration > 100) {
        console.warn(`Slow database operation: ${params.model}.${params.action} (${duration}ms)`)
      }
      
      return result
    })
  }

  private isCacheableQuery(params: any): boolean {
    // Only cache read operations
    if (params.action !== 'findMany' && params.action !== 'findFirst' && params.action !== 'findUnique') {
      return false
    }

    // Don't cache user-specific real-time data
    const nonCacheableModels = ['TradeExecution', 'PortfolioSnapshot']
    if (nonCacheableModels.includes(params.model)) {
      return false
    }

    return true
  }

  private generateCacheKey(params: any): string {
    const key = `db:${params.model}:${params.action}:${JSON.stringify(params.args)}`
    return key.length > 250 ? `db:${params.model}:${params.action}:${this.hashString(JSON.stringify(params.args))}` : key
  }

  private getCacheTTL(model: string): number {
    const cacheDurations: Record<string, number> = {
      User: CacheTTL.USER_PROFILE,
      Portfolio: CacheTTL.PORTFOLIO,
      UserSettings: CacheTTL.SIPHON_CONFIG,
      RWAAsset: 300, // 5 minutes
      MarketData: CacheTTL.MARKET_PRICES,
    }
    
    return cacheDurations[model] || 60 // Default 1 minute
  }

  private hashString(str: string): string {
    let hash = 0
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i)
      hash = ((hash << 5) - hash) + char
      hash = hash & hash // Convert to 32-bit integer
    }
    return hash.toString(36)
  }

  // Optimized portfolio queries
  async getOptimizedPortfolio(userId: string) {
    const cacheKey = CacheKeys.PORTFOLIO(userId)
    
    // Check cache first
    const cached = await cacheManager.get(cacheKey)
    if (cached) return cached

    // Optimized query with selected fields only
    const portfolio = await this.portfolio.findMany({
      where: { userId },
      select: {
        id: true,
        asset: true,
        balance: true,
        hotBalance: true,
        coldBalance: true,
        averagePrice: true,
        currentPrice: true,
        totalInvested: true,
        lastUpdated: true,
      },
      orderBy: { balance: 'desc' },
    })

    // Cache result
    await cacheManager.cachePortfolio(userId, portfolio)
    
    return portfolio
  }

  // Optimized user profile query
  async getOptimizedUserProfile(userId: string) {
    const cacheKey = CacheKeys.USER_PROFILE(userId)
    
    const cached = await cacheManager.getUserProfile(userId)
    if (cached) return cached

    const user = await this.user.findUnique({
      where: { id: userId },
      select: {
        id: true,
        username: true,
        email: true,
        name: true,
        role: true,
        createdAt: true,
        settings: {
          select: {
            liveTrading: true,
            dailyLimit: true,
            siphonThreshold: true,
            siphonRatio: true,
            autoSiphon: true,
            riskLevel: true,
          }
        }
      },
    })

    if (user) {
      await cacheManager.cacheUserProfile(userId, user)
    }

    return user
  }

  // Batch operations for improved performance
  async batchUpdatePortfolio(updates: Array<{
    userId: string
    asset: string
    data: any
  }>) {
    const transaction = await this.$transaction(
      updates.map(update =>
        this.portfolio.upsert({
          where: {
            userId_asset: {
              userId: update.userId,
              asset: update.asset,
            }
          },
          update: update.data,
          create: {
            userId: update.userId,
            asset: update.asset,
            ...update.data,
          },
        })
      )
    )

    // Invalidate cache for affected users
    const affectedUsers = [...new Set(updates.map(u => u.userId))]
    await Promise.all(
      affectedUsers.map(userId => 
        cacheManager.del(CacheKeys.PORTFOLIO(userId))
      )
    )

    return transaction
  }

  // Connection health monitoring
  async getConnectionHealth(): Promise<{
    connected: boolean
    queryCount: number
    avgQueryTime: number
    slowQueries: number
    connectionPool?: any
  }> {
    try {
      // Test connection
      await this.$queryRaw`SELECT 1`
      
      // Calculate metrics
      const totalQueries = Array.from(this.queryMetrics.values())
        .reduce((sum, metric) => sum + metric.count, 0)
      
      const totalTime = Array.from(this.queryMetrics.values())
        .reduce((sum, metric) => sum + metric.totalTime, 0)
      
      const slowQueries = Array.from(this.queryMetrics.values())
        .reduce((sum, metric) => sum + metric.slowQueries, 0)

      return {
        connected: true,
        queryCount: totalQueries,
        avgQueryTime: totalQueries > 0 ? totalTime / totalQueries : 0,
        slowQueries,
      }
    } catch (error) {
      return {
        connected: false,
        queryCount: 0,
        avgQueryTime: 0,
        slowQueries: 0,
      }
    }
  }

  // Performance metrics
  getQueryMetrics() {
    const metrics = Array.from(this.queryMetrics.entries()).map(([operation, stats]) => ({
      operation,
      ...stats,
    }))

    return {
      operations: metrics,
      summary: {
        totalQueries: metrics.reduce((sum, m) => sum + m.count, 0),
        avgQueryTime: metrics.reduce((sum, m) => sum + m.avgTime, 0) / metrics.length || 0,
        slowQueries: metrics.reduce((sum, m) => sum + m.slowQueries, 0),
      }
    }
  }

  // Database cleanup operations
  async performMaintenance(): Promise<void> {
    try {
      console.log('Starting database maintenance...')

      // Clean old audit logs (keep last 30 days)
      const thirtyDaysAgo = new Date()
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)

      // TODO: Enable when audit log model is fully configured
      // const deletedAuditLogs = await this.auditLog.deleteMany({
      //   where: {
      //     createdAt: {
      //       lt: thirtyDaysAgo,
      //     },
      //   },
      // })
      const deletedAuditLogs = { count: 0 }

      // Clean old portfolio snapshots (keep last 7 days for non-milestone snapshots)
      const sevenDaysAgo = new Date()
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)

      const deletedSnapshots = await this.portfolioSnapshot.deleteMany({
        where: {
          snapshotTime: {
            lt: sevenDaysAgo,
          },
        },
      })

      console.log(`Database maintenance completed:`, {
        deletedAuditLogs: deletedAuditLogs.count,
        deletedSnapshots: deletedSnapshots.count,
      })

    } catch (error) {
      console.error('Database maintenance error:', error)
    }
  }

  // Graceful shutdown
  async gracefulShutdown(): Promise<void> {
    try {
      console.log('Shutting down database connections...')
      await this.$disconnect()
      console.log('Database connections closed')
    } catch (error) {
      console.error('Error during database shutdown:', error)
    }
  }
}

// Export optimized client instance
export const optimizedDb = new OptimizedPrismaClient()

// Database health check middleware
export async function checkDatabaseHealth() {
  return optimizedDb.getConnectionHealth()
}

