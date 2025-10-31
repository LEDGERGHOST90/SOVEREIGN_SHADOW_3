
#!/usr/bin/env node
/**
 * CLI tool to test venue resolution
 * Usage: node scripts/resolveVenue.js <intent> --chain=<chain>
 */

const { resolveVenue } = require('../app/lib/role-router');

const args = process.argv.slice(2);
const intent = args[0] || 'defi';
const chainArg = args.find(arg => arg.startsWith('--chain='));
const chain = chainArg ? chainArg.split('=')[1] : undefined;

console.log('\n🔍 Venue Resolution Test');
console.log('═'.repeat(50));
console.log(`Intent: ${intent}`);
console.log(`Chain: ${chain || 'auto-detect'}`);
console.log('═'.repeat(50));

try {
  const resolution = resolveVenue(intent, chain);
  
  console.log('\n✅ Resolution Result:');
  console.log(JSON.stringify(resolution, null, 2));
  
  console.log('\n📊 Guardrails Status:');
  const { roleRouter } = require('../app/lib/role-router');
  console.log(JSON.stringify(roleRouter.getGuardrailsStatus(), null, 2));
  
} catch (error) {
  console.error('\n❌ Error:', error.message);
  process.exit(1);
}
