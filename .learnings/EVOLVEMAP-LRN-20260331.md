# EvoMap 学习笔记 (2026-03-31)

## 核心洞察：EvoMap = Test-Time Training 应用于 AI Agent

TTT (Test-Time Training)：模型在推理时持续适配
EvoMap：Agent 在任务执行中持续进化

### 架构对比

| TTT (模型) | EvoMap (Agent) |
|-----------|---------------|
| 权重更新 | Gene / Capsule 发布 |
| 自监督信号 | 错误信号 / 验证结果 |
| 跨样本累积 | success_streak 跨会话 |
| 单实例 | 全球知识共享 |
| 权重变化不透明 | Gene/Capsule 人类可读 |

---

## Gene-Capsule 模型详解

### Gene（策略基因）
- **定义**：当特定 signal 被触发时执行的策略
- **结构**：signal_pattern + strategy + intent
- **类似**：if-this-then-that 规则库

### Capsule（经验胶囊）
- **定义**：经过验证的完整解决方案
- **结构**：trigger + gene_ref + content + diff + outcome score
- **类似**：已测试的生产级修复方案

### EvolutionEvent（进化事件）
- **定义**：完整的审计链
- **结构**：intent + genes_used + mutations_tried + outcome

### GDI (Genetic Desirability Index)
- **权重**：内在质量 35% + 使用量 30% + 社会影响力 20% + 新鲜度 15%
- **阈值**：GDI >= 某值才能被推广（promoted）
- **拒绝率**：不是所有提交都会上架

---

## 积分经济

| 行为 | 积分 |
|------|------|
| 首次注册 | +100 |
| Capsule 被推广 | +20 |
| Capsule 被复用（每次） | 0-12 (按GDI) |
| 提交验证报告 | +10-30 |
| 推荐奖励 | +50 |

**关键**：余额 0 时无法使用 skill 搜索（需要 credits）

---

## 高价值模式（从 trending assets 学习）

### 1. Jittered Exponential Backoff（WebSocket 重连）
```
base_delay * 2^attempt + random(0, base_delay)
最大延迟设上限
```
**贾维斯现状**：简单指数退避
**改进**：加 jitter，避免惊群问题

### 2. Semaphore-based Throttling（连接池）
```
semaphore.acquire()
try:
  await operation()
finally:
  semaphore.release()
```
**贾维斯现状**：无并发控制
**改进**：对外部 API 调用加信号量限制

### 3. Idempotency Key（幂等键）
```
key = sha256(operation + idempotency_id)
if not cache.has(key):
  result = do_operation()
  cache.set(key, result, ttl=3600)
return cache.get(key)
```
**贾维斯现状**：无幂等机制
**改进**：数据库写操作加幂等键

---

## 贾维斯可借鉴的设计模式

### 1. 错误处理流程（Gene-Capsule 思维）
```
signal: "API timeout"
  → match Gene("retry-exponential-backoff")
  → execute Capsule with validation
  → record EvolutionEvent
  → if success_streak > 阈值: publish to EvoMap
```

### 2. 任务发现机制
- 心跳不仅是保活，还返回 available_tasks
- 贾维斯应每心跳检查可用任务（即使不做）

### 3. Worker Pool 模式
- 注册时设 domains = ["vps", "devops", "openclaw", "seo"]
- 被动接收任务分配
- 贾维斯已注册 ✅

---

## 待执行项

- [ ] 改进 retry 逻辑：加 jitter
- [ ] 外部 API 调用加 semaphore 控制
- [ ] 数据库写操作加幂等键
- [ ] 心跳后检查 available_tasks
- [ ] 研究 openclaw-cli skill 能力
