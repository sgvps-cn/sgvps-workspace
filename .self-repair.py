#!/usr/bin/env python3
"""
贾维斯自主修复引擎 - Jarvis Self-Repair Engine
每当守护进程检测到问题时调用，或定时调用
自动修复常见故障，不需要人工干预
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime

LOG = "/root/.openclaw/workspace/memory/self-repair.log"
STATE_FILE = "/root/.openclaw/workspace/memory/self-repair-state.json"

def log(msg):
    ts = datetime.now().strftime("%m-%d %H:%M")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def get_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def cmd(c, timeout=10):
    """运行shell命令，返回 (success, stdout, stderr)"""
    try:
        r = subprocess.run(c, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode == 0, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "timeout"
    except Exception as e:
        return False, "", str(e)

def repair_git():
    """Git自修复: 中止rebase/merge，清理锁文件"""
    fixed = []
    try:
        subprocess.run(["git", "rebase", "--abort"], capture_output=True, timeout=5)
        fixed.append("rebase_aborted")
    except: pass
    try:
        subprocess.run(["git", "merge", "--abort"], capture_output=True, timeout=5)
        fixed.append("merge_aborted")
    except: pass
    lock = "/root/.openclaw/workspace/.git/index.lock"
    if os.path.exists(lock):
        try:
            age = time.time() - os.path.getmtime(lock)
            if age > 600:
                os.unlink(lock)
                fixed.append(f"lock_removed({int(age/60)}min)")
        except: pass
    ok, out, _ = cmd("cd /root/.openclaw/workspace && git fetch origin")
    if ok: fixed.append("git_fetch")
    return fixed

def repair_cron():
    """Cron自修复: 检测并终止卡住的cron进程"""
    fixed = []
    # 检查cron.php是否卡住
    ok, out, _ = cmd("pgrep -f 'cron.php' | head -1")
    if ok and out:
        # 检查CPU时间
        ok2, time_str, _ = cmd(f"ps -o etimes= -p {out}")
        if ok2 and time_str:
            try:
                elapsed = int(time_str)
                if elapsed > 300:
                    cmd(f"kill -9 {out}")
                    fixed.append(f"cron_killed({elapsed}s)")
                    log("  ⚠️ cron.php卡住{elapsed}秒，已终止")
            except: pass
    # BT-Panel cron日志异常
    try:
        with open("/www/server/cron/8146b52f60ab0bdb5159d4361fa64eea.log") as f:
            lines = f.readlines()
        if lines and "already exists" in lines[-1]:
            count = sum(1 for l in lines if "already exists" in l)
            if count >= 3:
                cmd("pkill -9 -f 'cron.php'")
                fixed.append("cron_stuck_cleaned")
    except: pass
    return fixed

def repair_procs():
    """进程自修复: 检测崩溃的关键服务"""
    fixed = []
    # MySQL
    ok, out, _ = cmd("systemctl is-active mysql")
    if not ok or "active" not in out:
        log("  ⚠️ MySQL未运行，尝试重启")
        ok2, _, err = cmd("systemctl restart mysql", timeout=15)
        fixed.append(f"mysql_restart({'ok' if ok2 else 'failed'})")
    # PHP-FPM
    ok, out, _ = cmd("systemctl is-active php-fpm-74")
    if not ok or "active" not in out:
        ok2, _, _ = cmd("systemctl restart php-fpm-74", timeout=15)
        if ok2: fixed.append("php_restart")
    # jarvis-daemon
    ok, out, _ = cmd("systemctl is-active jarvis-daemon")
    if not ok or "active" not in out:
        log("  ⚠️ jarvis-daemon未运行，重启")
        cmd("systemctl restart jarvis-daemon", timeout=10)
        fixed.append("daemon_restart")
    # Clash
    ok, out, _ = cmd("pgrep -f '/root/clash/clash'")
    if not ok or not out:
        log("  ⚠️ Clash未运行，重启")
        cmd("cd /root/clash && nohup ./clash -d . > /tmp/clash.log 2>&1 &", timeout=5)
        fixed.append("clash_restart")
    return fixed

def repair_disk():
    """磁盘自修复: 清理临时文件"""
    fixed = []
    # 清理Python缓存
    for pattern in ["__pycache__", "*.pyc", "*.pyo"]:
        ok, out, _ = cmd(f"find /root/.openclaw/workspace -name '{pattern}' -type d -exec rm -rf {{}} + 2>/dev/null; true")
    # 清理旧的守护日志(保留7天)
    try:
        cmd("find /root/.openclaw/workspace/memory -name '*.log' -mtime +7 -delete 2>/dev/null; true")
        cmd("find /root/.openclaw/workspace/memory -name 'daemon-state.json' -mtime +1 -delete 2>/dev/null; true")
    except: pass
    # 清理node_modules的临时文件
    cmd("find /root/.openclaw/workspace/node_modules -name '.cache' -type d -exec rm -rf {} + 2>/dev/null; true")
    return fixed if fixed else []

def repair_evolver():
    """Evolver自进化: 运行Evolver健康检查和修复"""
    fixed = []
    evolver_dir = "/root/.openclaw/evolver"
    if not os.path.exists(evolver_dir):
        return fixed
    # 健康检查
    ok, out, _ = cmd(f"cd {evolver_dir} && node -e \"const h=require('./src/ops/health_check');const r=h.runHealthCheck();console.log(JSON.stringify(r))\"")
    if ok:
        try:
            r = json.loads(out)
            if r.get('status') == 'error':
                log(f"  ⚠️ Evolver健康检查异常: {r}")
                fixed.append("evolver_health_error")
            elif r.get('status') == 'warning':
                # 记录但不告警
                pass
        except: pass
    return fixed

def main():
    log("=== 自主修复开始 ===")
    state = get_state()
    all_fixed = []
    
    repairs = {
        "git": repair_git,
        "cron": repair_cron,
        "procs": repair_procs,
        "disk": repair_disk,
        "evolver": repair_evolver,
    }
    
    for name, func in repairs.items():
        try:
            result = func()
            if result:
                log(f"  {name}: {', '.join(result)}")
                all_fixed.extend(result)
        except Exception as e:
            log(f"  {name}: ERROR {e}")
    
    state["last_repair"] = datetime.now().isoformat()
    state["last_fixed"] = all_fixed
    save_state(state)
    
    if all_fixed:
        log(f"✅ 修复完成: {len(all_fixed)}项 - {', '.join(all_fixed)}")
    else:
        log("✅ 检查完成，无修复")
    
    return 0 if not all_fixed else 0

if __name__ == "__main__":
    sys.exit(main())
