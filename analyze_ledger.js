const fs = require('fs');

// Read the Ledger Live CSV
const csvData = fs.readFileSync('/home/ubuntu/Uploads/ledgerlive-operations-2025.09.26.csv', 'utf8');
const lines = csvData.trim().split('\n');
const headers = lines[0].split(',').map(h => h.trim());

console.log('╔═══════════════════════════════════════════════════════════════╗');
console.log('║             LEDGER LIVE PORTFOLIO ANALYSIS                    ║');
console.log('╚═══════════════════════════════════════════════════════════════╝');
console.log('\n📅 Data from: ledgerlive-operations-2025.09.26.csv\n');

// Parse CSV and aggregate balances
const balances = {};
const operations = [];

for (let i = 1; i < lines.length; i++) {
  const line = lines[i];
  if (!line.trim()) continue;
  
  const values = line.split(',').map(v => v.trim());
  const operation = {};
  
  headers.forEach((header, index) => {
    operation[header] = values[index] || '';
  });
  
  operations.push(operation);
  
  // Track balances by currency
  const currency = operation['Currency Ticker'] || operation['Currency'];
  const amount = parseFloat(operation['Operation Amount']) || 0;
  
  if (currency && !isNaN(amount)) {
    balances[currency] = (balances[currency] || 0) + amount;
  }
}

console.log('💰 CURRENT BALANCES:\n');
console.log('═'.repeat(80));

const sortedBalances = Object.entries(balances)
  .filter(([_, amount]) => Math.abs(amount) > 0.00000001)
  .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]));

if (sortedBalances.length === 0) {
  console.log('No balances found in Ledger Live data.');
} else {
  sortedBalances.forEach(([currency, amount], index) => {
    console.log(`${index + 1}. ${currency}: ${amount.toFixed(8)}`);
  });
  
  console.log('═'.repeat(80));
  console.log(`\nTotal unique assets: ${sortedBalances.length}`);
}

// Show recent operations
console.log('\n\n📜 RECENT OPERATIONS (Last 10):\n');
console.log('═'.repeat(80));

const recentOps = operations.slice(-10).reverse();
recentOps.forEach((op, index) => {
  const date = op['Operation Date'] || 'N/A';
  const type = op['Operation Type'] || 'N/A';
  const amount = op['Operation Amount'] || 'N/A';
  const currency = op['Currency Ticker'] || op['Currency'] || 'N/A';
  const hash = op['Operation Hash'] || 'N/A';
  
  console.log(`${index + 1}. ${type} - ${amount} ${currency}`);
  console.log(`   Date: ${date}`);
  console.log(`   Hash: ${hash.substring(0, 20)}...`);
  console.log('─'.repeat(80));
});

// Summary stats
console.log('\n📊 SUMMARY:\n');
console.log(`   Total operations: ${operations.length}`);
console.log(`   Unique assets: ${sortedBalances.length}`);
console.log(`   Data source: Ledger Live export`);
console.log(`   Export date: September 26, 2025`);

console.log('\n\n💡 NOTE: This is historical data from your Ledger Live export.');
console.log('   For real-time balances:');
console.log('   1. Open Ledger Live app on your computer');
console.log('   2. Connect your Ledger device');
console.log('   3. Check Portfolio tab for current balances');
console.log('   4. Export fresh CSV if needed (File > Export accounts)\n');

