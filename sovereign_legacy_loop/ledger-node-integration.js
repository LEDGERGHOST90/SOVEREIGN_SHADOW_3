// ledger-node-integration.js
import TransportNodeHid from '@ledgerhq/hw-transport-node-hid';
import AppEth from '@ledgerhq/hw-app-eth';
import AppBtc from '@ledgerhq/hw-app-btc';

class LedgerNodeIntegration {
    constructor() {
        this.transport = null;
        this.ethApp = null;
        this.btcApp = null;
        this.connected = false;
        this.addresses = new Map();
    }

    async connect() {
        try {
            console.log('🔍 Connecting to Ledger device...');
            
            // Create transport
            this.transport = await TransportNodeHid.create();
            this.connected = true;
            
            // Initialize apps
            this.ethApp = new AppEth(this.transport);
            this.btcApp = new AppBtc(this.transport);
            
            console.log('✅ Ledger device connected successfully');
            return true;
            
        } catch (error) {
            console.error('❌ Failed to connect to Ledger:', error.message);
            console.log('💡 Please ensure your Ledger device is:');
            console.log('   • Connected via USB');
            console.log('   • Unlocked');
            console.log('   • Has Ethereum or Bitcoin app open');
            return false;
        }
    }

    async getEthereumAddresses(count = 5) {
        if (!this.connected) {
            await this.connect();
        }

        const addresses = [];
        console.log(`🔍 Fetching ${count} Ethereum addresses...`);

        for (let i = 0; i < count; i++) {
            try {
                const path = `44'/60'/0'/0/${i}`;
                const result = await this.ethApp.getAddress(path);
                
                const addressInfo = {
                    address: result.address,
                    path: path,
                    currency: 'ETH',
                    publicKey: result.publicKey
                };
                
                addresses.push(addressInfo);
                this.addresses.set(result.address, addressInfo);
                
                console.log(`   Address ${i + 1}: ${result.address}`);
                
            } catch (error) {
                console.error(`Error getting Ethereum address ${i}:`, error.message);
            }
        }

        console.log(`✅ Retrieved ${addresses.length} Ethereum addresses`);
        return addresses;
    }

    async getBitcoinAddresses(count = 5) {
        if (!this.connected) {
            await this.connect();
        }

        const addresses = [];
        console.log(`🔍 Fetching ${count} Bitcoin addresses...`);

        for (let i = 0; i < count; i++) {
            try {
                const path = `44'/0'/0'/0/${i}`;
                const result = await this.btcApp.getWalletPublicKey(path);
                
                const addressInfo = {
                    address: result.bitcoinAddress,
                    path: path,
                    currency: 'BTC',
                    publicKey: result.publicKey
                };
                
                addresses.push(addressInfo);
                this.addresses.set(result.bitcoinAddress, addressInfo);
                
                console.log(`   Address ${i + 1}: ${result.bitcoinAddress}`);
                
            } catch (error) {
                console.error(`Error getting Bitcoin address ${i}:`, error.message);
            }
        }

        console.log(`✅ Retrieved ${addresses.length} Bitcoin addresses`);
        return addresses;
    }

    async signEthereumTransaction(transaction, path) {
        if (!this.connected) {
            await this.connect();
        }

        try {
            console.log('🔐 Signing Ethereum transaction...');
            const result = await this.ethApp.signTransaction(path, transaction);
            console.log('✅ Transaction signed successfully');
            return result;
        } catch (error) {
            console.error('❌ Error signing transaction:', error.message);
            return null;
        }
    }

    async signBitcoinTransaction(transaction, path) {
        if (!this.connected) {
            await this.connect();
        }

        try {
            console.log('🔐 Signing Bitcoin transaction...');
            const result = await this.btcApp.signTransaction(path, transaction);
            console.log('✅ Transaction signed successfully');
            return result;
        } catch (error) {
            console.error('❌ Error signing transaction:', error.message);
            return null;
        }
    }

    async getDeviceInfo() {
        if (!this.connected) {
            await this.connect();
        }

        try {
            const ethInfo = await this.ethApp.getAppConfiguration();
            return {
                connected: this.connected,
                ethereumApp: {
                    version: ethInfo.version,
                    arbitraryDataEnabled: ethInfo.arbitraryDataEnabled,
                    erc20ProvisioningNecessary: ethInfo.erc20ProvisioningNecessary
                },
                addressesCount: this.addresses.size
            };
        } catch (error) {
            console.error('Error getting device info:', error.message);
            return { connected: this.connected, error: error.message };
        }
    }

    disconnect() {
        if (this.transport) {
            this.transport.close();
            this.connected = false;
            console.log('🔌 Ledger device disconnected');
        }
    }

    // Integration with Sovereign Shadow AI
    async integrateWithSovereignShadow() {
        console.log('🏰 INTEGRATING LEDGER WITH SOVEREIGN SHADOW AI');
        console.log('=' * 50);

        const success = await this.connect();
        if (!success) {
            return { success: false, error: 'Failed to connect to Ledger' };
        }

        try {
            // Get addresses
            const ethAddresses = await this.getEthereumAddresses(3);
            const btcAddresses = await this.getBitcoinAddresses(2);
            
            // Get device info
            const deviceInfo = await this.getDeviceInfo();

            const integrationData = {
                success: true,
                timestamp: new Date().toISOString(),
                deviceInfo: deviceInfo,
                addresses: {
                    ethereum: ethAddresses,
                    bitcoin: btcAddresses
                },
                totalAddresses: ethAddresses.length + btcAddresses.length
            };

            console.log('✅ Ledger integration with Sovereign Shadow AI complete!');
            return integrationData;

        } catch (error) {
            console.error('❌ Integration failed:', error.message);
            return { success: false, error: error.message };
        }
    }
}

export default LedgerNodeIntegration;
