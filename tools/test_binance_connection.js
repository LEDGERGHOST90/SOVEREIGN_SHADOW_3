const crypto = require('crypto');
const https = require('https');
const fs = require('fs');

// Read .env file manually
const envFile = fs.readFileSync('/home/ubuntu/sovereign_legacy_loop/app/.env', 'utf8');
const envVars = {};
envFile.split('\n').forEach(line => {
  const [key, ...valueParts] = line.split('=');
  if (key && valueParts.length) {
    envVars[key.trim()] = valueParts.join('=').trim();
  }
});

const API_KEY = envVars.BINANCE_US_API_KEY;
const SECRET_KEY = envVars.BINANCE_US_SECRET_KEY;

console.log('🔑 API Key Check:');
console.log('   API Key loaded:', API_KEY ? `${API_KEY.substring(0, 10)}...${API_KEY.substring(API_KEY.length - 4)}` : 'NOT FOUND');
console.log('   Secret Key loaded:', SECRET_KEY ? `${SECRET_KEY.substring(0, 10)}...${SECRET_KEY.substring(SECRET_KEY.length - 4)}` : 'NOT FOUND');
console.log('   API Key length:', API_KEY ? API_KEY.length : 0);
console.log('   Secret Key length:', SECRET_KEY ? SECRET_KEY.length : 0);

// Test public endpoint first (no authentication needed)
console.log('\n📡 Testing public endpoint (no auth)...');

function testPublicEndpoint() {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.binance.us',
      path: '/api/v3/ping',
      method: 'GET'
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        console.log('✅ Public endpoint test successful!');
        console.log('   Response:', data);
        resolve();
      });
    });

    req.on('error', (error) => {
      console.error('❌ Public endpoint test failed:', error.message);
      reject(error);
    });
    req.end();
  });
}

function testServerTime() {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.binance.us',
      path: '/api/v3/time',
      method: 'GET'
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        const serverTime = JSON.parse(data);
        const localTime = Date.now();
        const timeDiff = Math.abs(serverTime.serverTime - localTime);
        
        console.log('\n⏰ Time Synchronization Check:');
        console.log('   Server time:', new Date(serverTime.serverTime).toISOString());
        console.log('   Local time:', new Date(localTime).toISOString());
        console.log('   Difference:', timeDiff, 'ms');
        
        if (timeDiff > 1000) {
          console.log('⚠️  WARNING: Time difference > 1 second. This may cause authentication issues.');
        } else {
          console.log('✅ Time sync OK');
        }
        resolve();
      });
    });

    req.on('error', reject);
    req.end();
  });
}

function testAuthenticatedEndpoint() {
  return new Promise((resolve, reject) => {
    const timestamp = Date.now();
    const queryString = `timestamp=${timestamp}&recvWindow=60000`;
    
    const signature = crypto
      .createHmac('sha256', SECRET_KEY)
      .update(queryString)
      .digest('hex');
    
    const fullPath = `/api/v3/account?${queryString}&signature=${signature}`;

    console.log('\n🔐 Testing authenticated endpoint...');
    console.log('   Timestamp:', timestamp);
    console.log('   Query string:', queryString);
    console.log('   Signature:', signature.substring(0, 16) + '...');

    const options = {
      hostname: 'api.binance.us',
      path: fullPath,
      method: 'GET',
      headers: {
        'X-MBX-APIKEY': API_KEY
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        console.log('   Status code:', res.statusCode);
        console.log('   Response:', data.substring(0, 200));
        
        try {
          const parsed = JSON.parse(data);
          if (parsed.code) {
            console.log('❌ Authentication failed:', parsed.msg);
            console.log('\n💡 Common issues:');
            console.log('   1. API key permissions: Enable "Read" permission in Binance US');
            console.log('   2. IP restriction: Check if your IP is whitelisted');
            console.log('   3. API key expired or revoked');
            console.log('   4. Incorrect API key/secret');
          } else {
            console.log('✅ Authentication successful!');
          }
        } catch (e) {
          console.log('Response:', data);
        }
        resolve();
      });
    });

    req.on('error', (error) => {
      console.error('❌ Request failed:', error.message);
      reject(error);
    });
    req.end();
  });
}

(async () => {
  try {
    await testPublicEndpoint();
    await testServerTime();
    await testAuthenticatedEndpoint();
  } catch (error) {
    console.error('Test failed:', error);
  }
})();
