
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Seeding database...');

  // Create test user with required credentials (hidden from UI)
  const hashedPassword = await bcrypt.hash('NEVERNEST', 12);
  
  const testUser = await prisma.user.upsert({
    where: { username: 'LEDGERGHOST90' },
    update: {},
    create: {
      username: 'LEDGERGHOST90',
      email: 'LEDGERGHOST90@sovereignlegacy.com',
      password: hashedPassword,
      firstName: 'LEDGER',
      lastName: 'GHOST90',
      name: 'LEDGERGHOST90',
      role: 'ADMIN'
    },
  });

  console.log(`👤 Created test user: ${testUser.username}`);

  // Create user settings
  await prisma.userSettings.upsert({
    where: { userId: testUser.id },
    update: {},
    create: {
      userId: testUser.id,
      liveTrading: false,
      dailyLimit: 1000,
      siphonRatio: 0.70,
      graduationThreshold: 3500,
      agentReviewInterval: 24,
      agentStrictMode: false,
      riskLevel: 'MODERATE'
    }
  });

  // Create sample portfolio data
  const portfolioAssets = [
    { asset: 'BTC', balance: 1.5, hotBalance: 0.5, coldBalance: 1.0, avgBuyPrice: 42000, totalInvested: 63000 },
    { asset: 'ETH', balance: 15.0, hotBalance: 5.0, coldBalance: 10.0, avgBuyPrice: 2500, totalInvested: 37500 },
    { asset: 'BNB', balance: 200.0, hotBalance: 100.0, coldBalance: 100.0, avgBuyPrice: 280, totalInvested: 56000 },
    { asset: 'USDT', balance: 5000.0, hotBalance: 2000.0, coldBalance: 3000.0, avgBuyPrice: 1.0, totalInvested: 5000 }
  ];

  for (const portfolio of portfolioAssets) {
    await prisma.portfolio.upsert({
      where: {
        userId_asset: {
          userId: testUser.id,
          asset: portfolio.asset
        }
      },
      update: {},
      create: {
        userId: testUser.id,
        ...portfolio
      }
    });
  }

  console.log('💼 Created sample portfolio data');

  // Create sample trades
  const sampleTrades = [
    {
      asset: 'BTC',
      type: 'MARKET' as const,
      side: 'BUY' as const,
      amount: 0.5,
      quantity: 0.5, // Add required quantity field
      price: 43000,
      fee: 21.5,
      pnl: 500,
      strategy: 'SCALP',
      status: 'FILLED' as const,
      executedAt: new Date(Date.now() - 2 * 60 * 60 * 1000) // 2 hours ago
    },
    {
      asset: 'ETH',
      type: 'LIMIT' as const,
      side: 'SELL' as const,
      amount: 2.0,
      quantity: 2.0, // Add required quantity field
      price: 2600,
      fee: 5.2,
      pnl: 200,
      strategy: 'SNIPE',
      status: 'FILLED' as const,
      executedAt: new Date(Date.now() - 4 * 60 * 60 * 1000) // 4 hours ago
    }
  ];

  for (const trade of sampleTrades) {
    await prisma.trade.create({
      data: {
        userId: testUser.id,
        ...trade
      }
    });
  }

  console.log('📈 Created sample trades');

  // Create sample vault logs
  const sampleVaultLogs = [
    {
      asset: 'BTC',
      amount: 0.3,
      type: 'SIPHON' as const,
      fromWallet: 'hot',
      toWallet: 'cold',
      status: 'COMPLETED' as const,
      createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1 day ago
      completedAt: new Date(Date.now() - 24 * 60 * 60 * 1000 + 5 * 60 * 1000) // 5 minutes later
    },
    {
      asset: 'ETH',
      amount: 5.0,
      type: 'GRADUATION' as const,
      fromWallet: 'hot',
      toWallet: 'cold',
      status: 'PENDING' as const,
      createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000) // 2 hours ago
    }
  ];

  for (const vaultLog of sampleVaultLogs) {
    await prisma.vaultLog.create({
      data: {
        userId: testUser.id,
        ...vaultLog
      }
    });
  }

  console.log('🔐 Created sample vault logs');

  // Create sample agent milestones
  const sampleMilestones = [
    {
      title: 'Reach $100K Portfolio Value',
      description: 'Achieve a total portfolio value of $100,000 across all assets',
      category: 'wealth',
      achieved: false
    },
    {
      title: 'Complete First Profitable Trade',
      description: 'Execute a trade that results in a net positive return',
      category: 'trading',
      achieved: true,
      achievedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) // 1 week ago
    },
    {
      title: 'Setup Hardware Wallet',
      description: 'Configure and secure a hardware wallet for cold storage',
      category: 'security',
      achieved: true,
      achievedAt: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000) // 2 weeks ago
    }
  ];

  for (const milestone of sampleMilestones) {
    await prisma.agentMilestone.create({
      data: {
        userId: testUser.id,
        ...milestone
      }
    });
  }

  console.log('🎯 Created sample milestones');

  // Create sample reflections
  const sampleReflections = [
    {
      content: 'Today\'s BTC scalp trade was successful. The market showed strong upward momentum around 3pm EST, which aligned perfectly with our technical analysis. Need to be more disciplined about position sizing going forward.',
      mood: 'confident',
      tags: ['trading', 'BTC', 'scalping', 'technical-analysis']
    },
    {
      content: 'The automated siphon rule is working well. Seeing consistent transfers to cold storage which gives me peace of mind. Should consider adjusting the ratio from 70% to 75% as portfolio grows.',
      mood: 'analytical',
      tags: ['vault', 'automation', 'security']
    }
  ];

  for (const reflection of sampleReflections) {
    await prisma.agentReflection.create({
      data: {
        userId: testUser.id,
        ...reflection
      }
    });
  }

  console.log('💭 Created sample reflections');

  // Create sample highlights
  const sampleHighlights = [
    {
      component: 'Trading Engine',
      issue: 'Daily limit approaching threshold (85% utilized)',
      severity: 'MEDIUM' as const,
      status: 'OPEN' as const
    },
    {
      component: 'Vault System',
      issue: 'Pending graduation transaction requires confirmation',
      severity: 'LOW' as const,
      status: 'OPEN' as const
    }
  ];

  for (const highlight of sampleHighlights) {
    await prisma.agentHighlight.create({
      data: {
        userId: testUser.id,
        ...highlight
      }
    });
  }

  console.log('⚡ Created sample highlights');

  // Create system health record
  await prisma.systemHealth.upsert({
    where: { id: 'system-health' },
    update: {
      binanceStatus: true,
      databaseStatus: true,
      aiAdvisorStatus: true,
      vaultStatus: true,
      lastCheck: new Date()
    },
    create: {
      id: 'system-health',
      binanceStatus: true,
      databaseStatus: true,
      aiAdvisorStatus: true,
      vaultStatus: true,
      lastCheck: new Date()
    }
  });

  console.log('🏥 Created system health data');
  console.log('✅ Database seeding completed successfully!');
}

main()
  .catch((e) => {
    console.error('❌ Seeding failed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
