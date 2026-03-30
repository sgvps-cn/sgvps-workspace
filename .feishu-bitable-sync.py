#!/usr/bin/env python3
"""
飞书Bitable业务监控 - 写入sgvps.cn关键指标
每小时更新一次
"""

import subprocess, json, time

TOKEN = "t-g1043v7PXWIOSWRMHOUKUEKNO2IPUC6HNT6JD7X4"
APP_TOKEN = "KQZ0bUqK1aNzqNstLpjcrLvDnQf"
TABLE_ID = "tbl8M9XPQDYQO9cq"
BASE_URL = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"

def get_token():
    r = subprocess.run(
        ["curl", "-s", "-X", "POST",
         "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
         "-H", "Content-Type: application/json",
         "-d", '{"app_id":"cli_a943e4427838dcd1","app_secret":"rnYXkg925E6JQnPjq4splbAA7Q2Lyb5u"}'],
        capture_output=True, text=True, timeout=10
    )
    try:
        return json.loads(r.stdout).get("tenant_access_token", "")
    except:
        return TOKEN  # fallback

def db_query(sql):
    r = subprocess.run(
        ["mysql", "-u", "www_sgvps_cn", "-pp6dd5z992Bpc8CQR", "-h", "127.0.0.1", "www_sgvps_cn", "-N", "-e", sql],
        capture_output=True, text=True, timeout=15
    )
    return r.stdout.strip()

def bitable_update(fields, record_id=None):
    """更新或创建Bitable记录"""
    token = get_token()
    headers = ["-H", f"Authorization: Bearer {token}", "-H", "Content-Type: application/json"]
    if record_id:
        # 更新
        cmd = ["curl", "-s", "-X", "PUT", f"{BASE_URL}/{record_id}"] + headers + ["-d", json.dumps({"fields": fields})]
    else:
        # 创建
        cmd = ["curl", "-s", "-X", "POST", BASE_URL] + headers + ["-d", json.dumps({"fields": fields})]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    try:
        return json.loads(r.stdout).get("code") == 0
    except:
        return False

def get_existing_records():
    """获取已有记录"""
    token = get_token()
    r = subprocess.run(
        ["curl", "-s", "-X", "GET", f"{BASE_URL}?page_size=100",
         "-H", f"Authorization: Bearer {token}"],
        capture_output=True, text=True, timeout=10
    )
    try:
        data = json.loads(r.stdout).get("data", {}).get("items", [])
        # 映射 hostname -> record_id
        result = {}
        for item in data:
            fields = item.get("fields", {})
            hostname = fields.get("主机名", "")
            if hostname:
                result[hostname] = item.get("record_id")
        return result
    except:
        return {}

def main():
    print("=== Bitable业务监控更新 ===")
    
    existing = get_existing_records()
    print(f"已有记录: {list(existing.keys())}")
    
    # 1. 订单统计
    pending_orders = db_query("SELECT COUNT(*) FROM shd_orders WHERE status='Pending'")
    today_orders = db_query("SELECT COUNT(*) FROM shd_orders WHERE create_time > UNIX_TIMESTAMP(CURDATE())")
    total_orders = db_query("SELECT COUNT(*) FROM shd_orders")
    
    # 2. 工单统计
    open_tickets = db_query("SELECT COUNT(*) FROM shd_ticket WHERE status='Open'")
    
    # 3. 主机统计
    active_hosts = db_query("SELECT COUNT(*) FROM shd_host WHERE domainstatus='Active'")
    expiring_hosts = db_query("SELECT COUNT(*) FROM shd_host WHERE domainstatus='Active' AND due_time > 0 AND due_time < UNIX_TIMESTAMP(NOW() + INTERVAL 3 DAY)")
    
    # 4. 文章统计
    articles = db_query("SELECT COUNT(*) FROM shd_news_menu WHERE parent_id > 0")
    
    print(f"待处理订单: {pending_orders}")
    print(f"今日订单: {today_orders}")
    print(f"总订单: {total_orders}")
    print(f"待处理工单: {open_tickets}")
    print(f"活跃主机: {active_hosts}")
    print(f"3天内到期: {expiring_hosts}")
    print(f"文章数: {articles}")
    
    # 更新Bitable (使用固定记录ID，或者创建新记录)
    # 这里我们创建一个汇总记录
    success = bitable_update({
        "主机名": "📊 业务汇总",
        "状态": "运行中",
        "IP": f"订单:{total_orders} 工单:{open_tickets} 主机:{active_hosts}",
        "产品": f"待处理:{pending_orders} 今日新:{today_orders} SEO文章:{articles}",
        "续费状态": "正常"
    })
    print(f"写入结果: {'✅' if success else '❌'}")

if __name__ == "__main__":
    main()
