
import '@testing-library/jest-dom'

// Mock environment variables for tests
process.env.DATABASE_URL = 'postgresql://test:test@localhost:5432/test_db'
process.env.NEXTAUTH_SECRET = 'test-secret-key'
process.env.BINANCE_US_API_KEY = 'test-api-key'
process.env.BINANCE_US_SECRET_KEY = 'test-secret-key'
process.env.ABACUSAI_API_KEY = 'test-abacus-key'
process.env.NEXTAUTH_URL = 'http://localhost:3000'

// Mock Prisma
jest.mock('./lib/db', () => ({
  prisma: {
    user: {
      findFirst: jest.fn(),
      findUnique: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
      delete: jest.fn(),
    },
    portfolio: {
      findMany: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
    },
    trade: {
      findMany: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
    },
    tradeExecution: {
      create: jest.fn(),
      findMany: jest.fn(),
    },
    $transaction: jest.fn(),
  },
}))

// Mock fetch globally
global.fetch = jest.fn()

// Mock WebSocket for real-time features
global.WebSocket = jest.fn(() => ({
  close: jest.fn(),
  send: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
}))

// Suppress console errors in tests unless explicitly needed
const originalError = console.error
beforeAll(() => {
  console.error = (...args) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render is no longer supported')
    ) {
      return
    }
    originalError.call(console, ...args)
  }
})

afterAll(() => {
  console.error = originalError
})
