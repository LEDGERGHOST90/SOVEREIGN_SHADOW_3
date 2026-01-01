/**
 * SS3 BRAIN - Google Apps Script
 *
 * Paste this into Extensions → Apps Script in your Google Sheet
 * This enables:
 * - Auto-refresh of prices
 * - Webhook push to Claude Code
 * - GIO signal logging
 */

// ============================================
// CONFIGURATION
// ============================================
const CONFIG = {
  // Your webhook URL (update after deploying webhook_server.py)
  WEBHOOK_URL: 'https://your-webhook-url.com/gio-update',

  // NTFY notification channel
  NTFY_TOPIC: 'sovereignshadow_dc4d2fa1',

  // Refresh interval in minutes
  REFRESH_INTERVAL: 15,

  // Sheet names
  SHEETS: {
    PORTFOLIO: 'Portfolio',
    SIGNALS: 'Signals',
    RESEARCH: 'Research',
    CONFIG: 'Config'
  }
};

// ============================================
// MENU SETUP
// ============================================
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('SS3 BRAIN')
    .addItem('Refresh Prices', 'refreshPrices')
    .addItem('Sync to BRAIN.json', 'syncToBrain')
    .addItem('Add Signal', 'showSignalDialog')
    .addSeparator()
    .addItem('Setup Auto-Refresh', 'setupAutoRefresh')
    .addItem('Stop Auto-Refresh', 'stopAutoRefresh')
    .addToUi();
}

// ============================================
// PRICE REFRESH
// ============================================
function refreshPrices() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEETS.PORTFOLIO);
  const data = sheet.getDataRange().getValues();

  // Skip header row
  for (let i = 1; i < data.length; i++) {
    const symbol = data[i][0]; // Column A: Symbol
    if (!symbol) continue;

    try {
      const price = fetchPrice(symbol);
      if (price) {
        // Update Column D (Current Price)
        sheet.getRange(i + 1, 4).setValue(price);

        // Calculate Value (Column E = Quantity * Price)
        const quantity = data[i][1];
        sheet.getRange(i + 1, 5).setValue(quantity * price);

        // Calculate P&L % (Column F)
        const entryPrice = data[i][2];
        if (entryPrice > 0) {
          const pnlPct = ((price - entryPrice) / entryPrice) * 100;
          sheet.getRange(i + 1, 6).setValue(pnlPct.toFixed(2) + '%');
        }

        // Update timestamp (Column H)
        sheet.getRange(i + 1, 8).setValue(new Date().toISOString());
      }
    } catch (e) {
      Logger.log(`Error fetching ${symbol}: ${e}`);
    }
  }

  // Notify
  sendNtfy('Prices refreshed', 'SS3 portfolio prices updated');
}

function fetchPrice(symbol) {
  // Use CoinGecko API (free, no key required)
  const coinIds = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'SOL': 'solana',
    'XRP': 'ripple',
    'FET': 'fetch-ai',
    'RENDER': 'render-token',
    'SUI': 'sui',
    'LINK': 'chainlink',
    'INJ': 'injective-protocol',
    'USDC': 'usd-coin'
  };

  const coinId = coinIds[symbol.toUpperCase()];
  if (!coinId) return null;

  const url = `https://api.coingecko.com/api/v3/simple/price?ids=${coinId}&vs_currencies=usd`;
  const response = UrlFetchApp.fetch(url);
  const data = JSON.parse(response.getContentText());

  return data[coinId]?.usd || null;
}

// ============================================
// SYNC TO BRAIN.json
// ============================================
function syncToBrain() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  // Gather portfolio data
  const portfolioSheet = ss.getSheetByName(CONFIG.SHEETS.PORTFOLIO);
  const portfolioData = portfolioSheet.getDataRange().getValues();

  const positions = [];
  for (let i = 1; i < portfolioData.length; i++) {
    const row = portfolioData[i];
    if (!row[0]) continue;

    positions.push({
      symbol: row[0],
      quantity: row[1],
      entry_price: row[2],
      current_price: row[3],
      value_usd: row[4],
      pnl_pct: parseFloat(row[5]) || 0,
      exchange: row[6],
      last_updated: row[7]
    });
  }

  // Gather signals
  const signalsSheet = ss.getSheetByName(CONFIG.SHEETS.SIGNALS);
  const signalsData = signalsSheet.getDataRange().getValues();

  const signals = [];
  for (let i = 1; i < Math.min(signalsData.length, 11); i++) { // Last 10 signals
    const row = signalsData[i];
    if (!row[0]) continue;

    signals.push({
      timestamp: row[0],
      asset: row[1],
      action: row[2],
      confidence: row[3],
      reasoning: row[4],
      status: row[5]
    });
  }

  // Build payload
  const payload = {
    source: 'google_sheets',
    timestamp: new Date().toISOString(),
    portfolio: {
      positions: positions,
      total_value: positions.reduce((sum, p) => sum + (p.value_usd || 0), 0)
    },
    signals: signals,
    sheet_id: ss.getId(),
    sheet_url: ss.getUrl()
  };

  // Send to webhook
  try {
    const options = {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    };

    const response = UrlFetchApp.fetch(CONFIG.WEBHOOK_URL, options);
    Logger.log('Sync response: ' + response.getContentText());

    sendNtfy('BRAIN Synced', `${positions.length} positions synced to BRAIN.json`);

  } catch (e) {
    Logger.log('Sync error: ' + e);
    // Try local file export as fallback
    exportToJson(payload);
  }
}

function exportToJson(data) {
  // Create a JSON file in Google Drive
  const fileName = `SS3_BRAIN_${new Date().toISOString().split('T')[0]}.json`;
  const content = JSON.stringify(data, null, 2);

  DriveApp.createFile(fileName, content, 'application/json');
  Logger.log(`Exported to Drive: ${fileName}`);
}

// ============================================
// SIGNAL MANAGEMENT
// ============================================
function addSignal(asset, action, confidence, reasoning) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEETS.SIGNALS);

  // Insert at row 2 (after header)
  sheet.insertRowAfter(1);
  sheet.getRange(2, 1, 1, 6).setValues([[
    new Date().toISOString(),
    asset.toUpperCase(),
    action.toUpperCase(),
    confidence,
    reasoning,
    'PENDING'
  ]]);

  // Notify
  sendNtfy(`GIO Signal: ${action} ${asset}`, `Confidence: ${confidence}% - ${reasoning}`);

  return true;
}

function showSignalDialog() {
  const html = HtmlService.createHtmlOutput(`
    <style>
      body { font-family: Arial, sans-serif; padding: 20px; }
      input, select, textarea { width: 100%; margin: 5px 0 15px 0; padding: 8px; }
      button { background: #4285f4; color: white; padding: 10px 20px; border: none; cursor: pointer; }
    </style>
    <h3>Add GIO Signal</h3>
    <form id="signalForm">
      <label>Asset:</label>
      <input type="text" id="asset" placeholder="BTC, ETH, SOL..." required>

      <label>Action:</label>
      <select id="action">
        <option value="BUY">BUY</option>
        <option value="SELL">SELL</option>
        <option value="HOLD">HOLD</option>
      </select>

      <label>Confidence (0-100):</label>
      <input type="number" id="confidence" min="0" max="100" value="75">

      <label>Reasoning:</label>
      <textarea id="reasoning" rows="3" placeholder="GIO analysis..."></textarea>

      <button type="submit">Add Signal</button>
    </form>
    <script>
      document.getElementById('signalForm').addEventListener('submit', function(e) {
        e.preventDefault();
        google.script.run
          .withSuccessHandler(() => google.script.host.close())
          .addSignal(
            document.getElementById('asset').value,
            document.getElementById('action').value,
            parseInt(document.getElementById('confidence').value),
            document.getElementById('reasoning').value
          );
      });
    </script>
  `).setWidth(400).setHeight(450);

  SpreadsheetApp.getUi().showModalDialog(html, 'Add Signal');
}

// ============================================
// AUTO-REFRESH TRIGGERS
// ============================================
function setupAutoRefresh() {
  // Remove existing triggers
  stopAutoRefresh();

  // Create new trigger
  ScriptApp.newTrigger('refreshPrices')
    .timeBased()
    .everyMinutes(CONFIG.REFRESH_INTERVAL)
    .create();

  SpreadsheetApp.getUi().alert(`Auto-refresh enabled every ${CONFIG.REFRESH_INTERVAL} minutes`);
}

function stopAutoRefresh() {
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === 'refreshPrices') {
      ScriptApp.deleteTrigger(trigger);
    }
  });
}

// ============================================
// NOTIFICATIONS
// ============================================
function sendNtfy(title, message) {
  try {
    UrlFetchApp.fetch(`https://ntfy.sh/${CONFIG.NTFY_TOPIC}`, {
      method: 'post',
      payload: message,
      headers: {
        'Title': title,
        'Priority': '3'
      }
    });
  } catch (e) {
    Logger.log('NTFY error: ' + e);
  }
}

// ============================================
// GEMINI INTEGRATION HELPERS
// ============================================
/**
 * Custom function for Gemini to log research
 * Usage in sheet: =LOG_RESEARCH("Topic", "Summary", "Insights")
 */
function LOG_RESEARCH(topic, summary, insights) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEETS.RESEARCH);

  sheet.insertRowAfter(1);
  sheet.getRange(2, 1, 1, 5).setValues([[
    new Date().toISOString(),
    topic,
    summary,
    insights,
    ''  // Action items (to be filled)
  ]]);

  return `Logged: ${topic}`;
}

/**
 * Custom function to get current portfolio value
 * Usage: =PORTFOLIO_VALUE()
 */
function PORTFOLIO_VALUE() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEETS.PORTFOLIO);
  const data = sheet.getDataRange().getValues();

  let total = 0;
  for (let i = 1; i < data.length; i++) {
    total += data[i][4] || 0; // Column E: Value USD
  }

  return total;
}

/**
 * Custom function to get asset price
 * Usage: =CRYPTO_PRICE("BTC")
 */
function CRYPTO_PRICE(symbol) {
  return fetchPrice(symbol);
}
