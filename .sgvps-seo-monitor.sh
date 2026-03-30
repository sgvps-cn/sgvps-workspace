#!/bin/bash
# sgvps.cn SEO运营监控 - 每天09:00执行
# 同时推送到飞书

SITE="https://www.sgvps.cn"
LOG="/root/.openclaw/workspace/memory/seo-monitor.log"

echo "=== SEO监控 $(date '+%Y-%m-%d %H:%M') ===" >> "$LOG"

# 1. 首页状态
STATUS=$(curl -o /dev/null -s -w "%{http_code}" --max-time 10 "$SITE")
TIME=$(curl -o /dev/null -s -w "%{time_total}" --max-time 10 "$SITE")
echo "状态: HTTP $STATUS | 响应: ${TIME}s" >> "$LOG"

# 2. SSL证书到期
EXPIRY=$(echo | openssl s_client -connect www.sgvps.cn:443 -servername www.sgvps.cn 2>/dev/null | openssl x509 -noout -dates 2>/dev/null | grep notAfter | cut -d= -f2)
echo "SSL到期: $EXPIRY" >> "$LOG"

# 3. 上游API状态
curl -s --max-time 5 "https://www.nmvps.com" -o /dev/null -w "柠檬云: HTTP %{http_code}\n" >> "$LOG"
curl -s --max-time 5 "https://www.zheyunidc.cn" -o /dev/null -w "折云: HTTP %{http_code}\n" >> "$LOG"

# 4. 数据库健康
mysql -u www_sgvps_cn -p'p6dd5z992Bpc8CQR' -h 127.0.0.1 www_sgvps_cn 2>/dev/null >> "$LOG" << SQL
SELECT '活跃主机:' as metric, COUNT(*) as value FROM shd_host WHERE domainstatus='Active';
SELECT '待处理工单:' as metric, COUNT(*) as value FROM shd_ticket WHERE status NOT IN ('Closed','Resolved');
SELECT '新闻文章:' as metric, COUNT(*) as value FROM shd_news;
SQL

echo "---" >> "$LOG"
