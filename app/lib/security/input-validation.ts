
/**
 * 🛡️ COMPREHENSIVE INPUT VALIDATION SYSTEM
 * Enterprise-grade validation for all user inputs
 */

import Joi from 'joi'
import { NextRequest } from 'next/server'

// Custom validation schemas for financial data
const tradingOrderSchema = Joi.object({
  symbol: Joi.string()
    .alphanum()
    .min(3)
    .max(12)
    .required()
    .messages({
      'string.alphanum': 'Symbol must contain only alphanumeric characters',
      'string.min': 'Symbol must be at least 3 characters',
      'string.max': 'Symbol must not exceed 12 characters',
      'any.required': 'Symbol is required'
    }),
    
  side: Joi.string()
    .valid('BUY', 'SELL')
    .required()
    .messages({
      'any.only': 'Side must be either BUY or SELL',
      'any.required': 'Side is required'
    }),
    
  type: Joi.string()
    .valid('MARKET', 'LIMIT', 'STOP_LOSS', 'TAKE_PROFIT', 'OCO')
    .default('MARKET')
    .messages({
      'any.only': 'Invalid order type'
    }),
    
  quantity: Joi.number()
    .positive()
    .precision(8) // 8 decimal places for crypto
    .min(0.00000001)
    .max(1000000)
    .required()
    .messages({
      'number.positive': 'Quantity must be positive',
      'number.min': 'Quantity must be at least 0.00000001',
      'number.max': 'Quantity exceeds maximum allowed',
      'any.required': 'Quantity is required'
    }),
    
  price: Joi.number()
    .positive()
    .precision(2)
    .when('type', {
      is: 'MARKET',
      then: Joi.optional(),
      otherwise: Joi.required()
    })
    .messages({
      'number.positive': 'Price must be positive',
      'any.required': 'Price is required for non-market orders'
    }),
    
  stopPrice: Joi.number()
    .positive()
    .precision(2)
    .when('type', {
      is: Joi.string().valid('STOP_LOSS', 'TAKE_PROFIT', 'OCO'),
      then: Joi.required(),
      otherwise: Joi.optional()
    }),
    
  timeInForce: Joi.string()
    .valid('GTC', 'IOC', 'FOK')
    .default('GTC'),
    
  executionStrategy: Joi.string()
    .valid('AGGRESSIVE', 'CONSERVATIVE', 'BALANCED')
    .default('BALANCED'),
    
  riskLevel: Joi.string()
    .valid('LOW', 'MEDIUM', 'HIGH')
    .default('MEDIUM'),
    
  maxLoss: Joi.number()
    .positive()
    .precision(2)
    .optional(),
    
  expectedProfit: Joi.number()
    .positive()
    .precision(2)
    .optional()
})

const siphonConfigSchema = Joi.object({
  thresholdAmount: Joi.number()
    .positive()
    .precision(2)
    .min(1)
    .max(1000000)
    .required()
    .messages({
      'number.positive': 'Threshold amount must be positive',
      'number.min': 'Threshold amount must be at least $1',
      'any.required': 'Threshold amount is required'
    }),
    
  baseSiphonRatio: Joi.number()
    .min(0)
    .max(1)
    .precision(3)
    .default(0.7)
    .messages({
      'number.min': 'Siphon ratio must be between 0 and 1',
      'number.max': 'Siphon ratio must be between 0 and 1'
    }),
    
  baseRetentionRatio: Joi.number()
    .min(0)
    .max(1)
    .precision(3)
    .default(0.3),
    
  volatilityAdjustment: Joi.number()
    .min(0)
    .max(1)
    .precision(3)
    .default(0.1),
    
  realTimeTracking: Joi.boolean()
    .default(true),
    
  feeOptimization: Joi.boolean()
    .default(true),
    
  autoTrigger: Joi.boolean()
    .default(false),
    
  minProfitThreshold: Joi.number()
    .positive()
    .precision(2)
    .min(1)
    .required(),
    
  maxHotRetention: Joi.number()
    .positive()
    .precision(2)
    .min(100)
    .max(100000)
    .required(),
    
  emergencyVaultRatio: Joi.number()
    .min(0.5)
    .max(1)
    .precision(3)
    .default(0.9),
    
  emergencyMode: Joi.boolean()
    .default(false)
})

const userRegistrationSchema = Joi.object({
  username: Joi.string()
    .alphanum()
    .min(3)
    .max(30)
    .required()
    .messages({
      'string.alphanum': 'Username must contain only letters and numbers',
      'string.min': 'Username must be at least 3 characters',
      'string.max': 'Username must not exceed 30 characters'
    }),
    
  email: Joi.string()
    .email()
    .required()
    .messages({
      'string.email': 'Please provide a valid email address'
    }),
    
  password: Joi.string()
    .min(8)
    .max(128)
    .pattern(new RegExp('^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])'))
    .required()
    .messages({
      'string.min': 'Password must be at least 8 characters',
      'string.max': 'Password must not exceed 128 characters',
      'string.pattern.base': 'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character'
    }),
    
  acceptTerms: Joi.boolean()
    .valid(true)
    .required()
    .messages({
      'any.only': 'You must accept the terms and conditions'
    })
})

const portfolioUpdateSchema = Joi.object({
  symbol: Joi.string()
    .alphanum()
    .min(3)
    .max(12)
    .required(),
    
  asset: Joi.string()
    .min(1)
    .max(100)
    .required(),
    
  quantity: Joi.number()
    .positive()
    .precision(8)
    .required(),
    
  avgBuyPrice: Joi.number()
    .positive()
    .precision(2)
    .required(),
    
  currentPrice: Joi.number()
    .positive()
    .precision(2)
    .required()
})

// Sanitization functions
export function sanitizeString(input: string): string {
  if (typeof input !== 'string') return ''
  
  return input
    .trim()
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '') // Remove script tags
    .replace(/[<>]/g, '') // Remove < and >
    .replace(/javascript:/gi, '') // Remove javascript: protocol
    .replace(/on\w+="[^"]*"/gi, '') // Remove event handlers
    .slice(0, 1000) // Limit length
}

export function sanitizeNumber(input: any): number | null {
  const num = Number(input)
  if (isNaN(num) || !isFinite(num)) return null
  return num
}

export function sanitizeBoolean(input: any): boolean {
  return Boolean(input)
}

// Validation functions
export async function validateTradingOrder(data: any) {
  try {
    const sanitizedData = {
      symbol: sanitizeString(data.symbol?.toString().toUpperCase() || ''),
      side: sanitizeString(data.side?.toString().toUpperCase() || ''),
      type: sanitizeString(data.type?.toString().toUpperCase() || 'MARKET'),
      quantity: sanitizeNumber(data.quantity),
      price: data.price ? sanitizeNumber(data.price) : undefined,
      stopPrice: data.stopPrice ? sanitizeNumber(data.stopPrice) : undefined,
      timeInForce: sanitizeString(data.timeInForce?.toString().toUpperCase() || 'GTC'),
      executionStrategy: sanitizeString(data.executionStrategy?.toString().toUpperCase() || 'BALANCED'),
      riskLevel: sanitizeString(data.riskLevel?.toString().toUpperCase() || 'MEDIUM'),
      maxLoss: data.maxLoss ? sanitizeNumber(data.maxLoss) : undefined,
      expectedProfit: data.expectedProfit ? sanitizeNumber(data.expectedProfit) : undefined,
    }
    
    const { error, value } = tradingOrderSchema.validate(sanitizedData, { 
      abortEarly: false,
      stripUnknown: true
    })
    
    if (error) {
      return {
        isValid: false,
        errors: error.details.map((detail: any) => ({
          field: detail.path.join('.'),
          message: detail.message,
          value: detail.context?.value
        })),
        data: null
      }
    }
    
    return {
      isValid: true,
      errors: [],
      data: value
    }
  } catch (error) {
    return {
      isValid: false,
      errors: [{ field: 'general', message: 'Invalid input format' }],
      data: null
    }
  }
}

export async function validateSiphonConfig(data: any) {
  try {
    const sanitizedData = {
      thresholdAmount: sanitizeNumber(data.thresholdAmount),
      baseSiphonRatio: sanitizeNumber(data.baseSiphonRatio),
      baseRetentionRatio: sanitizeNumber(data.baseRetentionRatio),
      volatilityAdjustment: sanitizeNumber(data.volatilityAdjustment),
      realTimeTracking: sanitizeBoolean(data.realTimeTracking),
      feeOptimization: sanitizeBoolean(data.feeOptimization),
      autoTrigger: sanitizeBoolean(data.autoTrigger),
      minProfitThreshold: sanitizeNumber(data.minProfitThreshold),
      maxHotRetention: sanitizeNumber(data.maxHotRetention),
      emergencyVaultRatio: sanitizeNumber(data.emergencyVaultRatio),
      emergencyMode: sanitizeBoolean(data.emergencyMode),
    }
    
    const { error, value } = siphonConfigSchema.validate(sanitizedData, { 
      abortEarly: false,
      stripUnknown: true
    })
    
    if (error) {
      return {
        isValid: false,
        errors: error.details.map((detail: any) => ({
          field: detail.path.join('.'),
          message: detail.message
        })),
        data: null
      }
    }
    
    return {
      isValid: true,
      errors: [],
      data: value
    }
  } catch (error) {
    return {
      isValid: false,
      errors: [{ field: 'general', message: 'Invalid input format' }],
      data: null
    }
  }
}

export async function validateUserRegistration(data: any) {
  try {
    const sanitizedData = {
      username: sanitizeString(data.username || ''),
      email: sanitizeString(data.email || '').toLowerCase(),
      password: data.password || '', // Don't sanitize passwords
      acceptTerms: sanitizeBoolean(data.acceptTerms),
    }
    
    const { error, value } = userRegistrationSchema.validate(sanitizedData, { 
      abortEarly: false,
      stripUnknown: true
    })
    
    if (error) {
      return {
        isValid: false,
        errors: error.details.map((detail: any) => ({
          field: detail.path.join('.'),
          message: detail.message
        })),
        data: null
      }
    }
    
    return {
      isValid: true,
      errors: [],
      data: value
    }
  } catch (error) {
    return {
      isValid: false,
      errors: [{ field: 'general', message: 'Invalid input format' }],
      data: null
    }
  }
}

// Middleware wrapper for automatic validation
export function createValidationMiddleware(schema: 'trading' | 'siphon' | 'user' | 'portfolio') {
  return async (request: NextRequest) => {
    try {
      const body = await request.json()
      
      let validationResult
      switch (schema) {
        case 'trading':
          validationResult = await validateTradingOrder(body)
          break
        case 'siphon':
          validationResult = await validateSiphonConfig(body)
          break
        case 'user':
          validationResult = await validateUserRegistration(body)
          break
        default:
          throw new Error('Unknown validation schema')
      }
      
      if (!validationResult.isValid) {
        return {
          isValid: false,
          response: Response.json(
            { 
              error: 'Validation failed',
              errors: validationResult.errors 
            },
            { status: 400 }
          )
        }
      }
      
      return {
        isValid: true,
        data: validationResult.data
      }
    } catch (error) {
      return {
        isValid: false,
        response: Response.json(
          { error: 'Invalid request format' },
          { status: 400 }
        )
      }
    }
  }
}

