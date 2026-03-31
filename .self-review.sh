#!/bin/bash
# 贾维斯每日自我复盘 - 动态生成
# 0 9 * * * /root/.openclaw/workspace/.self-review.sh

LOG_DIR="/root/.openclaw/workspace/memory"
LEARNINGS="/root/.openclaw/workspace/.learnings/LEARNINGS.md"
TODAY=$(date +%Y-%m-%d)
LOG="$LOG_DIR/review-$TODAY.md"

# 每日复盘
{
  echo "=== 贾维斯自我复盘 $TODAY ==="
  echo ""
  
  # learnings统计
  if [ -f "$LEARNINGS" ]; then
    total=$(grep -c "^\[LRN\|^\[ERR" "$LEARNINGS" 2>/dev/null || echo 0)
    today_lrn=$(grep -c "$(date +%Y%m%d)" "$LEARNINGS" 2>/dev/null || echo 0)
    echo "**Learnings:** 累计${total}条，今日+${today_lrn}条"
  fi
  
  # cron运行状态
  echo ""
  echo "**Cron状态:**"
  for f in "$LOG_DIR"/*.log; do
    name=$(basename "$f")
    lines=$(wc -l < "$f" 2>/dev/null || echo 0)
    last=$(tail -1 "$f" 2>/dev/null | cut -c1-60)
    echo "- $name: ${lines}行 | 最后: $last"
  done
  
  echo ""
  echo "**Gateway:** $(/usr/bin/curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:18789/ 2>/dev/null) | mem=$(ps aux | grep openclaw-gateway | grep -v grep | awk '{print $6}')KB"
  echo "**Clash:** $(pgrep -a clash | grep -v "sh -c" | awk '{print $1}' || echo '未运行')"
  
  echo ""
  echo "=== 复盘完成 $(date '+%H:%M') ==="
} > "$LOG"

# 发送飞书
python3 /root/.openclaw/workspace/.feishu-notify.py "贾维斯日报 $TODAY 完成" 2>/dev/null
