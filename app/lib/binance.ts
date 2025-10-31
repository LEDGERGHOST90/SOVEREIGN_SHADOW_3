
import crypto from 'crypto';

const BINANCE_BASE_URL = 'https://api.binance.us';

interface BinanceCredentials {
  apiKey: string;
  apiSecret: string;
}

export class BinanceClient {
  private apiKey: string;
  private apiSecret: string;

  constructor(credentials: BinanceCredentials) {
    this.apiKey = credentials.apiKey;
    this.apiSecret = credentials.apiSecret;
  }

  private createSignature(params: string): string {
    return crypto
      .createHmac('sha256', this.apiSecret)
      .update(params)
      .digest('hex');
  }

  private async makeRequest(endpoint: string, params: any = {}, method: 'GET' | 'POST' = 'GET') {
    const timestamp = Date.now();
    const queryString = new URLSearchParams({
      ...params,
      timestamp: timestamp.toString(),
    }).toString();
    
    const signature = this.createSignature(queryString);
    const signedParams = `${queryString}&signature=${signature}`;

    const url = `${BINANCE_BASE_URL}${endpoint}?${signedParams}`;
    
    const response = await fetch(url, {
      method,
      headers: {
        'X-MBX-APIKEY': this.apiKey,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    if (!response.ok) {
      throw new Error(`Binance API error: ${response.statusText}`);
    }

    return response.json();
  }

  async getAccountInfo() {
    return this.makeRequest('/api/v3/account');
  }

  async get24hrTicker(symbol?: string) {
    const params = symbol ? { symbol } : {};
    const response = await this.makeRequest('/api/v3/ticker/24hr', params);
    
    // Return single ticker if symbol provided, or first ticker if array returned
    if (Array.isArray(response)) {
      return symbol ? response.find(t => t.symbol === symbol) : response[0];
    }
    return response;
  }

  async getOrderBook(symbol: string, limit: number = 100) {
    return this.makeRequest('/api/v3/depth', { symbol, limit });
  }

  async placeOrder(params: {
    symbol: string;
    side: 'BUY' | 'SELL';
    type: 'MARKET' | 'LIMIT';
    quantity: number;
    price?: number;
  }) {
    return this.makeRequest('/api/v3/order', params, 'POST');
  }

  async getOpenOrders(symbol?: string) {
    const params = symbol ? { symbol } : {};
    return this.makeRequest('/api/v3/openOrders', params);
  }

  async cancelOrder(symbol: string, orderId: number) {
    return this.makeRequest('/api/v3/order', { symbol, orderId }, 'DELETE' as any);
  }
}

export const createMockBinanceClient = () => ({
  async getAccountInfo() {
    return {
      balances: [
        { asset: 'BTC', free: '0.12345678', locked: '0.00000000' },
        { asset: 'ETH', free: '5.67890123', locked: '0.00000000' },
        { asset: 'USDT', free: '1000.00000000', locked: '0.00000000' },
      ],
    };
  },
  async get24hrTicker(symbol?: string) {
    const mockData = [
      { symbol: 'BTCUSDT', priceChange: '1234.56', priceChangePercent: '2.15' },
      { symbol: 'ETHUSDT', priceChange: '89.12', priceChangePercent: '1.87' },
    ];
    return symbol ? mockData.find(d => d.symbol === symbol) : mockData;
  },
  async placeOrder(params: any) {
    return {
      orderId: Math.floor(Math.random() * 1000000),
      status: 'FILLED',
      executedQty: params.quantity,
      fills: [{ price: params.price || '50000.00', qty: params.quantity }],
    };
  },
});
