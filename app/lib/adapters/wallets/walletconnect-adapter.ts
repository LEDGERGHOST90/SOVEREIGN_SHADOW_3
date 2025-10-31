
/**
 * WalletConnect Adapter for The Sovereign Legacy Loop
 * Universal mobile wallet connector - delegates to MetaMask/Phantom based on chain
 */

import { BaseAdapter, BaseAdapterConfig, TransactionResult, BalanceInfo } from '../base-adapter';
import { createMetaMaskAdapter } from './metamask-adapter';
import { createPhantomAdapter } from './phantom-adapter';

interface WalletConnectParams {
  chain: 'evm' | 'solana';
  action: 'swap' | 'transfer' | 'stake';
  params: any;
}

export class WalletConnectAdapter extends BaseAdapter {
  private projectId: string;
  private metamaskDelegate: ReturnType<typeof createMetaMaskAdapter>;
  private phantomDelegate: ReturnType<typeof createPhantomAdapter>;
  
  constructor(config: BaseAdapterConfig) {
    super(config, 'WALLET');
    this.projectId = config.credentials?.projectId || process.env.WALLETCONNECT_PROJECT_ID || '';
    
    // Create delegate adapters
    this.metamaskDelegate = createMetaMaskAdapter(config.mode);
    this.phantomDelegate = createPhantomAdapter(config.mode);
  }

  getName(): string {
    return 'WalletConnect';
  }

  async getBalance(asset?: string): Promise<BalanceInfo[]> {
    if (this.isFakeMode()) {
      // Aggregate balances from both delegates
      const evmBalances = await this.metamaskDelegate.getBalance();
      const solBalances = await this.phantomDelegate.getBalance();
      
      const allBalances = [...evmBalances, ...solBalances];
      
      if (asset) {
        return allBalances.filter(b => b.asset.toUpperCase() === asset.toUpperCase());
      }
      
      return allBalances;
    }

    try {
      console.log('[WalletConnect] Fetching live balance for asset:', asset);
      throw new Error('LIVE mode not yet implemented - requires WalletConnect SDK integration');
    } catch (error) {
      console.error('[WalletConnect] Error fetching balance:', error);
      throw error;
    }
  }

  async executeTransaction(params: WalletConnectParams): Promise<TransactionResult> {
    if (this.isFakeMode()) {
      return this.executeDelegatedTransaction(params);
    }

    try {
      console.log('[WalletConnect] Executing LIVE transaction:', params);
      
      if (process.env.ALLOW_DEFI_ACTIONS !== '1') {
        throw new Error('LIVE DeFi actions are disabled. Set ALLOW_DEFI_ACTIONS=1 to enable.');
      }

      throw new Error('LIVE mode not yet implemented - requires WalletConnect SDK');
    } catch (error) {
      console.error('[WalletConnect] Error executing transaction:', error);
      return {
        success: false,
        status: 'FAILED',
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async executeDelegatedTransaction(params: WalletConnectParams): Promise<TransactionResult> {
    console.log('[WalletConnect FAKE] Delegating to chain-specific adapter:', params.chain);

    if (params.chain === 'evm') {
      return this.metamaskDelegate.executeTransaction(params.params);
    } else if (params.chain === 'solana') {
      return this.phantomDelegate.executeTransaction(params.params);
    } else {
      throw new Error(`Unsupported chain: ${params.chain}`);
    }
  }

  getSupportedChains(): string[] {
    return [
      'ethereum',
      'polygon',
      'arbitrum',
      'optimism',
      'base',
      'solana',
    ];
  }

  async initializeSession(): Promise<boolean> {
    if (this.isFakeMode()) {
      console.log('[WalletConnect FAKE] Session initialized');
      return true;
    }

    console.log('[WalletConnect] Initializing WalletConnect session...');
    throw new Error('Session initialization not yet implemented for LIVE mode');
  }
}

// Factory function
export function createWalletConnectAdapter(mode: 'FAKE' | 'LIVE' = 'FAKE'): WalletConnectAdapter {
  return new WalletConnectAdapter({
    mode,
    credentials: {
      projectId: process.env.WALLETCONNECT_PROJECT_ID || '',
    },
  });
}
