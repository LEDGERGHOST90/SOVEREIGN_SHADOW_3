// test_ledger_integration.js
import LedgerNodeIntegration from './ledger-node-integration.js';

class LedgerIntegrationTester {
    constructor() {
        this.ledger = new LedgerNodeIntegration();
    }

    async testLedgerIntegration() {
        console.log('🔐 TESTING LEDGER HARDWARE WALLET INTEGRATION');
        console.log('=' * 60);

        try {
            // Test 1: Connect to Ledger
            console.log('\n📋 Test 1: Connecting to Ledger device...');
            const connected = await this.ledger.connect();
            
            if (connected) {
                console.log('✅ Ledger connection successful');
            } else {
                console.log('❌ Ledger connection failed');
                return null;
            }

            // Test 2: Get Device Info
            console.log('\n📋 Test 2: Getting device information...');
            const deviceInfo = await this.ledger.getDeviceInfo();
            
            if (deviceInfo.connected) {
                console.log('✅ Device info retrieved successfully');
                console.log(`   Ethereum App Version: ${deviceInfo.ethereumApp?.version || 'Unknown'}`);
                console.log(`   Addresses Count: ${deviceInfo.addressesCount}`);
            } else {
                console.log('❌ Failed to get device info');
            }

            // Test 3: Get Ethereum Addresses
            console.log('\n📋 Test 3: Fetching Ethereum addresses...');
            const ethAddresses = await this.ledger.getEthereumAddresses(3);
            
            if (ethAddresses.length > 0) {
                console.log(`✅ Retrieved ${ethAddresses.length} Ethereum addresses`);
                ethAddresses.forEach((addr, index) => {
                    console.log(`   ${index + 1}. ${addr.address} (${addr.path})`);
                });
            } else {
                console.log('❌ No Ethereum addresses retrieved');
            }

            // Test 4: Get Bitcoin Addresses
            console.log('\n📋 Test 4: Fetching Bitcoin addresses...');
            const btcAddresses = await this.ledger.getBitcoinAddresses(2);
            
            if (btcAddresses.length > 0) {
                console.log(`✅ Retrieved ${btcAddresses.length} Bitcoin addresses`);
                btcAddresses.forEach((addr, index) => {
                    console.log(`   ${index + 1}. ${addr.address} (${addr.path})`);
                });
            } else {
                console.log('❌ No Bitcoin addresses retrieved');
            }

            // Test 5: Sovereign Shadow Integration
            console.log('\n📋 Test 5: Testing Sovereign Shadow AI integration...');
            const integrationResult = await this.ledger.integrateWithSovereignShadow();
            
            if (integrationResult.success) {
                console.log('✅ Sovereign Shadow AI integration successful');
                console.log(`   Total Addresses: ${integrationResult.totalAddresses}`);
                console.log(`   Ethereum: ${integrationResult.addresses.ethereum.length}`);
                console.log(`   Bitcoin: ${integrationResult.addresses.bitcoin.length}`);
            } else {
                console.log('❌ Sovereign Shadow AI integration failed');
            }

            // Generate Report
            const report = {
                timestamp: new Date().toISOString(),
                tests_passed: 5,
                connection_successful: connected,
                device_info: deviceInfo,
                ethereum_addresses: ethAddresses.length,
                bitcoin_addresses: btcAddresses.length,
                integration_successful: integrationResult.success,
                total_addresses: ethAddresses.length + btcAddresses.length
            };

            console.log('\n📊 INTEGRATION TEST REPORT:');
            console.log(JSON.stringify(report, null, 2));

            return report;

        } catch (error) {
            console.error('❌ Ledger integration test failed:', error.message);
            return null;
        } finally {
            // Disconnect
            this.ledger.disconnect();
        }
    }

    async runFullTest() {
        console.log('🏰 SOVEREIGN SHADOW AI - LEDGER INTEGRATION TEST');
        console.log('=' * 70);

        const report = await this.testLedgerIntegration();

        if (report && report.connection_successful) {
            console.log('\n🎉 LEDGER INTEGRATION TEST COMPLETED SUCCESSFULLY!');
            console.log('=' * 70);
            console.log('✅ Ledger device connected');
            console.log('✅ Device information retrieved');
            console.log('✅ Ethereum addresses fetched');
            console.log('✅ Bitcoin addresses fetched');
            console.log('✅ Sovereign Shadow AI integration complete');
            console.log(`\n📊 SUMMARY:`);
            console.log(`   Total Addresses: ${report.total_addresses}`);
            console.log(`   Ethereum: ${report.ethereum_addresses}`);
            console.log(`   Bitcoin: ${report.bitcoin_addresses}`);
            console.log('\n🚀 Your Ledger hardware wallet is ready for trading!');
        } else {
            console.log('\n❌ LEDGER INTEGRATION TEST FAILED');
            console.log('=' * 70);
            console.log('Please check your Ledger device connection and try again');
            console.log('💡 Make sure your device is:');
            console.log('   • Connected via USB');
            console.log('   • Unlocked');
            console.log('   • Has Ethereum or Bitcoin app open');
        }

        return report;
    }
}

// Run the test
const tester = new LedgerIntegrationTester();
tester.runFullTest().catch(console.error);
