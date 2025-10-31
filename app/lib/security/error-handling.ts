
/**
 * ⚠️ COMPREHENSIVE ERROR HANDLING SYSTEM
 * Secure error handling that prevents information leakage
 */

import { NextRequest, NextResponse } from 'next/server'
import { auditLogger, AuditAction, AuditSeverity } from './audit-logging'
import winston from 'winston'

// Error types for different scenarios
export enum ErrorType {
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR',
  AUTHORIZATION_ERROR = 'AUTHORIZATION_ERROR',
  RATE_LIMIT_ERROR = 'RATE_LIMIT_ERROR',
  EXTERNAL_SERVICE_ERROR = 'EXTERNAL_SERVICE_ERROR',
  DATABASE_ERROR = 'DATABASE_ERROR',
  TRADING_ERROR = 'TRADING_ERROR',
  SIPHON_ERROR = 'SIPHON_ERROR',
  VAULT_ERROR = 'VAULT_ERROR',
  NETWORK_ERROR = 'NETWORK_ERROR',
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  SECURITY_ERROR = 'SECURITY_ERROR',
}

export interface AppError extends Error {
  type: ErrorType
  statusCode: number
  isOperational: boolean
  context?: Record<string, any>
  originalError?: Error
}

export class CustomError extends Error implements AppError {
  public readonly type: ErrorType
  public readonly statusCode: number
  public readonly isOperational: boolean
  public readonly context?: Record<string, any>
  public readonly originalError?: Error

  constructor(
    message: string,
    type: ErrorType,
    statusCode: number = 500,
    isOperational: boolean = true,
    context?: Record<string, any>,
    originalError?: Error
  ) {
    super(message)
    
    this.name = this.constructor.name
    this.type = type
    this.statusCode = statusCode
    this.isOperational = isOperational
    this.context = context
    this.originalError = originalError

    Error.captureStackTrace(this, this.constructor)
  }
}

// Specific error classes
export class ValidationError extends CustomError {
  constructor(message: string, context?: Record<string, any>) {
    super(message, ErrorType.VALIDATION_ERROR, 400, true, context)
  }
}

export class AuthenticationError extends CustomError {
  constructor(message: string = 'Authentication required', context?: Record<string, any>) {
    super(message, ErrorType.AUTHENTICATION_ERROR, 401, true, context)
  }
}

export class AuthorizationError extends CustomError {
  constructor(message: string = 'Insufficient permissions', context?: Record<string, any>) {
    super(message, ErrorType.AUTHORIZATION_ERROR, 403, true, context)
  }
}

export class RateLimitError extends CustomError {
  constructor(message: string = 'Rate limit exceeded', context?: Record<string, any>) {
    super(message, ErrorType.RATE_LIMIT_ERROR, 429, true, context)
  }
}

export class TradingError extends CustomError {
  constructor(message: string, context?: Record<string, any>, originalError?: Error) {
    super(message, ErrorType.TRADING_ERROR, 400, true, context, originalError)
  }
}

export class SiphonError extends CustomError {
  constructor(message: string, context?: Record<string, any>, originalError?: Error) {
    super(message, ErrorType.SIPHON_ERROR, 400, true, context, originalError)
  }
}

export class VaultError extends CustomError {
  constructor(message: string, context?: Record<string, any>, originalError?: Error) {
    super(message, ErrorType.VAULT_ERROR, 400, true, context, originalError)
  }
}

export class ExternalServiceError extends CustomError {
  constructor(service: string, originalError?: Error) {
    super(
      `External service temporarily unavailable: ${service}`, 
      ErrorType.EXTERNAL_SERVICE_ERROR, 
      503, 
      true, 
      { service }, 
      originalError
    )
  }
}

export class DatabaseError extends CustomError {
  constructor(operation: string, originalError?: Error) {
    super(
      'Database operation failed', 
      ErrorType.DATABASE_ERROR, 
      500, 
      false, 
      { operation }, 
      originalError
    )
  }
}

export class SecurityError extends CustomError {
  constructor(message: string, context?: Record<string, any>) {
    super(message, ErrorType.SECURITY_ERROR, 403, true, context)
  }
}

// Error sanitization - remove sensitive information before sending to client
function sanitizeErrorForClient(error: AppError): any {
  const sanitized: any = {
    type: error.type,
    message: error.message,
    timestamp: new Date().toISOString(),
  }

  // Only include certain context fields for client
  if (error.context) {
    const allowedContextFields = ['field', 'symbol', 'side', 'operation', 'retryAfter']
    const sanitizedContext: Record<string, any> = {}
    
    allowedContextFields.forEach(field => {
      if (error.context && error.context[field] !== undefined) {
        sanitizedContext[field] = error.context[field]
      }
    })
    
    if (Object.keys(sanitizedContext).length > 0) {
      sanitized.context = sanitizedContext
    }
  }

  // Add helpful information based on error type
  switch (error.type) {
    case ErrorType.RATE_LIMIT_ERROR:
      sanitized.retryAfter = error.context?.retryAfter || 60
      break
    case ErrorType.EXTERNAL_SERVICE_ERROR:
      sanitized.message = 'External service temporarily unavailable. Please try again later.'
      break
    case ErrorType.DATABASE_ERROR:
      sanitized.message = 'Service temporarily unavailable. Please try again later.'
      break
    case ErrorType.INTERNAL_ERROR:
      sanitized.message = 'An internal error occurred. Please contact support if this persists.'
      break
  }

  return sanitized
}

// Error response formatter
function formatErrorResponse(error: AppError, requestId?: string): NextResponse {
  const sanitizedError = sanitizeErrorForClient(error)
  
  const response = {
    error: sanitizedError,
    requestId,
    support: process.env.NODE_ENV === 'production' 
      ? 'Contact support at support@sovereignlegacyloop.com' 
      : 'Development mode - check server logs',
  }

  return NextResponse.json(response, {
    status: error.statusCode,
    headers: {
      'X-Error-Type': error.type,
      'X-Request-ID': requestId || 'unknown',
    },
  })
}

// Global error handler
export async function handleError(
  error: Error | AppError,
  request?: NextRequest,
  requestId?: string
): Promise<NextResponse> {
  const isAppError = error instanceof CustomError
  const appError: AppError = isAppError 
    ? error as AppError
    : new CustomError(
        'An unexpected error occurred',
        ErrorType.INTERNAL_ERROR,
        500,
        false,
        undefined,
        error
      )

  // Log error with appropriate severity
  const severity = appError.statusCode >= 500 ? AuditSeverity.HIGH : AuditSeverity.MEDIUM
  const action = appError.statusCode >= 500 ? AuditAction.API_ERROR : AuditAction.INVALID_INPUT

  // Prepare audit log metadata
  const auditMetadata: Record<string, any> = {
    errorType: appError.type,
    statusCode: appError.statusCode,
    isOperational: appError.isOperational,
    requestId,
  }

  // Add context if available (sanitized)
  if (appError.context) {
    auditMetadata.context = appError.context
  }

  // Add original error details for internal errors
  if (!appError.isOperational && appError.originalError) {
    auditMetadata.originalError = {
      name: appError.originalError.name,
      message: appError.originalError.message,
      stack: appError.originalError.stack,
    }
  }

  // Log to audit system
  try {
    await auditLogger.logAudit({
      action,
      resource: request?.nextUrl?.pathname || 'unknown',
      severity,
      metadata: auditMetadata,
      success: false,
      errorMessage: appError.message,
      requestId,
    }, request)
  } catch (auditError) {
    // Fallback logging if audit fails
    console.error('Failed to log error to audit system:', auditError)
  }

  // Log to application logs
  const logger = winston.createLogger({
    level: 'error',
    format: winston.format.combine(
      winston.format.timestamp(),
      winston.format.errors({ stack: true }),
      winston.format.json()
    ),
    transports: [
      new winston.transports.Console(),
      new winston.transports.File({ filename: 'logs/error.log' }),
    ],
  })

  logger.error('Application error', {
    error: {
      name: appError.name,
      message: appError.message,
      type: appError.type,
      statusCode: appError.statusCode,
      isOperational: appError.isOperational,
      stack: appError.stack,
      context: appError.context,
    },
    request: request ? {
      method: request.method,
      url: request.url,
      userAgent: request.headers.get('user-agent'),
      ip: request.headers.get('x-forwarded-for') || 'unknown',
    } : null,
    requestId,
    timestamp: new Date().toISOString(),
  })

  // Send alerts for critical errors
  if (!appError.isOperational || appError.statusCode >= 500) {
    // In production, send alerts to monitoring services
    // await sendErrorAlert(appError, request, requestId)
  }

  return formatErrorResponse(appError, requestId)
}

// Middleware wrapper for error handling
export function withErrorHandling<T extends (...args: any[]) => any>(
  handler: T
): T {
  return (async (...args: any[]) => {
    const [request] = args
    const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

    try {
      return await handler(...args)
    } catch (error) {
      return await handleError(error as Error, request, requestId)
    }
  }) as T
}

// Promise wrapper for async operations
export async function safeAsync<T>(
  operation: () => Promise<T>,
  errorType: ErrorType,
  errorMessage: string,
  context?: Record<string, any>
): Promise<T> {
  try {
    return await operation()
  } catch (error) {
    throw new CustomError(
      errorMessage,
      errorType,
      500,
      true,
      context,
      error as Error
    )
  }
}

// Database operation wrapper
export async function safeDatabaseOperation<T>(
  operation: () => Promise<T>,
  operationName: string
): Promise<T> {
  try {
    return await operation()
  } catch (error) {
    throw new DatabaseError(operationName, error as Error)
  }
}

// External service operation wrapper
export async function safeExternalServiceCall<T>(
  operation: () => Promise<T>,
  serviceName: string
): Promise<T> {
  try {
    return await operation()
  } catch (error) {
    throw new ExternalServiceError(serviceName, error as Error)
  }
}

// Input validation wrapper
export function validateInput<T>(
  input: T,
  validator: (input: T) => boolean,
  errorMessage: string,
  context?: Record<string, any>
): T {
  if (!validator(input)) {
    throw new ValidationError(errorMessage, context)
  }
  return input
}

