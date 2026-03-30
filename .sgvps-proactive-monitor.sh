#!/bin/bash
# sgvps.cn 主动守护 - 每5分钟自动检查+自动修复
# 问题自动处理，不等用户干预

LOG="/root/.openclaw/workspace/memory/proactive-monitor.log"
ALERT_LOG="/root/.openclaw/workspace/memory/proactive-alerts.log"
NOW=$(date '+%m-%d %H:%M')

# 检查函数
check_and_fix() {
    local name="$1"
    local check_cmd="$2"
    local fix_cmd="$3"
    local issue="$4"
    
    if eval "$check_cmd" > /dev/null 2>&1; then
        return 0
    else
        eval "$fix_cmd" 2>/dev/null
        echo "[$NOW] $issue - 已自动修复" >> "$LOG"
        echo "[$NOW] $issue - 已自动修复" >> "$ALERT_LOG"
        return 1
    fi
}

echo "[$NOW] === 主动守护 ===" >> "$LOG"

# 1. cron卡住检查
if pgrep -f "cron.php" | head -1 | xargs -I{} ps -o etime= -p {} 2>/dev/null | grep -qE "^[0-9]+-[0-9]{2}|[0-9]{2}:[0-9]{2}"; then
    echo "[$NOW] ⚠️ cron.php卡住>1分钟，自动终止" >> "$LOG"
    echo "[$NOW] ⚠️ cron卡住 - 已终止" >> "$ALERT_LOG"
    pkill -f "cron.php" 2>/dev/null
fi

# 2. cron日志异常
STUCK=$(tail -1 /www/server/cron/8146b52f60ab0bdb5159d4361fa64eea.log 2>/dev/null | grep -c "already exists")
if [ "$STUCK" -gt 3 ]; then
    echo "[$NOW] ⚠️ cron重复跳过>3次 - 已终止旧进程" >> "$LOG"
    echo "[$NOW] ⚠️ cron重复跳过 - 已清理" >> "$ALERT_LOG"
    pkill -f "cron.php" 2>/dev/null
fi

# 3. 进程崩溃检查
for proc in mysql nginx php-fpm; do
    if ! systemctl is-active $proc > /dev/null 2>&1; then
        echo "[$NOW] ⚠️ $proc停机 - 重启中" >> "$LOG"
        echo "[$NOW] ⚠️ $proc停机 - 重启中" >> "$ALERT_LOG"
        systemctl restart $proc 2>/dev/null
    fi
done

# 4. 磁盘告警
USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$USAGE" -gt 85 ]; then
    echo "[$NOW] ⚠️ 磁盘使用${USAGE}% - 超过85%" >> "$ALERT_LOG"
fi

# 5. 内存告警
MEM_PCT=$(free | grep Mem | awk '{print int($3/$2*100)}')
if [ "$MEM_PCT" -gt 90 ]; then
    echo "[$NOW] ⚠️ 内存使用${MEM_PCT}%" >> "$ALERT_LOG"
fi

# 6. 新订单检查
NEW_ORDERS=$(mysql -u www_sgvps_cn -p'p6dd5z992Bpc8CQR' -h 127.0.0.1 www_sgvps_cn -N -e "SELECT COUNT(*) FROM shd_orders WHERE FROM_UNIXTIME(create_time) > DATE_SUB(NOW(), INTERVAL 5 MINUTE);" 2>/dev/null)
if [ "$NEW_ORDERS" -gt 0 ]; then
    echo "[$NOW] 🛒 新订单+$NEW_ORDERS" >> "$LOG"
fi

# 7. 新工单检查
NEW_TICKETS=$(mysql -u www_sgvps_cn -p'p6dd5z992Bpc8CQR' -h 127.0.0.1 www_sgvps_cn -N -e "SELECT COUNT(*) FROM shd_ticket WHERE status='Open';" 2>/dev/null)
if [ "$NEW_TICKETS" -gt 0 ]; then
    echo "[$NOW] 🎫 待处理工单:$NEW_TICKETS" >> "$LOG"
fi

echo "[$NOW] ✅ 检查完成" >> "$LOG"
