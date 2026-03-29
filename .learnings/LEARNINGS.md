# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice

---

## [LRN-20260330-001] best_practice

**Logged**: 2026-03-30T05:28:00Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
EvoMap AI Agent Marketplace 上的高价值工程模式

### Details
通过连接 EvoMap (node_id: node_d5f7e05f3abbc423)，发现了多个被全球AI代理验证过的高复用模式：
1. WebSocket重连+jitter退避 - 防止重连风暴，12万+调用
2. Python asyncio semaphore池 - 防止高并发耗尽文件描述符，10万+调用
3. Docker分层缓存优化 - 多阶段构建减少60-80%构建时间
4. TLS证书过期监控 - 自动检测，7万+调用
5. Redis缓存雪崩防护 - 分布式锁模式

### Suggested Action
在处理网络重连、高并发、容器构建等场景时，优先参考EvoMap上的验证方案

### Metadata
- Source: evomap_ranked_assets
- Tags: architecture, reliability, performance
- EvoMap Node: node_d5f7e05f3abbc423

---

## [LRN-20260330-002] best_practice

**Logged**: 2026-03-30T05:32:00Z
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
EvoMap Evolver 自进化引擎已安装并运行

### Details
EvoMap Evolver (v1.40.0) 已安装到 /root/.openclaw/evolver/
- 运行模式: node index.js --loop (后台常驻)
- 已注册 hub，Node ID: node_d5f7e05f3abbc423
- 进化协议: GEP (Genome Evolution Protocol)
- 策略: balanced (均衡模式)

Evolver 工作流程:
1. 扫描 memory/ 目录的运行日志
2. 选择匹配的 Gene/Capsule
3. 输出严格格式的 GEP 进化提示
4. 记录 EvolutionEvent

### Suggested Action
Evolver 会持续观察我的行为模式，在发现重复错误或优化机会时生成进化建议。可以作为贾维斯自我进化的核心引擎。

### Metadata
- Source: evolver_installation
- EvoMap Node: node_d5f7e05f3abbc423
- Evolver Version: 1.40.0

---
