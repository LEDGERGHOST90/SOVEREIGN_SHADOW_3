
/**
 * 🛡️ SECURITY HEADERS MIDDLEWARE
 * Enterprise-grade security headers for all responses
 */

import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

interface SecurityHeadersConfig {
  contentSecurityPolicy?: boolean
  strictTransportSecurity?: boolean
  xFrameOptions?: boolean
  xContentTypeOptions?: boolean
  xXssProtection?: boolean
  referrerPolicy?: boolean
  permissionsPolicy?: boolean
}

const DEFAULT_CONFIG: SecurityHeadersConfig = {
  contentSecurityPolicy: true,
  strictTransportSecurity: true,
  xFrameOptions: true,
  xContentTypeOptions: true,
  xXssProtection: true,
  referrerPolicy: true,
  permissionsPolicy: true,
}

export function createSecurityHeaders(config: SecurityHeadersConfig = DEFAULT_CONFIG) {
  return (request: NextRequest, response: NextResponse) => {
    const headers = new Headers(response.headers)

    // Content Security Policy - Strict policy for financial app
    if (config.contentSecurityPolicy) {
      const csp = [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com https://static.cloudflareinsights.com", // Allow inline scripts for React + Cloudflare
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
        "img-src 'self' data: https: blob:",
        "font-src 'self' https://fonts.gstatic.com",
        "connect-src 'self' https://api.binance.us wss://stream.binance.us:9443 https://*.abacus.ai https://cloudflareinsights.com",
        "media-src 'self'",
        "object-src 'none'",
        "base-uri 'self'",
        "form-action 'self'",
        "frame-ancestors 'none'",
        "upgrade-insecure-requests",
        "block-all-mixed-content"
      ].join('; ')
      
      headers.set('Content-Security-Policy', csp)
    }

    // Strict Transport Security - Force HTTPS
    if (config.strictTransportSecurity) {
      headers.set('Strict-Transport-Security', 'max-age=63072000; includeSubDomains; preload')
    }

    // X-Frame-Options - Prevent clickjacking
    if (config.xFrameOptions) {
      headers.set('X-Frame-Options', 'DENY')
    }

    // X-Content-Type-Options - Prevent MIME sniffing
    if (config.xContentTypeOptions) {
      headers.set('X-Content-Type-Options', 'nosniff')
    }

    // X-XSS-Protection - Enable XSS filtering
    if (config.xXssProtection) {
      headers.set('X-XSS-Protection', '1; mode=block')
    }

    // Referrer Policy - Control referrer information
    if (config.referrerPolicy) {
      headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')
    }

    // Permissions Policy - Control browser features
    if (config.permissionsPolicy) {
      const permissions = [
        'camera=()',
        'microphone=()',
        'geolocation=()',
        'payment=*', // Allow payment features for financial app
        'fullscreen=*',
        'accelerometer=()',
        'gyroscope=()',
        'magnetometer=()',
        'usb=()',
        'bluetooth=()'
      ].join(', ')
      
      headers.set('Permissions-Policy', permissions)
    }

    // Additional security headers
    headers.set('X-DNS-Prefetch-Control', 'off')
    headers.set('X-Download-Options', 'noopen')
    headers.set('X-Permitted-Cross-Domain-Policies', 'none')
    headers.set('Cross-Origin-Embedder-Policy', 'require-corp')
    headers.set('Cross-Origin-Opener-Policy', 'same-origin')
    headers.set('Cross-Origin-Resource-Policy', 'same-site')

    // Remove server information
    headers.delete('X-Powered-By')
    headers.delete('Server')

    // Set secure cookie attributes globally
    const cookieHeader = headers.get('Set-Cookie')
    if (cookieHeader) {
      const secureCookie = cookieHeader.replace(
        /(?<!Secure)(; |$)/,
        '; Secure; SameSite=Strict$1'
      )
      headers.set('Set-Cookie', secureCookie)
    }

    return NextResponse.next({
      request: {
        headers: request.headers,
      },
      headers,
    })
  }
}

// CORS configuration for API endpoints
export function createCorsHeaders(request: NextRequest) {
  const origin = request.headers.get('origin')
  const allowedOrigins = [
    'http://localhost:3000',
    'https://localhost:3000',
    'https://sovereignlegacyloop.com', // Your production domain
    // Add other allowed origins
  ]

  const headers = new Headers()

  // Only allow specific origins
  if (origin && allowedOrigins.includes(origin)) {
    headers.set('Access-Control-Allow-Origin', origin)
  } else if (!origin) {
    // Allow same-origin requests (no origin header)
    headers.set('Access-Control-Allow-Origin', 'null')
  }

  // Specify allowed methods for financial API
  headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
  
  // Specify allowed headers
  headers.set('Access-Control-Allow-Headers', [
    'Content-Type',
    'Authorization',
    'X-Requested-With',
    'X-API-Key',
    'X-Request-ID'
  ].join(', '))

  // Allow credentials for authenticated requests
  headers.set('Access-Control-Allow-Credentials', 'true')

  // Set preflight cache time
  headers.set('Access-Control-Max-Age', '86400') // 24 hours

  // Security headers for CORS preflight
  headers.set('Vary', 'Origin, Access-Control-Request-Method, Access-Control-Request-Headers')

  return headers
}

// API-specific security headers
export function createApiSecurityHeaders() {
  const headers = new Headers()

  // API-specific security
  headers.set('X-Content-Type-Options', 'nosniff')
  headers.set('X-Frame-Options', 'DENY')
  headers.set('X-XSS-Protection', '1; mode=block')
  headers.set('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate')
  headers.set('Pragma', 'no-cache')
  headers.set('Expires', '0')
  headers.set('Surrogate-Control', 'no-store')

  // Rate limiting headers (will be set by rate limiter)
  // headers.set('X-RateLimit-Limit', '')
  // headers.set('X-RateLimit-Remaining', '')
  // headers.set('X-RateLimit-Reset', '')

  return headers
}

// Middleware wrapper for Next.js API routes
export function withSecurityHeaders<T extends (...args: any[]) => any>(
  handler: T,
  config?: SecurityHeadersConfig
): T {
  return (async (...args: any[]) => {
    const [request, ...restArgs] = args
    
    try {
      // Execute the original handler
      const response = await handler(request, ...restArgs)
      
      // Apply security headers
      const securityHeaders = createApiSecurityHeaders()
      
      // If response has headers, merge them
      if (response && response.headers) {
        securityHeaders.forEach((value, key) => {
          response.headers.set(key, value)
        })
      }
      
      return response
    } catch (error) {
      // Even on error, ensure security headers are applied
      const errorResponse = Response.json(
        { error: 'Internal server error' },
        { status: 500 }
      )
      
      const securityHeaders = createApiSecurityHeaders()
      securityHeaders.forEach((value, key) => {
        errorResponse.headers.set(key, value)
      })
      
      throw errorResponse
    }
  }) as T
}

// Security headers for static assets
export function createAssetSecurityHeaders() {
  const headers = new Headers()

  headers.set('X-Content-Type-Options', 'nosniff')
  headers.set('X-Frame-Options', 'DENY')
  headers.set('Cache-Control', 'public, max-age=31536000, immutable')
  headers.set('Cross-Origin-Resource-Policy', 'same-site')

  return headers
}

// Content Security Policy nonce generator
export function generateCSPNonce(): string {
  const nonce = Buffer.from(crypto.getRandomValues(new Uint8Array(16))).toString('base64')
  return nonce
}

// CSP violation reporting endpoint
export function createCSPViolationHandler() {
  return async (request: NextRequest) => {
    try {
      const violation = await request.json()
      
      // Log CSP violations for security monitoring
      console.warn('CSP Violation:', {
        documentUri: violation['document-uri'],
        violatedDirective: violation['violated-directive'],
        blockedUri: violation['blocked-uri'],
        lineNumber: violation['line-number'],
        sourceFile: violation['source-file'],
        timestamp: new Date().toISOString(),
      })

      // In production, send to security monitoring service
      // await sendToSecurityMonitoring(violation)

      return new Response('OK', { status: 200 })
    } catch (error) {
      console.error('Error handling CSP violation report:', error)
      return new Response('Error', { status: 500 })
    }
  }
}

