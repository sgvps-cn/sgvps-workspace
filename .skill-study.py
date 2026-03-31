#!/usr/bin/env python3
"""
贾维斯技能学习系统 - Skill Study Tracker
每天9点自动运行，审计/深化技能，推送给刘总
"""
import os, json, subprocess, re, glob
from datetime import datetime

SKILLS_DIR = "/root/.openclaw/workspace/skills"
STUDY_STATE = "/root/.openclaw/workspace/memory/skill-study-state.json"
LOG = "/root/.openclaw/workspace/memory/skill-study.log"
FEISHU = "/root/.openclaw/workspace/.feishu-notify.py"
STAGE_REPORT = "/root/.openclaw/workspace/.evolution-stage.py"

def log(msg):
    ts = datetime.now().strftime("%m-%d %H:%M")
    print(f"[{ts}] {msg}")
    with open(LOG, "a") as f:
        f.write(f"[{ts}] {msg}\n")

def feishu(text):
    try:
        subprocess.run(["python3", FEISHU, text], capture_output=True, timeout=10)
    except: pass

def get_state():
    try:
        with open(STUDY_STATE) as f:
            return json.load(f)
    except:
        return {}

def save_state(state):
    with open(STUDY_STATE, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

# ─── 技能审计 ────────────────────────────────────────────────────
def audit_skills():
    """全面审计所有技能（统计所有md文件，不只看SKILL.md）"""
    skills = {}
    for name in os.listdir(SKILLS_DIR):
        sk_path = os.path.join(SKILLS_DIR, name, "SKILL.md")
        skill_dir = os.path.join(SKILLS_DIR, name)
        if not os.path.isfile(sk_path):
            skills[name] = {"status": "❌无SKILL.md", "lines": 0, "quality": 0, "total_kb": 0}
            continue
        # 统计所有md文件（支持引用md文件的skill，如php有7个引用md）
        total_lines = 0
        ref_files = 0
        for md in glob.glob(os.path.join(skill_dir, "*.md")):
            with open(md) as f:
                total_lines += len(f.read().splitlines())
            ref_files += 1
        total_kb = sum(os.path.getsize(f) for f in glob.glob(os.path.join(skill_dir, "*.md"))) / 1024
        # 质量评分
        with open(sk_path) as f:
            content = f.read()
        score = 0
        if "description:" in content: score += 1
        if content.count("## ") >= 2: score += 1
        if total_lines > 50: score += 1
        if total_lines > 100: score += 1
        if total_kb > 4: score += 1
        skills[name] = {
            "status": "✅",
            "lines": total_lines,
            "ref_files": ref_files,
            "total_kb": round(total_kb, 1),
            "quality": score
        }
    return skills

# ─── 薄弱技能列表 ────────────────────────────────────────────────
def find_weak_skills():
    weak = []
    for name in os.listdir(SKILLS_DIR):
        sk_path = os.path.join(SKILLS_DIR, name, "SKILL.md")
        if not os.path.isfile(sk_path):
            weak.append((name, "无SKILL.md", 0))
            continue
        skill_dir = os.path.join(SKILLS_DIR, name)
        total_lines = sum(len(open(md).read().splitlines()) for md in glob.glob(os.path.join(skill_dir, "*.md")))
        if total_lines < 50:
            weak.append((name, f"仅{total_lines}行，内容过薄", total_lines))
    weak.sort(key=lambda x: x[2])
    return weak

# ─── 技能分类 ────────────────────────────────────────────────────
def categorize_skills():
    return {
        "🔧 核心执行": ["playwright", "database-operations", "sql-toolkit", "code-analyzer", "php", "seo"],
        "🛡️ 主动守护": ["self-health-monitor", "auto-monitor", "monitoring", "memory-self-heal", "recursive-self-improvement", "self-improving-agent", "self-improving"],
        "🧬 进化学习": ["evolver", "feishu-evolver-wrapper", "inner-life-core", "inner-life-evolve"],
        "🌐 内容生成": ["content-writer", "zh-humanizer", "chatbot-engine"],
        "🔍 搜索研究": ["find-skills-skill", "openclaw-find-skills"],
        "💻 系统运维": ["vps-maintenance", "host-hardening", "docker-essentials", "docker-manager", "website-monitor", "system-resource-monitor"],
        "📊 性能分析": ["perf-profiler", "security-audit-toolkit", "decision-frameworks"],
    }

# ─── 改进薄弱技能（自动化）────────────────────────────────────────
IMPROVEMENT_TEMPLATES = {
    "code-review-fix": """---
name: code_review_fix
description: 智能代码审查与修复 - 分析代码发现问题、解释问题原因、给出修复建议。不替代人工code review，是辅助工具。
---

# Code Review & Fix

**注意：** 这是代码审查辅助工具，不是完整的自动化修复系统。

## 能力范围

### 能做的
- ✅ 静态分析：未使用变量、死代码、基本逻辑错误
- ✅ 安全扫描：SQL注入风险、XSS风险、敏感信息暴露
- ✅ 性能提示：大循环、低效查询、不必要的重复计算
- ✅ 代码风格：命名不规范、缺少注释
- ✅ PHP/JS/Python/Go 基础支持

### 不能做的
- ❌ 自动修改代码（需要人工确认）
- ❌ 复杂业务逻辑审查
- ❌ 完整的CI/CD集成

## 使用方式

```
用户：帮我审查 /root/.openclaw/workspace/.self-repair.py
→ 读取文件内容
→ 分析问题（类型/安全性/性能）
→ 输出：问题列表 + 严重程度 + 建议修复方式
```

## 输出格式

```
## 代码审查报告: filename

### 🔴 严重问题
1. [行X] 安全问题：...

### 🟡 警告
2. [行Y] 性能问题：...

### 🟢 建议
3. [行Z] 代码风格：...

修复优先级：高/中/低
"""
}

# ─── 汇报 ───────────────────────────────────────────────────────
def main():
    log("=== 技能学习报告 ===")

    skills = audit_skills()
    weak = find_weak_skills()
    categories = categorize_skills()

    total = len(skills)
    strong = sum(1 for s in skills.values() if s["quality"] >= 3)
    weak_count = len(weak)

    state = get_state()
    # 连续学习天数追踪
    today = datetime.now().strftime('%Y-%m-%d')
    last_study = state.get("last_study_date", "")
    streak = state.get("study_streak", 0)
    if last_study == today:
        pass  # 今日已学习
    elif last_study == "":
        streak = 1
    else:
        from datetime import timedelta
        try:
            last_dt = datetime.strptime(last_study, '%Y-%m-%d')
            today_dt = datetime.strptime(today, '%Y-%m-%d')
            gap = (today_dt - last_dt).days
            streak = streak + 1 if gap == 1 else 1
        except:
            streak = 1
    state["last_study_date"] = today
    state["study_streak"] = streak
    state["last_audit"] = datetime.now().isoformat()
    state["total_skills"] = total
    state["strong_skills"] = strong
    save_state(state)

    # 飞书汇报
    lines = [
        f"## 🛠️ 贾维斯技能学习报告",
        f"",
        f"**审计时间:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**连续学习:** 🔥 {streak} 天",
        f"**技能总览:** {total}个 | 优质:{strong}⭐ | 薄弱:{weak_count}",
        f"",
    ]

    if weak:
        lines.append("**⚠️ 薄弱技能（<50行）:**")
        for name, reason, lines_cnt in weak[:5]:
            lines.append(f"- `{name}`: {reason}")
        lines.append("")

    for cat, members in categories.items():
        present = [m for m in members if m in skills]
        if present:
            scores = [f"{m}({skills[m]['quality']}⭐)" for m in present]
            lines.append(f"{cat}: {', '.join(scores)}")

    msg = "\n".join(lines)
    log(msg)
    feishu(msg)

    # 自动改进薄弱技能
    improved_this_run = []
    for name, reason, lines_cnt in weak:
        if name in IMPROVEMENT_TEMPLATES:
            sk_path = os.path.join(SKILLS_DIR, name, "SKILL.md")
            with open(sk_path, "w") as f:
                f.write(IMPROVEMENT_TEMPLATES[name])
            improved_this_run.append(name)
            log(f"✅ 已改进: {name}")

    if improved_this_run:
        state.setdefault("improved", []).extend(improved_this_run)
        save_state(state)
        subprocess.run(["python3", STAGE_REPORT, "skill-improvement",
                        f"技能深化: {', '.join(improved_this_run)} 已完成内容增强"],
                       capture_output=True, timeout=15)

    return 0

if __name__ == "__main__":
    main()
