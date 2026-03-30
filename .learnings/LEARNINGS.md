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

## [LRN-20260331-005] knowledge_gap

**Logged**: 2026-03-31T03:20:00+08:00
**Priority**: critical
**Status**: resolved
**Area**: backend

### Summary
sgvps.cn/ZJMF项目深度学习完成

### System Architecture
- **Framework**: ThinkCMF 3.7.6 (ThinkPHP内核) + ionCube加密
- **Frontend**: Vue.js组件化前端 (ZdsjuM1主题)
- **上游**: ZJMF API (柠檬云/折云) 用于服务器开通和库存同步
- **数据库**: MySQL 175张表
- **授权**: ionCube Loader 加密所有核心PHP文件

### Key Tables
- shd_products / shd_product_groups: 产品配置
- shd_host: 已开通的服务器
- shd_orders: 订单
- shd_ticket: 工单
- shd_clients: 客户
- shd_configuration: 全局配置
- shd_seo_settings: SEO设置(通过seo()函数读取)
- shd_menu / shd_menus: 导航菜单

### SEO标题问题根因
- 数据库title: "星耀云 - 专业云服务器IDC服务商"
- 实际显示: "首页_星耀云"
- 原因: header.html模板用 `{$seo.ymbt}` 或 `[title]_{$setting.company_name}`
- `[title]`是后台"页面标题"配置项
- 首页[title]在后台显示为"首页"
- 解决方案: 后台修改"首页"页面标题，或通过zdsju.php的seo()函数返回值修改

### 可安全修改的部分
1. 模板文件: /www/wwwroot/www.sgvps.cn/public/themes/web/ZdsjuM1/*.html
2. CSS: themes/web/ZdsjuM1/style/css/
3. JS: themes/web/ZdsjuM1/style/js/
4. banner/广告图片: /www/wwwroot/www.sgvps.cn/upload/
5. 数据库配置: shd_configuration表

### 不能修改的部分(加密)
- 所有app/home/controller/*.php
- app/common.php
- app/zjmf.php
- app/zdsju.php

### 二次开发限制
- ionCube加密=无法安全二次开发核心逻辑
- 只能做模板修改+数据库配置
- 如果需要深度定制，需联系ZJMF官方

---

## [LRN-20260331-006] knowledge_gap

**Logged**: 2026-03-31T05:50:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: infra

### Summary
Clash深度学习完成

### System Info
- 版本: Clash n2023-09-05-gdcc8d87 (Go 1.21.0)
- 配置文件: /root/clash/config.yaml
- 运行端口:
  - 7890: HTTP代理 ✅
  - 7891: SOCKS5代理 ✅  
  - 7892: RedirPort (未监听，透明代理未配置)
  - 9090: Clash控制API (RESTful) ✅
- 控制口认证: 123456:123456

### 代理节点清单
共59个节点，包括:
- 🇭🇰 香港: 11个 (IEPL专线/x0.8折扣/下载专用)
- 🇯🇵 日本: 11个 (IEPL专线/免费节点/下载专用)
- 🇸🇬 新加坡: 3个 (IEPL专线/x2倍率)
- 🇺🇲 美国: 2个 (IEPL专线/x1.5倍率)
- 其他: 台湾/英国/阿根廷/俄罗斯/土耳其/韩国/印度/德国/加拿大/澳大利亚/法国/乌克兰

### 代理组配置
| 组名 | 类型 | 说明 |
|---|---|---|
| GLOBAL | Selector | 手动选择节点 |
| Auto | URL Test | 自动选最快节点 |
| 国内网站 | Selector | 国内站点直连 |
| 漏网之鱼 | Selector | 未匹配流量 |
| 学术网站 | Selector | 学术资源代理 |
| ☁️ OneDrive | Selector | OneDrive专用 |
| 🎮 Steam | Selector | Steam下载/商店 |
| 🌏 爱奇哩哔哩 | Selector | 视频网站 |

### Control API (端口9090)
通过 `curl -u "123456:123456" http://127.0.0.1:9090/{endpoint}` 调用

可用端点:
- GET /proxies - 所有代理信息
- GET /proxies/{name} - 单个代理详情
- PUT /proxies/{name} - 切换代理 (需是Selector类型)
- GET /providers/proxies - 提供商快照
- GET /configs - 当前配置
- PUT /configs - 更新配置

### 实际用途
1. 我可以用API动态切换代理节点
2. 可以自动测试节点延迟并选最优
3. 可以给不同流量自动分配不同代理
4. HTTP代理(7890)已可用，SOCKS5(7891)也通

### 待解决问题
- 7892 RedirPort未监听，无法做Linux系统级透明代理
- 系统环境变量无proxy设置（无需设置，走我配置的代理）

---
