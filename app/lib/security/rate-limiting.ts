
/**
 * 🔐 ADVANCED RATE LIMITING SYSTEM
 * Multi-tier rate limiting for different API endpoints
 */

import { NextRequest, NextResponse } from 'next/server'
import { headers } from 'next/headers'

interface RateLimitConfig {
  windowMs: number
  maxRequests: number
  message?: string
  skipSuccessfulRequests?: boolean
  skipFailedRequests?: boolean
}

interface RateLimitStore {
  [key: string]: {
    count: number
    resetTime: number
  }
}

class RateLimitManager {
  private store: RateLimitStore = {}

  // Different rate limits for different endpoint types
  private static configs: Record<string, RateLimitConfig> = {
    // Trading endpoints - very strict
    'trading': {
      windowMs: 60 * 1000, // 1 minute
      maxRequests: 10,
      message: 'Too many trading requests. Please slow down for security.',
    },
    
    // Siphon endpoints - strict
    'siphon': {
      windowMs: 60 * 60 * 1000, // 1 hour
      maxRequests: 5,
      message: 'Siphon operations are limited to 5 per hour for security.',
    },
    
    // Vault operations - strict
    'vault': {
      windowMs: 60 * 1000, // 1 minute
      maxRequests: 20,
      message: 'Too many vault requests. Please wait before trying again.',
    },
    
    // Portfolio/analytics - moderate
    'portfolio': {
      windowMs: 60 * 1000, // 1 minute
      maxRequests: 100,
      message: 'Too many portfolio requests. Please slow down.',
    },
    
    // Authentication - strict
    'auth': {
      windowMs: 15 * 60 * 1000, // 15 minutes
      maxRequests: 5,
      message: 'Too many authentication attempts. Please try again later.',
    },
    
    // General API - moderate
    'general': {
      windowMs: 60 * 1000, // 1 minute
      maxRequests: 100,
      message: 'Too many requests. Please slow down.',
    }
  }

  private getClientIdentifier(request: NextRequest): string {
    // Try to get user ID from token, fallback to IP
    const authHeader = request.headers.get('authorization')
    if (authHeader) {
      try {
        // Extract user ID from JWT token (simplified)
        const token = authHeader.replace('Bearer ', '')
        const payload = JSON.parse(atob(token.split('.')[1]))
        return `user:${payload.sub || payload.userId}`
      } catch (error) {
        // Fallback to IP if token parsing fails
      }
    }
    
    // Get IP address
    const forwarded = request.headers.get('x-forwarded-for')
    const ip = forwarded ? forwarded.split(',')[0] : 'unknown'
    return `ip:${ip}`
  }

  private getEndpointType(pathname: string): string {
    if (pathname.includes('/trading/')) return 'trading'
    if (pathname.includes('/siphon/')) return 'siphon'
    if (pathname.includes('/vault/')) return 'vault'
    if (pathname.includes('/portfolio/')) return 'portfolio'
    if (pathname.includes('/auth/') || pathname.includes('/signup')) return 'auth'
    return 'general'
  }

  checkRateLimit(request: NextRequest): {
    allowed: boolean
    remaining: number
    resetTime: number
    message?: string
  } {
    const clientId = this.getClientIdentifier(request)
    const endpointType = this.getEndpointType(request.nextUrl.pathname)
    const config = (RateLimitManager as any).configs[endpointType]
    
    const key = `${clientId}:${endpointType}`
    const now = Date.now()
    
    // Clean expired entries
    if (this.store[key] && now > this.store[key].resetTime) {
      delete this.store[key]
    }
    
    // Initialize or increment counter
    if (!this.store[key]) {
      this.store[key] = {
        count: 1,
        resetTime: now + config.windowMs
      }
      return {
        allowed: true,
        remaining: config.maxRequests - 1,
        resetTime: this.store[key].resetTime
      }
    }
    
    this.store[key].count++
    
    const remaining = Math.max(0, config.maxRequests - this.store[key].count)
    const allowed = this.store[key].count <= config.maxRequests
    
    return {
      allowed,
      remaining,
      resetTime: this.store[key].resetTime,
      message: allowed ? undefined : config.message
    }
  }

  // Clean up expired entries periodically
  cleanup() {
    const now = Date.now()
    Object.keys(this.store).forEach(key => {
      if (now > this.store[key].resetTime) {
        delete this.store[key]
      }
    })
  }
}

// Singleton instance
const rateLimitManager = new RateLimitManager()

// Cleanup every 5 minutes
setInterval(() => rateLimitManager.cleanup(), 5 * 60 * 1000)

export function createRateLimitMiddleware() {
  return (request: NextRequest) => {
    const result = rateLimitManager.checkRateLimit(request)
    
    const headers = new Headers()
    headers.set('X-RateLimit-Limit', '100') // Default general limit
    headers.set('X-RateLimit-Remaining', result.remaining.toString())
    headers.set('X-RateLimit-Reset', Math.ceil(result.resetTime / 1000).toString())
    
    if (!result.allowed) {
      return NextResponse.json(
        { 
          error: result.message || 'Rate limit exceeded',
          retryAfter: Math.ceil((result.resetTime - Date.now()) / 1000)
        },
        { 
          status: 429,
          headers
        }
      )
    }
    
    return { headers }
  }
}

export { rateLimitManager }

