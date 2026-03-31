#!/usr/bin/env python3
"""
贾维斯自主修复引擎 v3 - Jarvis Self-Repair Engine v3
核心原则：只报告真正修了的，例行检查不报告（诚实原则）
"""

import os, sys, json, subprocess, time, re, random
from datetime import datetime

LOG = "/root/.openclaw/workspace/memory/self-repair.log"
STATE_FILE = "/root/.openclaw/workspace/memory/self-repair-state.json"
MAX_LOG_SIZE_MB = 10

def jitter_backoff(attempt, base=1, max_delay=32, jitter_range=0.5):
    """
    指数退避 + jitter（防止惊群）
    attempt: 重试次数（0起）
    base: 基础延迟秒数
    max_delay: 最大延迟秒数
    jitter_range: jitter 比例（0-1），0.5 表示 ±50%
    """
    delay = min(base * (2 ** attempt), max_delay)
    jitter = delay * jitter_range * (2 * random.random() - 1)
    return max(0.1, delay + jitter)

def log(msg):
    ts = datetime.now().strftime("%m-%d %H:%M")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def rotate_log():
    try:
        if os.path.exists(LOG) and os.path.getsize(LOG) > MAX_LOG_SIZE_MB * 1024 * 1024:
            bak = f"{LOG}.{datetime.now().strftime('%Y%m%d%H%M')}"
            os.rename(LOG, bak)
            log(f"日志轮转: {bak}")
    except: pass

def feishu(text):
    try:
        subprocess.run(["python3", "/root/.openclaw/workspace/.feishu-notify.py", text],
                      capture_output=True, timeout=10)
    except: pass

def cmd(c, timeout=10):
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

# ─── Git ────────────────────────────────────────────────────────
def repair_git():
    """只修真正存在的git问题，不报告例行检查结果"""
    repaired = []
    try:
        st = subprocess.run(["git", "status"], capture_output=True, text=True, timeout=5).stdout
        if "rebase in progress" in st or "You are currently rebasing" in st:
            subprocess.run(["git", "rebase", "--abort"], capture_output=True, timeout=5)
            repaired.append("rebase_aborted")
        if "merge in progress" in st or "You have unmerged" in st:
            subprocess.run(["git", "merge", "--abort"], capture_output=True, timeout=5)
            repaired.append("merge_aborted")
    except: pass
    lock = "/root/.openclaw/workspace/.git/index.lock"
    if os.path.exists(lock):
        try:
            age = time.time() - os.path.getmtime(lock)
            if age > 600:
                os.unlink(lock)
                repaired.append(f"lock_removed({int(age/60)}min)")
        except: pass
    # 例行fetch不报告（不是修复）
    cmd("cd /root/.openclaw/workspace && git fetch origin")
    return repaired

# ─── Cron ────────────────────────────────────────────────────────
def repair_cron():
    repaired = []
    ok, out, _ = cmd("pgrep -f 'cron.php' | head -1")
    if ok and out:
        ok2, time_str, _ = cmd(f"ps -o etimes= -p {out}")
        if ok2 and time_str:
            try:
                elapsed = int(time_str)
                if elapsed > 300:
                    cmd(f"kill -9 {out}")
                    repaired.append(f"cron_killed({elapsed}s)")
                    log(f"  ⚠️ cron.php卡住{elapsed}秒，已终止")
            except: pass
    try:
        with open("/www/server/cron/8146b52f60ab0bdb5159d4361fa64eea.log") as f:
            lines = f.readlines()
        if lines and "already exists" in lines[-1]:
            count = sum(1 for l in lines if "already exists" in l)
            if count >= 3:
                cmd("pkill -9 -f 'cron.php'")
                repaired.append("cron_stuck_cleaned")
    except: pass
    return repaired

# ─── 关键进程 ───────────────────────────────────────────────────
def repair_procs():
    repaired = []
    ok, out, _ = cmd("systemctl is-active mysql")
    if not ok or "active" not in out:
        log("  ⚠️ MySQL未运行，尝试重启")
        ok2, _, _ = cmd("systemctl restart mysql", timeout=15)
        repaired.append(f"mysql_restart({'ok' if ok2 else 'failed'})")
    ok, out, _ = cmd("systemctl is-active php-fpm-74")
    if not ok or "active" not in out:
        ok2, _, _ = cmd("systemctl restart php-fpm-74", timeout=15)
        if ok2: repaired.append("php_restart")
    ok, out, _ = cmd("systemctl is-active jarvis-daemon")
    if not ok or "active" not in out:
        log("  ⚠️ jarvis-daemon未运行，重启")
        cmd("systemctl restart jarvis-daemon", timeout=10)
        repaired.append("daemon_restart")
    # Clash - 只在真正未运行时报告
    _, out, _ = cmd("pgrep -a clash 2>/dev/null")
    lines = [l for l in out.strip().split("\n") if l and "./clash" in l]
    clash_pids = [l.split()[0] for l in lines]
    if not clash_pids:
        _, wrapper_out, _ = cmd("ps aux | grep 'nohup.*clash -d' | grep -v grep | awk '{print $2}'")
        wrapper_pids = [p for p in wrapper_out.strip().split("\n") if p]
        if wrapper_pids:
            time.sleep(jitter_backoff(0, base=1, max_delay=8))
            _, out2, _ = cmd("pgrep -a clash 2>/dev/null")
            lines2 = [l for l in out2.strip().split("\n") if l and "./clash" in l]
            if not lines2:
                cmd("cd /root/clash && nohup ./clash -d . > /tmp/clash.log 2>&1 &", timeout=5)
                repaired.append("clash_restart")
        else:
            cmd("cd /root/clash && nohup ./clash -d . > /tmp/clash.log 2>&1 &", timeout=5)
            repaired.append("clash_restart")
    elif len(clash_pids) > 1:
        for pid in clash_pids[:-1]:
            cmd(f"kill -9 {pid} 2>/dev/null")
        repaired.append(f"clash_dedup({len(clash_pids)-1})")
    return repaired

# ─── Gateway ────────────────────────────────────────────────────
def repair_gateway():
    repaired = []
    # 第一次检查
    ok, code, _ = cmd("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:18789/ 2>/dev/null", timeout=5)
    if ok and code == "200":
        return repaired

    # 第一次失败，重试2次（指数退避）
    for attempt in range(2):
        log(f"  ⚠️ Gateway响应异常({code})，重试中 (attempt {attempt+1}/2)")
        time.sleep(jitter_backoff(attempt, base=1, max_delay=8))
        ok, code, _ = cmd("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:18789/ 2>/dev/null", timeout=5)
        if ok and code == "200":
            return repaired

    # 重试都失败，执行重启
    log(f"  ⚠️ Gateway持续异常({code})，执行重启")
    cmd("openclaw gateway restart 2>/dev/null", timeout=15)
    time.sleep(jitter_backoff(0, base=1, max_delay=8))
    ok2, code2, _ = cmd("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:18789/ 2>/dev/null", timeout=5)
    repaired.append("gateway_restart_ok" if (ok2 and code2 == "200") else "gateway_restart_failed")
    return repaired

# ─── 重复进程 ───────────────────────────────────────────────────
def repair_dup_procs():
    repaired = []
    ok, out, _ = cmd("ps aux | grep nohup | grep -v grep | awk '{print $11,$2}'")
    if ok and out:
        lines = out.strip().split("\n")
        counts = {}
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                cn = parts[0]
                counts[cn] = counts.get(cn, [])
                counts[cn].append(parts[1])
        for name, pids in counts.items():
            if len(pids) >= 3:
                log(f"  ⚠️ 重复后台进程 {name}: {len(pids)}个")
                for pid in pids[:-1]:
                    cmd(f"kill -9 {pid} 2>/dev/null")
                repaired.append(f"dup_clean_{name}({len(pids)-1})")
    return repaired

# ─── 内存 ────────────────────────────────────────────────────────
def repair_memory():
    repaired = []
    ok, out, _ = cmd("free | grep Mem")
    if ok and out:
        parts = out.split()
        total = int(parts[1]); used = int(parts[2]); pct = int(used/total*100)
        if pct >= 90:
            log(f"  ⚠️ 内存使用率{pct}%，清理中")
            cmd("ps aux --sort=-%mem | grep -E 'python3|node' | grep -v grep | awk 'NR>3 {print $2}' | xargs -r kill -9 2>/dev/null")
            repaired.append(f"mem_cleanup({pct}%)")
        ok2, swap, _ = cmd("free | grep Swap")
        if ok2 and swap:
            sw_parts = swap.split()
            if len(sw_parts) >= 4 and int(sw_parts[2]) > 1024*1024:
                log("  ⚠️ Swap使用过高")
                cmd("swapoff -a && swapon -a 2>/dev/null", timeout=30)
                repaired.append("swap_recycle")
    return repaired

# ─── 网络（Clash API）────────────────────────────────────────────
def repair_network():
    repaired = []
    _, code, _ = cmd("curl -s -o /dev/null -w '%{http_code}' --connect-timeout 3 http://127.0.0.1:9090/proxies 2>/dev/null")
    if code != "200":
        log(f"  ⚠️ Clash API无响应({code})")
        repaired.append(f"clash_api_fail({code})")
    return repaired

# ─── Self-Repair Cron ───────────────────────────────────────────
def repair_self_cron():
    """检查并确保所有关键cron job存在，防止技能学习/进化系统被中断"""
    repaired = []
    # 全部关键cron jobs
    CRON_JOBS = [
        ("self-repair", "0 * * * * python3 /root/.openclaw/workspace/.self-repair.py >> /root/.openclaw/workspace/memory/self-repair.log 2>&1"),
        ("evolution-hourly", "5 * * * * python3 /root/.openclaw/workspace/.evolution-hourly.py >> /root/.openclaw/workspace/memory/evolution-report.log 2>&1"),
        ("gateway-watchdog", "* * * * * python3 /root/.openclaw/workspace/.gateway-watchdog.py >> /root/.openclaw/workspace/memory/watchdog.log 2>&1"),
        ("skill-study", "0 9 * * * python3 /root/.openclaw/workspace/.skill-study.py >> /root/.openclaw/workspace/memory/skill-study.log 2>&1"),
        ("proactive-planner", "0 9 * * * python3 /root/.openclaw/workspace/.proactive-planner.py >> /root/.openclaw/workspace/memory/proactive-planner.log 2>&1"),
    ]
    ok, current, _ = cmd("crontab -l 2>/dev/null")
    current_ct = current + "\n" if ok else ""
    reregistered = []
    for name, cron_line in CRON_JOBS:
        if not (ok and name in current):
            if cron_line not in current_ct:
                current_ct += cron_line + "\n"
                reregistered.append(name)
    if reregistered:
        try:
            p = subprocess.run("crontab -", shell=True, input=current_ct, capture_output=True, text=True, timeout=5)
            if p.returncode == 0:
                repaired.append(f"cron_reregistered:{','.join(reregistered)}")
                log(f"  ⚠️ Cron丢失已补: {', '.join(reregistered)}")
        except: pass
    return repaired

# ─── Evolver ────────────────────────────────────────────────────
def repair_evolver():
    repaired = []
    ed = "/root/.openclaw/evolver"
    if not os.path.exists(ed):
        return repaired
    ok, out, _ = cmd(f"cd {ed} && node -e \"const h=require('./src/ops/health_check');const r=h.runHealthCheck();console.log(JSON.stringify(r))\"")
    if ok:
        try:
            r = json.loads(out)
            if r.get('status') == 'error':
                log(f"  ⚠️ Evolver健康检查异常")
                repaired.append("evolver_health_error")
        except: pass
    return repaired

# ─── 磁盘 ───────────────────────────────────────────────────────
def repair_disk():
    """清理临时文件，不报告（例行维护不算"修复"）"""
    for pattern in ["__pycache__", "*.pyc", "*.pyo"]:
        cmd(f"find /root/.openclaw/workspace -name '{pattern}' -type d -exec rm -rf {{}} + 2>/dev/null; true")
    try:
        cmd("find /root/.openclaw/workspace/memory -name '*.log' -mtime +7 -delete 2>/dev/null; true")
        cmd("find /root/.openclaw/workspace/memory -name 'daemon-state.json' -mtime +1 -delete 2>/dev/null; true")
    except: pass
    cmd("find /root/.openclaw/workspace/node_modules -name '.cache' -type d -exec rm -rf {} + 2>/dev/null; true")
    return []

# ─── Exec健康 ──────────────────────────────────────────────────
def repair_exec():
    repaired = []
    ok, out, _ = cmd("echo 'ok'", timeout=5)
    if not ok or "ok" not in out:
        repaired.append("exec_unhealthy")
    return repaired

# ─── 主流程 ─────────────────────────────────────────────────────
def main():
    rotate_log()
    state = get_state()
    repaired = []

    checks = {
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

    for name, func in checks.items():
        try:
            result = func()
            if result:
                log(f"  [{name}] {', '.join(result)}")
                repaired.extend(result)
        except Exception as e:
            log(f"  [{name}] ERROR: {e}")

    state["last_repair"] = datetime.now().isoformat()
    state["last_fixed"] = repaired
    state["repair_count"] = state.get("repair_count", 0) + 1
    save_state(state)

    if repaired:
        msg = f"🔧 贾维斯自我修复\n✅ {len(repaired)}项 - {', '.join(repaired)}"
        log(msg)
        feishu(msg)
    else:
        log("✅ 检查完成，无问题")

    return 0

if __name__ == "__main__":
    sys.exit(main())
