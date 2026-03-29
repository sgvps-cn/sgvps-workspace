# SGOVPS_CN.md - 星耀云深度知识库

## 网站基本信息
- **域名**: www.sgvps.cn
- **公司**: 星耀云
- **成立**: 2015年
- **注册资金**: 1000万
- **资质**: ISP证、IDC证、云牌照
- **客服**: 400呼叫中心、QQ/微信、6X12小时全年响应

## 产品线

### 1. 企业云服务器
- 定位: 标准云服务器，面向企业
- 特点: 网络稳定、高速读写

### 2. 高防云服务器
- 定位: 抗DDoS/CC攻击
- 防御: 单机50-200G
- 架构: KVM虚拟化
- 适合: 游戏、金融、政务

### 3. 外贸云服务器
- 定位: 外贸企业
- 网络: 国际BGP、CN2优质线路

### 4. 裸金属物理机
- 定位: 高性能物理机
- 特点: 独享性能，无虚拟化损耗

### 5. 其他产品
- 虚拟主机
- CDN加速
- 云电脑

## 技术架构

### 前端
- 框架: Element UI + jQuery
- 类型: 动态加载（疑似Vue/React SPA）

### 后端/CDN
- CDN: Alibaba Cloud (a1.initac.com)
- IP段: 220.181.141.x (阿里云北京节点)
- SSL: TLC DV TLS CA (有效期至2026-11-11)

### 数据中心
- 节点: 北京、广州、湖北、四川、江苏、辽宁、内蒙古、香港
- 带宽: 多线BGP
- 运维: 7x24现场维护

## 安全配置

### 当前服务器安全状态
- SSH端口: 22 (待改)
- 密码登录: 开启 (高危)
- Fail2Ban: 已运行
- BBR: 已启用 ✅
- nftables: 已配置 ✅
- 开放端口: 22,80,443,18789,22036

### 安全建议
1. 禁用SSH密码登录（需公钥）
2. 改SSH端口为非标准
3. 启用自动安全更新
4. 配置入侵检测

## 监控体系

### 现有监控
- cloud-monitor-agent (云监控Agent)
- BT-Panel 宝塔面板
- Fail2Ban (SSH防护)

### 已建立监控
- sgvps.cn可达性监控 (每小时)
- SSL证书到期监控
- 响应时间监控
- DNS解析监控

## 已安装相关技能

| 技能 | 用途 |
|---|---|
| vps-maintenance | VPS初始化、安全加固、性能优化 |
| host-hardening | SSH加固、防火墙、fail2ban |
| monitoring | 监控体系建立(metrics/logs/traces) |
| docker-manager | 容器管理(查看/启停/日志) |
| docker-essentials | Docker优化(分层缓存等) |

## 运维知识

### 常用端口
- SSH: 22 (默认)
- HTTP: 80
- HTTPS: 443
- OpenClaw: 18789
- BT-Panel: 22036

### 关键路径
- 网站根目录: /www/wwwroot/www.sgvps.cn
- OpenClaw: /root/.openclaw
- 宝塔: /www/server/panel

### 性能基线(当前)
- CPU: 14.7% (Evolver进程)
- 内存: 3.8GB total, 1.7GB used (45%)
- 磁盘: 40GB total, 12GB used (32%)
- 网络: 阿里云CDN

## 待完成项
- [ ] SSH密码登录禁用（需用户提供公钥）
- [ ] SSH端口改为非标准
- [ ] 配置自动备份策略
- [ ] 建立客户网站监控体系
- [ ] Docker容器化部署调研
