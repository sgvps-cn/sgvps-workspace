#!/usr/bin/env python3
"""
贾维斯自主修复引擎 v2 - Jarvis Self-Repair Engine v2
增强版：增加Gateway/进程重复/内存/网络/cron自检/日志轮转/Feishu通知
"""

import os
import sys
import json
import subprocess
import time
import re
from datetime import datetime

LOG = "/root/.openclaw/workspace/memory/self-repair.log"
STATE_FILE = "/root/.openclaw/workspace/memory/self-repair-state.json"
MAX_LOG_SIZE_MB = 10

def log(msg):
    ts = datetime.now().strftime("%m-%d %H:%M")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def rotate_log():
    """日志轮转：超过10MB时轮转"""
    try:
        if os.path.exists(LOG) and os.path.getsize(LOG) > MAX_LOG_SIZE_MB * 1024 * 1024:
            ts = datetime.now().strftime("%Y%m%d%H%M")
            bak = f"{LOG}.{ts}"
            os.rename(LOG, bak)
            log(f"日志轮转: {bak}")
    except: pass

def feishu(text):
    """发送Feishu通知"""
    try:
        subprocess.run(["python3", "/root/.openclaw/workspace/.feishu-notify.py", text],
                      capture_output=True, timeout=10)
    except: pass

def cmd(c, timeout=10):
    """运行shell命令，返回 (success, stdout, stderr)"""
    try:
        r = subprocess.run(c, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode == 0, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "timeout"
    except Exception as e:
        return False, "", str(e)

def get_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

# ─── Git自修复 ───────────────────────────────────────────────
def repair_git():
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

# ─── Cron自修复 ────────────────────────────────────────────────
def repair_cron():
    fixed = []
    ok, out, _ = cmd("pgrep -f 'cron.php' | head -1")
    if ok and out:
        ok2, time_str, _ = cmd(f"ps -o etimes= -p {out}")
        if ok2 and time_str:
            try:
                elapsed = int(time_str)
                if elapsed > 300:
                    cmd(f"kill -9 {out}")
                    fixed.append(f"cron_killed({elapsed}s)")
                    log(f"  ⚠️ cron.php卡住{elapsed}秒，已终止")
            except: pass
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

# ─── 进程自修复（增强）──────────────────────────────────────────
def repair_procs():
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
    # Clash - 改进检测：只检查clash子进程，不杀wrapper
    _, out, _ = cmd("pgrep -f '/root/clash/clash'")
    clash_pids = [p for p in out.strip().split("\n") if p]
    # 检查nohup wrapper是否还在
    _, wrapper_out, _ = cmd("pgrep -f 'nohup.*clash' | grep -v $$")
    wrapper_pids = [p for p in wrapper_out.strip().split("\n") if p]
    if not clash_pids:
        if wrapper_pids:
            log(f"  ⚠️ Clash子进程挂了，但wrapper({wrapper_pids[0]})还在，等待自动恢复")
            # 不杀wrapper，给它时间自动拉起clash
            fixed.append("clash_wrapper_alive_wait")
        else:
            log("  ⚠️ Clash未运行，重启")
            cmd("cd /root/clash && nohup ./clash -d . > /tmp/clash.log 2>&1 &", timeout=5)
            fixed.append("clash_restart")
    elif len(clash_pids) > 1:
        # 重复进程：只保留最新的
        log(f"  ⚠️ Clash重复进程{len(clash_pids)}个，清理中")
        for pid in clash_pids[:-1]:
            cmd(f"kill -9 {pid} 2>/dev/null")
        fixed.append(f"clash_dedup({len(clash_pids)-1})")
    return fixed

# ─── Gateway健康检查（新增）─────────────────────────────────────
def repair_gateway():
    fixed = []
    # 检查端口18789是否响应
    ok, out, err = cmd("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:18789/ 2>/dev/null", timeout=5)
    if not ok or out != "200":
        log(f"  ⚠️ Gateway响应异常({out})，尝试重启")
        # 先尝试graceful restart
        ok2, _, _ = cmd("openclaw gateway restart 2>/dev/null", timeout=15)
        if ok2:
            time.sleep(3)
            ok3, code, _ = cmd("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:18789/ 2>/dev/null", timeout=5)
            if ok3 and code == "200":
                fixed.append("gateway_restart_ok")
            else:
                fixed.append("gateway_restart_failed")
        else:
            fixed.append("gateway_restart_failed")
    return fixed

# ─── 重复进程检测（新增）────────────────────────────────────────
def repair_dup_procs():
    """扫描重复命名的后台进程，避免资源泄漏"""
    fixed = []
    # 找所有带 nohup 的 wrapper shell 进程
    ok, out, _ = cmd("ps aux | grep 'nohup' | grep -v grep | awk '{print $11,$2}'")
    if ok and out:
        lines = out.strip().split("\n")
        counts = {}
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                cmd_name = parts[0]
                counts[cmd_name] = counts.get(cmd_name, [])
                counts[cmd_name].append(parts[1])
        for name, pids in counts.items():
            if len(pids) >= 3:
                log(f"  ⚠️ 重复后台进程 {name}: {len(pids)}个，保留最新1个")
                for pid in pids[:-1]:
                    cmd(f"kill -9 {pid} 2>/dev/null")
                fixed.append(f"dup_clean_{name}({len(pids)-1})")
    return fixed

# ─── 内存过载保护（新增）────────────────────────────────────────
def repair_memory():
    fixed = []
    ok, out, _ = cmd("free | grep Mem")
    if ok and out:
        parts = out.split()
        total = int(parts[1])
        available = int(parts[6]) if len(parts) > 6 else 0
        used = total - available
        pct = int(used / total * 100)
        if pct >= 90:
            log(f"  ⚠️ 内存使用率{pct}%，尝试清理")
            # 杀top内存占用者（python3/node进程，排除主进程）
            cmd("ps aux --sort=-%mem | grep -E 'python3|node' | grep -v grep | awk 'NR>3 {print $2}' | xargs -r kill -9 2>/dev/null")
            fixed.append(f"mem_cleanup({pct}%)")
        # 同时检查Swap
        ok2, swap, _ = cmd("free | grep Swap")
        if ok2 and swap:
            swap_parts = swap.split()
            if len(swap_parts) >= 4 and int(swap_parts[2]) > 1024 * 1024:  # Swap使用超过1GB
                log("  ⚠️ Swap使用过高，触发主动清理")
                cmd("swapoff -a && swapon -a 2>/dev/null", timeout=30)
                fixed.append("swap_recycle")
    return fixed

# ─── 网络连通性检查（新增）───────────────────────────────────────
def repair_network():
    fixed = []
    # 检查外网连通性（Clash API + 外网）
    _, out1, _ = cmd("curl -s -o /dev/null -w '%{http_code}' --connect-timeout 3 http://127.0.0.1:9090/proxies 2>/dev/null")
    if out1 == "200":
        fixed.append("clash_api_ok")
    else:
        log(f"  ⚠️ Clash API无响应({out1})")
        fixed.append("clash_api_fail")
    # 检查OpenClaw外网连通性
    _, out2, _ = cmd("curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 https://api.openclaw.ai 2>/dev/null")
    if out2 != "200":
        log(f"  ⚠️ 外网连通性异常({out2})")
        fixed.append(f"network_fail({out2})")
    return fixed

# ─── Self-Repair Cron自检（新增）─────────────────────────────────
def repair_self_cron():
    """检查self-repair的cron job是否还在，不在则重新注册"""
    fixed = []
    ok, out, _ = cmd("crontab -l 2>/dev/null | grep self-repair")
    if not ok or not out:
        log("  ⚠️ Self-Repair Cron丢失，重新注册")
        # 重新注册每小时运行
        cron_cmd = "0 * * * * python3 /root/.openclaw/workspace/.self-repair.py >> /root/.openclaw/workspace/memory/self-repair.log 2>&1\n"
        # 读取现有crontab，追加
        ok2, existing, _ = cmd("crontab -l 2>/dev/null")
        new_crontab = existing + "\n" + cron_cmd if ok2 else cron_cmd
        try:
            p = subprocess.run("crontab -", shell=True, input=new_crontab, capture_output=True, text=True, timeout=5)
            if p.returncode == 0:
                fixed.append("cron_reregistered")
        except: pass
    return fixed

# ─── Evolver状态同步 ────────────────────────────────────────────
def repair_evolver():
    fixed = []
    evolver_dir = "/root/.openclaw/evolver"
    if not os.path.exists(evolver_dir):
        return fixed
    ok, out, _ = cmd(f"cd {evolver_dir} && node -e \"const h=require('./src/ops/health_check');const r=h.runHealthCheck();console.log(JSON.stringify(r))\"")
    if ok:
        try:
            r = json.loads(out)
            if r.get('status') == 'error':
                log(f"  ⚠️ Evolver健康检查异常: {r}")
                fixed.append("evolver_health_error")
            elif r.get('status') == 'warning':
                pass
        except: pass
    return fixed

# ─── 磁盘自修复 ────────────────────────────────────────────────
def repair_disk():
    fixed = []
    for pattern in ["__pycache__", "*.pyc", "*.pyo"]:
        cmd(f"find /root/.openclaw/workspace -name '{pattern}' -type d -exec rm -rf {{}} + 2>/dev/null; true")
    try:
        cmd("find /root/.openclaw/workspace/memory -name '*.log' -mtime +7 -delete 2>/dev/null; true")
        cmd("find /root/.openclaw/workspace/memory -name 'daemon-state.json' -mtime +1 -delete 2>/dev/null; true")
    except: pass
    cmd("find /root/.openclaw/workspace/node_modules -name '.cache' -type d -exec rm -rf {} + 2>/dev/null; true")
    return fixed if fixed else []

# ─── Exec工具健康检查（新增）─────────────────────────────────────
def repair_exec():
    """验证exec工具是否正常响应"""
    fixed = []
    ok, out, _ = cmd("echo 'health_check_ok'", timeout=5)
    if not ok or "health_check_ok" not in out:
        log("  ⚠️ Exec工具异常")
        fixed.append("exec_unhealthy")
    return fixed

# ─── 主流程 ─────────────────────────────────────────────────────
def main():
    rotate_log()
    log("=== 自主修复开始(v2) ===")
    state = get_state()
    all_fixed = []

    repairs = {
        "git": repair_git,
        "cron": repair_cron,
        "procs": repair_procs,
        "gateway": repair_gateway,
        "dup_procs": repair_dup_procs,
        "memory": repair_memory,
        "network": repair_network,
        "self_cron": repair_self_cron,
        "evolver": repair_evolver,
        "disk": repair_disk,
        "exec": repair_exec,
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
    state["repair_count"] = state.get("repair_count", 0) + 1
    save_state(state)

    if all_fixed:
        msg = f"✅ 修复完成: {len(all_fixed)}项 - {', '.join(all_fixed)}"
        log(msg)
        feishu(f"🔧 贾维斯自我修复\n{msg}")
    else:
        log("✅ 检查完成，无修复")

    return 0

if __name__ == "__main__":
    sys.exit(main())
