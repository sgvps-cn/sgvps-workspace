#!/usr/bin/env python3
"""
贾维斯递归自我优化引擎
基于 recursive-self-improvement skill 的 REPAIRING + OPTIMIZING 双模式框架
"""
import os, json, time, subprocess
from datetime import datetime, timedelta

MEMDIR = "/root/.openclaw/workspace/memory"
STATE_FILE = f"{MEMDIR}/optimize-state.json"
LOG_FILE = f"{MEMDIR}/optimize-cycle.log"

# 状态定义
STATES = ["INITIAL", "REPAIRING", "OPTIMIZING", "STABLE", "ERROR", "OPTIMIZED"]

def log(msg):
    ts = datetime.now().strftime("%m-%d %H:%M")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"mode": "INITIAL", "stable_rounds": 0, "round": 0, "last_run": None}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

# ============ 修复模式 ============
def repair_mode():
    log("🔧 [REPAIRING] 进入修复模式")
    fixes = []
    
    # 1. 检查 Gateway 是否正常
    try:
        r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://127.0.0.1:18789/"],
                          capture_output=True, text=True, timeout=5)
        if r.stdout.strip() != "200":
            fixes.append("Gateway_HTTP异常")
    except:
        fixes.append("Gateway_检查失败")
    
    # 2. 检查 Clash 是否在跑
    try:
        r = subprocess.run(["pgrep", "-a", "clash"], capture_output=True, text=True)
        if "clash" not in r.stdout:
            fixes.append("Clash_进程丢失")
    except:
        pass
    
    # 3. 检查 cron 任务是否漏掉
    log_files = {
        "watchdog": f"{MEMDIR}/watchdog.log",
        "self-repair": f"{MEMDIR}/self-repair.log",
        "evolver": f"{MEMDIR}/evolver-loop.log",
    }
    for name, path in log_files.items():
        if os.path.exists(path):
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            age = datetime.now() - mtime
            if age > timedelta(hours=2):
                fixes.append(f"{name}_日志老化({age.seconds//60}分钟无更新)")
    
    if fixes:
        log(f"⚠️ 发现问题: {', '.join(fixes)}")
        return "REPAIRING", fixes
    else:
        log("✅ [STABLE] 无问题")
        return "STABLE", []

# ============ 优化模式 ============
def optimize_mode():
    log("🚀 [OPTIMIZING] 进入优化模式")
    improvements = []
    
    # 1. 检查日志大小，尝试截断
    for fname in os.listdir(MEMDIR):
        if fname.endswith(".log"):
            fpath = f"{MEMDIR}/{fname}"
            lines = sum(1 for _ in open(fpath, "r", errors="ignore"))
            if lines > 500:
                with open(fpath, "r") as f:
                    content = f.readlines()[-500:]
                with open(fpath, "w") as f:
                    f.writelines(content)
                improvements.append(f"{fname}_截断{lines-500}行")
    
    # 2. 检查 learndings 是否有 pending
    lrn_file = "/root/.openclaw/workspace/.learnings/LEARNINGS.md"
    if os.path.exists(lrn_file):
        pending = sum(1 for l in open(lrn_file) if "pending" in l.lower())
        if pending > 5:
            improvements.append(f"learndings待处理项{pending}个")
    
    # 3. 检查 skill 文件是否有改进空间
    skill_dir = "/root/.openclaw/workspace/skills"
    thin_skills = []
    if os.path.exists(skill_dir):
        for s in os.listdir(skill_dir):
            sk = f"{skill_dir}/{s}/SKILL.md"
            if os.path.exists(sk):
                lines = sum(1 for _ in open(sk, errors="ignore"))
                if lines < 30:
                    thin_skills.append(s)
    if thin_skills:
        improvements.append(f"薄skill: {', '.join(thin_skills[:3])}")
    
    if improvements:
        log(f"📈 优化项: {', '.join(improvements)}")
    else:
        log("✨ 无需优化")
    
    return "OPTIMIZED", improvements

# ============ 主循环 ============
def main():
    state = load_state()
    mode = state.get("mode", "INITIAL")
    stable_rounds = state.get("stable_rounds", 0)
    
    log(f"=== 优化循环启动 | mode={mode} stable_rounds={stable_rounds} ===")
    
    if mode == "REPAIRING":
        new_mode, items = repair_mode()
        if not items:
            state["mode"] = "STABLE"
            state["stable_rounds"] = 1
        else:
            state["mode"] = "REPAIRING"
        save_state(state)
        
    elif mode == "STABLE":
        _, items = repair_mode()
        if not items:
            stable_rounds += 1
            state["stable_rounds"] = stable_rounds
            if stable_rounds >= 3:
                state["mode"] = "OPTIMIZING"
                state["stable_rounds"] = 0
                log("3轮稳定 → 进入OPTIMIZING")
        else:
            state["mode"] = "REPAIRING"
            state["stable_rounds"] = 0
        save_state(state)
        
    elif mode == "OPTIMIZING":
        new_mode, items = optimize_mode()
        state["mode"] = "STABLE"
        state["stable_rounds"] = 0
        save_state(state)
        
    else:
        # INITIAL or OPTIMIZED → 从REPAIRING开始
        state["mode"] = "REPAIRING"
        save_state(state)
    
    state = load_state()
    log(f"=== 完成 | mode={state['mode']} ===")

if __name__ == "__main__":
    main()
