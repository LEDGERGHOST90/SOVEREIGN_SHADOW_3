// sovereign-trading-integration.js
import SovereignCoinbaseIntegration from './coinbase-cdp-integration.js';

class SovereignTradingPlatform {
    constructor() {
        this.coinbaseCDP = new SovereignCoinbaseIntegration();
        this.exchanges = ['okx', 'kraken', 'coinbase_cdp'];
    }

    async initializeAllExchanges() {
        // Your existing OKX and Kraken connections
        await this.initializeOKX();
        await this.initializeKraken();
        
        // New Coinbase CDP integration
        const cdpSuccess = await this.coinbaseCDP.initialize(
            process.env.CDP_API_KEY_NAME,
            process.env.CDP_PRIVATE_KEY
        );

        if (cdpSuccess) {
            await this.coinbaseCDP.createWallet();
            console.log('🎉 All exchanges integrated successfully!');
        }
    }

    async getAllBalances() {
        const allBalances = {
            okx: await this.getOKXBalances(),
            kraken: await this.getKrakenBalances(),
            coinbase_cdp: await this.coinbaseCDP.getBalances()
        };

        return allBalances;
    }

    async executeArbitrageWithCDP(opportunity) {
        // Your arbitrage logic enhanced with CDP capabilities
        console.log('🚀 Executing arbitrage with CDP integration');
        
        if (opportunity.buyExchange === 'coinbase_cdp') {
            // Execute buy on CDP
            return await this.coinbaseCDP.sendAsset(
                opportunity.amount,
                opportunity.asset,
                opportunity.destinationAddress
            );
        }
    }
}

export default SovereignTradingPlatform;
