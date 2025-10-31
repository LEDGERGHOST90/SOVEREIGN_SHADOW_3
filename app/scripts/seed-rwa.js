"use strict";
// Oracle RWA Engine Seed Data - Inspired by Larry Ellison's $393B Strategy
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.seedOracleRWAData = void 0;
var client_1 = require("@prisma/client");
var prisma = new client_1.PrismaClient();
function seedOracleRWAData() {
    return __awaiter(this, void 0, void 0, function () {
        var existingUser, rwaAssets, _i, rwaAssets_1, asset, oracleVault, vaultAllocations, _a, vaultAllocations_1, allocation, wealthMilestones, _b, wealthMilestones_1, milestone, rwaTransactions, _c, _d, rwaTransactions_1, transaction, error_1;
        var _e, _f, _g;
        return __generator(this, function (_h) {
            switch (_h.label) {
                case 0:
                    console.log('🏛️ Seeding Oracle RWA Engine data...');
                    _h.label = 1;
                case 1:
                    _h.trys.push([1, 24, , 25]);
                    return [4 /*yield*/, prisma.user.findUnique({
                            where: { username: 'LEDGERGHOST90' }
                        })];
                case 2:
                    existingUser = _h.sent();
                    if (!existingUser) {
                        console.log('❌ User LEDGERGHOST90 not found. Please run main seed first.');
                        return [2 /*return*/];
                    }
                    console.log('✅ Found user:', existingUser.username);
                    rwaAssets = [
                        {
                            userId: existingUser.id,
                            assetType: 'TOKENIZED_TREASURY',
                            symbol: 'OUSG',
                            name: 'Ondo Short-Term US Government Bond Fund',
                            balance: 1000.0,
                            value: 105230.0,
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
                            assetType: 'TOKENIZED_TREASURY',
                            symbol: 'USDY',
                            name: 'US Dollar Yield Token',
                            balance: 2000.0,
                            value: 2104.20,
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
                            assetType: 'MONEY_MARKET',
                            symbol: 'OMMF',
                            name: 'Ondo Money Market Fund',
                            balance: 1500.0,
                            value: 1535.25,
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
                    _i = 0, rwaAssets_1 = rwaAssets;
                    _h.label = 3;
                case 3:
                    if (!(_i < rwaAssets_1.length)) return [3 /*break*/, 6];
                    asset = rwaAssets_1[_i];
                    return [4 /*yield*/, prisma.rWAAsset.upsert({
                            where: {
                                userId_symbol: {
                                    userId: asset.userId,
                                    symbol: asset.symbol
                                }
                            },
                            update: asset,
                            create: asset
                        })];
                case 4:
                    _h.sent();
                    _h.label = 5;
                case 5:
                    _i++;
                    return [3 /*break*/, 3];
                case 6:
                    console.log('✅ Created/updated RWA assets');
                    return [4 /*yield*/, prisma.rWAVault.upsert({
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
                                currentValue: 108869.45,
                                totalDeposits: 100000.00,
                                totalYield: 8869.45,
                                averageYield: 5.07,
                                autoRebalance: true,
                                rebalanceThreshold: 5.00,
                                nextRebalance: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
                            }
                        })];
                case 7:
                    oracleVault = _h.sent();
                    console.log('✅ Created Oracle vault');
                    vaultAllocations = [
                        {
                            vaultId: oracleVault.id,
                            assetType: 'TOKENIZED_TREASURY',
                            symbol: 'OUSG',
                            targetPercent: 40.00,
                            currentPercent: 42.50,
                            currentValue: 46291.70
                        },
                        {
                            vaultId: oracleVault.id,
                            assetType: 'TOKENIZED_TREASURY',
                            symbol: 'USDY',
                            targetPercent: 35.00,
                            currentPercent: 33.80,
                            currentValue: 36804.00
                        },
                        {
                            vaultId: oracleVault.id,
                            assetType: 'MONEY_MARKET',
                            symbol: 'OMMF',
                            targetPercent: 25.00,
                            currentPercent: 23.70,
                            currentValue: 25773.75
                        }
                    ];
                    _a = 0, vaultAllocations_1 = vaultAllocations;
                    _h.label = 8;
                case 8:
                    if (!(_a < vaultAllocations_1.length)) return [3 /*break*/, 11];
                    allocation = vaultAllocations_1[_a];
                    return [4 /*yield*/, prisma.vaultAllocation.upsert({
                            where: {
                                vaultId_symbol: {
                                    vaultId: allocation.vaultId,
                                    symbol: allocation.symbol
                                }
                            },
                            update: allocation,
                            create: allocation
                        })];
                case 9:
                    _h.sent();
                    _h.label = 10;
                case 10:
                    _a++;
                    return [3 /*break*/, 8];
                case 11:
                    console.log('✅ Created vault allocations');
                    wealthMilestones = [
                        {
                            userId: existingUser.id,
                            milestoneType: 'NET_WORTH_MILESTONE',
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
                            milestoneType: 'RWA_YIELD_MILESTONE',
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
                            milestoneType: 'DAILY_GAIN_RECORD',
                            amount: 3250.0,
                            description: 'Best single-day gain following Oracle systematic approach',
                            trigger: 'Oracle AI Infrastructure Surge Replication',
                            dayGain: 3250.0,
                            percentGain: 3.15,
                            assetClass: 'Mixed',
                            achievedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) // 7 days ago
                        }
                    ];
                    _b = 0, wealthMilestones_1 = wealthMilestones;
                    _h.label = 12;
                case 12:
                    if (!(_b < wealthMilestones_1.length)) return [3 /*break*/, 15];
                    milestone = wealthMilestones_1[_b];
                    return [4 /*yield*/, prisma.wealthMilestone.create({
                            data: milestone
                        })];
                case 13:
                    _h.sent();
                    _h.label = 14;
                case 14:
                    _b++;
                    return [3 /*break*/, 12];
                case 15:
                    console.log('✅ Created wealth milestones');
                    _e = {
                        userId: existingUser.id
                    };
                    return [4 /*yield*/, prisma.rWAAsset.findFirst({
                            where: { userId: existingUser.id, symbol: 'OUSG' }
                        })];
                case 16:
                    _c = [
                        (_e.rwaAssetId = (_h.sent()).id,
                            _e.type = 'MINT',
                            _e.amount = 500.0,
                            _e.price = 105.23,
                            _e.value = 52615.0,
                            _e.status = 'CONFIRMED',
                            _e.executedAt = new Date(Date.now() - 10 * 24 * 60 * 60 * 1000),
                            _e.createdAt = new Date(Date.now() - 10 * 24 * 60 * 60 * 1000),
                            _e)
                    ];
                    _f = {
                        userId: existingUser.id
                    };
                    return [4 /*yield*/, prisma.rWAAsset.findFirst({
                            where: { userId: existingUser.id, symbol: 'USDY' }
                        })];
                case 17:
                    _c = _c.concat([
                        (_f.rwaAssetId = (_h.sent()).id,
                            _f.type = 'MINT',
                            _f.amount = 1000.0,
                            _f.price = 1.0521,
                            _f.value = 1052.10,
                            _f.status = 'CONFIRMED',
                            _f.executedAt = new Date(Date.now() - 8 * 24 * 60 * 60 * 1000),
                            _f.createdAt = new Date(Date.now() - 8 * 24 * 60 * 60 * 1000),
                            _f)
                    ]);
                    _g = {
                        userId: existingUser.id
                    };
                    return [4 /*yield*/, prisma.rWAAsset.findFirst({
                            where: { userId: existingUser.id, symbol: 'OMMF' }
                        })];
                case 18:
                    rwaTransactions = _c.concat([
                        (_g.rwaAssetId = (_h.sent()).id,
                            _g.type = 'DIVIDEND',
                            _g.amount = 75.25,
                            _g.price = 0.0485,
                            _g.value = 3.65,
                            _g.status = 'CONFIRMED',
                            _g.executedAt = new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
                            _g.createdAt = new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
                            _g)
                    ]);
                    _d = 0, rwaTransactions_1 = rwaTransactions;
                    _h.label = 19;
                case 19:
                    if (!(_d < rwaTransactions_1.length)) return [3 /*break*/, 22];
                    transaction = rwaTransactions_1[_d];
                    return [4 /*yield*/, prisma.rWATransaction.create({
                            data: transaction
                        })];
                case 20:
                    _h.sent();
                    _h.label = 21;
                case 21:
                    _d++;
                    return [3 /*break*/, 19];
                case 22:
                    console.log('✅ Created RWA transactions');
                    // Update system health to include Oracle components
                    return [4 /*yield*/, prisma.systemHealth.upsert({
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
                        })];
                case 23:
                    // Update system health to include Oracle components
                    _h.sent();
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
                    return [3 /*break*/, 25];
                case 24:
                    error_1 = _h.sent();
                    console.error('❌ Error seeding Oracle RWA data:', error_1);
                    throw error_1;
                case 25: return [2 /*return*/];
            }
        });
    });
}
exports.seedOracleRWAData = seedOracleRWAData;
// Run if called directly
if (require.main === module) {
    seedOracleRWAData()
        .then(function () {
        console.log('🏛️ Oracle RWA seeding completed');
        process.exit(0);
    })
        .catch(function (error) {
        console.error('❌ Oracle RWA seeding failed:', error);
        process.exit(1);
    })
        .finally(function () { return __awaiter(void 0, void 0, void 0, function () {
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, prisma.$disconnect()];
                case 1:
                    _a.sent();
                    return [2 /*return*/];
            }
        });
    }); });
}
