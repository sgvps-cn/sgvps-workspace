#!/usr/bin/env python3
"""
贾维斯进化汇报 - 每小时运行一次
收集进化数据，推送给刘总
"""
import os, sys, json, subprocess, time
from datetime import datetime

STATE_FILE = "/root/.openclaw/workspace/memory/evolution-state.json"
LEARNINGS_FILE = "/root/.openclaw/workspace/.learnings/LEARNINGS.md"
SELF_REPAIR_STATE = "/root/.openclaw/workspace/memory/self-repair-state.json"
REPAIR_LOG = "/root/.openclaw/workspace/memory/self-repair.log"
EVOLVER_LOG = "/root/.openclaw/workspace/.evolver.log"
LOG = "/root/.openclaw/workspace/memory/evolution-report.log"

def log(msg):
    ts = datetime.now().strftime("%m-%d %H:%M")
    print(f"[{ts}] {msg}")

def feishu(text):
    try:
        subprocess.run(["python3", "/root/.openclaw/workspace/.feishu-notify.py", text],
                      capture_output=True, timeout=15)
    except: pass

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
    try:
        r = subprocess.run(c, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode == 0, r.stdout.strip(), r.stderr.strip()
    except: return False, "", ""

# ─── 收集各项数据 ────────────────────────────────────────────────
def collect():
    now = datetime.now()
    hour_str = now.strftime("%Y-%m-%d %H:00")
    state = get_state()
    prev_hour = state.get("last_report_hour", "")

    sections = []

    # 1. Self-Repair 本小时修复
    if os.path.exists(REPAIR_LOG):
        with open(REPAIR_LOG) as f:
            lines = f.readlines()
        repairs_this_hour = [l.strip() for l in lines if hour_str in l and "修复完成" in l]
        if repairs_this_hour:
            sections.append(f"🔧 Self-Repair本小时: {len(repairs_this_hour)}项")

    # 2. Learnings 新增
    if os.path.exists(LEARNINGS_FILE):
        mtime = os.path.getmtime(LEARNINGS_FILE)
        # 简化：统计文件行数变化
        with open(LEARNINGS_FILE) as f:
            new_lines = len(f.readlines())
        prev_lines = state.get("learnings_lines", 0)
        new_learnings = new_lines - prev_lines
        if new_learnings > 0:
            sections.append(f"📝 新增Learnings: {new_learnings}条")
        state["learnings_lines"] = new_lines

    # 3. Skills 变化
    skills_dir = "/root/.openclaw/workspace/skills"
    if os.path.exists(skills_dir):
        skill_count = len(os.listdir(skills_dir))
        prev_skills = state.get("skill_count", 0)
        if skill_count != prev_skills:
            sections.append(f"🛠️ Skills: {skill_count}个")
            state["skill_count"] = skill_count

    # 4. 系统状态
    _, mem_out, _ = cmd("free -m | grep Mem")
    if mem_out:
        parts = mem_out.split()
        mem_pct = int(int(parts[2]) / int(parts[1]) * 100)
        sections.append(f"💻 内存: {mem_pct}%")
    _, disk_out, _ = cmd("df /root | tail -1 | awk '{print $5}'")
    if disk_out:
        sections.append(f"💾 磁盘: {disk_out}")

    # 5. Self-Repair统计
    if os.path.exists(SELF_REPAIR_STATE):
        with open(SELF_REPAIR_STATE) as f:
            sr = json.load(f)
        total_repairs = sr.get("repair_count", 0)
        last_fixed = sr.get("last_fixed", [])
        prev_count = state.get("repair_count", 0)
        if total_repairs > prev_count:
            sections.append(f"🔄 总修复次数: {total_repairs}")
            state["repair_count"] = total_repairs

    # 6. Gateway状态
    _, code, _ = cmd("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:18789/ 2>/dev/null", timeout=5)
    gateway = "✅" if code == "200" else f"❌({code})"
    sections.append(f"🌐 Gateway: {gateway}")

    # 7. Clash状态
    _, clash_out, _ = cmd("pgrep -a clash 2>/dev/null")
    clash_ok = "✅" if (clash_out and "./clash" in clash_out) else "❌"
    sections.append(f"🔁 Clash: {clash_ok}")

    # 8. Evolver状态
    _, evo_out, _ = cmd("ps aux | grep 'evolver/index.js' | grep -v grep")
    evo_ok = "✅运行中" if evo_out else "❌未运行"
    sections.append(f"🧬 Evolver: {evo_ok}")

    state["last_report_hour"] = hour_str
    save_state(state)

    return hour_str, sections

# ─── 发送汇报 ───────────────────────────────────────────────────
def main():
    hour_str, sections = collect()

    if not sections:
        return

    lines = [f"**贾维斯进化汇报 · {hour_str}**", ""]
    for s in sections:
        lines.append(s)
    lines += ["", "持续进化中 🦞"]
    msg = "\n".join(lines)
    log(msg)
    feishu(msg)

if __name__ == "__main__":
    main()
