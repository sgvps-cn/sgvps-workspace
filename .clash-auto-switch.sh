#!/bin/bash
# Clash主动选优 - 每5分钟自动选最快节点
# 修复: history是list不是dict，且需要查单个节点的history
AUTH="123456:123456"
HOST="http://127.0.0.1:9090"
LOG="/root/.openclaw/workspace/memory/clash-auto-switch.log"

log() { echo "[$(date '+%m-%d %H:%M')] $1" >> "$LOG"; }

log "=== 测速开始 ==="

# 获取AUTO-HK当前选中的节点名
hk_data=$(curl -s --max-time 5 -u "$AUTH" "$HOST/proxies/%F0%9F%94%A7%20AUTO-HK" 2>/dev/null)
best=$(echo "$hk_data" | python3 -c "
import sys,json; d=json.load(sys.stdin); print(d.get('now','?'))
" 2>/dev/null)

if [ -z "$best" ] || [ "$best" = "?" ]; then
    log "⚠️ 未获取到AUTO-HK状态"
    exit 1
fi

# URL编码best节点名
best_encoded=$(python3 -c "import urllib.parse; print(urllib.parse.quote(input()))" <<< "$best")

# 获取该节点的延迟（history是list，最后一项有delay）
delay=$(curl -s --max-time 5 -u "$AUTH" "$HOST/proxies/$best_encoded" 2>/dev/null | python3 -c "
import sys,json; d=json.load(sys.stdin)
h=d.get('history', [])
if h and isinstance(h, list) and len(h) > 0:
    print(h[-1].get('delay', '?'))
elif h and isinstance(h, dict) and h:
    print(list(h.values())[-1].get('delay', '?'))
else:
    print('?')
" 2>/dev/null)

# 切换GLOBAL到最优节点
curl -s --max-time 5 -u "$AUTH" -X PUT "$HOST/proxies/GLOBAL" \
    -H "Content-Type: application/json" -d "{\"name\":\"$best\"}" > /dev/null 2>&1

# 切换AUTO-全球到最优节点
curl -s --max-time 5 -u "$AUTH" -X PUT "$HOST/proxies/%F0%9F%9A%80%20%F0%9F%94%A7%20AUTO-%E5%85%A8%E7%90%83" \
    -H "Content-Type: application/json" -d "{\"name\":\"$best\"}" > /dev/null 2>&1

log "✅ 最优: $best (${delay}ms)"
echo "✅ $best (${delay}ms)"
