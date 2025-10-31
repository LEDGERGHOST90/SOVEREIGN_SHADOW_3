
/**
 * Test suite for wallet adapters
 */

import { createMetaMaskAdapter } from '../lib/adapters/wallets/metamask-adapter';
import { createPhantomAdapter } from '../lib/adapters/wallets/phantom-adapter';
import { createLedgerAdapter } from '../lib/adapters/wallets/ledger-adapter';
import { createWalletConnectAdapter } from '../lib/adapters/wallets/walletconnect-adapter';

describe('Wallet Adapters', () => {
  
  describe('MetaMask Adapter', () => {
    it('should create adapter in FAKE mode by default', () => {
      const adapter = createMetaMaskAdapter();
      expect(adapter.isFakeMode()).toBe(true);
      expect(adapter.getName()).toBe('MetaMask');
    });

    it('should return mock balances in FAKE mode', async () => {
      const adapter = createMetaMaskAdapter('FAKE');
      const balances = await adapter.getBalance();
      
      expect(Array.isArray(balances)).toBe(true);
      expect(balances.length).toBeGreaterThan(0);
      expect(balances[0]).toHaveProperty('asset');
      expect(balances[0]).toHaveProperty('free');
      expect(balances[0]).toHaveProperty('address');
    });

    it('should execute fake swap successfully', async () => {
      const adapter = createMetaMaskAdapter('FAKE');
      const result = await adapter.executeTransaction({
        tokenIn: 'USDC',
        tokenOut: 'ETH',
        amountIn: '100',
        slippageTolerance: 0.5,
      });
      
      expect(result.success).toBe(true);
      expect(result.txHash).toBeDefined();
      expect(result.status).toBe('CONFIRMED');
      expect(result.gasUsed).toBeDefined();
    });
  });

  describe('Phantom Adapter', () => {
    it('should create adapter in FAKE mode by default', () => {
      const adapter = createPhantomAdapter();
      expect(adapter.isFakeMode()).toBe(true);
      expect(adapter.getName()).toBe('Phantom');
    });

    it('should return Solana balances in FAKE mode', async () => {
      const adapter = createPhantomAdapter('FAKE');
      const balances = await adapter.getBalance();
      
      const solBalance = balances.find(b => b.asset === 'SOL');
      expect(solBalance).toBeDefined();
      
      const bonkBalance = balances.find(b => b.asset === 'BONK');
      expect(bonkBalance).toBeDefined();
    });

    it('should execute fake Solana swap', async () => {
      const adapter = createPhantomAdapter('FAKE');
      const result = await adapter.executeTransaction({
        tokenIn: 'SOL',
        tokenOut: 'BONK',
        amountIn: '1',
        slippageTolerance: 1.0,
        dex: 'orca',
      });
      
      expect(result.success).toBe(true);
      expect(result.txHash).toBeDefined();
      expect(result.txHash?.length).toBe(64);
    });
  });

  describe('Ledger Adapter', () => {
    it('should create adapter in FAKE mode by default', () => {
      const adapter = createLedgerAdapter();
      expect(adapter.isFakeMode()).toBe(true);
      expect(adapter.getName()).toBe('Ledger');
    });

    it('should return vault balances in FAKE mode', async () => {
      const adapter = createLedgerAdapter('FAKE');
      const balances = await adapter.getBalance();
      
      const btcBalance = balances.find(b => b.asset === 'BTC');
      expect(btcBalance).toBeDefined();
      
      const ethBalance = balances.find(b => b.asset === 'ETH');
      expect(ethBalance).toBeDefined();
    });

    it('should simulate hardware confirmation', async () => {
      const adapter = createLedgerAdapter('FAKE');
      
      const startTime = Date.now();
      const result = await adapter.executeTransaction({
        chain: 'btc',
        to: 'bc1qtest',
        amount: '0.1',
        asset: 'BTC',
      });
      const endTime = Date.now();
      
      expect(result.success).toBe(true);
      expect(endTime - startTime).toBeGreaterThanOrEqual(2000); // Should take ~2 seconds
    });
  });

  describe('WalletConnect Adapter', () => {
    it('should create adapter in FAKE mode by default', () => {
      const adapter = createWalletConnectAdapter();
      expect(adapter.isFakeMode()).toBe(true);
      expect(adapter.getName()).toBe('WalletConnect');
    });

    it('should aggregate balances from delegates', async () => {
      const adapter = createWalletConnectAdapter('FAKE');
      const balances = await adapter.getBalance();
      
      // Should have both EVM and Solana tokens
      const ethBalance = balances.find(b => b.asset === 'ETH');
      const solBalance = balances.find(b => b.asset === 'SOL');
      
      expect(ethBalance).toBeDefined();
      expect(solBalance).toBeDefined();
    });

    it('should delegate EVM transactions to MetaMask', async () => {
      const adapter = createWalletConnectAdapter('FAKE');
      const result = await adapter.executeTransaction({
        chain: 'evm',
        action: 'swap',
        params: {
          tokenIn: 'USDC',
          tokenOut: 'ETH',
          amountIn: '100',
          slippageTolerance: 0.5,
        },
      });
      
      expect(result.success).toBe(true);
    });

    it('should delegate Solana transactions to Phantom', async () => {
      const adapter = createWalletConnectAdapter('FAKE');
      const result = await adapter.executeTransaction({
        chain: 'solana',
        action: 'swap',
        params: {
          tokenIn: 'SOL',
          tokenOut: 'BONK',
          amountIn: '1',
          slippageTolerance: 1.0,
        },
      });
      
      expect(result.success).toBe(true);
    });
  });
});
