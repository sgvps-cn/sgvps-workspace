#!/bin/bash
# sgvps.cn 网站监控脚本 - 每小时检查
# 监控：网站可达性 + SSL证书 + 响应时间 + DNS解析

SITE="www.sgvps.cn"
LOG="/root/.openclaw/workspace/memory/sgvps-monitor.log"
ALERT_LOG="/root/.openclaw/workspace/memory/sgvps-alerts.log"

check_ssl() {
  echo | openssl s_client -connect $SITE:443 -servername $SITE 2>/dev/null | openssl x509 -noout -dates 2>/dev/null | grep notAfter | cut -d= -f2
}

check_response() {
  curl -o /dev/null -s -w "%{http_code}|%{time_total}" --max-time 10 "https://$SITE" 2>/dev/null
}

check_dns() {
  dig $SITE A +short 2>/dev/null | head -1
}

echo "=== sgvps.cn 监控 $(date) ===" >> "$LOG"

# SSL 检查
ssl_exp=$(check_ssl)
echo "SSL到期: $ssl_exp" >> "$LOG"

# 响应检查
response=$(check_response)
code=$(echo $response | cut -d'|' -f1)
time=$(echo $response | cut -d'|' -f2)
echo "HTTP: $code | 响应: ${time}s" >> "$LOG"

# DNS 检查
dns=$(check_dns)
echo "DNS: $dns" >> "$LOG"

# 告警条件
if [ "$code" != "200" ]; then
  echo "[ALERT] 网站不可达! HTTP: $code" >> "$ALERT_LOG"
fi

if [ -n "$ssl_exp" ]; then
  exp_epoch=$(date -d "$ssl_exp" +%s 2>/dev/null)
  now_epoch=$(date +%s)
  days_left=$(( (exp_epoch - now_epoch) / 86400 ))
  if [ "$days_left" -lt 30 ]; then
    echo "[ALERT] SSL证书即将过期! 剩余: ${days_left}天" >> "$ALERT_LOG"
  fi
fi

echo "---" >> "$LOG"
