#!/bin/bash
# Clash管理脚本
# 用法: .clash-manage.sh [start|stop|restart|status|test|switch NODE]

AUTH="123456:123456"
PORT=9090
HOST="http://127.0.0.1:$PORT"
LOG="/root/.openclaw/workspace/memory/clash-manage.log"

cmd="$1"
shift

case "$cmd" in
  start)
    cd /root/clash && nohup ./clash -d . > /tmp/clash.log 2>&1 &
    echo "Clash已启动 PID: $!" | tee -a "$LOG"
    ;;
  stop)
    pkill -f "/root/clash/clash" && echo "已停止" | tee -a "$LOG"
    ;;
  restart)
    pkill -f "/root/clash/clash"; sleep 1
    cd /root/clash && nohup ./clash -d . > /tmp/clash.log 2>&1 &
    echo "已重启 PID: $!" | tee -a "$LOG"
    ;;
  status)
    if pgrep -f "/root/clash/clash" > /dev/null; then
      echo "运行中"
      curl -s -u "$AUTH" "$HOST/proxies/GLOBAL" | python3 -c "import sys,json; d=json.load(sys.stdin); print('当前节点:', d.get('now','?'))"
    else
      echo "未运行"
    fi
    ;;
  test)
    echo "=== 节点延迟测试 ===" >> "$LOG"
    nodes=$(curl -s -u "$AUTH" "$HOST/proxies/GLOBAL" | python3 -c "import sys,json; print('\n'.join(json.load(sys.stdin).get('all',[])))" 2>/dev/null)
    for n in $nodes; do
      delay=$(curl -s -u "$AUTH" -X PUT "$HOST/proxies/$(python3 -c "import urllib.parse; print(urllib.parse.quote(input()))" <<< "$n")" -H "Content-Type: application/json" -d "{\"name\":\"$n\"}" --max-time 5 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('delay','?'))" 2>/dev/null)
      echo "$n: ${delay}ms" | tee -a "$LOG"
    done
    ;;
  switch)
    node="$*"
    encoded=$(python3 -c "import urllib.parse; print(urllib.parse.quote(input()))" <<< "$node")
    result=$(curl -s -u "$AUTH" -X PUT "$HOST/proxies/GLOBAL" -H "Content-Type: application/json" -d "{\"name\":\"$node\"}" 2>/dev/null)
    echo "切换到 $node: $(echo $result | python3 -c "import sys,json; print(json.load(sys.stdin).get('message',''))" 2>/dev/null)" | tee -a "$LOG"
    ;;
  *)
    echo "用法: clash-manage.sh start|stop|restart|status|test|switch \"节点名\""
    ;;
esac
