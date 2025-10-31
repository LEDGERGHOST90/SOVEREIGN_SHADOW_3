
/**
 * MetaMask Adapter for The Sovereign Legacy Loop
 * Handles EVM-compatible chains (Ethereum, Polygon, Arbitrum, Optimism)
 */

import { BaseAdapter, BaseAdapterConfig, TransactionResult, BalanceInfo } from '../base-adapter';

interface MetaMaskSwapParams {
  tokenIn: string;
  tokenOut: string;
  amountIn: string;
  slippageTolerance: number;
  deadline?: number;
}

export class MetaMaskAdapter extends BaseAdapter {
  private rpcUrl: string;
  private chainId: number;
  private walletAddress?: string;

  constructor(config: BaseAdapterConfig) {
    super(config, 'WALLET');
    this.rpcUrl = config.rpcUrl || process.env.METAMASK_RPC_URL || 'https://mainnet.infura.io/v3/';
    this.chainId = config.chainId || 1; // Default to Ethereum mainnet
  }

  getName(): string {
    return 'MetaMask';
  }

  async getBalance(asset?: string): Promise<BalanceInfo[]> {
    if (this.isFakeMode()) {
      return this.getFakeBalance(asset);
    }

    try {
      // In LIVE mode, connect to actual MetaMask/Web3 provider
      // This would require ethers.js or web3.js integration
      console.log('[MetaMask] Fetching live balance for asset:', asset);
      
      // Placeholder for actual implementation
      throw new Error('LIVE mode not yet implemented - requires Web3 provider integration');
    } catch (error) {
      console.error('[MetaMask] Error fetching balance:', error);
      throw error;
    }
  }

  private getFakeBalance(asset?: string): BalanceInfo[] {
    const mockBalances: BalanceInfo[] = [
      { asset: 'ETH', free: '2.5', locked: '0.0', address: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb' },
      { asset: 'USDC', free: '5000.0', locked: '0.0', address: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48' },
      { asset: 'POLYX', free: '1000.0', locked: '0.0', address: '0x9e32b13ce7f2e80a01932b42553652e053d6ed8e' },
      { asset: 'MATIC', free: '500.0', locked: '0.0', address: '0x0000000000000000000000000000000000001010' },
    ];

    if (asset) {
      const filtered = mockBalances.filter(b => b.asset.toUpperCase() === asset.toUpperCase());
      return filtered.length > 0 ? filtered : [];
    }

    return mockBalances;
  }

  async executeTransaction(params: MetaMaskSwapParams): Promise<TransactionResult> {
    if (this.isFakeMode()) {
      return this.executeFakeSwap(params);
    }

    try {
      console.log('[MetaMask] Executing LIVE swap:', params);
      
      // Guard: Check if ALLOW_DEFI_ACTIONS is enabled
      if (process.env.ALLOW_DEFI_ACTIONS !== '1') {
        throw new Error('LIVE DeFi actions are disabled. Set ALLOW_DEFI_ACTIONS=1 to enable.');
      }

      // Placeholder for actual DEX swap implementation
      throw new Error('LIVE mode not yet implemented - requires DEX router integration (Uniswap/Sushi)');
    } catch (error) {
      console.error('[MetaMask] Error executing transaction:', error);
      return {
        success: false,
        status: 'FAILED',
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async executeFakeSwap(params: MetaMaskSwapParams): Promise<TransactionResult> {
    // Simulate transaction processing
    await new Promise(resolve => setTimeout(resolve, 1000));

    const mockTxHash = `0x${Math.random().toString(16).slice(2)}${Math.random().toString(16).slice(2)}`;
    const mockGasUsed = (Math.random() * 0.01 + 0.005).toFixed(6); // Random gas 0.005-0.015 ETH

    console.log('[MetaMask FAKE] Simulated swap:', {
      tokenIn: params.tokenIn,
      tokenOut: params.tokenOut,
      amountIn: params.amountIn,
      txHash: mockTxHash,
      gasUsed: mockGasUsed,
    });

    return {
      success: true,
      txHash: mockTxHash,
      status: 'CONFIRMED',
      gasUsed: mockGasUsed,
      executedQty: parseFloat(params.amountIn) * (0.95 + Math.random() * 0.05), // Simulated output
    };
  }

  async estimateGas(params: MetaMaskSwapParams): Promise<string> {
    if (this.isFakeMode()) {
      return (Math.random() * 0.01 + 0.005).toFixed(6);
    }
    
    // Actual gas estimation would go here
    throw new Error('Gas estimation not yet implemented for LIVE mode');
  }

  getSupportedChains(): string[] {
    return ['ethereum', 'polygon', 'arbitrum', 'optimism', 'base'];
  }
}

// Factory function
export function createMetaMaskAdapter(mode: 'FAKE' | 'LIVE' = 'FAKE'): MetaMaskAdapter {
  return new MetaMaskAdapter({
    mode,
    rpcUrl: process.env.METAMASK_RPC_URL,
    chainId: parseInt(process.env.METAMASK_CHAIN_ID || '1'),
  });
}
