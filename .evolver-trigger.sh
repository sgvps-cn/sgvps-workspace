#!/bin/bash
# 贾维斯进化引擎触发器 - 每小时运行一次Evolver进化周期
# 0 * * * * /root/.openclaw/workspace/.evolver-trigger.sh

EVOLVER_DIR="/root/.openclaw/evolver"
LOG="/root/.openclaw/workspace/memory/evolver-trigger.log"
STATUS_FILE="/root/.openclaw/workspace/memory/evolver-status.json"

log() { echo "[$(date '+%m-%d %H:%M')] $1" >> "$LOG"; }

cd "$EVOLVER_DIR"

# 加载环境变量
set -a && . .env > /dev/null 2>&1 && set +a

log "=== Evolver触发开始 ==="

# 1. 健康检查
log "1. 健康检查..."
HEALTH=$(node -e "
const {runHealthCheck} = require('./src/ops/health_check');
const r = runHealthCheck();
console.log(JSON.stringify(r));
" 2>&1)
HEALTH_STATUS=$(echo "$HEALTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status','?'))" 2>/dev/null)
log "  健康状态: $HEALTH_STATUS"

# 2. 自我修复
log "2. 自我修复..."
REPAIR=$(node src/ops/self_repair.js 2>&1)
log "  $REPAIR"

# 3. 运行进化周期(非阻塞)
log "3. 触发Evolver..."
node index.js run >> "$LOG" 2>&1 &
EVOLVER_PID=$!
log "  Evolver PID: $EVOLVER_PID"

# 等待最多60秒
sleep 60
if kill -0 $EVOLVER_PID 2>/dev/null; then
    log "  Evolver运行中，超时，继续..."
    kill $EVOLVER_PID 2>/dev/null
else
    log "  Evolver完成"
fi

log "=== 完成 ==="
echo "$HEALTH_STATUS" > "$STATUS_FILE"
