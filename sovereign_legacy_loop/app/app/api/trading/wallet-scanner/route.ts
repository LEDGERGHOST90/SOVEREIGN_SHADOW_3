import { NextRequest, NextResponse } from 'next/server';

export async function GET() {
  try {
    return NextResponse.json({
      success: true,
      scanner: {
        name: "Wallet Scanner/Watcher",
        status: "active",
        monitoredAddresses: [
          { address: "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", balance: 0.0, type: "genesis" },
          { address: "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh", balance: 0.001, type: "hot" },
          { address: "0x742d35Cc6634C0532925a3b8D", balance: 1.5, type: "cold" }
        ],
        transactions: [
          { hash: "abc123...", amount: 0.001, type: "incoming", timestamp: new Date().toISOString() },
          { hash: "def456...", amount: 0.002, type: "outgoing", timestamp: new Date().toISOString() }
        ],
        alerts: [
          { type: "large_transfer", amount: 5.0, threshold: 1.0, timestamp: new Date().toISOString() },
          { type: "new_address", address: "0x...", timestamp: new Date().toISOString() }
        ],
        totalWatched: 156,
        activeAlerts: 2,
        lastScan: new Date().toISOString()
      },
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Failed to get wallet scanner data' },
      { status: 500 }
    );
  }
}

