# HEARTBEAT.md - 主动检查清单

## 每次心跳（5分钟）必须执行

**1. 系统状态自检**
- Gateway 进程是否正常（port 18789）
- 守护进程是否运行（jarvis-daemon）
- 今日是否有异常日志（Error/WARN）

**2. self-improving 热内存检查（~/self-improving/）**
- 每次心跳开始先写 `last_heartbeat_started_at`（ISO 8601）
- 检查 heartbeat-state.md：距上次审查超过1小时则扫描变更
- 检查 ~/self-improving/memory.md 是否有过期条目需要归档
- 有实质变更 → 更新 index.md + compact 过载文件
- 无变更 → 写 HEARTBEAT_OK

**3. learnings 速查**
- 打开 .learnings/QUICKREF.md 快速索引
- 检查 pending 状态的 learnings
- 遇到相关领域立刻查完整记录

**4. 主动推送检查**
满足任一即推送飞书：
- 系统异常（进程崩/磁盘满/配置错误）
- SLA告警（新订单/工单/主机到期）
- 任务执行完毕（结果汇报）
- 距上次交互 >6 小时且有新发现
- 安全风险（groupPolicy变更/新插件安装）

**5. 记忆维护**
- 检查 memory/YYYY-MM-DD.md 是否存在
- 重要发现立即归档到 learnings 和 ~/self-improving/memory.md
- 修正（用户纠错）→ 写入 ~/self-improving/corrections.md + 更新 memory.md

## 不推送场景

- 深夜（23:00-08:00），除非紧急
- 正常状态下的常规心跳
- 距上次推送 <30 分钟

## 执行后记录

心跳执行后：
1. 更新 ~/self-improving/heartbeat-state.md 的 last_heartbeat_result
2. 记录到 memory/YYYY-MM-DD.md

## 主动任务检查
心跳时检查 TASKS.md，主动推进未完成任务：
- 发现可以优化的地方 → 立即做
- 发现系统问题 → 立即告警+修复
- 发现学习机会 → 立即学习

## 自我改进触发规则
- 修正收到 → 写入 corrections.md + 评估是否入 memory.md
- 相同错误3次 → 合并到 memory.md 规则
- memory.md >100行 → 触发 compact（移至 projects/domains/archive/）

## 主动规划（每日9点）

.proactive-planner.py 自动运行：
- 系统健康检查
- 新订单/工单/主机到期扫描
- SEO文章状态
- learnings pending项
- 有告警立即飞书通知

## 主动执行标准

以下情况立即执行并通知，不需要等指令：
- 系统异常（进程崩/磁盘满/服务停）
- 待处理订单/工单（>3个）
- 主机3天内到期
- learnings发现pending错误
- cron任务失败

