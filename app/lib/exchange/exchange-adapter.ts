/**
 * Trading modes to enforce safety
 */
export enum TradingMode {
  FAKE = 'FAKE',       // No real API calls, simulated responses
  SANDBOX = 'SANDBOX', // Using exchange sandbox/testnet APIs
  LIVE = 'LIVE'        // Live trading with real funds (requires explicit enablement)
}

/**
 * Order side (buy/sell)
 */
export enum OrderSide {
  BUY = 'BUY',
  SELL = 'SELL'
}

/**
 * Order type
 */
export enum OrderType {
  MARKET = 'MARKET',
  LIMIT = 'LIMIT',
  STOP_LOSS = 'STOP_LOSS',
  STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT',
  TAKE_PROFIT = 'TAKE_PROFIT',
  TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
}

/**
 * Time in force options
 */
export enum TimeInForce {
  GTC = 'GTC', // Good Till Canceled
  IOC = 'IOC', // Immediate or Cancel
  FOK = 'FOK'  // Fill or Kill
}

/**
 * Order status
 */
export enum OrderStatus {
  NEW = 'NEW',
  PARTIALLY_FILLED = 'PARTIALLY_FILLED',
  FILLED = 'FILLED',
  CANCELED = 'CANCELED',
  PENDING_CANCEL = 'PENDING_CANCEL',
  REJECTED = 'REJECTED',
  EXPIRED = 'EXPIRED'
}

/**
 * Standard balance format
 */
export interface Balance {
  asset: string;
  free: number;
  locked: number;
  total: number;
}

/**
 * Standard ticker format
 */
export interface Ticker {
  symbol: string;
  price: number;
  timestamp: number;
  volume: number;
  changePercent: number;
  exchange: string;
}

/**
 * Standard order format
 */
export interface Order {
  id: string;
  symbol: string;
  side: OrderSide;
  type: OrderType;
  quantity: number;
  price?: number;
  stopPrice?: number;
  status: OrderStatus;
  timeInForce?: TimeInForce;
  timestamp: number;
  filled: number;
  remaining: number;
  cost: number;
  fee: number;
  feeAsset: string;
  exchange: string;
}

/**
 * Standard trade format
 */
export interface Trade {
  id: string;
  orderId: string;
  symbol: string;
  side: OrderSide;
  price: number;
  quantity: number;
  cost: number;
  fee: number;
  feeAsset: string;
  timestamp: number;
  exchange: string;
}

/**
 * Request parameters for creating orders
 */
export interface CreateOrderParams {
  symbol: string;
  side: OrderSide;
  type: OrderType;
  quantity: number;
  price?: number;
  stopPrice?: number;
  timeInForce?: TimeInForce;
}

/**
 * Exchange adapter configuration
 */
export interface ExchangeConfig {
  apiKey: string;
  secretKey: string;
  passphrase?: string;
  mode: TradingMode;
  maxTradeAmountUsd: number;
  emergencyStopLossPercent: number;
}

/**
 * Standard interface for all exchange adapters
 */
export interface ExchangeAdapter {
  /**
   * Get the current trading mode (FAKE, SANDBOX, LIVE)
   */
  getTradingMode(): TradingMode;
  
  /**
   * Check if the adapter is properly configured and connected
   */
  isConnected(): Promise<boolean>;
  
  /**
   * Get account balances
   * @param assets Optional filter for specific assets
   */
  getBalances(assets?: string[]): Promise<Balance[]>;
  
  /**
   * Get current ticker information for symbols
   * @param symbols List of symbols to get tickers for
   */
  getTickers(symbols: string[]): Promise<Ticker[]>;
  
  /**
   * Create a new order
   * @param params Order parameters
   */
  createOrder(params: CreateOrderParams): Promise<Order>;
  
  /**
   * Cancel an existing order
   * @param symbol Trading pair symbol
   * @param orderId Order ID to cancel
   */
  cancelOrder(symbol: string, orderId: string): Promise<boolean>;
  
  /**
   * Get details of a specific order
   * @param symbol Trading pair symbol
   * @param orderId Order ID
   */
  getOrder(symbol: string, orderId: string): Promise<Order | null>;
  
  /**
   * Get open orders
   * @param symbol Optional symbol filter
   */
  getOpenOrders(symbol?: string): Promise<Order[]>;
  
  /**
   * Get historical trades
   * @param symbol Trading pair symbol
   * @param limit Maximum number of trades to return
   * @param fromId Optional starting trade ID
   */
  getMyTrades(symbol: string, limit?: number, fromId?: string): Promise<Trade[]>;
}

/**
 * Factory function to create the appropriate exchange adapter
 * @param exchange Exchange name
 * @param config Configuration parameters
 */
export async function createExchangeAdapter(
  exchange: 'binance' | 'okx' | 'coinbase',
  config: Partial<ExchangeConfig> = {}
): Promise<ExchangeAdapter> {
  // Determine trading mode with safety defaults
  let tradingMode = TradingMode.FAKE;
  
  if (process.env.DISABLE_REAL_EXCHANGES === 'true') {
    tradingMode = TradingMode.FAKE;
  } else if (config.mode === TradingMode.LIVE && process.env.ALLOW_LIVE_EXCHANGE === 'true') {
    tradingMode = TradingMode.LIVE;
  } else if (config.mode === TradingMode.SANDBOX) {
    tradingMode = TradingMode.SANDBOX;
  }
  
  // Apply defaults and environment overrides
  const safeConfig: ExchangeConfig = {
    apiKey: config.apiKey || '',
    secretKey: config.secretKey || '',
    passphrase: config.passphrase,
    mode: tradingMode,
    maxTradeAmountUsd: config.maxTradeAmountUsd || 
      parseFloat(process.env.MAX_TRADE_AMOUNT_USD || '100'),
    emergencyStopLossPercent: config.emergencyStopLossPercent ||
      parseFloat(process.env.EMERGENCY_STOP_LOSS_PERCENT || '5'),
  };
  
  // Log trading mode for visibility
  console.log(`Creating ${exchange} adapter in ${safeConfig.mode} mode`);
  
  // Import the appropriate adapter based on exchange
  switch (exchange) {
    case 'binance':
      // Dynamic import to avoid loading all adapters
      const binanceModule = await import('./binance-adapter');
      return new binanceModule.BinanceAdapter(safeConfig);
    case 'okx':
      const okxModule = await import('./okx-adapter');
      return new okxModule.OkxAdapter(safeConfig);
    case 'coinbase':
      const coinbaseModule = await import('./coinbase-adapter');
      return new coinbaseModule.CoinbaseAdapter(safeConfig);
    default:
      throw new Error(`Unsupported exchange: ${exchange}`);
  }
}

