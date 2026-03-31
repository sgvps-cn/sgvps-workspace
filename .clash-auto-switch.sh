#!/bin/bash
# Clash主动选优 - 每5分钟自动选最优节点
# 改进: 直接使用AUTO-全球的自动测速结果，不做人工干预
# Clash的AUTO组自带url-test每5分钟测速，直接复用
AUTH="123456:123456"
HOST="http://127.0.0.1:9090"
LOG="/root/.openclaw/workspace/memory/clash-auto-switch.log"
STATE="/root/.openclaw/workspace/memory/clash-auto-switch-state.json"

log() { echo "[$(date '+%m-%d %H:%M')] $1" >> "$LOG"; }

# 获取AUTO-全球当前选中的最优节点
auto_global_data=$(curl -s --max-time 5 -u "$AUTH" \
  "$HOST/proxies/%F0%9F%9A%80%20%F0%9F%94%A7%20AUTO-%E5%85%A8%E7%90%83" 2>/dev/null)

now_node=$(echo "$auto_global_data" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(d.get('now','?'))
" 2>/dev/null)

if [ -z "$now_node" ] || [ "$now_node" = "?" ]; then
    log "⚠️ 获取AUTO-全球状态失败"
    exit 1
fi

# 获取该节点的延迟（history是list，取最后一项）
delay=$(echo "$auto_global_data" | python3 -c "
import sys,json
d=json.load(sys.stdin)
h=d.get('history',[])
if h and isinstance(h,list) and len(h)>0:
    print(h[-1].get('delay','?'))
else:
    print('?')
" 2>/dev/null)

# 读取上次节点
last_node=$(python3 -c "
import json,sys
try:
    with open('$STATE') as f:
        d=json.load(f)
    print(d.get('last_node','?'))
except:
    print('?')
" 2>/dev/null)

# 只有节点变化才记录
if [ "$now_node" != "$last_node" ]; then
    log "🔄 切换: $last_node → $now_node (${delay}ms)"
    python3 -c "
import json
with open('$STATE','w') as f:
    json.dump({'last_node':'$now_node','last_delay':'$delay','last_switch':'$(date +%Y-%m-%d\ %H:%M)'},f)
" 2>/dev/null
else
    log "✅ $now_node (${delay}ms) [未变化]"
fi

echo "✅ $now_node (${delay}ms)"
