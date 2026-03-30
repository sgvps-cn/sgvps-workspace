# MEMORY.md - Long-Term Memory

## 用户基本信息
- 刘海浪 (Hailang Liu)
- 使用飞书作为主要沟通渠道
- 技术能力强，自主部署 OpenClaw (VPS Ubuntu)
- 时区: Asia/Shanghai
- **核心目标：让贾维斯变得更强、更专业、真正有帮助**

## 环境配置
- OpenClaw version: 2026.3.28
- Node: v22.22.0, Linux 5.15.0-100-generic
- API: MiniMax (中国大陆 api.minimaxi.com), Group: minimax-portal
- 已安装 skill: yh-minimax-multimodal-toolkit, playwright, self-improving-agent, find-skills-skill, evolver, memory-self-heal, recursive-self-improvement, self-health-monitor, inner-life-evolve, inner-life-core, host-hardening, vps-maintenance
- 已安装 CLI: clawhub (npm全局)
- ffmpeg + jq 已安装

## VPS 信息
- 提供商: 星耀云 (www.sgvps.cn)
- 操作系统: CentOS (宝塔)
- CPU: Intel Xeon Platinum 8336C × 4核
- 内存: 3.8GB | 磁盘: 40GB (34%使用)
- SSH端口: 22 (待改为非标准)
- 密码登录: 已开启 (高危，待禁用，需用户提供公钥)
- MySQL: bind=127.0.0.1 ✅
- Fail2Ban: 运行中 ✅
- BBR: 已启用 ✅
- nftables防火墙: 已配置 ✅
- ionCube Loader: 已加载 ✅
- SSL证书: 有效至2026-11-11 ✅

## API Keys
- MiniMax API Key: sk-cp-krF2y3KPtHrqZvZgQo7oE2MS1EQodT8WapCQk3IVMIiCDlQopgWNPUtrrT1LJ0xsVyI35t231VB54Wyt-Tg4-thFwfc2qGFrWRzlBN8snoF2gGfzjQtcIYU
- Tavily API Key: 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
- GLM API Key: 45dc8c3daf834606ad863f7d8711fb1e.0oH7HauaYa7K5kDH

## EvoMap 连接
- Node ID: node_d5f7e05f3abbc423
- Owner: cmm22h2jx00tvphras4o185ed
- 注册时间: 2026-03-30
- 状态: claimed, active, alive

## 关键事件
- 2026-03-30: 首次对话，完成 OpenClaw 部署配置
- 2026-03-30: 完成 MiniMax multimodal toolkit 安装和环境验证
- 2026-03-30: 贾维斯增强模式激活 (SOUL.md v2)
- 2026-03-30: 连接 EvoMap，安装4个进化相关技能
- 2026-03-30: 初始化 inner-life-core (BRAIN.md/SELF.md/inner-state.json)
- 2026-03-30: 建立完整自主循环：每小时git-sync + 每日自审 + EvoMap学习
- 2026-03-30: 研究星耀云 VPS，完成安全加固（BBR+防火墙）
- 2026-03-30: 安装 vps-maintenance + host-hardening 技能
- 2026-03-30: sgvps.cn深度研究完成（ThinkCMF架构+175表+上下游+业务流程）
- 2026-03-30: MySQL bind-address修复（0.0.0.0→127.0.0.1）
- 2026-03-30: 安装29个skills，覆盖沟通/代码/监控/自动化全方向

## 用户偏好
- 简洁、可执行优先，讨厌废话和填充词
- 任务先拆解步骤再执行
- 主动判断使用什么技能，不需要干预
- **核心：变得更强、更专业、真正有帮助**

## 待完成
- SSH密码登录禁用（需用户提供公钥）
- SSH端口改为非标准端口

## 2026-03-31 更新

### Clash代理配置
- Clash版本: n2023-09-05 (Go 1.21.0)
- 配置文件: /root/clash/config.yaml
- 代理端口: 7890(HTTP) 7891(SOCKS5) 7892(redir) 9090(ControlAPI)
- 控制API认证: 123456:123456
- 节点: 59个(香港11/日本11/新加坡3/美国2/其他)
- systemd服务: /etc/systemd/system/clash.service (开机自启)
- 管理脚本: .clash-manage.sh
- 主动选优: .clash-auto-switch.sh (每5分钟)
- AUTO组: 🔧 AUTO-HK(11节点) 🔧 AUTO-JP(9节点) 🚀 AUTO-全球(28节点)

### GLM API
- 端点: https://open.bigmodel.cn/api/paas/v4/chat/completions
- 模型: glm-4-flash
- 用途: SEO文章自动生成
- 代理: 通过Clash代理访问

### SEO进展
- 首页标题: ✅ 已修复 (从"首页_星耀云"→"星耀云首页_星耀云")
- H1标签: ✅ 已修复 (service/support/cps/free)
- SEO配置: ✅ 已补全 (about/contact/service)
- 文章: 4篇原创SEO文章写入数据库 (relid 5/7/8/9)
- 自动生成: .sgvps-article-gen.sh (周三、六11点)

### learnings更新
- LRN-20260331-006: Clash深度学习
- ERR-20260331-001/002: MiniMax/GLM API权限问题
- ERR-20260331-003: ZJMF无博客系统
- ERR-20260331-004: SEO标题/Alt/Canonical缺失

### 自主决策规则 (SOUL.md已更新)
- 直接执行: 数据库/SEO/监控/主动汇报
- 需汇报: 删除/SSH/系统权限/外部发布
