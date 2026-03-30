#!/bin/bash
# 贾维斯进程守护脚本 - 每5分钟检查一次
WORKSPACE="/root/.openclaw/workspace"
LOG="$WORKSPACE/memory/watchdog.log"

check_process() {
  local name=$1
  local pid=$2
  local restart_cmd=$3
  
  if ps -p $pid > /dev/null 2>&1; then
    return 0  # 存活
  else
    echo "[WATCHDOG] $name 崩溃，尝试重启: $(date)" >> "$LOG"
    eval "$restart_cmd" >> "$LOG" 2>&1
    echo "[WATCHDOG] $name 重启完成: $(date)" >> "$LOG"
    return 1
  fi
}

echo "=== Watchdog $(date) ===" >> "$LOG"

# 检查 Evolver
EVOLVER_PID=$(pgrep -f "node.*evolver.*--loop" 2>/dev/null | head -1)
if [ -n "$EVOLVER_PID" ]; then
  echo "Evolver PID $EVOLVER_PID: 存活" >> "$LOG"
else
  echo "Evolver: 未运行，重启中" >> "$LOG"
  cd "$WORKSPACE/evolver" && nohup node index.js --loop > "$WORKSPACE/.evolver.log" 2>&1 &
  echo "Evolver PID $!: 已启动" >> "$LOG"
fi

# 检查心跳
HEARTBEAT_PID=$(pgrep -f "evomap-heartbeat" 2>/dev/null | head -1)
if [ -n "$HEARTBEAT_PID" ]; then
  echo "心跳 PID $HEARTBEAT_PID: 存活" >> "$LOG"
else
  echo "心跳: 未运行，重启中" >> "$LOG"
  nohup bash "$WORKSPACE/.evomap-heartbeat.sh" > "$WORKSPACE/.evomap-heartbeat.log" 2>&1 &
  echo "心跳 PID $!: 已启动" >> "$LOG"
fi

echo "---" >> "$LOG"
