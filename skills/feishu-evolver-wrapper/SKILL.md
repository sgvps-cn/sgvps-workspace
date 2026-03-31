---
name: feishu_evolver_wrapper
description: Feishu集成的进化引擎包装器 - 管理Evolver生命周期、发送富卡片汇报、提供可视化仪表盘。用于飞书环境的进化汇报。
version: 1.0.0
author: Jarvis v3
---

# Feishu Evolver Wrapper v1.0

**功能：** 给 evolver 加飞书汇报能力，管理进化循环生命周期。

## 文件结构

| 文件 | 作用 |
|---|---|
| `lifecycle.js` | 生命周期管理（start/stop/status/ensure） |
| `health_check.js` | 健康检查 |
| `report.js` | 生成飞书汇报卡片 |
| `send-card-cli.js` | 发送飞书卡片 |
| `visualize_dashboard.js` | 生成进化仪表盘 |
| `self-repair.js` | 进化器自修复 |
| `weekly_insight.js` | 周洞察 |
| `daemon.sh` | 守护脚本 |

## 使用方法

### 生命周期管理
```bash
node skills/feishu-evolver-wrapper/lifecycle.js status   # 查看状态
node skills/feishu-evolver-wrapper/lifecycle.js ensure   # 确保运行中（重启崩溃/挂起的）
node skills/feishu-evolver-wrapper/lifecycle.js start    # 启动
node skills/feishu-evolver-wrapper/lifecycle.js stop     # 停止
```

### 手动发送进化报告
```bash
node skills/feishu-evolver-wrapper/report.js
```

### 健康检查
```bash
node skills/feishu-evolver-wrapper/check_health.js
```

### 生成仪表盘
```bash
node skills/feishu-evolver-wrapper/visualize_dashboard.js
```

## 守护机制

每10分钟自动运行 `lifecycle.js ensure`：
- 检测 evolver 是否崩溃/挂起
- 挂起 → 自动重启
- 丢失 → 重新启动
- 防止 evolver 长时间离线

## 飞书卡片格式

汇报卡片包含：
- 进化阶段标题
- 成果列表
- 指标数据（修复次数/错误率/技能数量）
- 时间戳

## 与 .self-repair.py 的关系

| 组件 | 职责 |
|---|---|
| `lifecycle.js ensure` | 确保 evolver 进程运行 |
| `self-repair.js` | 通用故障自修复 |
| `.evolution-hourly.py` | 每小时汇报（独立于 evolver）|

## 贾维斯集成

```bash
# 检查 evolver 状态
node ~/.openclaw/workspace/skills/feishu-evolver-wrapper/lifecycle.js status
```

## 环境变量

| 变量 | 说明 |
|---|---|
| `EVOLVE_REPORT_TOOL` | 设为 `feishu` 启用飞书汇报 |
| `EVOLVE_LOOP_INTERVAL` | 进化循环间隔（默认60000ms）|

---
*最后更新: 2026-03-31 by Jarvis*
