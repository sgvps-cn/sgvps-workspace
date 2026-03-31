#!/usr/bin/env python3
"""
贾维斯递归自我优化引擎
基于 Capability Evolver Pro 日志分析逻辑
REPAIRING + OPTIMIZING 双模式框架
"""
import os, json, subprocess
from datetime import datetime

MEMDIR = "/root/.openclaw/workspace/memory"
STATE_FILE = f"{MEMDIR}/optimize-state.json"
LOG_FILE = f"{MEMDIR}/optimize-cycle.log"

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

# ─── Capability Evolver Pro 日志分析 ───────────────────────────────────────────
def run_log_analyzer() -> dict:
    """运行本地日志分析器（Capability Evolver Pro 逻辑）"""
    script = "/root/.openclaw/workspace/.log-analyzer.py"
    try:
        r = subprocess.run(["python3", script], capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            return json.loads(r.stdout)
    except:
        pass
    return {}

# ─── 修复模式 ────────────────────────────────────────────────────────────────
def repair_mode():
    log("🔧 [REPAIRING] 进入修复模式")
    fixes = []

    # 1. Gateway HTTP 检查
    try:
        r = subprocess.run(["/usr/bin/curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://127.0.0.1:18789/"],
                          capture_output=True, text=True, timeout=5)
        if r.stdout.strip() != "200":
            fixes.append("Gateway_HTTP异常")
    except:
        fixes.append("Gateway_检查失败")

    # 2. Clash 进程检查
    try:
        r = subprocess.run(["pgrep", "-a", "clash"], capture_output=True, text=True)
        if "clash" not in r.stdout:
            fixes.append("Clash_进程丢失")
    except:
        pass

    # 3. 日志老化检查
    for name, fname in [
        ("watchdog", "watchdog.log"),
        ("self-repair", "self-repair.log"),
        ("evolver", "evolver-loop.log"),
    ]:
        fpath = f"{MEMDIR}/{fname}"
        if os.path.exists(fpath):
            mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
            age = datetime.now() - mtime
            if age.total_seconds() > 7200:  # 2小时
                fixes.append(f"{name}_日志老化({int(age.total_seconds()/60)}分钟无更新)")

    # 4. 日志分析器检查（基于 Capability Evolver Pro）
    result = run_log_analyzer()
    score = result.get("health_score", 100)
    patterns = result.get("patterns", [])
    if score < 60:
        fixes.append(f"健康评分低({score}/100)")
    for p in patterns:
        if p.get("severity") in ("critical", "high"):
            fixes.append(f"模式_{p['description']}")

    if fixes:
        log(f"⚠️ 发现问题: {', '.join(fixes)}")
    else:
        log("✅ [STABLE] 无问题")

    return "STABLE", fixes

# ─── 优化模式 ────────────────────────────────────────────────────────────────
def optimize_mode():
    log("🚀 [OPTIMIZING] 进入优化模式")
    improvements = []

    # 1. 日志分析（基于 Capability Evolver Pro recommendations）
    result = run_log_analyzer()
    for rec in result.get("recommendations", []):
        if rec.get("priority") in ("immediate", "high"):
            improvements.append(f"建议: {rec['description']}")

    # 2. 日志大小管理
    for fname in os.listdir(MEMDIR):
        if not fname.endswith(".log"):
            continue
        fpath = f"{MEMDIR}/{fname}"
        lines = sum(1 for _ in open(fpath, "r", errors="ignore"))
        if lines > 500:
            excess = lines - 500
            with open(fpath, "r") as f:
                content = f.readlines()[-500:]
            with open(fpath, "w") as f:
                f.writelines(content)
            improvements.append(f"{fname}_截断{excess}行")

    # 3. learnings 待处理项
    lrn_file = "/root/.openclaw/workspace/.learnings/LEARNINGS.md"
    if os.path.exists(lrn_file):
        pending = sum(1 for l in open(lrn_file) if "pending" in l.lower())
        if pending > 5:
            improvements.append(f"learndings待处理{pending}项")

    # 4. 薄 skill 检查
    skill_dir = "/root/.openclaw/workspace/skills"
    thin = []
    if os.path.exists(skill_dir):
        for s in os.listdir(skill_dir):
            sk = f"{skill_dir}/{s}/SKILL.md"
            if os.path.exists(sk):
                lines = sum(1 for _ in open(sk, errors="ignore"))
                if 0 < lines < 30:
                    thin.append(s)
    if thin:
        improvements.append(f"薄skill: {', '.join(thin[:3])}")

    if improvements:
        log(f"📈 优化项: {', '.join(improvements)}")
    else:
        log("✨ 无需优化")

    return "OPTIMIZED", improvements

# ─── 主循环 ────────────────────────────────────────────────────────────────
def main():
    state = load_state()
    mode = state.get("mode", "INITIAL")
    stable_rounds = state.get("stable_rounds", 0)

    log(f"=== 优化循环 | mode={mode} stable_rounds={stable_rounds} ===")

    if mode == "REPAIRING":
        _, items = repair_mode()
        state["mode"] = "STABLE" if not items else "REPAIRING"
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
        _, items = optimize_mode()
        state["mode"] = "STABLE"
        save_state(state)

    else:
        state["mode"] = "REPAIRING"
        save_state(state)

    state = load_state()
    log(f"=== 完成 | mode={state['mode']} ===")

if __name__ == "__main__":
    main()
