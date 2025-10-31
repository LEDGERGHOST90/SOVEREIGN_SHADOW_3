
/**
 * Test suite for Role Router
 */

import { resolveVenue, roleRouter } from '../lib/role-router';

describe('Role Router', () => {
  
  beforeEach(() => {
    // Reset environment to safe defaults
    process.env.ENV = 'dev';
    process.env.DISABLE_REAL_EXCHANGES = '1';
    process.env.ALLOW_LIVE_EXCHANGE = '0';
    process.env.ALLOW_DEFI_ACTIONS = '0';
  });

  describe('Venue Resolution', () => {
    it('should resolve spot intent to Kraken by default', () => {
      const result = resolveVenue('spot');
      expect(result.venue).toBe('kraken');
      expect(result.mode).toBe('FAKE');
    });

    it('should resolve sniper intent to OKX', () => {
      const result = resolveVenue('sniper');
      expect(result.venue).toBe('okx');
      expect(result.mode).toBe('FAKE');
    });

    it('should resolve fiat intent to Binance US', () => {
      const result = resolveVenue('fiat');
      expect(result.venue).toBe('binanceus');
      expect(result.mode).toBe('FAKE');
    });

    it('should resolve vault intent to Ledger', () => {
      const result = resolveVenue('vault');
      expect(result.venue).toBe('ledger');
      expect(result.adapter).toBeDefined();
    });

    it('should resolve DeFi intent based on chain', () => {
      const ethResult = resolveVenue('defi', 'ethereum');
      expect(ethResult.venue).toBe('metamask');
      expect(ethResult.adapter).toBeDefined();
      
      const solResult = resolveVenue('defi', 'solana');
      expect(solResult.venue).toBe('phantom');
      expect(solResult.adapter).toBeDefined();
    });
  });

  describe('Guardrails', () => {
    it('should enforce FAKE mode by default', () => {
      const result = resolveVenue('spot');
      expect(result.mode).toBe('FAKE');
    });

    it('should block LIVE mode when guards are active', () => {
      process.env.ENV = 'prod';
      process.env.ALLOW_LIVE_EXCHANGE = '1';
      // But DISABLE_REAL_EXCHANGES is still '1'
      
      const result = resolveVenue('spot');
      expect(result.mode).toBe('FAKE');
    });

    it('should allow LIVE mode only when all guards pass', () => {
      process.env.ENV = 'prod';
      process.env.DISABLE_REAL_EXCHANGES = '0';
      process.env.ALLOW_LIVE_EXCHANGE = '1';
      
      const result = resolveVenue('spot');
      expect(result.mode).toBe('LIVE');
    });

    it('should block DeFi LIVE without ALLOW_DEFI_ACTIONS', () => {
      process.env.ENV = 'prod';
      process.env.DISABLE_REAL_EXCHANGES = '0';
      process.env.ALLOW_LIVE_EXCHANGE = '1';
      // But ALLOW_DEFI_ACTIONS is still '0'
      
      const result = resolveVenue('defi', 'ethereum');
      expect(result.mode).toBe('FAKE');
    });

    it('should show correct guardrails status', () => {
      const status = roleRouter.getGuardrailsStatus();
      
      expect(status).toHaveProperty('env');
      expect(status).toHaveProperty('disableRealExchanges');
      expect(status).toHaveProperty('allowLiveExchange');
      expect(status).toHaveProperty('allowDefiActions');
      expect(status).toHaveProperty('primaryTradeExchange');
    });
  });

  describe('Custom Environment Variables', () => {
    it('should respect PRIMARY_TRADE_EXCHANGE', () => {
      process.env.PRIMARY_TRADE_EXCHANGE = 'coinbase';
      const result = resolveVenue('spot');
      expect(result.venue).toBe('coinbase');
    });

    it('should respect DEFAULT_DEFI_RAIL', () => {
      process.env.DEFAULT_DEFI_RAIL = 'walletconnect';
      const result = resolveVenue('defi');
      expect(result.venue).toBe('walletconnect');
    });

    it('should respect DEFAULT_SOLANA_RAIL', () => {
      process.env.DEFAULT_SOLANA_RAIL = 'phantom';
      const result = resolveVenue('defi', 'solana');
      expect(result.venue).toBe('phantom');
    });
  });
});
