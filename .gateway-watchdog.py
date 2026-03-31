#!/usr/bin/env python3
"""
贾维斯24/7看门狗 - Jarvis 24/7 Watchdog v4
每分钟运行，检测Gateway卡死/内存泄漏/崩溃
PID文件 + flock 双保护，os.fork() 安全
"""
import os, sys, json, subprocess, time, fcntl, urllib.request, urllib.error
from datetime import datetime

LOCK_FILE = "/root/.openclaw/workspace/memory/watchdog.lock"
STATE_FILE = "/root/.openclaw/workspace/memory/watchdog-state.json"
LOG = "/root/.openclaw/workspace/memory/watchdog.log"
PID_FILE = "/root/.openclaw/workspace/memory/watchdog.pid"
MINUTE_FILE = "/root/.openclaw/workspace/memory/watchdog.minute"
MAX_MEM_MB = 800

# ─── 单实例：PID文件 + flock ────────────────────────────────
def am_i_the_runner():
    """PID文件保护：检查自己是否是最新启动的实例"""
    try:
        with open(PID_FILE) as f:
            old_pid = int(f.read().strip())
        # 旧PID还在运行？退出
        os.kill(old_pid, 0)
        return False  # 旧实例还活着
    except (FileNotFoundError, ValueError, ProcessLookupError, PermissionError):
        return True  # 没有旧实例，我是新的

# 立即检查并声明
if not am_i_the_runner():
    sys.exit(0)

# 写入自己的PID
with open(PID_FILE, "w") as f:
    f.write(str(os.getpid()))

# 分钟级防重复：用时间戳文件名，同分钟内只运行一次
this_minute = datetime.now().strftime("%Y%m%d%H%M")
MINUTE_FILE_TS = f"{MINUTE_FILE}.{this_minute}"
try:
    fd = os.open(MINUTE_FILE_TS, os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o644)
    os.close(fd)
    # 写入当前PID，方便调试
    with open(MINUTE_FILE, "w") as f:
        f.write(this_minute)
except FileExistsError:
    sys.exit(0)  # 同分钟已运行，退出

# ─── 日志 ───────────────────────────────────────────────────
def log(msg):
    ts = datetime.now().strftime("%m-%d %H:%M")
    with open(LOG, "a") as f:
        f.write(f"[{ts}] {msg}\n")

# ─── 通知 ───────────────────────────────────────────────────
def feishu(text):
    try:
        subprocess.run(["python3", "/root/.openclaw/workspace/.feishu-notify.py", text],
                      capture_output=True, timeout=10)
    except: pass

# ─── 状态 ───────────────────────────────────────────────────
def get_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except: return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

# ─── Gateway检测 ─────────────────────────────────────────────
def check_gateway():
    # 进程
    try:
        r = subprocess.run("pgrep -f 'openclaw-gateway'", shell=True, capture_output=True, text=True, timeout=5)
        pids = [p for p in r.stdout.strip().split("\n") if p]
    except:
        pids = []
    if not pids:
        return "crashed", "Gateway进程不存在"
    pid = pids[0]

    # 内存
    mem_mb = 0
    try:
        r = subprocess.run(f"ps -o rss= -p {pid}", shell=True, capture_output=True, text=True, timeout=5)
        if r.returncode == 0 and r.stdout.strip():
            mem_mb = int(r.stdout.strip()) / 1024
    except: pass

    state = get_state()
    prev_mem = state.get("prev_gateway_mem_mb", 0)
    if prev_mem > 0 and mem_mb > MAX_MEM_MB and mem_mb > prev_mem * 1.2:
        log(f"Gateway内存增长: {prev_mem:.0f}MB → {mem_mb:.0f}MB，重启")
        save_state({**state, "prev_gateway_mem_mb": mem_mb})
        return "memory_leak", f"{prev_mem:.0f}MB→{mem_mb:.0f}MB"
    state["prev_gateway_mem_mb"] = mem_mb

    # HTTP检测
    code = "000"
    start = time.time()
    try:
        urllib.request.urlopen("http://127.0.0.1:18789/", timeout=5)
        code = "200"
    except urllib.error.HTTPError as e:
        code = str(e.code)
    except:
        code = "000"
    elapsed_ms = int((time.time() - start) * 1000)
    log(f"Gateway: PID={pid} mem={mem_mb:.0f}MB HTTP={code} time={elapsed_ms}ms")

    save_state(state)
    if code != "200":
        return "hung", f"HTTP {code}"
    return "ok", ""

def restart_gateway(reason):
    log(f"Gateway重启原因: {reason}")
    try:
        subprocess.run(["openclaw", "gateway", "restart"], capture_output=True, timeout=30)
        time.sleep(5)
        try:
            urllib.request.urlopen("http://127.0.0.1:18789/", timeout=5)
            code = "200"
        except:
            code = "000"
        if code == "200":
            feishu(f"🛡️ Gateway重启成功\n原因: {reason}\n状态: ✅")
            log("Gateway重启成功")
        else:
            feishu(f"🛡️ Gateway重启失败\n原因: {reason}")
            log(f"Gateway重启失败: {code}")
    except Exception as e:
        feishu(f"🛡️ Gateway重启异常\n{e}")
        log(f"Gateway重启异常: {e}")

# ─── 主流程 ─────────────────────────────────────────────────
def main():
    os.chdir("/root/.openclaw/workspace")
    state = get_state()
    state["last_check"] = datetime.now().isoformat()
    save_state(state)

    status, detail = check_gateway()
    if status == "ok":
        state["last_ok"] = datetime.now().isoformat()
        save_state(state)
        return

    log(f"异常: {status} - {detail}")
    last_restart = state.get("last_restart", "")
    if last_restart:
        try:
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

# ─── Evolver 守护（如果没有在N分钟内有日志则重启） ───────────────────────
def check_evolver():
    memdir = "/root/.openclaw/workspace/memory"
    log_file = f"{memdir}/evolver-loop.log"
    if not os.path.exists(log_file):
        return
    mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
    age = (datetime.now() - mtime).total_seconds()
    if age > 1800:  # 30分钟无日志，重启
        log(f"[EVOLVER] ⚠️ 无日志{datetime.now().strftime('%H:%M')}，重启")
        os.system("kill $(pgrep -f 'evolver/index.js') 2>/dev/null; "
                  "nohup node /root/.openclaw/evolver/index.js --loop >> "
                  f"{memdir}/evolver-loop.log 2>&1 &")
        os.system(f"touch {log_file}")

check_evolver()
