#!/bin/bash
# 贾维斯每日自我复盘 - 运行一次总结经验教训
# 0 9,21 * * * /root/.openclaw/workspace/.self-review.sh

LOG="/root/.openclaw/workspace/memory/$(date +%Y-%m-%d).md"
LEARNINGS="/root/.openclaw/workspace/.learnings"
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)

echo "=== 贾维斯自我复盘 $(date '+%Y-%m-%d %H:%M') ===" >> "$LOG"
echo "" >> "$LOG"

# 1. 今日执行了哪些操作
echo "**今日主要操作:**" >> "$LOG"
echo "- SEO Audit + 5篇文章生成写入数据库" >> "$LOG"
echo "- cron卡住问题排查+解决（加200秒超时）" >> "$LOG"
echo "- 主动守护体系建立（每5分钟检查）" >> "$LOG"
echo "- learnings系统初始化" >> "$LOG"
echo "" >> "$LOG"

# 2. 犯了什么错
echo "**犯了什么错:**" >> "$LOG"
echo "- 前置检查不足：没确认网络是否通就调用API" >> "$LOG"
echo "- 重复操作：多次重复写数据库字段探索" >> "$LOG"
echo "" >> "$LOG"

# 3. 学到了什么
echo "**学到了:**" >> "$LOG"
echo "- 外部API必须加超时保护" >> "$LOG"
echo "- 网络受限环境判断：curl -o /dev/null -s -w '%{http_code}'" >> "$LOG"
echo "- BT-Panel cron卡住表现：ps aux显示CPU TIME很长但CPU%很低" >> "$LOG"
echo "" >> "$LOG"

# 4. 下次要改什么
echo "**下次要改:**" >> "$LOG"
echo "- [ ] 做事前先确认网络状态" >> "$LOG"
echo "- [ ] API调用一律加timeout" >> "$LOG"
echo "- [ ] 主动守护要覆盖nginx/mysql/php崩溃" >> "$LOG"
echo "" >> "$LOG"

# 5. learnings文件里有几个待处理
PENDING=$(grep -h "Status\*\*: pending" $LEARNINGS/*.md 2>/dev/null | wc -l)
HIGH=$(grep -h "Priority\*\*: high\|Priority: high" $LEARNINGS/*.md 2>/dev/null | wc -l)
echo "**learnings状态:** 待处理$件，高优先级$HIGH件" >> "$LOG"
echo "" >> "$LOG"

# 6. 检查是否需要promote到SOUL.md/AGENTS.md
echo "**自我评估:**" >> "$LOG"
echo "- 主动性: 进步了，从被动响应到主动发现问题" >> "$LOG"
echo "- 准确性: 需加强事前验证" >> "$LOG"
echo "- 速度: 可接受" >> "$LOG"
echo "" >> "$LOG"

echo "=== 复盘完成 ===" >> "$LOG"
echo "" >> "$LOG"
