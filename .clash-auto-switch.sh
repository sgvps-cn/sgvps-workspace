#!/bin/bash
# Clash主动选优 - 每5分钟自动选最快节点
AUTH="123456:123456"
HOST="http://127.0.0.1:9090"
LOG="/root/.openclaw/workspace/memory/clash-auto-switch.log"

# 测试一个节点的延迟(通过API历史)
test_delay() {
    local node="$1"
    local encoded=$(python3 -c "import urllib.parse; print(urllib.parse.quote(input()))" <<< "$node")
    local data=$(curl -s --max-time 5 -u "$AUTH" "$HOST/proxies/$encoded" 2>/dev/null)
    if [ -z "$data" ]; then echo 999; return; fi
    echo "$data" | python3 -c "
import sys,json
d=json.load(sys.stdin)
h=d.get('history',{})
if h:
    print(list(h.values())[-1].get('delay',999))
else:
    print(999)
" 2>/dev/null
}

# 主逻辑: 从AUTO-HK获取当前选中的节点
log() { echo "[$(date '+%m-%d %H:%M')] $1" >> "$LOG"; }

log "=== 测速开始 ==="

# 获取AUTO-HK当前最优节点
hk_data=$(curl -s --max-time 5 -u "$AUTH" "$HOST/proxies/%F0%9F%94%A7%20AUTO-HK" 2>/dev/null)
best=$(echo "$hk_data" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(d.get('now','?'))
" 2>/dev/null)
delay=$(echo "$hk_data" | python3 -c "
import sys,json
d=json.load(sys.stdin)
h=d.get('history',{})
if h: print(list(h.values())[-1].get('delay','?'))
else: print('?')
" 2>/dev/null)

if [ -n "$best" ]; then
    # 切换GLOBAL和选择节点到最优
    curl -s --max-time 5 -u "$AUTH" -X PUT "$HOST/proxies/GLOBAL" \
        -H "Content-Type: application/json" -d "{\"name\":\"$best\"}" > /dev/null 2>&1
    curl -s --max-time 5 -u "$AUTH" -X PUT "$HOST/proxies/%F0%9F%9A%80%20%F0%9F%94%A7%20AUTO-%E5%85%A8%E7%90%83" \
        -H "Content-Type: application/json" -d "{\"name\":\"$best\"}" > /dev/null 2>&1
    log "✅ 最优: $best (${delay}ms)"
    echo "✅ $best (${delay}ms)"
else
    log "⚠️ 未获取到AUTO-HK状态"
fi
