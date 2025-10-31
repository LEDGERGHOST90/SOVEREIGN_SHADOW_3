# 📝 NOTION INTEGRATION GUIDE

**Track your trading empire in Notion**

---

## 🎯 OVERVIEW

Use Notion to create a command center for:
- Trade journal and performance tracking
- API key management (encrypted references)
- Strategy documentation
- Market intelligence notes
- Daily/weekly reviews

**Available via MCP:** Notion tools integrated with Claude Code ✅

---

## 🔧 NOTION MCP TOOLS AVAILABLE

You have access to these Notion operations:

### Pages & Databases
- ✅ **Search pages** - Find pages by title/content
- ✅ **Retrieve page** - Get page details
- ✅ **Create page** - Add new pages
- ✅ **Update page** - Modify existing pages

### Databases
- ✅ **Query database** - Filter and search entries
- ✅ **Create database** - New structured data
- ✅ **Update database** - Modify structure

### Blocks & Content
- ✅ **Get block children** - Read page content
- ✅ **Append blocks** - Add content to pages
- ✅ **Update block** - Modify existing content

### Comments
- ✅ **Create comment** - Add notes to pages
- ✅ **Retrieve comments** - Read discussions

---

## 🏗️ RECOMMENDED NOTION STRUCTURE

### 1. **Trading Dashboard** (Master Page)

```
📊 Sovereign Shadow Trading Empire
├─ 💰 Portfolio Overview
│   ├─ Total Capital: $8,260
│   ├─ Ledger: $6,600 (Vault)
│   └─ Coinbase: $1,660 (Active)
│
├─ 📈 Strategy Arsenal
│   ├─ BTC Range Scalper
│   ├─ Cross-Exchange Arbitrage
│   └─ [9 total strategies]
│
├─ 📝 Trade Journal (Database)
│   ├─ Date | Strategy | P&L | Notes
│   └─ Filter by: Win/Loss, Strategy, Date
│
├─ 🔐 API Keys Reference (Encrypted)
│   ├─ Coinbase: Active ✅
│   ├─ OKX: Pending 🟡
│   └─ Kraken: Pending 🟡
│
├─ 🧠 Market Intelligence
│   ├─ Current Regime: Consolidation Range
│   ├─ BTC: $109K-$116K
│   └─ Volatility: Choppy
│
└─ 📚 Documentation Hub
    ├─ Link to GitHub
    ├─ Link to Abacus AI
    └─ Quick reference guides
```

### 2. **Trade Journal Database**

**Properties:**
- 📅 Date (Date)
- 🎯 Strategy (Select)
- 💱 Pair (Select: BTC/USD, ETH/USD, etc.)
- 💰 Size (Number)
- 📊 Entry Price (Number)
- 📉 Exit Price (Number)
- 💵 P&L (Number - Formula)
- ⏱️ Duration (Number - minutes)
- ✅ Status (Select: Win, Loss, Break-even)
- 📝 Notes (Text)
- 🔗 Trade ID (Text)

**Views:**
- All Trades
- This Week
- Winning Trades
- By Strategy
- By Pair

### 3. **Strategy Performance Database**

**Properties:**
- 🎯 Strategy Name (Title)
- 📈 Total Trades (Number)
- ✅ Wins (Number)
- ❌ Losses (Number)
- 📊 Win Rate (Formula: Wins/Total)
- 💰 Total P&L (Number)
- 💵 Avg Win (Number)
- 💸 Avg Loss (Number)
- 📉 Max Drawdown (Number)
- ⚡ Status (Select: Active, Paused, Disabled)
- 📝 Notes (Text)

### 4. **API Configuration Tracker**

**Properties:**
- 🔐 Service (Title: Coinbase, OKX, Kraken)
- ✅ Status (Select: Connected, Pending, Error)
- 📅 Created Date (Date)
- 📅 Last Updated (Date)
- 🌐 IP Whitelist (Text: 83.171.251.233)
- ⚠️ Permissions (Multi-select: View, Trade)
- 🔒 Key Location (Text: .env file)
- 📝 Notes (Text)

---

## 🚀 QUICK SETUP

### Step 1: Create Notion Account
1. Go to https://notion.so
2. Sign up (free account works)
3. Get your Notion integration token

### Step 2: Create Integration
1. Go to https://www.notion.so/my-integrations
2. Click "New integration"
3. Name: `Sovereign Shadow Trading`
4. Select workspace
5. Copy "Internal Integration Token"

### Step 3: Add to Environment
```bash
cd /Volumes/LegacySafe/SovereignShadow
nano .env

# Add:
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 4: Create Master Page
1. In Notion, create page: "Sovereign Shadow Empire"
2. Add icon: 🏴
3. Click "..." → Add connections → Select your integration
4. Copy Page ID from URL

### Step 5: Test Connection
```python
# Test script
import os
from notion_client import Client

notion = Client(auth=os.environ["NOTION_API_KEY"])

# Test - get page
page_id = "your-page-id"
page = notion.pages.retrieve(page_id=page_id)
print(f"✅ Connected to: {page['properties']['title']['title'][0]['plain_text']}")
```

---

## 📊 AUTOMATED LOGGING

### Log Trades to Notion

```python
#!/usr/bin/env python3
"""
Log trading activity to Notion database
"""
import os
from notion_client import Client
from datetime import datetime

notion = Client(auth=os.environ["NOTION_API_KEY"])

def log_trade_to_notion(trade_data: dict):
    """
    Log a trade to Notion trade journal

    Args:
        trade_data: {
            'strategy': 'BTC Range Scalper',
            'pair': 'BTC/USD',
            'side': 'long',
            'entry': 109200,
            'exit': 110200,
            'size': 100,
            'pnl': 0.91,
            'duration': 23,  # minutes
            'status': 'win'
        }
    """

    # Your trade journal database ID
    database_id = "your-database-id"

    # Calculate P&L percentage
    pnl_pct = (trade_data['pnl'] / trade_data['size']) * 100

    # Create page in database
    notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "Name": {
                "title": [{
                    "text": {
                        "content": f"{trade_data['strategy']} - {trade_data['pair']}"
                    }
                }]
            },
            "Date": {
                "date": {"start": datetime.now().isoformat()}
            },
            "Strategy": {
                "select": {"name": trade_data['strategy']}
            },
            "Pair": {
                "select": {"name": trade_data['pair']}
            },
            "Entry Price": {
                "number": trade_data['entry']
            },
            "Exit Price": {
                "number": trade_data['exit']
            },
            "Size": {
                "number": trade_data['size']
            },
            "P&L": {
                "number": trade_data['pnl']
            },
            "Duration": {
                "number": trade_data['duration']
            },
            "Status": {
                "select": {"name": trade_data['status'].capitalize()}
            }
        },
        children=[
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": f"P&L: {pnl_pct:+.2f}% | Duration: {trade_data['duration']}min"
                        }
                    }]
                }
            }
        ]
    )

    print(f"✅ Trade logged to Notion: {trade_data['strategy']}")


# Example usage
if __name__ == "__main__":
    trade = {
        'strategy': 'BTC Range Scalper',
        'pair': 'BTC/USD',
        'side': 'long',
        'entry': 109200,
        'exit': 110200,
        'size': 100,
        'pnl': 0.91,
        'duration': 23,
        'status': 'win'
    }

    log_trade_to_notion(trade)
```

### Daily Summary to Notion

```python
def create_daily_summary():
    """Create end-of-day summary page"""

    # Your dashboard page ID
    parent_page_id = "your-page-id"

    today = datetime.now().strftime("%Y-%m-%d")

    # Get today's stats from logs
    stats = get_daily_stats()  # Your function

    notion.pages.create(
        parent={"page_id": parent_page_id},
        properties={
            "title": {
                "title": [{
                    "text": {"content": f"Daily Summary - {today}"}
                }]
            }
        },
        children=[
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "Performance"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{
                        "text": {"content": f"Trades: {stats['total_trades']}"}
                    }]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{
                        "text": {"content": f"Win Rate: {stats['win_rate']:.1%}"}
                    }]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{
                        "text": {"content": f"P&L: ${stats['pnl']:+.2f}"}
                    }]
                }
            }
        ]
    )

    print(f"✅ Daily summary created for {today}")
```

---

## 🎯 INTEGRATION WITH TRADING SYSTEM

### Add to BTC Scalper

```python
# In btc_range_scalper_110k.py

# Add after trade closes:
async def _close_position(self, position: Dict, price: float, reason: str):
    # ... existing code ...

    # Log to Notion
    try:
        log_trade_to_notion({
            'strategy': position['strategy'],
            'pair': 'BTC/USD',
            'side': position['type'],
            'entry': position['entry_price'],
            'exit': price,
            'size': position['size'],
            'pnl': position['pnl'],
            'duration': (datetime.now() - position['entry_time']).seconds / 60,
            'status': 'win' if position['pnl'] > 0 else 'loss'
        })
    except Exception as e:
        self.logger.error(f"Failed to log to Notion: {e}")
```

---

## 📱 NOTION MOBILE APP

**Benefits:**
- Check trades on the go
- Review portfolio anywhere
- Add notes during market hours
- Track strategy performance mobile

**Setup:**
1. Install Notion app (iOS/Android)
2. Login with same account
3. Access your trading dashboard
4. Enable offline mode

---

## 🔐 SECURITY BEST PRACTICES

### For API Keys Page in Notion:

**✅ DO:**
- Store references only (e.g., "Key stored in .env")
- Note IP whitelist address
- Track creation dates
- Document permissions

**❌ DON'T:**
- Store actual API keys in Notion
- Share API key pages
- Include secrets in page titles
- Make API pages public

### Example Safe Entry:
```
Service: Coinbase
Status: ✅ Connected
Key Location: .env file (COINBASE_API_KEY)
IP Whitelist: 83.171.251.233
Permissions: View + Trade (NO withdraw)
Created: 2025-10-19
Notes: Main hot wallet for active trading
```

---

## 📊 NOTION TEMPLATES

### Pre-built templates available:

1. **Trade Journal Template**
   - Ready-to-use database
   - All properties configured
   - Multiple views set up

2. **Strategy Tracker Template**
   - Performance metrics
   - Status tracking
   - Notes and optimization ideas

3. **Daily Review Template**
   - Trade summary
   - Market conditions
   - Lessons learned
   - Tomorrow's plan

### Import Templates:
```
1. Visit notion.so/templates
2. Search "trading journal"
3. Duplicate to your workspace
4. Customize for your needs
```

---

## 🎯 QUICK ACTIONS

### Using MCP Tools (via Claude Code):

**Search for trades this week:**
```
"Search my Notion for trades from this week"
```

**Create new trade entry:**
```
"Log this trade to my Notion journal:
- Strategy: BTC Scalper
- P&L: +$0.91
- Notes: Perfect range entry at $109K"
```

**Update strategy performance:**
```
"Update my BTC Scalper strategy in Notion:
- Total trades: 15
- Win rate: 73%
- Total P&L: $12.50"
```

**Get daily summary:**
```
"Show me today's trading summary from Notion"
```

---

## 📚 RESOURCES

**Notion API:**
- Docs: https://developers.notion.com/
- Python SDK: https://github.com/ramnes/notion-sdk-py

**MCP Notion Integration:**
- Available via Claude Code MCP tools ✅
- Real-time access to your workspace

**Templates:**
- Trading Journal: https://notion.so/templates/trading-journal
- Performance Tracker: https://notion.so/templates/performance

---

## 🎯 NEXT STEPS

### Today:
1. Create Notion account (if needed)
2. Create "Sovereign Shadow Empire" page
3. Add trade journal database
4. Test with one manual entry

### This Week:
1. Set up Notion integration token
2. Add NOTION_API_KEY to .env
3. Create all databases (trades, strategies, API)
4. Test automated logging script

### Ongoing:
1. Review Notion daily after trading
2. Update strategy notes
3. Track API configuration changes
4. Archive old trade data monthly

---

**Status:** Ready to integrate
**Tools:** Available via MCP ✅
**Setup Time:** 15 minutes
**Value:** Complete trading journal + analytics

🏴 **Track your empire in Notion** 🏴
