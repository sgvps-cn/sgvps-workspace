#!/bin/bash
# Clash 主动选优监控 v2
# 职责：
#   1. 确保 GLOBAL 组指向 AUTO-全球（自动选优）
#   2. 监控 AUTO 组状态和切换
#   3. 记录测速历史
#   4. 异常时推送飞书告警
# Clash 的 url-test 每300s自动测速，此脚本负责监控和保障

AUTH="123456:123456"
HOST="http://127.0.0.1:9090"
LOG="/root/.openclaw/workspace/memory/clash-auto-switch.log"
STATE="/root/.openclaw/workspace/memory/clash-auto-switch-state.json"
FEISHU="/root/.openclaw/workspace/.feishu-notify.py"

log() { echo "[$(date '+%m-%d %H:%M')] $1" >> "$LOG"; }

send_feishu() {
    python3 "$FEISHU" "$1" 2>/dev/null
}

# ── 获取代理状态 ──────────────────────────────────────────
get_proxy() {
    local name="$1"
    curl -s --max-time 5 -u "$AUTH" "$HOST/proxies/$(python3 -c "import urllib.parse; print(urllib.parse.quote(input()))" <<< "$name")" 2>/dev/null
}

# ── 从 Clash API 获取所有关键组状态 ────────────────────────
STATUS=$(curl -s --max-time 5 -u "$AUTH" "$HOST/proxies" 2>/dev/null)
if [ -z "$STATUS" ]; then
    log "⚠️ 连接Clash API失败"
    send_feishu "⚠️ Clash API 无响应，可能已停止"
    exit 1
fi

# GLOBAL 当前指向
GLOBAL_NOW=$(echo "$STATUS" | python3 -c "
import sys,json
d=json.load(sys.stdin)
g=d['proxies'].get('GLOBAL',{})
print(g.get('now','?'))
" 2>/dev/null)

# AUTO-全球
AUTO_NOW=$(echo "$STATUS" | python3 -c "
import sys,json
d=json.load(sys.stdin)
g=d['proxies'].get('🚀 AUTO-全球',{})
print(g.get('now','?'))
" 2>/dev/null)

AUTO_DELAY=$(echo "$STATUS" | python3 -c "
import sys,json
d=json.load(sys.stdin)
g=d['proxies'].get('🚀 AUTO-全球',{})
h=g.get('history',[])
if h and isinstance(h,list) and len(h)>0:
    print(h[-1].get('delay','?'))
else:
    print('?')
" 2>/dev/null)

# AUTO-HK
HK_NOW=$(echo "$STATUS" | python3 -c "
import sys,json
d=json.load(sys.stdin)
g=d['proxies'].get('🔧 AUTO-HK',{})
print(g.get('now','?'))
" 2>/dev/null)

# AUTO-JP
JP_NOW=$(echo "$STATUS" | python3 -c "
import sys,json
d=json.load(sys.stdin)
g=d['proxies'].get('🔧 AUTO-JP',{})
print(g.get('now','?'))
" 2>/dev/null)

# 连接数
CONN_COUNT=$(echo "$STATUS" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(len(d.get('connections',[])))
" 2>/dev/null)

log "GLOBAL=$GLOBAL_NOW | AUTO=$AUTO_NOW(${AUTO_DELAY}ms) | HK=$HK_NOW | JP=$JP_NOW"

# ── 保障：GLOBAL 必须指向 AUTO-全球 ────────────────────────
if [ "$GLOBAL_NOW" != "🚀 AUTO-全球" ]; then
    log "⚠️ GLOBAL 异常($GLOBAL_NOW)，切换到 AUTO-全球"
    send_feishu "⚠️ GLOBAL 被重置为 $GLOBAL_NOW，已自动恢复为 🚀 AUTO-全球"
    curl -s --max-time 5 -u "$AUTH" -X PUT "$HOST/proxies/GLOBAL" \
        -H "Content-Type: application/json" \
        -d '{"name":"🚀 AUTO-全球"}' > /dev/null 2>&1
    GLOBAL_NOW="🚀 AUTO-全球"
fi

# ── 节点切换告警 ──────────────────────────────────────────
LAST_NODE=$(python3 -c "
import json
try:
    with open('$STATE') as f: d=json.load(f)
    print(d.get('auto_node','?'))
except: print('?')
" 2>/dev/null)

if [ "$AUTO_NOW" != "$LAST_NODE" ] && [ "$LAST_NODE" != "?" ]; then
    log "🔄 AUTO切换: $LAST_NODE → $AUTO_NOW (${AUTO_DELAY}ms)"
    send_feishu "🔄 节点切换: $LAST_NODE → $AUTO_NOW (${AUTO_DELAY}ms)"
fi

# ── 记录状态 ──────────────────────────────────────────────
python3 -c "
import json
d={
    'auto_node': '$AUTO_NOW',
    'auto_delay': '$AUTO_DELAY',
    'hk_node': '$HK_NOW',
    'jp_node': '$JP_NOW',
    'global': '$GLOBAL_NOW',
    'connections': '$CONN_COUNT',
    'updated': '$(date +%Y-%m-%d\ %H:%M)'
}
with open('$STATE','w') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
" 2>/dev/null

echo "✅ $AUTO_NOW (${AUTO_DELAY}ms) | HK:$HK_NOW | JP:$JP_NOW"
