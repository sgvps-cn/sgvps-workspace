#!/usr/bin/env python3
"""
贾维斯日志分析器 - 基于 Capability Evolver Pro 逻辑（纯 Python 实现）
分析日志文件 → 检测错误模式 → 计算健康评分 → 生成改进建议
无需外部 API，纯确定性算法
"""
import re, os, json
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional

MEMDIR = "/root/.openclaw/workspace/memory"

# ─── 日志解析 ────────────────────────────────────────────────

def parse_watchdog_log(path: str) -> list:
    """解析 watchdog 日志"""
    entries = []
    if not os.path.exists(path):
        return entries
    for line in open(path):
        # 跳过空行和分隔线
        line = line.strip()
        if not line or line.startswith("===") or line.startswith("---"):
            continue
        m = re.match(r"\[(\d\d-\d\d) (\d\d:\d\d)\] (.*)", line)
        if not m:
            continue
        date, time, msg = m.groups()
        level = "error" if "ERROR" in msg or "FAIL" in msg else \
                "warn" if "WARN" in msg or "⚠" in msg else "info"
        entries.append({
            "timestamp": f"2026-{date} {time}:00",
            "level": level,
            "message": msg.strip(),
            "context": "watchdog"
        })
    return entries

def parse_self_repair_log(path: str) -> list:
    """解析 self-repair 日志"""
    entries = []
    if not os.path.exists(path):
        return entries
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("==="):
            continue
        m = re.match(r"\[(\d\d-\d\d) (\d\d:\d\d)\] (.*)", line)
        if not m:
            continue
        date, time, msg = m.groups()
        level = "error" if "❌" in msg or "FAIL" in msg else \
                "warn" if "⚠" in msg else "info"
        entries.append({
            "timestamp": f"2026-{date} {time}:00",
            "level": level,
            "message": msg.strip(),
            "context": "self-repair"
        })
    return entries

def parse_proactive_log(path: str) -> list:
    """解析 proactive-monitor/proactive-alerts 日志"""
    entries = []
    if not os.path.exists(path):
        return entries
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("==="):
            continue
        m = re.match(r"\[(\d\d-\d\d) (\d\d:\d\d)\] (.*)", line)
        if not m:
            continue
        date, time, msg = m.groups()
        # 自动恢复的停机/崩溃 = info（不算错误）
        if ("停机" in msg or "崩溃" in msg) and ("重启" in msg or "恢复" in msg):
            level = "info"
        elif "FAIL" in msg or "❌" in msg:
            level = "error"
        elif "⚠" in msg:
            level = "warn"
        else:
            level = "info"
        entries.append({
            "timestamp": f"2026-{date} {time}:00",
            "level": level,
            "message": msg.strip(),
            "context": "proactive"
        })
    return entries

def parse_daemon_log(path: str) -> list:
    """解析 daemon 日志"""
    entries = []
    if not os.path.exists(path):
        return entries
    for line in open(path):
        m = re.match(r"\[(\d\d-\d\d) (\d\d:\d\d)\] (.*)", line)
        if not m:
            continue
        date, time, msg = m.groups()
        level = "error" if "ERROR" in msg or "❌" in msg else \
                "warn" if "WARN" in msg or "⚠" in msg else "info"
        entries.append({
            "timestamp": f"2026-{date} {time}:00",
            "level": level,
            "message": msg.strip(),
            "context": "daemon"
        })
    return entries

# ─── 模式检测 ────────────────────────────────────────────────

ERROR_PATTERNS = [
    ("curl_路径问题", re.compile(r"curl|shadowsocks|clash")),
    ("Gateway_异常", re.compile(r"Gateway|PID=\d+|HTTP_\d+")),
    ("进程_丢失", re.compile(r"进程.*丢失|PID.*不存在|not found")),
    ("php_fpm_停机", re.compile(r"php-fpm.*停机|php.*停机|fpm.*crash")),
    ("网络_超时", re.compile(r"timeout|ETIMEDOUT|TIMEOUT")),
    ("Clash_故障", re.compile(r"clash.*fail|proxy.*error|节点.*失败")),
    ("git_冲突", re.compile(r"CONFLICT|merge.*fail|git.*error")),
    ("token_失败", re.compile(r"FAIL.*token|token.*fail|auth.*fail")),
]

def detect_patterns(entries: list) -> list:
    """检测错误模式"""
    patterns = defaultdict(lambda: {"count": 0, "msgs": [], "contexts": set(), "first": None, "last": None})
    
    for e in entries:
        if e["level"] not in ("error", "warn"):
            continue
        msg = e["message"]
        # 过滤正常项
        if "HTTP=200" in msg or "Gateway: PID" in msg:
            continue  # 健康检查OK
        if "✅ 检查完成" in msg or "完成" in msg:
            continue  # 正常完成
        # 自动恢复的停机 = 不算错误（系统正常响应）
        if ("停机" in msg or "崩溃" in msg) and ("重启" in msg or "恢复" in msg):
            continue  # 已自动恢复，不算错误
        for name, pat in ERROR_PATTERNS:
            if pat.search(msg):
                key = name
                patterns[key]["count"] += 1
                patterns[key]["msgs"].append(msg[:80])
                patterns[key]["contexts"].add(e["context"])
                patterns[key]["first"] = patterns[key]["first"] or e["timestamp"]
                patterns[key]["last"] = e["timestamp"]
    
    result = []
    for name, data in patterns.items():
        # 频繁停机但自动恢复 = medium（不是critical）
        if name == "php_fpm_停机":
            severity = "high" if data["count"] >= 50 else "medium"
        else:
            severity = "critical" if data["count"] >= 10 else "high" if data["count"] >= 5 else "medium" if data["count"] >= 2 else "low"
        result.append({
            "type": "error",
            "severity": severity,
            "description": f"{name} 出现 {data['count']} 次",
            "occurrences": data["count"],
            "first_seen": data["first"] or "",
            "last_seen": data["last"] or "",
            "affected_files": list(data["contexts"]),
            "sample_messages": data["msgs"][:3]
        })
    
    # 按严重程度排序
    sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    return sorted(result, key=lambda x: sev_order.get(x["severity"], 3))

# ─── 健康评分 ────────────────────────────────────────────────

def compute_health_score(entries: list, patterns: list) -> int:
    """计算健康评分 0-100"""
    if not entries:
        return 100
    
    total = len(entries)
    errors = sum(1 for e in entries if e["level"] == "error")
    warnings = sum(1 for e in entries if e["level"] == "warn")
    
    error_rate = errors / total
    warn_rate = warnings / total
    
    # 基础分（错误率和警告率）
    score = 100 - (error_rate * 100 * 2) - (warn_rate * 100 * 0.5)
    
    # 模式扣分（根据出现次数和严重程度）
    critical_penalty = sum(1 for p in patterns if p["severity"] == "critical") * 10
    high_penalty = sum(1 for p in patterns if p["severity"] == "high") * 5
    medium_penalty = sum(1 for p in patterns if p["severity"] == "medium") * 2
    
    score -= critical_penalty + high_penalty + medium_penalty
    
    # 有自动恢复的停机：少量扣分（不算严重）
    recovered = sum(1 for e in entries if ("停机" in e["message"] or "崩溃" in e["message"]) and "重启" in e["message"])
    score -= min(recovered * 0.5, 10)  # 最多扣10分（自动恢复不算大罪）
    
    return max(0, min(100, int(score)))

# ─── 建议生成 ────────────────────────────────────────────────

def generate_recommendations(patterns: list, health_score: int) -> list:
    """生成改进建议"""
    recs = []
    
    # 基于模式
    for p in patterns:
        sev = p["severity"]
        desc = p["description"]
        
        if "curl" in desc or "路径" in desc:
            recs.append({"priority": "high" if sev in ("critical","high") else "medium",
                         "category": "error-handling",
                         "description": "cron 环境 PATH 受限，使用绝对路径替代命令名",
                         "affected_files": p["affected_files"],
                         "suggested_approach": "将 curl → /usr/bin/curl，python3 → /usr/bin/python3"})
        
        if "Gateway" in desc:
            recs.append({"priority": "high" if sev == "critical" else "medium",
                         "category": "stability",
                         "description": "Gateway 无响应，可能是进程卡死",
                         "affected_files": p["affected_files"],
                         "suggested_approach": "检查内存使用率，必要时重启"})
        
        if "php_fpm" in desc or "停机" in desc:
            recs.append({"priority": "high",
                         "category": "stability",
                         "description": "php-fpm 频繁停机",
                         "affected_files": p["affected_files"],
                         "suggested_approach": "检查 php-fpm 配置，增加重试逻辑"})
        
        if "进程" in desc:
            recs.append({"priority": "high",
                         "category": "stability",
                         "description": "关键进程丢失未被检测到",
                         "affected_files": p["affected_files"],
                         "suggested_approach": "扩展看门狗检测范围"})
        
        if "token" in desc:
            recs.append({"priority": "high",
                         "category": "error-handling",
                         "description": "API token 获取失败",
                         "affected_files": p["affected_files"],
                         "suggested_approach": "使用绝对路径 curl + 添加重试机制"})
    
    # 通用建议
    if health_score < 60:
        recs.append({"priority": "high",
                     "category": "monitoring",
                     "description": "健康评分低于60，建议全面检查",
                     "affected_files": [],
                     "suggested_approach": "运行 .self-repair.py 全面检查"})
    
    # 去重
    seen = set()
    unique = []
    for r in recs:
        key = r["description"][:30]
        if key not in seen:
            seen.add(key)
            unique.append(r)
    
    return unique

# ─── 主分析 ──────────────────────────────────────────────────

def analyze_logs() -> dict:
    """分析所有日志文件"""
    all_entries = []
    
    # 收集日志
    sources = {
        "watchdog": f"{MEMDIR}/watchdog.log",
        "self-repair": f"{MEMDIR}/self-repair.log",
        "proactive": f"{MEMDIR}/proactive-monitor.log",
        "daemon": f"{MEMDIR}/daemon.log",
        "proactive-alerts": f"{MEMDIR}/proactive-alerts.log",
    }
    
    for name, path in sources.items():
        if name == "watchdog":
            entries = parse_watchdog_log(path)
        elif name == "self-repair":
            entries = parse_self_repair_log(path)
        elif name == "proactive" or name == "proactive-alerts":
            entries = parse_proactive_log(path)
        elif name == "daemon":
            entries = parse_daemon_log(path)
        else:
            entries = []
        for e in entries:
            e["context"] = name
        all_entries.extend(entries)
    
    # 只分析最近 500 条
    all_entries = all_entries[-500:]
    
    # 检测模式
    patterns = detect_patterns(all_entries)
    
    # 健康评分
    health_score = compute_health_score(all_entries, patterns)
    
    # 建议
    recommendations = generate_recommendations(patterns, health_score)
    
    # 统计
    error_count = sum(1 for e in all_entries if e["level"] == "error")
    warn_count = sum(1 for e in all_entries if e["level"] == "warn")
    
    return {
        "patterns": patterns,
        "health_score": health_score,
        "recommendations": recommendations,
        "summary": {
            "total_logs": len(all_entries),
            "error_count": error_count,
            "warn_count": warn_count,
            "unique_patterns": len(patterns),
            "critical_count": sum(1 for p in patterns if p["severity"] == "critical")
        }
    }

def status() -> dict:
    """返回状态"""
    return {
        "status": "ok",
        "version": "1.0.0",
        "framework": "capability-evolver-pro (Python port)",
        "log_sources": ["watchdog", "self-repair", "proactive", "daemon", "proactive-alerts"]
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        action = "analyze"
    else:
        action = sys.argv[1]
    
    if action == "status":
        result = status()
    else:
        result = analyze_logs()
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
