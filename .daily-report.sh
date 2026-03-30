#!/bin/bash
# 贾维斯主动管理 - 每日业务报告
# 每天 09:00 自动生成并推送到飞书

WORKSPACE="/root/.openclaw/workspace"
LOG="$WORKSPACE/memory/daily-report.log"

mysql -u www_sgvps_cn -p'p6dd5z992Bpc8CQR' -h 127.0.0.1 www_sgvps_cn 2>/dev/null > /tmp/daily_stats.txt << 'SQL'
SELECT '客户总数' as metric, COUNT(*) as value FROM shd_clients
UNION ALL SELECT '活跃订单', COUNT(*) FROM shd_orders WHERE status='Active'
UNION ALL SELECT '活跃主机', COUNT(*) FROM shd_host WHERE domainstatus='Active'
UNION ALL SELECT '待处理工单', COUNT(*) FROM shd_ticket WHERE status NOT IN ('Closed','Resolved')
UNION ALL SELECT '今日新订单', COUNT(*) FROM shd_orders WHERE FROM_UNIXTIME(create_time) >= CURDATE();
SQL

STATS=$(cat /tmp/daily_stats.txt)
REPORT="🦞 贾维斯日报 $(date '+%m-%d')

---
📊 运营数据
$(echo "$STATS" | grep -A1 "metric" | head -2 | tail -1) 客户
$(echo "$STATS" | grep -A2 "Active" | head -2 | tail -1) 活跃订单
$(echo "$STATS" | grep -A3 "Active" | head -2 | tail -1) 活跃主机

---
🚨 系统状态
$(systemctl is-active mysql 2>/dev/null || echo "❌") MySQL
$(systemctl is-active fail2ban 2>/dev/null || echo "❌") Fail2Ban

---
⏰ $(date '+%H:%M')"

# 发送到飞书
curl -s -X POST "https://open.feishu.cn/open-apis/bot/v2/hook/$(cat $WORKSPACE/.env | grep FEISHU_WEBHOOK | cut -d= -f2)" \
  -H "Content-Type: application/json" \
  -d "{\"msg_type\":\"text\",\"content\":{\"text\":\"$REPORT\"}}" 2>/dev/null

echo "[$(date)] Daily report sent" >> "$LOG"
