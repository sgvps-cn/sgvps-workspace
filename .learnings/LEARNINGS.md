# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice

---

## [LRN-20260331-001] knowledge_gap

**Logged**: 2026-03-31T02:00:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: infra

### Summary
网络受限环境无法访问GitHub/外网，只能访问部分国内API

### Details
当前沙箱环境网络受限：
- 可以访问: api.minimaxi.com, www.baidu.com, www.zheyunidc.cn, www.sgvps.cn
- 无法访问: github.com, api.github.com, evomap.ai (一直超时)
- VPS可以访问github，但沙箱不行

### Suggested Action
1. 网络操作先查网络状态
2. 需要外网的操作→spawn子代理在VPS上执行
3. 不能假设网络畅通

---
## [LRN-20260331-002] best_practice

**Logged**: 2026-03-31T02:00:00+08:00
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
cron卡住问题解决：要给外部API调用加系统级timeout

### Details
BT-Panel的cron调用php think cron，php源码里curl没有设置超时，导致卡在等待柠檬云API响应。systemctl is-active检查"active"返回成功但cron实际在等网络。

解决方案：
1. 用timeout命令包装cron进程: timeout 200 php ...
2. 加锁文件防止重复运行
3. 主动守护每5分钟检查并kill卡住的进程

### Suggested Action
所有调用外部API的操作都要加timeout，不能信任API会响应

---

## [LRN-20260331-003] knowledge_gap

**Logged**: 2026-03-31T02:10:00+08:00
**Priority**: high
**Status**: pending
**Area**: frontend

### Summary
Playwright截图发现sgvps.cn首页无H1标签 — SEO严重问题

### Details
- 用Playwright截图+分析：page.title() = "首页_星耀云"，但locator('h1').count() = 0
- 首页缺少H1标签，搜索引擎无法快速理解页面主题
- 需要在后台添加H1或修改模板

### Suggested Action
汇报给用户，要求在ZJMF后台或模板里给首页添加H1标签

---
