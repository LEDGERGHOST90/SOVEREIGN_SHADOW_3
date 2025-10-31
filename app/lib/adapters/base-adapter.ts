
/**
 * Base Adapter Interface for The Sovereign Legacy Loop
 * All exchange and wallet adapters must implement this interface
 */

export type AdapterMode = 'FAKE' | 'LIVE';
export type AdapterType = 'EXCHANGE' | 'WALLET';

export interface BaseAdapterConfig {
  mode: AdapterMode;
  credentials?: Record<string, string>;
  rpcUrl?: string;
  chainId?: number;
}

export interface TransactionResult {
  success: boolean;
  txHash?: string;
  orderId?: string;
  status: string;
  error?: string;
  gasUsed?: string;
  executedQty?: number;
  executedPrice?: number;
}

export interface BalanceInfo {
  asset: string;
  free: string;
  locked: string;
  address?: string;
}

export abstract class BaseAdapter {
  protected mode: AdapterMode;
  protected type: AdapterType;
  
  constructor(config: BaseAdapterConfig, type: AdapterType) {
    this.mode = config.mode;
    this.type = type;
  }

  abstract getBalance(asset?: string): Promise<BalanceInfo[]>;
  abstract executeTransaction(params: any): Promise<TransactionResult>;
  abstract getName(): string;
  
  isFakeMode(): boolean {
    return this.mode === 'FAKE';
  }
  
  isLiveMode(): boolean {
    return this.mode === 'LIVE';
  }
  
  getType(): AdapterType {
    return this.type;
  }
}
