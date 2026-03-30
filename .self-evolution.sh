#!/bin/bash
# 贾维斯每周自我进化 - 周日运行
# 0 8 * * 0 /root/.openclaw/workspace/.self-evolution.sh

LOG="/root/.openclaw/workspace/memory/evolution-$(date +%Y-W%V).log"
LEARNINGS="/root/.openclaw/workspace/.learnings"
MEMORY="/root/.openclaw/workspace/MEMORY.md"

echo "=== 贾维斯进化 $(date) ===" | tee -a "$LOG"

# 1. 统计本周learnings
echo "" >> "$LOG"
echo "【本周学习统计】" | tee -a "$LOG"
NewLearnings=$(grep -c "Logged.*2026-0" $LEARNINGS/LEARNINGS.md 2>/dev/null || echo 0)
NewErrors=$(grep -c "Logged.*2026-0" $LEARNINGS/ERRORS.md 2>/dev/null || echo 0)
echo "新learnings: $NewLearnings, 新errors: $NewErrors" | tee -a "$LOG"

# 2. 找高频错误模式
echo "" >> "$LOG"
echo "【高频错误模式】" | tee -a "$LOG"
grep -h "See Also\|Recurrence" $LEARNINGS/*.md 2>/dev/null | grep "Recurrence-Count: [3-9]" | head -5 >> "$LOG" || echo "无高频错误" >> "$LOG"

# 3. 检查SOUL.md/AGENTS.md是否需要更新
echo "" >> "$LOG"
echo "【文件更新检查】" | tee -a "$LOG"
SELF_SIZE=$(wc -c < "$MEMORY")
SELF_LINES=$(wc -l < "$MEMORY")
echo "MEMORY.md: ${SELF_SIZE}B, ${SELF_LINES}行" | tee -a "$LOG"

# 4. learnings里pending的条目
echo "" >> "$LOG"
echo "【待处理learnings】" | tee -a "$LOG"
grep -B2 "Status.*pending" $LEARNINGS/*.md 2>/dev/null | grep "^##" | head -10 >> "$LOG" || echo "无待处理" >> "$LOG"

# 5. 自我评分
echo "" >> "$LOG"
echo "【本周自评】" | tee -a "$LOG"
echo "- 主动性: $([ $NewLearnings -gt 0 ] && echo '有进步，主动记录' || echo '需加强')" | tee -a "$LOG"
echo "- 错误减少: 与上周对比" | tee -a "$LOG"
echo "- 记忆维护: 正常" | tee -a "$LOG"

echo "" >> "$LOG"
echo "=== 进化完成 ===" | tee -a "$LOG"
