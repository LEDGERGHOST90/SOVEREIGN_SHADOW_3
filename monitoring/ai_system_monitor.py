#!/usr/bin/env python3
"""
🧠 AI SYSTEM MONITOR
Real-time monitoring dashboard for AI trading platform
"""

import os
import sys
import time
import json
import psutil
import logging
import subprocess
from datetime import datetime
from pathlib import Path
import argparse
try:
    import pynvml  # optional GPU telemetry
except Exception:
    pynvml = None

# Configure logging
os.makedirs('logs/ai_enhanced', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ai_enhanced/ai_system_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ai_system_monitor")

class AISystemMonitor:
    """AI System Health Monitor"""
    
    def __init__(self):
        self.monitoring_active = True
        self.ai_processes = []
        self.system_health = {}
        self._last_net = psutil.net_io_counters()
        self._last_net_ts = time.time()
        self._last_update_ts = 0
        self._last_eod_date = None
        logger.info("🧠 AI System Monitor Initialized")
    
    def scan_ai_processes(self):
        """Scan for AI-related processes"""
        ai_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
            try:
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                
                # Check for AI-related processes
                if any(keyword in cmdline.lower() for keyword in [
                    'ai_portfolio_protection', 'empire_automation', 'trading', 'claude', 'mcp',
                    'deepagent', 'sovereign_shadow_unified', 'okx', 'kraken', 'coinbase', 'ledger'
                ]):
                    ai_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': cmdline,
                        'cpu_percent': proc.info['cpu_percent'],
                        'memory_percent': proc.info['memory_percent']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        self.ai_processes = ai_processes
        return ai_processes
    
    def check_system_health(self):
        """Check overall system health"""
        # CPU/mem/disk
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        # Network throughput
        now = time.time()
        net = psutil.net_io_counters()
        elapsed = max(now - self._last_net_ts, 1e-6)
        bytes_sent_s = (net.bytes_sent - self._last_net.bytes_sent) / elapsed
        bytes_recv_s = (net.bytes_recv - self._last_net.bytes_recv) / elapsed
        self._last_net = net
        self._last_net_ts = now

        # GPU stats (optional)
        gpu_stats = []
        if pynvml is not None:
            try:
                pynvml.nvmlInit()
                count = pynvml.nvmlDeviceGetCount()
                for i in range(count):
                    h = pynvml.nvmlDeviceGetHandleByIndex(i)
                    name = pynvml.nvmlDeviceGetName(h).decode('utf-8') if hasattr(pynvml.nvmlDeviceGetName(h), 'decode') else str(pynvml.nvmlDeviceGetName(h))
                    util = pynvml.nvmlDeviceGetUtilizationRates(h)
                    meminfo = pynvml.nvmlDeviceGetMemoryInfo(h)
                    gpu_stats.append({
                        'index': i,
                        'name': name,
                        'gpu_util_percent': getattr(util, 'gpu', 0),
                        'mem_util_percent': getattr(util, 'memory', 0),
                        'mem_used_bytes': getattr(meminfo, 'used', 0),
                        'mem_total_bytes': getattr(meminfo, 'total', 0),
                    })
            except Exception:
                gpu_stats = [{'error': 'pynvml_error'}]
            finally:
                try:
                    pynvml.nvmlShutdown()
                except Exception:
                    pass

        health = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': cpu,
            'memory_percent': mem,
            'disk_percent': disk,
            'net_bytes_sent_per_s': bytes_sent_s,
            'net_bytes_recv_per_s': bytes_recv_s,
            'gpu': gpu_stats,
            'ai_processes_count': len(self.ai_processes),
            'ai_processes': self.ai_processes,
            'guardrails': self.check_guardrails()
        }

        self.system_health = health
        return health

    def check_guardrails(self):
        """Report trading guardrail environment flags"""
        env = os.getenv('ENV', 'dev')
        allow_live = os.getenv('ALLOW_LIVE_EXCHANGE', '0')
        disable_real = os.getenv('DISABLE_REAL_EXCHANGES', '1')
        sandbox = os.getenv('SANDBOX', '0')
        live = (env == 'prod' and allow_live == '1' and disable_real != '1')
        effective = 'LIVE' if live else ('SANDBOX' if sandbox == '1' else 'FAKE')
        # Extended policy/risk flags (optional)
        risk_profile = os.getenv('RISK_PROFILE', 'UNSET')
        sweep_mode = os.getenv('SWEEP_MODE', 'PARK')
        okx_day_cap = os.getenv('OKX_DAY_LOSS_CAP', '')
        okx_risk_min = os.getenv('OKX_RISK_UNIT_MIN', '')
        okx_risk_max = os.getenv('OKX_RISK_UNIT_MAX', '')
        okx_max_legs = os.getenv('OKX_MAX_LEGS', '')
        okx_max_exp = os.getenv('OKX_MAX_EXPOSURE_PCT', '')
        cb_trade_size_pct = os.getenv('COINBASE_TRADE_SIZE_PCT', '')
        cb_open_risk_pct = os.getenv('COINBASE_MAX_OPEN_RISK_PCT', '')
        cb_buffer_floor = os.getenv('COINBASE_BUFFER_FLOOR', '')

        return {
            'ENV': env,
            'ALLOW_LIVE_EXCHANGE': allow_live,
            'DISABLE_REAL_EXCHANGES': disable_real,
            'SANDBOX': sandbox,
            'effective_mode': effective,
            'RISK_PROFILE': risk_profile,
            'SWEEP_MODE': sweep_mode,
            'OKX_DAY_LOSS_CAP': okx_day_cap,
            'OKX_RISK_UNIT_MIN': okx_risk_min,
            'OKX_RISK_UNIT_MAX': okx_risk_max,
            'OKX_MAX_LEGS': okx_max_legs,
            'OKX_MAX_EXPOSURE_PCT': okx_max_exp,
            'COINBASE_TRADE_SIZE_PCT': cb_trade_size_pct,
            'COINBASE_MAX_OPEN_RISK_PCT': cb_open_risk_pct,
            'COINBASE_BUFFER_FLOOR': cb_buffer_floor
        }
    
    def generate_status_report(self):
        """Generate comprehensive status report"""
        self.scan_ai_processes()
        self.check_system_health()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_health': self.system_health,
            'guardrails': self.system_health.get('guardrails', {}),
            'ai_systems': {
                'portfolio_protection': self.check_ai_portfolio_protection(),
                'empire_automation': self.check_empire_automation(),
                'claude_sdk': self.check_claude_sdk(),
                'mcp_framework': self.check_mcp_framework()
            },
            'dependencies': self.check_dependencies(),
            'logs': self.check_log_files()
        }
        
        return report
    
    def check_ai_portfolio_protection(self):
        """Check AI Portfolio Protection status"""
        for proc in self.ai_processes:
            if 'ai_portfolio_protection' in proc['cmdline']:
                return {
                    'status': 'ACTIVE',
                    'pid': proc['pid'],
                    'cpu_percent': proc['cpu_percent'],
                    'memory_percent': proc['memory_percent']
                }
        return {'status': 'INACTIVE'}
    
    def check_empire_automation(self):
        """Check Empire Automation status"""
        for proc in self.ai_processes:
            if 'empire_automation' in proc['cmdline']:
                return {
                    'status': 'ACTIVE',
                    'pid': proc['pid'],
                    'cpu_percent': proc['cpu_percent'],
                    'memory_percent': proc['memory_percent']
                }
        return {'status': 'INACTIVE'}
    
    def check_claude_sdk(self):
        """Check Claude SDK status"""
        # Check for Claude SDK environment variables
        claude_active = os.getenv('CLAUDE_SDK_ACTIVE', 'false') == 'true'
        return {
            'status': 'ACTIVE' if claude_active else 'INACTIVE',
            'environment': 'SET' if claude_active else 'NOT_SET'
        }
    
    def check_mcp_framework(self):
        """Check MCP Framework status"""
        # Check for MCP Framework environment variables
        mcp_active = os.getenv('MCP_FRAMEWORK_ACTIVE', 'false') == 'true'
        return {
            'status': 'ACTIVE' if mcp_active else 'INACTIVE',
            'environment': 'SET' if mcp_active else 'NOT_SET'
        }
    
    def check_dependencies(self):
        """Check Python dependencies"""
        dependencies = {
            'websocket-client': False,
            'pyyaml': False,
            'pandas': False,
            'numpy': False
        }
        
        try:
            import websocket
            dependencies['websocket-client'] = True
        except ImportError:
            pass
        
        try:
            import yaml
            dependencies['pyyaml'] = True
        except ImportError:
            pass
        
        try:
            import pandas
            dependencies['pandas'] = True
        except ImportError:
            pass
        
        try:
            import numpy
            dependencies['numpy'] = True
        except ImportError:
            pass
        
        return dependencies
    
    def check_log_files(self):
        """Check log file status"""
        log_files = {
            'ai_portfolio_protection.log': False,
            'ai_system_monitor.log': False,
            'empire_automation.log': False
        }
        
        log_paths = [
            'logs/ai_enhanced/ai_portfolio_protection.log',
            'logs/ai_enhanced/ai_system_monitor.log',
            'logs/empire_automation.log'
        ]
        
        for log_path in log_paths:
            if os.path.exists(log_path):
                log_files[os.path.basename(log_path)] = True
        
        return log_files
    
    def maybe_run_trading_update(self):
        """
        Optionally invoke the trading updates hub script on an interval and at EOD.
        Controlled by environment variables:
          TRADING_UPDATE_ENABLE=1
          TRADING_UPDATE_SCRIPT=scripts/trading_updates_hub.py
          TRADING_UPDATE_INTERVAL_MIN=60
          TRADING_UPDATE_EOD=23:55     # local time (America/Los_Angeles)
          TRADING_UPDATE_WINDOW=24h    # passed to --window
          TRADING_UPDATE_NO_CLAUDE=0   # 1 to add --no-claude
        """
        if os.getenv('TRADING_UPDATE_ENABLE', '0') != '1':
            return
        script_path = os.getenv('TRADING_UPDATE_SCRIPT', 'scripts/trading_updates_hub.py')
        if not os.path.exists(script_path):
            logger.debug(f"Trading update script not found: {script_path}")
            return
        try:
            interval_min = int(os.getenv('TRADING_UPDATE_INTERVAL_MIN', '60'))
        except Exception:
            interval_min = 60
        window_arg = os.getenv('TRADING_UPDATE_WINDOW', '24h')
        no_claude = os.getenv('TRADING_UPDATE_NO_CLAUDE', '0') == '1'
        eod_hhmm = os.getenv('TRADING_UPDATE_EOD', '23:55')
        # Parse EOD target
        try:
            eod_h, eod_m = [int(x) for x in eod_hhmm.split(':', 1)]
        except Exception:
            eod_h, eod_m = 23, 55
        now = datetime.now()
        # Run on interval
        if (time.time() - self._last_update_ts) >= max(1, interval_min) * 60:
            cmd = [sys.executable, script_path, '--window', window_arg]
            if no_claude:
                cmd.append('--no-claude')
            try:
                os.makedirs('logs/ai_enhanced', exist_ok=True)
                with open('logs/ai_enhanced/trading_updates.log', 'a') as lf:
                    lf.write(f"[{datetime.now().isoformat()}] Running interval update: {' '.join(cmd)}\n")
                subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            except Exception as e:
                logger.error(f"Trading update interval run failed: {e}")
            self._last_update_ts = time.time()
        # Run once at EOD
        is_eod_window = (now.hour == eod_h and now.minute >= eod_m)
        if is_eod_window and (self._last_eod_date != now.date()):
            cmd = [sys.executable, script_path, '--window', '24h']
            if no_claude:
                cmd.append('--no-claude')
            try:
                os.makedirs('logs/ai_enhanced', exist_ok=True)
                with open('logs/ai_enhanced/trading_updates.log', 'a') as lf:
                    lf.write(f"[{datetime.now().isoformat()}] Running EOD update: {' '.join(cmd)}\n")
                subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            except Exception as e:
                logger.error(f"Trading update EOD run failed: {e}")
            self._last_eod_date = now.date()

    def display_dashboard(self):
        """Display real-time dashboard"""
        report = self.generate_status_report()
        
        print("\n" + "="*80)
        print("🧠 AI TRADING PLATFORM - SYSTEM MONITOR")
        print("="*80)
        print(f"📅 Timestamp: {report['timestamp']}")
        print(f"💻 CPU Usage: {report['system_health']['cpu_percent']:.1f}%")
        print(f"🧠 Memory Usage: {report['system_health']['memory_percent']:.1f}%")
        print(f"💾 Disk Usage: {report['system_health']['disk_percent']:.1f}%")
        print(f"📡 Net TX: {report['system_health']['net_bytes_sent_per_s']:.0f} B/s | RX: {report['system_health']['net_bytes_recv_per_s']:.0f} B/s")
        if report['system_health']['gpu']:
            first = report['system_health']['gpu'][0]
            if 'error' not in first:
                print(f"🟩 GPU0 {first['name']}: {first['gpu_util_percent']}% / {first['mem_util_percent']}% mem")
        print(f"🔧 AI Processes: {report['system_health']['ai_processes_count']}")
        
        print("\n🤖 AI SYSTEMS STATUS:")
        print("-" * 40)
        for system, status in report['ai_systems'].items():
            status_icon = "✅" if status['status'] == 'ACTIVE' else "❌"
            print(f"{status_icon} {system.replace('_', ' ').title()}: {status['status']}")
            if 'pid' in status:
                print(f"   PID: {status['pid']}, CPU: {status['cpu_percent']:.1f}%, Memory: {status['memory_percent']:.1f}%")
        
        print("\n🛡️ GUARDRAILS:")
        print("-" * 40)
        gr = report.get('guardrails', {})
        print(f"ENV={gr.get('ENV','?')} | ALLOW_LIVE_EXCHANGE={gr.get('ALLOW_LIVE_EXCHANGE','?')} | DISABLE_REAL_EXCHANGES={gr.get('DISABLE_REAL_EXCHANGES','?')} | SANDBOX={gr.get('SANDBOX','0')} → Mode: {gr.get('effective_mode','?')}")
        print(f"RiskProfile={gr.get('RISK_PROFILE','UNSET')} | SweepMode={gr.get('SWEEP_MODE','PARK')} | OKX DayCap={gr.get('OKX_DAY_LOSS_CAP','')} | OKX Legs={gr.get('OKX_MAX_LEGS','')} | CB OpenRisk%={gr.get('COINBASE_MAX_OPEN_RISK_PCT','')}")
        if os.getenv('TRADING_UPDATE_ENABLE', '0') == '1':
            print(f"📝 Trading updates: interval={os.getenv('TRADING_UPDATE_INTERVAL_MIN','60')} min, EOD={os.getenv('TRADING_UPDATE_EOD','23:55')}, window={os.getenv('TRADING_UPDATE_WINDOW','24h')}")
        
        print("\n📦 DEPENDENCIES STATUS:")
        print("-" * 40)
        for dep, installed in report['dependencies'].items():
            status_icon = "✅" if installed else "❌"
            print(f"{status_icon} {dep}: {'INSTALLED' if installed else 'MISSING'}")
        
        print("\n📋 LOG FILES STATUS:")
        print("-" * 40)
        for log, exists in report['logs'].items():
            status_icon = "✅" if exists else "❌"
            print(f"{status_icon} {log}: {'EXISTS' if exists else 'MISSING'}")
        
        print("="*80)
        
        return report
    
    def run_monitor(self, interval=30):
        """Run continuous monitoring"""
        logger.info(f"🧠 Starting AI System Monitor (interval: {interval}s)")
        
        try:
            while self.monitoring_active:
                self.display_dashboard()
                
                # Save report to file
                report = self.generate_status_report()
                with open('logs/ai_enhanced/system_status.json', 'w') as f:
                    json.dump(report, f, indent=2)
                with open('logs/ai_enhanced/system_status.jsonl', 'a') as f:
                    f.write(json.dumps(report, default=str) + '\n')
                # Optionally emit trading updates (interval + EOD)
                self.maybe_run_trading_update()
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("🧠 AI System Monitor stopped by user")
        except Exception as e:
            logger.error(f"🧠 AI System Monitor error: {e}")

def _print_json(obj):
    print(json.dumps(obj, indent=2, default=str))

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI System Monitor")
    parser.add_argument('--continuous', action='store_true', help='Run continuous monitoring loop')
    parser.add_argument('--interval', type=int, default=30, help='Loop interval seconds')
    parser.add_argument('--json', action='store_true', help='Print JSON report instead of human dashboard')
    args = parser.parse_args()

    monitor = AISystemMonitor()

    if args.continuous:
        # run continuous loop
        logger.info(f"🧠 Starting AI System Monitor (interval: {args.interval}s)")
        try:
            while monitor.monitoring_active:
                report = monitor.generate_status_report()
                # print
                if args.json:
                    _print_json(report)
                else:
                    monitor.display_dashboard()
                # persist snapshot and jsonl
                os.makedirs('logs/ai_enhanced', exist_ok=True)
                with open('logs/ai_enhanced/system_status.json', 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                with open('logs/ai_enhanced/system_status.jsonl', 'a') as f:
                    f.write(json.dumps(report, default=str) + '\n')
                time.sleep(args.interval)
        except KeyboardInterrupt:
            logger.info("🧠 AI System Monitor stopped by user")
        return

    # one-shot
    report = monitor.generate_status_report()
    if args.json:
        _print_json(report)
    else:
        monitor.display_dashboard()
    # save one-shot
    with open('logs/ai_enhanced/system_status.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)

if __name__ == "__main__":
    main()
