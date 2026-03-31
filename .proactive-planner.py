#!/usr/bin/env python3
"""
贾维斯主动规划引擎 - Jarvis Proactive Planner
每天9点自动运行，扫描所有来源，主动规划今日任务并执行
不需要人工干预
"""

import subprocess, json, time, os
from datetime import datetime, timedelta

LOG = "/root/.openclaw/workspace/memory/proactive-planner.log"
STATE = "/root/.openclaw/workspace/memory/proactive-planner-state.json"
MEMORY = "/root/.openclaw/workspace/MEMORY.md"
TASKS = "/root/.openclaw/workspace/TASKS.md"
NOTIFY = "/root/.openclaw/workspace/.feishu-notify.py"

def log(msg):
    ts = datetime.now().strftime("%m-%d %H:%M")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def get_state():
    try:
        with open(STATE) as f:
            return json.load(f)
    except:
        return {}

def save_state(state):
    with open(STATE, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def feishu(text):
    """发送飞书通知"""
    os.system(f"python3 {NOTIFY} {repr(text)} > /dev/null 2>&1")

def db(sql):
    try:
        r = subprocess.run(
            ["mysql", "-u", "www_sgvps_cn", "-pp6dd5z992Bpc8CQR", "-h", "127.0.0.1", "www_sgvps_cn", "-N", "-e", sql],
            capture_output=True, text=True, timeout=15
        )
        return r.stdout.strip()
    except:
        return ""

def do_task(name, func):
    """执行单个主动任务"""
    try:
        result = func()
        log(f"  ✅ {name}: {result}")
        return result
    except Exception as e:
        log(f"  ❌ {name}: {e}")
        return None

# ===== 主动任务函数 =====

def check_new_orders():
    """检查新订单，主动通知"""
    orders = db("SELECT COUNT(*) FROM shd_orders WHERE create_time > UNIX_TIMESTAMP(CURDATE())")
    return f"今日新订单: {orders}" if orders and int(orders) > 0 else None

def check_open_tickets():
    """检查待处理工单"""
    tickets = db("SELECT COUNT(*) FROM shd_ticket WHERE status='Open'")
    return f"待处理工单: {tickets}" if tickets and int(tickets) > 0 else None

def check_expiring_hosts():
    """检查3天内到期的机器"""
    hosts = db("SELECT COUNT(*) FROM shd_host WHERE due_time > 0 AND due_time < UNIX_TIMESTAMP(NOW() + INTERVAL 3 DAY) AND domainstatus='Active'")
    return f"3天内到期: {hosts}" if hosts and int(hosts) > 0 else None

def check_suspended_hosts():
    """检查已暂停的机器"""
    hosts = db("SELECT COUNT(*) FROM shd_host WHERE domainstatus='Suspended'")
    return f"已暂停: {hosts}" if hosts and int(hosts) > 0 else None

def check_system_health():
    """系统健康检查"""
    results = []
    # MySQL
    if subprocess.run(["systemctl", "is-active", "mysql"], capture_output=True, text=True).stdout.strip() != "active":
        results.append("MySQL异常")
    # Disk
    r = subprocess.run(["df", "-h", "/"], capture_output=True, text=True)
    usage = int(r.stdout.split()[-2].replace("%", ""))
    if usage > 85:
        results.append(f"磁盘{usage}%")
    # Memory
    r = subprocess.run(["free"], capture_output=True, text=True)
    lines = r.stdout.strip().split("\n")
    mem = lines[1].split()
    pct = int(int(mem[2]) / int(mem[1]) * 100)
    if pct > 90:
        results.append(f"内存{pct}%")
    return f"系统: {', '.join(results)}" if results else "系统正常"

def check_seo_articles():
    """SEO文章生成检查"""
    articles = db("SELECT COUNT(*) FROM shd_news_menu WHERE parent_id > 0")
    today = db("SELECT COUNT(*) FROM shd_news_menu WHERE create_time > UNIX_TIMESTAMP(CURDATE())")
    return f"文章:{articles} (今日新增:{today})"

def check_pending_orders_detail():
    """待处理订单详情"""
    orders = db("SELECT COUNT(*) FROM shd_orders WHERE status='Pending'")
    if orders and int(orders) > 0:
        return f"待处理订单: {orders}"
    return None

def scan_learnings():
    """扫描learnings，发现pending项"""
    state = get_state()
    try:
        with open("/root/.openclaw/workspace/.learnings/LEARNINGS.md") as f:
            content = f.read()
        pending = content.count("Status**: pending")
        return f"待处理learnings: {pending}"
    except:
        return None

# ===== 今日任务规划 =====

def plan_today():
    """规划今日主动任务"""
    state = get_state()
    today = datetime.now().strftime("%Y-%m-%d")
    tasks = []
    
    # 每日必做
    daily = [
        ("系统健康", check_system_health),
        ("新订单", check_new_orders),
        ("待处理工单", check_open_tickets),
        ("到期检查", check_expiring_hosts),
        ("暂停主机", check_suspended_hosts),
        ("SEO文章", check_seo_articles),
        ("learnings扫描", scan_learnings),
    ]
    
    results = []
    alerts = []
    for name, func in daily:
        r = do_task(name, func)
        if r:
            results.append(r)
            if any(x in r for x in ["异常", "待处理", "到期", "暂停"]):
                alerts.append(r)
    
    # 如果有告警，推飞书
    if alerts:
        feishu("🚨 贾维斯晨检告警\n" + "\n".join(alerts))
    else:
        feishu(f"✅ 贾维斯晨检完成\n" + "\n".join(results[:4]))
    
    # 更新状态
    state["last_run"] = datetime.now().isoformat()
    state["today"] = today
    state["results"] = results
    state["alerts"] = alerts
    save_state(state)
    
    log("=== 今日规划完成 ===")
    return results

if __name__ == "__main__":
    plan_today()
