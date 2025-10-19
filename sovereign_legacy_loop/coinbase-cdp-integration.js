// coinbase-cdp-integration.js
import { Coinbase, Wallet } from '@coinbase/cdp-sdk';

class SovereignCoinbaseIntegration {
    constructor() {
        this.projectId = 'f5b80ba9-92fd-4d0f-bb26-b9f546edcc1e';
        this.coinbase = null;
        this.wallet = null;
    }

    async initialize(apiKeyName, privateKey) {
        try {
            // Initialize Coinbase CDP
            this.coinbase = new Coinbase({
                apiKeyName: apiKeyName,
                privateKey: privateKey,
                projectId: this.projectId
            });

            console.log('✅ Coinbase CDP initialized successfully');
            return true;
        } catch (error) {
            console.error('❌ CDP initialization failed:', error);
            return false;
        }
    }

    async createWallet() {
        try {
            this.wallet = await this.coinbase.createWallet();
            console.log('✅ Wallet created:', this.wallet.getId());
            return this.wallet;
        } catch (error) {
            console.error('❌ Wallet creation failed:', error);
            return null;
        }
    }

    async getBalances() {
        try {
            const balances = await this.wallet.listBalances();
            console.log('💰 CDP Wallet Balances:', balances);
            return balances;
        } catch (error) {
            console.error('❌ Balance fetch failed:', error);
            return {};
        }
    }

    async sendAsset(amount, asset, destinationAddress) {
        try {
            const transfer = await this.wallet.createTransfer({
                amount: amount,
                assetId: asset,
                destination: destinationAddress
            });
            
            console.log('🚀 Transfer initiated:', transfer.getId());
            return transfer;
        } catch (error) {
            console.error('❌ Transfer failed:', error);
            return null;
        }
    }

    // Integration with your existing arbitrage system
    async integrateWithSovereignSystem() {
        const balances = await this.getBalances();
        
        // Send balance data to your main trading system
        return {
            exchange: 'coinbase_cdp',
            balances: balances,
            wallet_id: this.wallet?.getId(),
            status: 'integrated'
        };
    }
}

export default SovereignCoinbaseIntegration;
