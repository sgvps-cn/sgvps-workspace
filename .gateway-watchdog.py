#!/usr/bin/env python3
"""
贾维斯24/7看门狗 - Jarvis 24/7 Watchdog v2
每分钟运行，用flock确保单实例，检测Gateway卡死/内存泄漏/崩溃
"""
import os, sys, json, subprocess, time, fcntl
from datetime import datetime

LOCK_FILE = "/root/.openclaw/workspace/memory/watchdog.lock"
PID_FILE = "/root/.openclaw/workspace/memory/watchdog.pid"
STATE_FILE = "/root/.openclaw/workspace/memory/watchdog-state.json"
LOG = "/root/.openclaw/workspace/memory/watchdog.log"
MAX_MEM_MB = 800

def log(msg):
    ts = datetime.now().strftime("%m-%d %H:%M")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def cmd(c, timeout=10):
    try:
        r = subprocess.run(c, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode == 0, r.stdout.strip(), r.stderr.strip()
    except: return False, "", ""

def feishu(text):
    try:
        subprocess.run(["python3", "/root/.openclaw/workspace/.feishu-notify.py", text],
                      capture_output=True, timeout=10)
    except: pass

def get_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except: return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def check_gateway():
    """检测Gateway是否卡死/崩溃"""
    # 1. 检查进程是否存在
    ok, out, _ = cmd("pgrep -f 'openclaw-gateway' 2>/dev/null")
    if not ok or not out:
        return "crashed", "Gateway进程不存在"

    pid = out.strip().split()[0]

    # 2. 检查内存（检测内存泄漏）
    ok2, mem_out, _ = cmd(f"ps -o rss= -p {pid} 2>/dev/null")
    if ok2 and mem_out.strip():
        mem_mb = int(mem_out.strip()) / 1024
        state = get_state()
        prev_mem = state.get("prev_gateway_mem_mb", 0)
        if prev_mem > 0 and mem_mb > MAX_MEM_MB and mem_mb > prev_mem * 1.2:
            log(f"Gateway内存持续增长: {prev_mem:.0f}MB → {mem_mb:.0f}MB，疑似泄漏，重启")
            return "memory_leak", f"{prev_mem:.0f}MB→{mem_mb:.0f}MB"
        state["prev_gateway_mem_mb"] = mem_mb
        save_state(state)

    # 3. 检查HTTP响应
    ok3, code, _ = cmd("curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 http://127.0.0.1:18789/ 2>/dev/null")
    if not ok3 or code != "200":
        return "hung", f"HTTP {code}"

    return "ok", ""

def restart_gateway(reason):
    log(f"Gateway重启原因: {reason}")
    try:
        subprocess.run(["openclaw", "gateway", "restart"], capture_output=True, timeout=30)
        time.sleep(5)
        ok, code, _ = cmd("curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 http://127.0.0.1:18789/ 2>/dev/null")
        if ok and code == "200":
            feishu(f"🛡️ Gateway重启成功\n原因: {reason}\n状态: ✅ 恢复正常")
            log("Gateway重启成功")
        else:
            feishu(f"🛡️ Gateway重启失败\n原因: {reason}\n状态: ❌ 请检查")
            log(f"Gateway重启失败: {code}")
    except Exception as e:
        feishu(f"🛡️ Gateway重启异常\n{e}")
        log(f"Gateway重启异常: {e}")

def main():
    # flock确保单实例（即使cron重复触发也不会并发）
    lock_fd = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        # 已有实例在跑，退出
        sys.exit(0)

    os.chdir("/root/.openclaw/workspace")
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

    log("看门狗检查")
    state = get_state()
    state["last_check"] = datetime.now().isoformat()
    save_state(state)

    status, detail = check_gateway()

    if status == "ok":
        state["last_ok"] = datetime.now().isoformat()
        save_state(state)
        return

    log(f"异常: {status} - {detail}")

    # 防止频繁重启（上次重启在5分钟内则跳过）
    last_restart = state.get("last_restart", "")
    if last_restart:
        try:
            from datetime import timedelta
            last_dt = datetime.fromisoformat(last_restart)
            if (datetime.now() - last_dt).seconds < 300:
                log("距上次重启<5分钟，跳过")
                return
        except: pass

    state["last_down_time"] = datetime.now().isoformat()
    state["last_restart"] = datetime.now().isoformat()
    state["restart_count"] = state.get("restart_count", 0) + 1
    save_state(state)
    restart_gateway(f"{status}: {detail}")

if __name__ == "__main__":
    main()
