# GIO → Google Sheets → BRAIN.json Integration

## Overview
This integration creates a data pipeline from Gemini (GIO) through Google Sheets to update BRAIN.json automatically.

```
GEMINI (GIO) → GOOGLE SHEETS → PYTHON SYNC → BRAIN.json
     ↓              ↓               ↓            ↓
  Analysis    Live Portfolio    API Read     System State
  Signals     P&L Tracking      Webhooks     Trade Execution
  Research    History Log       Validation   Risk Checks
```

## Setup Instructions

### Step 1: Create Google Sheet
1. Create a new Google Sheet named `SS3_BRAIN`
2. Create these tabs:
   - `Portfolio` - Live holdings
   - `Signals` - Trade signals from GIO
   - `Research` - Exported analysis
   - `Config` - API keys and settings

### Step 2: Enable Google Sheets API
1. Go to Google Cloud Console: https://console.cloud.google.com
2. Create a new project or select existing
3. Enable "Google Sheets API"
4. Create credentials → Service Account
5. Download JSON key file
6. Save as `credentials/google_sheets_key.json`
7. Share the sheet with the service account email

### Step 3: Install Dependencies
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client gspread
```

### Step 4: Configure Environment
Add to your `.env`:
```
GOOGLE_SHEETS_ID=your_sheet_id_here
GOOGLE_CREDENTIALS_PATH=integrations/gemini_sheets/credentials/google_sheets_key.json
```

### Step 5: Add Apps Script to Sheet
1. In Google Sheets, go to Extensions → Apps Script
2. Paste the contents of `apps_script.js`
3. Deploy as web app (for webhook functionality)

### Step 6: Run Sync
```bash
python integrations/gemini_sheets/sync_brain.py
```

## File Structure
```
integrations/gemini_sheets/
├── README.md           # This file
├── apps_script.js      # Google Apps Script (paste into sheet)
├── sync_brain.py       # Main sync script
├── sheets_client.py    # Google Sheets API wrapper
├── webhook_server.py   # Receives push updates from GIO
└── credentials/        # Store your Google API credentials here
    └── .gitkeep
```

## Usage

### Manual Sync
```bash
python integrations/gemini_sheets/sync_brain.py --once
```

### Continuous Sync (every 5 min)
```bash
python integrations/gemini_sheets/sync_brain.py --daemon
```

### Webhook Mode (real-time)
```bash
python integrations/gemini_sheets/webhook_server.py
```
The server will listen on port 5000 (or $PORT) and expose `/gio-update` endpoint. Configure the webhook URL in Google Apps Script to point to this endpoint.


## Sheet Structure

### Portfolio Tab
| Column | Description |
|--------|-------------|
| A | Asset Symbol |
| B | Quantity |
| C | Entry Price |
| D | Current Price |
| E | Value USD |
| F | P&L % |
| G | Exchange |
| H | Last Updated |

### Signals Tab
| Column | Description |
|--------|-------------|
| A | Timestamp |
| B | Asset |
| C | Action (BUY/SELL/HOLD) |
| D | Confidence (0-100) |
| E | Reasoning |
| F | Status (PENDING/EXECUTED/IGNORED) |

### Research Tab
| Column | Description |
|--------|-------------|
| A | Timestamp |
| B | Topic |
| C | Summary |
| D | Key Insights |
| E | Action Items |
