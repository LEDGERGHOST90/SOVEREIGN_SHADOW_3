
/**
 * Test suite for DeFi Orchestrator
 */

import { defiOrchestrator } from '../lib/defi-orchestrator';

describe('DeFi Orchestrator', () => {
  
  beforeEach(() => {
    process.env.ENV = 'dev';
    process.env.ALLOW_DEFI_ACTIONS = '0';
    process.env.ALLOW_BRIDGE_OPERATIONS = '0';
  });

  describe('Swap Execution', () => {
    it('should execute EVM swap in FAKE mode', async () => {
      const result = await defiOrchestrator.executeSwap({
        chain: 'ethereum',
        tokenIn: 'USDC',
        tokenOut: 'ETH',
        amountIn: '100',
        slippageTolerance: 0.5,
      });
      
      expect(result.success).toBe(true);
      expect(result.txHash).toBeDefined();
      expect(result.amountOut).toBeDefined();
      expect(result.gasUsed).toBeDefined();
    });

    it('should execute Solana swap in FAKE mode', async () => {
      const result = await defiOrchestrator.executeSwap({
        chain: 'solana',
        tokenIn: 'SOL',
        tokenOut: 'BONK',
        amountIn: '1',
        slippageTolerance: 1.0,
      });
      
      expect(result.success).toBe(true);
      expect(result.txHash).toBeDefined();
      expect(result.txHash?.length).toBe(64);
    });

    it('should handle insufficient balance', async () => {
      const result = await defiOrchestrator.executeSwap({
        chain: 'ethereum',
        tokenIn: 'USDC',
        tokenOut: 'ETH',
        amountIn: '999999999', // Exceeds mock balance
        slippageTolerance: 0.5,
      });
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('Insufficient');
    });
  });

  describe('Bridge Operations', () => {
    it('should block bridges when not enabled', async () => {
      const result = await defiOrchestrator.executeBridge({
        fromChain: 'ethereum',
        toChain: 'polygon',
        token: 'USDC',
        amount: '100',
      });
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('disabled');
    });

    it('should simulate bridge in FAKE mode when enabled', async () => {
      process.env.ALLOW_BRIDGE_OPERATIONS = '1';
      
      const result = await defiOrchestrator.executeBridge({
        fromChain: 'ethereum',
        toChain: 'polygon',
        token: 'USDC',
        amount: '100',
        bridgeProtocol: 'wormhole',
      });
      
      expect(result.success).toBe(true);
      expect(result.txHash).toBeDefined();
      expect(parseFloat(result.amountOut || '0')).toBeCloseTo(99.9, 1); // ~0.1% fee
    });
  });

  describe('Chain Finality Verification', () => {
    it('should auto-confirm in FAKE mode', async () => {
      const confirmed = await defiOrchestrator.verifyChainFinality(
        '0x123',
        'ethereum',
        12
      );
      
      expect(confirmed).toBe(true);
    });
  });

  describe('Configuration', () => {
    it('should return supported chains', () => {
      const chains = defiOrchestrator.getSupportedChains();
      
      expect(chains).toContain('ethereum');
      expect(chains).toContain('polygon');
      expect(chains).toContain('solana');
    });

    it('should return supported bridges', () => {
      const bridges = defiOrchestrator.getSupportedBridges();
      
      expect(bridges).toContain('wormhole');
      expect(bridges).toContain('celer');
      expect(bridges).toContain('synapse');
    });
  });
});
