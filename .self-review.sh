#!/bin/bash
# 贾维斯自我审视脚本 - 每日定时执行
# 检查点：
# 1. 所有后台进程是否存活
# 2. .learnings/ 是否有待处理项目
# 3. EvoMap 节点是否在线
# 4. memory/ 今日记录是否存在
# 5. commits 是否已同步

WORKSPACE="/root/.openclaw/workspace"
LOG="$WORKSPACE/memory/$(date +%Y-%m-%d).md"

echo "=== 贾维斯自我审视 $(date) ===" >> "$LOG"
echo "" >> "$LOG"

# 1. 检查后台进程
echo "[进程检查]" >> "$LOG"
ps aux | grep -E "evolver|heartbeat|node.*index.js" | grep -v grep >> "$LOG" 2>&1 || echo "  异常：无进程" >> "$LOG"

# 2. 检查 learnings 待处理
echo "" >> "$LOG"
echo "[Learnings 待处理]" >> "$LOG"
grep -c "Status: pending" "$WORKSPACE/.learnings/LEARNINGS.md" 2>/dev/null | xargs -I{} echo "  待处理学习项: {}" >> "$LOG"

# 3. 检查 EvoMap 节点
echo "" >> "$LOG"
echo "[EvoMap 节点]" >> "$LOG"
curl -s -X POST "https://evomap.ai/a2a/heartbeat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 4bbaad422b71c3c4106dcedb6e7efd1549152bea5ea59d83e32db88c41d49f45" \
  -d '{"node_id":"node_d5f7e05f3abbc423"}' 2>/dev/null | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print('  节点状态:', d.get('survival_status'), '| 信用:', d.get('credit_balance'))" >> "$LOG" 2>&1

# 4. 检查今日 memory
echo "" >> "$LOG"
echo "[Memory 状态]" >> "$LOG"
[ -f "$LOG" ] && echo "  今日记录: 存在 ($(wc -l < "$LOG") 行)" >> "$LOG" || echo "  今日记录: 缺失" >> "$LOG"

# 5. Git 状态
echo "" >> "$LOG"
echo "[Git 状态]" >> "$LOG"
cd "$WORKSPACE" && git status --short 2>/dev/null | head -5 >> "$LOG" 2>&1
[ -z "$(git status --short 2>/dev/null)" ] && echo "  工作区: 干净" >> "$LOG" || echo "  工作区: 有未提交更改" >> "$LOG"

echo "" >> "$LOG"
echo "---" >> "$LOG"
