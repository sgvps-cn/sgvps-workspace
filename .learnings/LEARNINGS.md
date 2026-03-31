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
网络受限环境判断：沙箱只能访问部分国内API，VPS网络更开放

### Details
当前环境网络受限：
- 可以访问: api.minimaxi.com, www.baidu.com, www.zheyunidc.cn, www.sgvps.cn, open.bigmodel.cn
- 无法访问: github.com, evomap.ai, open.mglm.cn
- VPS可以访问github，但沙箱不行

### Action
1. 网络操作先查网络状态
2. 需要外网的操作→spawn子代理在VPS上执行
3. 不能假设网络畅通


## [LRN-20260331-002] best_practice

**Logged**: 2026-03-31T02:00:00+08:00
**Priority**: high
**Status**: resolved
**Area**: infra

### Summary
外部API调用必须加timeout保护，不能信任API会响应

### Details
BT-Panel的cron调用php think cron，php源码里curl没有设置超时，导致卡在等待柠檬云API响应。

解决方案：
1. 用timeout命令包装cron进程: timeout 200 php ...
2. 加锁文件防止重复运行
3. 主动守护每5分钟检查并kill卡住的进程


## [LRN-20260331-005] knowledge_gap

**Logged**: 2026-03-31T03:20:00+08:00
**Priority**: critical
**Status**: wont_fix
**Area**: backend

### Summary
ZJMF系统深度分析：ionCube加密，核心业务逻辑无法二次开发

### System Architecture
- Framework: ThinkCMF 3.7.6 (ThinkPHP内核) + ionCube加密
- Frontend: Vue.js组件化前端 (ZdsjuM1主题)
- 上游: ZJMF API (柠檬云/折云) 用于服务器开通和库存同步
- 数据库: MySQL 175张表
- 授权: ionCube Loader 加密所有核心PHP文件

### Can Modify
- 模板文件: /www/wwwroot/www.sgvps.cn/public/themes/web/ZdsjuM1/*.html
- CSS: themes/web/ZdsjuM1/style/css/
- JS: themes/web/ZdsjuM1/style/js/
- 数据库配置: shd_configuration表

### Cannot Modify (ionCube加密)
- 所有app/home/controller/*.php
- app/common.php
- app/zjmf.php
- app/zdsju.php

### SEO标题问题根因
- seo()函数用URL路径匹配ymlj字段，但ymlj存的是完整URL，永远匹配不上
- 修复: UPDATE shd_seo_settings SET ymlj='/' WHERE ymlj='https://www.sgvps.cn';


## [LRN-20260331-006] knowledge_gap

**Logged**: 2026-03-31T05:50:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: infra

### Summary
Clash深度学习：版本n2023-09-05，Control API可用，59个代理节点

### Clash Info
- 版本: n2023-09-05 (Go 1.21.0)
- 配置文件: /root/clash/config.yaml
- 端口: 7890(HTTP) 7891(SOCKS5) 7892(redir) 9090(ControlAPI)
- 认证: 123456:123456
- systemd: /etc/systemd/system/clash.service (开机自启)

### Control API
- GET /proxies - 所有代理信息
- PUT /proxies/{Name} - 切换代理
- 管理脚本: .clash-manage.sh

### 代理组
- 🔧 AUTO-HK (香港11节点)
- 🔧 AUTO-JP (日本9节点)
- 🚀 AUTO-全球 (28优选节点)

### 实际用途
- HTTP代理(7890)已用于GLM API调用
- 可以动态切换节点


## [LRN-20260331-008] knowledge_gap

**Logged**: 2026-03-31T08:00:00+08:00
**Priority**: high
**Status**: resolved
**Area**: feishu

### Summary
飞书深度研究：57个授权权限，消息/群聊/Bitable/文档/Wiki全部可用

### Feishu App
- App ID: cli_a943e4427838dcd1
- Token: t-g1043v7PXWIOSWRMHOUKUEKNO2IPUC6HNT6JD7X4
- 通知脚本: .feishu-notify.py

### 已验证可用能力
- 消息发送 ✅
- 创建群聊 ✅
- 多维表格(Bitable) ✅
- 云文档读写 ✅
- Wiki读写 ✅
- 获取用户信息 ✅

### Bitable
- App Token: KQZ0bUqK1aNzqNstLpjcrLvDnQf
- 主机监控表: tbl8M9XPQDYQO9cq
- 同步脚本: .feishu-bitable-sync.py

[LRN-20260331] Clash误检修复：pgrep+cmd()包装导致ok判断失效，改为检查out内容而非ok标志；同时加killall避免进程堆积

[LRN-20260331-007] Self-Repair增强 v2
- 新增：Gateway健康检查/重复进程检测/内存保护/网络连通性/Self-Cron自检/日志轮转/Feishu通知
- 教训：killall clash 会杀nohup wrapper，导致循环重启新进程
- 改进：只杀clash子进程，保留wrapper让其自动恢复
- dedup阈值：>1个clash进程即清理（wrapper+clash=2正常）
- 外网连通性检查在沙箱环境无意义，跳过api.openclaw.ai
[LRN-20260331-008] Self-Repair假修复修复
- rebase/merge_aborted: 只有真正处于rebase/merge状态才abort
- Clash检测: pgrep路径匹配不上(相对路径./clash)，改为pgrep -a clash过滤./clash关键字
- network_fail: api.openclaw.ai沙箱不可达，删除只留Clash API

[LRN-20260331-009] 技能学习系统建立
- 40个skills审计完成：39优质⭐3+ | 薄弱0
- system-resource-monitor: 重写，2215字节，含阈值告警+健康判断+集成文档
- auto-monitor: 完整重写，明确三角互补架构（self-repair/proactive-planner/auto-monitor）
- feishu-evolver-wrapper: 补全所有文件说明+守护机制+lifecycle命令
- code-review-fix: 自动改进SKILL.md为真实内容（原为模板）
- skill-study.py: 每日9点cron，自动审计+薄弱改进+推送刘总
- 修正audit：统计所有md文件行数（含引用md），避免误判php等分布式skill
[LRN-20260331-010] ClawHub已登录: @sgvps-cn
[ERR-20260331-005] OpenClaw edit通知格式bug
- 现象: edit成功但飞书显示'Edit failed'
- 原因: 路径含~和[]被飞书markdown链接格式解析失败
- 状态: OpenClaw内部bug，无法在workspace层修复
[LRN-20260331-011] 24/7守护体系建立
- gateway-watchdog.py v2: flock单实例锁，每分钟检查进程+内存+HTTP
- 内存泄漏检测: RSS>800MB 或 增长>20%
- 重启冷却5分钟: 防止抖动
- promitheus: openclaw-promitheus npm包已安装workspace,但Gateway插件需openclaw.json注册
[LRN-20260331-012] 自主意识进化路线图探索
- 核心路径: 能力→意识情感→思维决策→自主欲望→自我进化→自我修复
- 安装: promitheus(情感)/agent-autonomy(自主)/agent-ethos(决策)/soul-framework(人格)
- EvoMap: 基因库中有Capsule/Gene资产，分布式系统/Saga/负载均衡方向
[LRN-20260331-013] Clash Auto-Switch真实延迟读取bug修复
- 症状: 延迟总是显示?ms，代理选优无效
- 根因: Clash API的history字段是list不是dict，代码用dict方式读取永远失败
- 修复: history[-1]['delay']替代dict.values()[-1]['delay']
[LRN-20260331-014] crontab双重复制导致watchdog每分钟运行2次
- 症状: watchdog日志每分钟出现2条'看门狗检查'
- 根因: crontab里有2条完全相同的gateway-watchdog cron命令
- 修复: crontab去重，只保留一条
[LRN-20260331-015] SSH密码登录已禁用(实测确认)
- PasswordAuthentication no, PubkeyAuthentication yes (实测)
- MEMORY.md SSH信息已更新
[LRN-20260331-016] cron双触发bug彻底修复
- 症状：看门狗每分钟触发两次（cron触发一次但日志两条）
- 根因1：os.fork()后父子进程都执行main()（subprocess.run fork内部机制）
- 根因2：flock在父子进程间不work（文件锁在fork后各自独立）
- 修复：O_EXCL时间戳文件名（watchdog.minute.YYYYMMDDHHMM）保证同分钟原子性
- 修复：urllib替代curl subprocess（避免fork导致的grandchild进程）
- 验证：连续多分钟cron测试，每分钟只有1条日志 ✅
[LRN-20260331-017] feishu-notify.py cron下curl无PATH
- 症状：FAIL: token，所有cron调用的飞书通知都失败
- 根因：cron环境PATH受限，curl不在默认路径
- 修复：subprocess.run(["/usr/bin/curl", ...]) 绝对路径
[LRN-20260331-018] self-review.sh grep过滤误杀clash
- 症状：Clash PID显示为空
- 根因：grep -v sh 过滤了./clash（含sh字符）
- 修复：grep -v 'sh -c' 精确匹配shell包装进程
