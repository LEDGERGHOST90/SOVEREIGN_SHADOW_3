# 🚀 SovereignShadow VES - Quick Start Guide

## 5-Minute Setup

### 1️⃣ Run Setup Script
```bash
cd /workspace/SovereignShadow
./setup.sh
```

### 2️⃣ Configure API Keys
```bash
nano .env
```

**Required keys:**
- `COINBASE_API_KEY` - Your Coinbase Advanced Trade API key
- `COINBASE_API_SECRET` - Your Coinbase API secret

### 3️⃣ Test Connection
```bash
# Activate virtual environment
source venv/bin/activate

# Test system
python main.py --mode status
```

### 4️⃣ Run Your First Cycle
```bash
python main.py --mode single
```

## 🎮 Command Cheat Sheet

| Command | Description |
|---------|-------------|
| `python main.py --mode single` | Run one cycle and exit |
| `python main.py --mode continuous` | Run continuously (15 min intervals) |
| `python main.py --mode status` | Check system status |
| `python main.py --mode rebalance` | Manual rebalancing |
| `python main.py --mode emergency` | EMERGENCY STOP (closes all) |

## 📊 Quick Monitoring

### View Logs
```bash
# System logs
tail -f logs/system.log

# Watch for errors
grep ERROR logs/system.log

# Check trade history
cat data/engine/trades.jsonl | tail -5
```

### Check Positions
```python
from modules.engine_manager import EngineManager
engine = EngineManager()
print(engine.get_performance_metrics())
```

### View Vault Health
```python
from modules.vault_manager import VaultManager
vault = VaultManager()
health = vault.check_health()
print(f"Health Score: {health.health_score}")
```

## 🔧 Quick Configuration Changes

### Adjust Risk Parameters
Edit `.env`:
```env
MAX_POSITION_SIZE_USD=500    # Lower position size
DAILY_LOSS_LIMIT_USD=100     # Tighter loss limit
```

### Change Allocations
Edit `config/ves_architecture.yaml`:
```yaml
vault:
  assets:
    stETH:
      allocation_percent: 50  # Increase stETH
```

## 🚨 Emergency Procedures

### Stop All Trading
```bash
python main.py --mode emergency
# Type 'yes' to confirm
```

### Manual Position Close
```python
from modules.engine_manager import EngineManager
engine = EngineManager()
engine.close_position("SOL-USD", "MANUAL")
```

### System Reset
```bash
# Stop system
pkill -f "python main.py"

# Clear state
rm -rf data/*

# Restart
python main.py --mode single
```

## 📈 Performance Check

### Daily Summary
```python
import json
from pathlib import Path

# Read today's cycles
cycle_file = Path(f"data/cycles_{datetime.now().strftime('%Y%m%d')}.jsonl")
with open(cycle_file, 'r') as f:
    cycles = [json.loads(line) for line in f]
    
print(f"Cycles run: {len(cycles)}")
print(f"Last cycle: {cycles[-1]['timestamp']}")
```

## 🔄 Automation Setup

### Linux/Mac (cron)
```bash
# Edit crontab
crontab -e

# Add this line for hourly runs
0 * * * * cd /workspace/SovereignShadow && /usr/bin/python3 main.py --mode single >> logs/cron.log 2>&1
```

### Windows (Task Scheduler)
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily/Hourly
4. Set action: Start Program
5. Program: `python.exe`
6. Arguments: `C:\path\to\SovereignShadow\main.py --mode single`

## 💡 Pro Tips

1. **Start Small**: Use minimal position sizes initially
2. **Monitor Closely**: Check logs frequently in first week
3. **Manual Vault Updates**: Update Ledger positions weekly
4. **Backup Regularly**: Copy `data/` folder weekly
5. **Test Changes**: Use single mode after config changes

## 🐛 Common Issues

**"API rate limit exceeded"**
→ Increase interval between cycles

**"Insufficient balance"**
→ Check siphon distributions, may need rebalance

**"Connection refused"**
→ Check API credentials and network

**"Module not found"**
→ Activate virtual environment: `source venv/bin/activate`

## 📞 Need Help?

1. Check `logs/system.log` for errors
2. Review configuration in `.env` and `config/`
3. Run status check: `python main.py --mode status`
4. See full documentation: `README.md`

---

**Remember**: Start with small amounts, monitor closely, never invest more than you can afford to lose! 🎯