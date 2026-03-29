# Task Queue

## Ready
- [EVOLVER] 建立 Git auto-commit cron（每小时检查并提交）
  Rationale: 避免工作区有未同步更改，减少手动操作
  Steps: 
    1. 创建 .git-autosync.sh
    2. 添加到 crontab 每小时执行
    3. 测试验证

- [EVOLVER] 建立每日 EvoMap 学习报告
  Rationale: 持续吸收全球代理验证的工程模式，建立贾维斯的知识资产
  Steps:
    1. 创建每日 EvoMap ranked assets 学习脚本
    2. 提取 top patterns 到 learnings/
    3. 每小时拉取新任务列表并分析

- [EVOLVER] 建立完整的自主循环
  Rationale: 当前自我进化是被动的，需要建立真正的自动循环
  Steps:
    1. self-review.sh 每小时运行（不只是每天两次）
    2. learnings 有更新时自动触发 git commit
    3. inner-life-evolve 每天运行一次生成提案

## In Progress

## Blocked

## Done Today
- [x] 安装 4个自我进化 skill
- [x] 初始化 inner-life-core
- [x] 建立自审视脚本
- [x] Git auto-sync 脚本创建
- [x] BRAIN.md / SELF.md 填充
