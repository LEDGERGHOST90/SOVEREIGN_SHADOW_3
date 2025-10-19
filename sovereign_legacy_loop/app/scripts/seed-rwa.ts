
// Oracle RWA Engine Seed Data - Inspired by Larry Ellison's $393B Strategy

import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function seedOracleRWAData() {
  console.log('🏛️ Seeding Oracle RWA Engine data...');

  try {
    // Find the existing user (LedgerGhost90)
    const existingUser = await prisma.user.findUnique({
      where: { username: 'LEDGERGHOST90' }
    });

    if (!existingUser) {
      console.log('❌ User LEDGERGHOST90 not found. Please run main seed first.');
      return;
    }

    console.log('✅ Found user:', existingUser.username);

    // Create Oracle-inspired RWA assets
    const rwaAssets = [
      {
        userId: existingUser.id,
        assetType: 'TOKENIZED_TREASURY' as const,
        symbol: 'OUSG',
        name: 'Ondo Short-Term US Government Bond Fund',
        balance: 1000.0,
        value: 105230.0, // $105.23 per token
        yield: 5.15,
        issuer: 'Ondo Finance',
        underlying: 'US Treasuries',
        historicalHigh: 106.50,
        historicalLow: 104.80,
        dayChange: 523.50,
        dayChangePercent: 0.50,
        weekChange: 1050.00,
        monthChange: 2100.00
      },
      {
        userId: existingUser.id,
        assetType: 'TOKENIZED_TREASURY' as const,
        symbol: 'USDY',
        name: 'US Dollar Yield Token',
        balance: 2000.0,
        value: 2104.20, // $1.0521 per token
        yield: 5.21,
        issuer: 'Ondo Finance',
        underlying: 'US Treasuries',
        historicalHigh: 1.0635,
        historicalLow: 1.0450,
        dayChange: 42.08,
        dayChangePercent: 0.52,
        weekChange: 84.16,
        monthChange: 168.32
      },
      {
        userId: existingUser.id,
        assetType: 'MONEY_MARKET' as const,
        symbol: 'OMMF',
        name: 'Ondo Money Market Fund',
        balance: 1500.0,
        value: 1535.25, // $1.0235 per token
        yield: 4.85,
        issuer: 'Ondo Finance',
        underlying: 'Money Market',
        historicalHigh: 1.0298,
        historicalLow: 1.0180,
        dayChange: 30.71,
        dayChangePercent: 0.48,
        weekChange: 61.41,
        monthChange: 122.82
      }
    ];

    // Create RWA assets
    for (const asset of rwaAssets) {
      await prisma.rWAAsset.upsert({
        where: {
          userId_symbol: {
            userId: asset.userId,
            symbol: asset.symbol
          }
        },
        update: asset,
        create: asset
      });
    }

    console.log('✅ Created/updated RWA assets');

    // Create Oracle-inspired vault
    const oracleVault = await prisma.rWAVault.upsert({
      where: {
        id: 'oracle-vault-1'
      },
      update: {},
      create: {
        id: 'oracle-vault-1',
        userId: existingUser.id,
        name: 'Oracle Treasury Vault',
        description: 'Systematic wealth preservation inspired by Larry Ellison\'s $393B strategy',
        strategy: 'ORACLE_INSPIRED',
        targetAllocation: 25.00,
        currentValue: 108869.45, // Sum of RWA values
        totalDeposits: 100000.00,
        totalYield: 8869.45,
        averageYield: 5.07,
        autoRebalance: true,
        rebalanceThreshold: 5.00,
        nextRebalance: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
      }
    });

    console.log('✅ Created Oracle vault');

    // Create vault allocations
    const vaultAllocations = [
      {
        vaultId: oracleVault.id,
        assetType: 'TOKENIZED_TREASURY' as const,
        symbol: 'OUSG',
        targetPercent: 40.00,
        currentPercent: 42.50,
        currentValue: 46291.70
      },
      {
        vaultId: oracleVault.id,
        assetType: 'TOKENIZED_TREASURY' as const,
        symbol: 'USDY',
        targetPercent: 35.00,
        currentPercent: 33.80,
        currentValue: 36804.00
      },
      {
        vaultId: oracleVault.id,
        assetType: 'MONEY_MARKET' as const,
        symbol: 'OMMF',
        targetPercent: 25.00,
        currentPercent: 23.70,
        currentValue: 25773.75
      }
    ];

    for (const allocation of vaultAllocations) {
      await prisma.vaultAllocation.upsert({
        where: {
          vaultId_symbol: {
            vaultId: allocation.vaultId,
            symbol: allocation.symbol
          }
        },
        update: allocation,
        create: allocation
      });
    }

    console.log('✅ Created vault allocations');

    // Create Oracle-inspired wealth milestones
    const wealthMilestones = [
      {
        userId: existingUser.id,
        milestoneType: 'NET_WORTH_MILESTONE' as const,
        amount: 100000.0,
        description: 'First $100K achieved - Oracle pathway initiated',
        trigger: 'RWA Portfolio Milestone',
        dayGain: 2500.0,
        percentGain: 2.56,
        assetClass: 'RWA',
        achievedAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) // 30 days ago
      },
      {
        userId: existingUser.id,
        milestoneType: 'RWA_YIELD_MILESTONE' as const,
        amount: 5000.0,
        description: 'Oracle-inspired yield generation milestone',
        trigger: 'Systematic RWA Yield Accumulation',
        dayGain: 127.50,
        percentGain: 2.61,
        assetClass: 'RWA',
        achievedAt: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000) // 15 days ago
      },
      {
        userId: existingUser.id,
        milestoneType: 'DAILY_GAIN_RECORD' as const,
        amount: 3250.0,
        description: 'Best single-day gain following Oracle systematic approach',
        trigger: 'Oracle AI Infrastructure Surge Replication',
        dayGain: 3250.0,
        percentGain: 3.15,
        assetClass: 'Mixed',
        achievedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) // 7 days ago
      }
    ];

    for (const milestone of wealthMilestones) {
      await prisma.wealthMilestone.create({
        data: milestone
      });
    }

    console.log('✅ Created wealth milestones');

    // Create some RWA transactions
    const rwaTransactions = [
      {
        userId: existingUser.id,
        rwaAssetId: (await prisma.rWAAsset.findFirst({ 
          where: { userId: existingUser.id, symbol: 'OUSG' } 
        }))!.id,
        type: 'MINT' as const,
        amount: 500.0,
        price: 105.23,
        value: 52615.0,
        status: 'CONFIRMED' as const,
        executedAt: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000),
        createdAt: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000)
      },
      {
        userId: existingUser.id,
        rwaAssetId: (await prisma.rWAAsset.findFirst({ 
          where: { userId: existingUser.id, symbol: 'USDY' } 
        }))!.id,
        type: 'MINT' as const,
        amount: 1000.0,
        price: 1.0521,
        value: 1052.10,
        status: 'CONFIRMED' as const,
        executedAt: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000),
        createdAt: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000)
      },
      {
        userId: existingUser.id,
        rwaAssetId: (await prisma.rWAAsset.findFirst({ 
          where: { userId: existingUser.id, symbol: 'OMMF' } 
        }))!.id,
        type: 'DIVIDEND' as const,
        amount: 75.25,
        price: 0.0485, // Yield payment
        value: 3.65,
        status: 'CONFIRMED' as const,
        executedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
        createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000)
      }
    ];

    for (const transaction of rwaTransactions) {
      await prisma.rWATransaction.create({
        data: transaction
      });
    }

    console.log('✅ Created RWA transactions');

    // Update system health to include Oracle components
    await prisma.systemHealth.upsert({
      where: { id: 'system-health-1' },
      update: {
        ondoStatus: true,
        ibkrStatus: true,
        lastCheck: new Date()
      },
      create: {
        id: 'system-health-1',
        binanceStatus: true,
        databaseStatus: true,
        aiAdvisorStatus: true,
        vaultStatus: true,
        ondoStatus: true,
        ibkrStatus: true,
        lastCheck: new Date()
      }
    });

    console.log('✅ Updated system health');

    console.log('🏛️ Oracle RWA Engine seeding completed successfully!');
    console.log('\n📊 Summary:');
    console.log('   • 3 RWA assets (OUSG, USDY, OMMF)');
    console.log('   • 1 Oracle Treasury Vault');
    console.log('   • 3 vault allocations');
    console.log('   • 3 wealth milestones');
    console.log('   • 3 RWA transactions');
    console.log('   • Updated system health');
    console.log('\n🎯 Oracle Metrics:');
    console.log('   • Total RWA Value: $108,869.45');
    console.log('   • Average Yield: 5.07%');
    console.log('   • Oracle Score Target: 75/100');

  } catch (error) {
    console.error('❌ Error seeding Oracle RWA data:', error);
    throw error;
  }
}

// Run if called directly
if (require.main === module) {
  seedOracleRWAData()
    .then(() => {
      console.log('🏛️ Oracle RWA seeding completed');
      process.exit(0);
    })
    .catch((error) => {
      console.error('❌ Oracle RWA seeding failed:', error);
      process.exit(1);
    })
    .finally(async () => {
      await prisma.$disconnect();
    });
}

export { seedOracleRWAData };
