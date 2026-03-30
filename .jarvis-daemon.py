#!/usr/bin/env python3
"""
贾维斯持续守护进程 - Jarvis Persistent Daemon
每小时运行，自动监控系统/订单/工单/SLA，推送飞书通知
"""

import time
import os
import sys
import json
import subprocess
import requests
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers import interval

# ========== 配置 ==========
STATE_FILE = "/root/.openclaw/workspace/memory/daemon-state.json"
LOG_FILE = "/root/.openclaw/workspace/memory/daemon.log"
FEISHU_APP_ID = "cli_a943e4427838dcd1"
FEISHU_APP_SECRET = "rnYXkg925E6JQnPjq4splbAA7Q2Lyb5u"
FEISHU_USER_ID = "ou_08ac6d09db0b76c0f90f4ef5e46cff78"  # 刘海浪

DB_HOST = "127.0.0.1"
DB_USER = "www_sgvps_cn"
DB_PASS = "p6dd5z992Bpc8CQR"
DB_NAME = "www_sgvps_cn"

# ========== 工具函数 ==========

def log(msg):
    ts = datetime.now().strftime("%m-%d %H:%M")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def get_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, ensure_ascii=False)

def feishu_send(text):
    """获取tenant_access_token"""
    try:
        r = requests.post(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET},
            timeout=10
        )
        token = r.json().get("tenant_access_token", "")
        if not token:
            return False
        
        # 发送消息
        r2 = requests.post(
            "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "receive_id": FEISHU_USER_ID,
                "msg_type": "text",
                "content": json.dumps({"text": text})
            },
            timeout=10
        )
        return r2.status_code == 200
    except Exception as e:
        log(f"飞书推送失败: {e}")
        return False

def db_query(sql):
    """执行MySQL查询"""
    try:
        result = subprocess.run(
            ["mysql", "-u", DB_USER, f"-p{DB_PASS}", "-h", DB_HOST, DB_NAME, "-N", "-e", sql],
            capture_output=True, text=True, timeout=15
        )
        return result.stdout.strip()
    except Exception as e:
        log(f"数据库查询失败: {e}")
        return ""

# ========== 检查任务 ==========

def check_system():
    """系统健康检查"""
    checks = []
    
    # 1. MySQL
    try:
        r = subprocess.run(["systemctl", "is-active", "mysql"], capture_output=True, text=True, timeout=5)
        if "active" in r.stdout:
            checks.append("✅ MySQL正常")
        else:
            checks.append("⚠️ MySQL异常")
            subprocess.run(["systemctl", "restart", "mysql"], capture_output=True, timeout=15)
            checks.append("  已尝试重启MySQL")
    except:
        checks.append("⚠️ MySQL检查失败")
    
    # 2. Nginx (BT-Panel用init.d启的, systemctl可能显示failed)
    try:
        r1 = subprocess.run(["systemctl", "is-active", "nginx"], capture_output=True, text=True, timeout=5)
        r2 = subprocess.run(["pgrep", "-x", "nginx"], capture_output=True, text=True, timeout=5)
        if "active" in r1.stdout or r2.stdout.strip():
            checks.append("✅ Nginx正常")
        else:
            checks.append("⚠️ Nginx异常，已重启")
            subprocess.run(["systemctl", "restart", "nginx"], capture_output=True, timeout=15)
    except:
        pass
    
    # 3. PHP-FPM
    try:
        r = subprocess.run(["systemctl", "is-active", "php-fpm-74"], capture_output=True, text=True, timeout=5)
        if "active" not in r.stdout:
            checks.append("⚠️ PHP-FPM异常")
    except:
        pass
    
    # 4. 磁盘
    try:
        r = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, timeout=5)
        usage = int(r.stdout.split()[-2].replace("%", ""))
        if usage > 85:
            checks.append(f"⚠️ 磁盘使用{usage}%")
        else:
            checks.append(f"✅ 磁盘{usage}%")
    except:
        pass
    
    # 5. 内存
    try:
        r = subprocess.run(["free", "-m"], capture_output=True, text=True, timeout=5)
        lines = r.stdout.strip().split("\n")
        mem = lines[1].split()
        used, total = int(mem[2]), int(mem[1])
        pct = int(used / total * 100)
        if pct > 90:
            checks.append(f"⚠️ 内存{pct}%")
        else:
            checks.append(f"✅ 内存{pct}%")
    except:
        pass
    
    return checks

def check_orders():
    """新订单检查"""
    results = []
    
    # 待处理订单
    pending = db_query("SELECT COUNT(*) FROM shd_orders WHERE status='Pending'")
    if pending and int(pending) > 0:
        results.append(f"🛒 待处理订单: {pending}")
    
    # 新订单(最近1小时)
    new_orders = db_query(
        "SELECT COUNT(*) FROM shd_orders WHERE create_time > UNIX_TIMESTAMP(NOW() - 3600)"
    )
    if new_orders and int(new_orders) > 0:
        results.append(f"🛒 新订单(1h): {new_orders}")
    
    return results

def check_tickets():
    """工单检查"""
    results = []
    
    # 待处理工单
    open_tickets = db_query("SELECT COUNT(*) FROM shd_ticket WHERE status='Open'")
    if open_tickets and int(open_tickets) > 0:
        results.append(f"🎫 待处理工单: {open_tickets}")
    
    return results

def check_website():
    """网站可用性检查"""
    try:
        r = requests.get("https://www.sgvps.cn", timeout=10)
        if r.status_code == 200:
            return ["✅ 网站正常"]
        else:
            return [f"⚠️ 网站异常: HTTP {r.status_code}"]
    except Exception as e:
        return [f"⚠️ 网站不可达: {e}"]

def check_sla():
    """SLA相关检查"""
    results = []
    
    # 检查是否有主机即将到期(3天内)
    expiring = db_query(
        "SELECT COUNT(*) FROM shd_host WHERE due_time > 0 AND due_time < UNIX_TIMESTAMP(NOW() + INTERVAL 3 DAY)"
    )
    if expiring and int(expiring) > 0:
        results.append(f"📅 即将到期主机(3天内): {expiring}")
    
    # 检查暂停的主机
    suspended = db_query("SELECT COUNT(*) FROM shd_host WHERE domainstatus='Suspended'")
    if suspended and int(suspended) > 0:
        results.append(f"⏸️ 已暂停主机: {suspended}")
    
    return results

def check_cron():
    """cron健康检查"""
    results = []
    
    # 检查BT-cron日志
    try:
        with open("/www/server/cron/8146b52f60ab0bdb5159d4361fa64eea.log") as f:
            lines = f.readlines()
        if lines:
            last = lines[-1].strip()
            if "already exists" in last:
                # 检查进程是否真的在跑
                r = subprocess.run(["pgrep", "-f", "cron.php"], capture_output=True, text=True)
                if r.stdout.strip():
                    results.append("⚠️ cron进程卡住，已终止")
                    subprocess.run(["pkill", "-9", "-f", "cron.php"], capture_output=True)
                else:
                    results.append("⚠️ cron重复跳过(进程已死)")
    except:
        pass
    
    return results

# ========== 主循环 ==========

def run_checks():
    """执行所有检查，发送飞书通知"""
    log("=== 检查开始 ===")
    state = get_state()
    alerts = []
    all_ok = []
    
    checks = {
        "系统": check_system(),
        "网站": check_website(),
        "订单": check_orders(),
        "工单": check_tickets(),
        "SLA": check_sla(),
        "Cron": check_cron(),
    }
    
    for category, results in checks.items():
        for r in results:
            if r.startswith("✅"):
                all_ok.append(f"{category}: {r}")
            else:
                alerts.append(f"{category}: {r}")
    
    # 告警才推送
    if alerts:
        alert_text = "🚨 贾维斯监控告警\n" + "\n".join(alerts)
        log("发送告警")
        feishu_send(alert_text)
    
    # 保存状态
    state["last_check"] = datetime.now().isoformat()
    state["alerts"] = alerts
    state["all_ok"] = all_ok
    save_state(state)
    
    log(f"检查完成: {len(alerts)}告警, {len(all_ok)}正常")

# ========== 启动 ==========

def main():
    log("========== 贾维斯守护进程启动 ==========")
    
    # 确保日志目录存在
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    scheduler = BlockingScheduler()
    
    # 每5分钟执行一次检查
    scheduler.add_job(run_checks, "interval", minutes=5, id="main_check")
    
    # 启动时立即执行一次
    run_checks()
    
    log("守护进程运行中 (每5分钟检查一次)")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log("守护进程停止")
        sys.exit(0)

if __name__ == "__main__":
    main()
