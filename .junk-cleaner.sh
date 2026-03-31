#!/bin/bash
# 贾维斯垃圾清理 - 每日定时清理临时文件
# 0 3 * * * /root/.openclaw/workspace/.junk-cleaner.sh

MEMDIR="/root/.openclaw/workspace/memory"
LOG="$MEMDIR/junk-clean.log"
TODAY=$(date +%Y-%m-%d)

# 写入日志
exec >> "$LOG" 2>&1
echo "=== 清理开始 $(date '+%Y-%m-%d %H:%M') ==="

TOTAL_FREED=0
REPORT=""

# 1. 清理旧的watchdog minute文件（只保留最新10个）
minute_files=$(find $MEMDIR -name "watchdog.minute.2*" | wc -l)
if [ "$minute_files" -gt 10 ]; then
  removed=$(find $MEMDIR -name "watchdog.minute.2*" | sort | head -n -10 | wc -l)
  find $MEMDIR -name "watchdog.minute.2*" | sort | head -n -10 | xargs -r rm -f
  echo "🗑️ watchdog minute文件: 清理${removed}个旧文件"
  REPORT="${REPORT}watchdog minute: ${removed}个 | "
fi

# 2. 清理超过指定大小的日志文件（截断到100行）
MAX_LOG_LINES=500
for f in $MEMDIR/*.log; do
  [ -f "$f" ] || continue
  lines=$(wc -l < "$f" 2>/dev/null || echo 0)
  if [ "$lines" -gt $MAX_LOG_LINES ]; then
    excess=$((lines - MAX_LOG_LINES))
    # 保留最后MAX_LOG_LINES行
    tail -n $MAX_LOG_LINES "$f" > "$f.tmp" && mv "$f.tmp" "$f"
    echo "✂️ ${f##*/}: ${excess}行 (${lines}→${MAX_LOG_LINES})"
    REPORT="${REPORT}${f##*/}截断${excess}行 | "
  fi
done

# 3. 清理npm缓存 (不清理.cache因为太大需确认)
npm_freed=$(du -sh /root/.npm 2>/dev/null | cut -f1)
if [ -d "/root/.npm" ]; then
  find /root/.npm -type f -mtime +1 -delete 2>/dev/null
  echo "🧹 npm缓存: 已清理（保留最近1天）"
fi

# 4. 清理pip缓存
pip_freed=$(du -sh /root/.cache/pip 2>/dev/null | cut -f1)
if [ -d "/root/.cache/pip" ]; then
  find /root/.cache/pip -type f -mtime +1 -delete 2>/dev/null
  echo "🧹 pip缓存: 已清理（保留最近1天）"
fi

# 5. 清理临时文件（/tmp下24小时前的root文件，不影响系统）
tmp_count=$(find /tmp -maxdepth 1 -type f -user root -mtime +1 2>/dev/null | wc -l)
if [ "$tmp_count" -gt 0 ]; then
  find /tmp -maxdepth 1 -type f -user root -mtime +1 -delete 2>/dev/null
  echo "🧹 /tmp临时文件: 清理${tmp_count}个"
  REPORT="${REPORT}/tmp: ${tmp_count}个 | "
fi

# 6. 清理git reflog（如果仓库干净）
cd /root/.openclaw/workspace 2>/dev/null && git reflog expire --expire=all --ours --quiet 2>/dev/null
git_sz=$(du -sh /root/.openclaw/workspace/.git 2>/dev/null | cut -f1)
echo "📦 .git目录: ${git_sz}"

# 汇总
echo ""
echo "=== 清理完成 $(date '+%H:%M') ==="
REPORT="${REPORT}npm:${npm_freed:-0} pip:${pip_freed:-0}"
echo "$REPORT"

# 发送飞书（如果有问题）
if [ ${#REPORT} -gt 5 ]; then
  python3 /root/.openclaw/workspace/.feishu-notify.py "🧹 贾维斯清理 $TODAY: ${REPORT}" 2>/dev/null
fi
