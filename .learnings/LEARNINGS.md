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

## [LRN-20260331-004] knowledge_gap

**Logged**: 2026-03-31T02:45:00+08:00
**Priority**: critical
**Status**: pending
**Area**: frontend

### Summary
SEO深度学习: sgvps.cn 首页标题只有6字符"首页_星耀云"

### Details
通过学习seo skill的on-page.md后发现:
- Title应50-60字符，需含关键词
- sgvps.cn首页标题"首页_星耀云"仅6字符，严重浪费SEO机会
- 应改为: "星耀云 - 云服务器/高防服务器/海外服务器托管 | 持牌IDC"
- 描述110字符，在合理范围(150-160)
- Canonical URL缺失 — 所有页面都应该有canonical标签

### Technical SEO学习清单:
1. Core Web Vitals: LCP<2.5s, INP<200ms, CLS<0.1
2. TTFB目标<200ms (sgvps.cn当前309ms需优化)
3. HSTS已设置 ✅
4. Viewport ✅
5. 图片Alt: 7/8缺失 ❌
6. robots.txt ✅
7. sitemap ✅
8. 无JS错误 ✅

### On-Page SEO学习清单:
1. Title长度50-60字符，关键词放前30
2. H1只能有1个 ✅(已修复)
3. H2-H6层次分明
4. 图片Alt描述性文字
5. Canonical self-referencing

### Content SEO:
- ZJMF无博客系统，需独立WordPress
- 问答FAQ schema可提升CTR

### Suggested Action
修复首页标题(后台ZJMF或代码修改)

---
