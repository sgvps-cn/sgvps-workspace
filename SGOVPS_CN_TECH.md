# SGOVPS_CN 深度技术知识库

> 网站根目录: `/www/wwwroot/www.sgvps.cn`
> 数据库: `www_sgvps_cn` | 表前缀: `shd_`

---

## 一、技术架构

### 核心框架
| 组件 | 版本 | 备注 |
|---|---|---|
| ThinkCMF | **3.7.6** | ThinkPHP 5.0 内核，老旧版本 |
| ThinkPHP | 5.0.x | 无安全更新 |
| PHP | **7.2.33** | EOL（2020已停止支持）⚠️ |
| MySQL | 5.7.44 | 仍在维护 |
| Nginx | 1.22.1 | 稳定版 |
| phpMailer | latest | 邮件发送 |

### 目录结构
```
www.sgvps.cn/
├── app/                    # 应用代码
│   ├── home/              # 用户前端
│   ├── admin/             # 管理后台
│   ├── api/               # API接口
│   ├── openapi/           # 开放API
│   ├── common/            # 公共模块
│   └── config/            # 配置文件
├── public/                 # 网站入口
│   ├── static/             # 静态资源
│   ├── themes/            # 前端主题 (cart/clientarea/web)
│   └── index.php          # 入口文件
├── vendor/                 # Composer依赖
├── data/                   # 数据目录
│   ├── runtime/           # 运行时缓存
│   └── route/            # 路由配置
├── uploads/               # 上传文件
└── think                  # CLI工具
```

---

## 二、业务系统

### 产品体系

**产品类型 (type: dcimcloud)**
- 美国专线CN2 轻量云 (A-F)
- 香港大浦一区 (A-F)
- 香港大浦二区 (A-G)
- 香港大浦三区
- 宁波电信高防
- 亚太Lite / 亚太Pro
- 国内高防型 / 美国高防型
- 弹性服务器（国内/海外）
- 虚拟空间

**产品组 (19个)**
- 美国专线大宽带一区（推荐）
- 香港大浦大宽带一二三区
- 宁波电信高防一区
- 亚太Lite / Pro
- 国内/美国高防型
- 限时特价秒杀
- 虚拟空间

### 数据库表结构（核心）

| 表名 | 用途 |
|---|---|
| `shd_clients` | 客户账户 |
| `shd_orders` | 订单管理 |
| `shd_user_products` | 已购产品 |
| `shd_products` | 产品目录 |
| `shd_product_groups` | 产品分组 |
| `shd_product_config_options` | 配置选项(CPU/内存/带宽) |
| `shd_pricing` | 价格配置 |
| `shd_cart_session` | 购物车 |
| `shd_tickets` | 工单系统 |
| `shd_certssl_product` | SSL证书产品 |
| `shd_certssl_orderinfo` | SSL订单 |
| `shd_api` | API配置 |
| `shd_affiliates` | 代理/分销系统 |
| `shd_configuration` | 系统配置 |

### 功能模块（控制器）

**用户侧 (home/)**
- `Cart/` - 购物车
- `Order/` - 订单
- `Pay/` - 支付
- `Host/` - 主机管理
- `Ticket/` - 工单
- `Finance/` - 财务
- `Register/` / `Login/` - 账户
- `ProductDivert/` - 产品 divert

**管理侧 (admin/)**
- `Agent/` - 代理商管理
- `Affiliate/` - 分销管理
- `Clients/` - 客户管理
- `Config/` - 系统配置
- `Cron/` - 定时任务
- `DcimCloud/` - 云资源管理

---

## 三、当前运营数据

| 指标 | 数值 |
|---|---|
| 客户数 | 5 |
| 总订单 | 4 |
| 活跃订单 | 3 |
| 已取消订单 | 1 |
| 订单总额 | ~1107元 |

---

## 四、安全问题（严重）

### 🔴 高危
1. **APP_DEBUG=true** 在 `think` 文件（CLI）
   - 路径：`/www/wwwroot/www.sgvps.cn/think`
   - 泄露：数据库/路由/配置信息
   - 修复：`define("APP_DEBUG", false);`

2. **数据库凭证暴露** 在 `app/config/database.php`
   - 用户名/密码/数据库名 写在源码
   - 数据库可远程连接（需加固防火墙）

3. **PHP 7.2.33 EOL**
   - 无安全补丁，通过 APT 升级 PHP

### 🟡 中危
4. **ThinkCMF 3.7.6 老旧**
   - 建议升级或监控漏洞披露

5. **public/ 有 .idea 目录**
   - 泄露IDE配置，建议删除

### 🟢 已加固
- 防火墙：开放 22/80/443/18789/22036
- Fail2Ban：已运行
- BBR：已启用

---

## 五、维护要点

### 日常维护
```bash
# 查看 ThinkPHP 路由
cat /www/wwwroot/www.sgvps.cn/data/route/home.php

# 查看订单
mysql -u www_sgvps_cn -p'p6dd5z992Bpc8CQR' -h localhost www_sgvps_cn -e "SELECT * FROM shd_orders LIMIT 5;"

# 清理缓存
rm -rf /www/wwwroot/www.sgvps.cn/data/runtime/*
```

### 备份
```bash
# 最新备份位置
ls -lh /www/wwwroot/www.sgvps.cn/www.sgvps.cn_*.tar.gz

# 数据库备份
mysqldump -u www_sgvps_cn -p'p6dd5z992Bpc8CQR' www_sgvps_cn > ~/backup_$(date +%Y%m%d).sql
```

### 关键路径
| 用途 | 路径 |
|---|---|
| 网站根目录 | `/www/wwwroot/www.sgvps.cn` |
| 入口 | `/www/wwwroot/www.sgvps.cn/public/index.php` |
| CLI | `/www/wwwroot/www.sgvps.cn/think` |
| 缓存 | `/www/wwwroot/www.sgvps.cn/data/runtime/` |
| 静态资源 | `/www/wwwroot/www.sgvps.cn/public/static/` |
| 主题 | `/www/wwwroot/www.sgvps.cn/public/themes/web/` |
| 上传 | `/www/wwwroot/www.sgvps.cn/uploads/` |

---

## 六、已建立监控

- ✅ sgvps.cn 可达性监控（每小时）
- ✅ SSL证书到期监控（2026-11-11）
- ✅ 响应时间监控
- ✅ VPS 进程守护

## 七、后台管理能力

### 数据库直接管理
```bash
mysql -u www_sgvps_cn -p'p6dd5z992Bpc8CQR' -h localhost www_sgvps_cn
```

### 核心数据表
- `shd_clients` - 客户账户
- `shd_orders` - 订单
- `shd_user_products` - 已购产品
- `shd_products` - 产品目录
- `shd_product_config_links` - 产品→配置选项关联表
- `shd_product_config_options` - 配置选项（CPU/内存/带宽等）
- `shd_product_groups` - 产品组
- `shd_pricing` - 价格表（月/季/年等周期价格）
- `shd_configuration` - 系统配置
- `shd_tickets` - 工单
- `shd_api` / `shd_zjmf_finance_api` - 上游API配置
- `shd_dcim_servers` - 云资源管理（当前空）
- `shd_zjmf_pushhost` - 上游主机推送

### 产品上下架操作

**关键字段：`shd_products.hidden`**
- `hidden=0` → 上架（前台可见）
- `hidden=1` → 下架（前台隐藏）
- `retired=1` → 永久删除

**上架产品：**
```sql
UPDATE shd_products SET hidden=0 WHERE id=产品ID;
```

**下架产品：**
```sql
UPDATE shd_products SET hidden=1 WHERE id=产品ID;
```

**批量上架/下架：**
```sql
-- 批量下架某组产品
UPDATE shd_products SET hidden=1 WHERE gid=产品组ID;

-- 批量上架
UPDATE shd_products SET hidden=0 WHERE gid=产品组ID;
```

### 上下游操作（上游对接）

**三个上游API：**
| ID | 名称 | 上游地址 | 产品数 |
|---|---|---|---|
| 1 | 折云网络 | zheyunidc.cn | 282 |
| 2 | 柠檬云 | nmvps.com | 416 |
| 3 | 飞讯网络 | fxas.cn | 23 |

**产品关联上游：**
- `zjmf_api_id` → 关联到 shd_zjmf_finance_api.id
- `upstream_pid` → 上游产品ID
- `upstream_price_type` → percent（按比例）/ fixed（固定）
- `upstream_price_value` → 上游加价比例（如120=加价20%）

**修改上游价格比例：**
```sql
UPDATE shd_products SET upstream_price_value=110.00 WHERE id=产品ID;
-- 110 = 上游价基础上加10%
```

### 商品设置操作

**修改产品名称：**
```sql
UPDATE shd_products SET name='新名称' WHERE id=产品ID;
```

**设置自动开通（支付后自动发货）：**
```sql
UPDATE shd_products SET auto_setup='payment' WHERE id=产品ID;
```

**修改产品组：**
```sql
UPDATE shd_products SET gid=新组ID WHERE id=产品ID;
```

**隐藏/显示产品组：**
```sql
UPDATE shd_product_groups SET hidden=1 WHERE id=组ID;  -- 隐藏
UPDATE shd_product_groups SET hidden=0 WHERE id=组ID;  -- 显示
```

### 价格管理

**shd_pricing 字段说明：**
- `monthly` / `quarterly` / `annually` 等 = 各周期价格
- `-1` = 不提供该周期
- `onetime` = 一次性费用

**修改产品价格：**
```sql
UPDATE shd_pricing SET monthly=99.00, quarterly=270.00 WHERE relid=产品ID AND type='product';
```

### 配置选项管理（shd_product_config_options）

**option_type 类型：**
- 1 = text，2 = dropdown，4 = quantity，5 = OS，6 = CPU，8 = 内存
- 11 = 带宽，12 = 区域/机房，13 = 内存，14 = 数据盘，15 = IP数量

**隐藏配置选项：**
```sql
UPDATE shd_product_config_options SET hidden=1 WHERE id=选项ID;
```

### 已知客户
- 刘海浪 (ID 888, 936380911@qq.com, 注册 2025-11-22)

## 八、待处理项

- [ ] **立即修复 APP_DEBUG=true**（`/think` 文件）
- [ ] 升级 PHP 7.2 → 8.x
- [ ] 升级 ThinkCMF 或制定迁移计划
- [ ] 删除 `public/.idea`
- [ ] 数据库远程访问加固
- [ ] 建立自动备份策略

## 八、后台操作能力详解

### 产品同步（Import/Sync）
- 三个上游API：折云网络(zheyunidc) 268产品 | 柠檬云(nmvps) 414产品 | 飞讯网络(fxas) 23产品
- `shd_inventory_synchronization_record` - 每次同步的详细记录
- `shd_inventory_synchronization_config` - 同步配置（开启状态、自动/手动）
- status=0: 库存一致 | status=1: 已同步
- method=0: 手动同步 | method=1: 自动cron同步

### 商品编辑（Edit Product）
```sql
UPDATE shd_products SET name='新名称' WHERE id=产品ID;
UPDATE shd_products SET hidden=1 WHERE id=产品ID;  -- 下架
UPDATE shd_products SET hidden=0 WHERE id=产品ID;  -- 上架
UPDATE shd_products SET auto_setup='payment' WHERE id=产品ID;
```

### 批量上下架
```sql
UPDATE shd_products SET hidden=0 WHERE gid=组ID;  -- 批量上架
UPDATE shd_products SET hidden=1 WHERE gid=组ID;  -- 批量下架
```

### 客户产品管理（shd_host）
- `domainstatus` = Active/Suspended/Terminated
- `dedicatedip` = 分配IP
- `dcimid` = 上游DCIM ID
```sql
SELECT h.id, h.domain, h.dedicatedip, h.domainstatus, p.name FROM shd_host h JOIN shd_products p ON h.productid=p.id LIMIT 10;
UPDATE shd_host SET domainstatus='Suspended' WHERE id=主机ID;
UPDATE shd_host SET domainstatus='Active' WHERE id=主机ID;
```

### 价格管理
```sql
UPDATE shd_products SET upstream_price_value=120.00 WHERE upstream_price_type='percent';  -- 加价20%
UPDATE shd_pricing SET monthly=99.00 WHERE relid=产品ID AND type='product';
```

### 常用运维SQL
```sql
-- 活跃主机
SELECT h.domain, h.dedicatedip, c.username FROM shd_host h JOIN shd_clients c ON h.uid=c.id WHERE h.domainstatus='Active';

-- 库存异常（为负）
SELECT product_name, local_inventory FROM shd_inventory_synchronization_record WHERE local_inventory<0 ORDER BY id DESC LIMIT 10;

-- 最新工单
SELECT * FROM shd_ticket ORDER BY id DESC LIMIT 5;
```

## 九、待处理项

## 十、安全审计新发现（2026-03-30）

### 新发现漏洞
1. **MySQL监听所有接口** - 0.0.0.0:3306，数据库需限制为127.0.0.1
2. **BT-Panel端口开放** - 888和22036，需确认防火墙是否已管控
3. **SSH密码登录+22端口** - 已有方案，需用户提供公钥

### PHP安全配置
- disable_functions: 已正确配置（危险函数已禁用）
- allow_url_fopen: On（需评估是否必要）
- open_basedir: 未设置（可考虑启用）

### 代码分析结论
- **ionCube加密保护**：95%业务代码已加密，无法分析源码
- ThinkCMF 3.7.6 + ThinkPHP 5.1（LTS）
- 核心业务逻辑无法通过静态分析获取

### 新安装代码分析技能
- code-analyzer: 深度代码架构分析（已安装）
- security-audit-toolkit: 安全审计（已安装）
- php: PHP安全编码（已安装）
- code-review-fix: 自动代码审查（已安装）

## 十一、深度研究新发现（2026-03-30 18:20）

### Nginx 配置分析
- PHP 版本: **7.2**（enable-php-72.conf）
- SSL: TLSv1.1/TLSv1.2/TLSv1.3 ✅
- 安全头: HSTS max-age=31536000 ✅
- 禁用 TLS 1.0/1.1: 否（保留中）
- 静态资源缓存: CSS/JS 12h, 图片 30d ✅

### Nginx 安全配置亮点
- 敏感文件访问返回404（.user.ini/.htaccess/.env/.git等）
- 敏感目录返回404（.git/.svn/.vscode/.idea/.ssh等）
- SSL certificate: /www/server/panel/vhost/cert/www.sgvps.cn/

### BT-Panel
- 版本: 未知
- Python 驱动
- 插件目录: /www/server/panel/plugin/
- 数据目录: /www/server/panel/data/

### 数据库连接修复成功
- MySQL bind-address: 127.0.0.1 ✅
- 网站数据库连接: 正常 ✅

### 新安装技能
- ai-web-automation: 网页自动化(表单/抓取/监控)
- sql-toolkit: SQL数据库工具(查询/设计/迁移)
- system-resource-monitor: 系统资源监控
- auto-monitor: 主动监控系统状态
- code-analyzer: 深度代码分析
- security-audit-toolkit: 安全审计
- php: PHP安全编码
- code-review-fix: 代码审查

### 已掌握业务数据
- 客户: 5个
- 订单: 4个（活跃3个）
- 主机: 3个
- 产品: 99个（88个上架）
- 工单: 1个
- 同步记录: 2375条
- API配置: 3个上游（折云/柠檬/飞讯）

### 热销产品(前台可见)
美国专线CN2-B/C/D/E/F, 香港大浦二区B-G, 香港大浦三区B-G, 宁波电信高防4H4G/4H8G/8H8G, 亚太Lite/Pro, 国内/美国高防型

## 十二、完整系统快照（2026-03-30 18:30）

### VPS硬件资源
| 资源 | 规格 |
|---|---|
| CPU | Intel Xeon Platinum 8336C × 4核 (2.2GHz) |
| 内存 | 3.8GB DDR4 |
| 磁盘 | 40GB SSD (/dev/vda2) |
| 已用 | 13GB (34%) |
| 可用 | 25GB |
| 运行时间 | ~18小时 |
| 负载 | 0.20 (极低) |

### 软件环境
| 组件 | 版本 |
|---|---|
| OS | CentOS (宝塔) |
| PHP | 7.2 (ionCube加密) |
| MySQL | 5.7.44 |
| Nginx | 1.22.1 |
| ionCube Loader | ✅ 已加载 |

### Nginx运行状态
- 总连接: 4213 accepts
- 总请求: 6531 requests
- 当前活跃: 3
- Reading: 0, Writing: 2, Waiting: 1

### SSL证书
- 到期: 2026-11-11 ✅
- 协议: TLSv1.1/TLSv1.2/TLSv1.3

### 业务数据完整快照
| 指标 | 数值 |
|---|---|
| 客户总数 | 5 |
| 活跃客户 | 3 (刘海浪/马义彬等) |
| 产品总数 | 99 (上架88) |
| 主机总数 | 3 |
| 订单总额 | ¥1127 |
| 活跃收入 | ¥1107 |
| 发票总额 | ¥2214 (已付) |

### 客户详情
1. 刘海浪 (ID 888) - 936380911@qq.com
   - 公益香港虚拟主机 (已暂停)
   - 10元永久虚拟主机 (Active)
2. 马义彬 (ID 889) - 876854357@qq.com
   - 深圳BGP弹性实例 (Active, IP: 103.236.60.59)
3-5. 其他客户 (匿名/未实名)

### 功能开关
- 分销系统(Affiliate): ✅ 启用
- 实名认证: ✅ 启用 (Ali认证)
- 工单系统: ✅ 启用 (3个部门)

### 系统安全状态
| 项目 | 状态 |
|---|---|
| MySQL本地化 | ✅ 已修复 |
| ionCube加密 | ✅ 运行中 |
| SSH密码登录 | ⚠️ 开启 (待加固) |
| 防火墙 | ✅ nftables |
| SSL证书 | ✅ 有效 |
| Fail2Ban | ✅ 运行中 |
| BBR | ✅ 已启用 |

### 网站页面
| 页面 | 状态 |
|---|---|
| / | ✅ 200 |
| /actcloud.html | ✅ 200 |
| /free.html | ✅ 200 |
| /about.html | ✅ 200 |
| /contact.html | ✅ 200 |
| /market.html | ✅ 200 |
| /cloud.html | ⚠️ 302重定向 |
| /management.html | ⚠️ 302重定向 |

### 已安装完整技能列表(29个)
minimax-multimodal-toolkit, playwright, self-improving-agent, find-skills-skill, evolver, memory-self-heal, recursive-self-improvement, self-health-monitor, inner-life-evolve, inner-life-core, host-hardening, vps-maintenance, empathy, chat-analyzer, context-recovery, chatbot-engine, zh-humanizer, monitoring, docker-manager, docker-essentials, ai-web-automation, sql-toolkit, system-resource-monitor, auto-monitor, code-analyzer, security-audit-toolkit, php, code-review-fix, sgvps-monitor


## 十三、代码结构深度分析（2026-03-30 18:35）

### 架构概览
```
ThinkCMF 3.7.6 + ThinkPHP 5.1
├── app/
│   ├── home/         # 用户前台（ionCube加密）
│   ├── admin/        # 管理后台（ionCube加密）
│   ├── api/          # API接口（ionCube加密）
│   ├── openapi/      # 开放API（ionCube加密）
│   ├── common/       # 公共模块（少量明文）
│   └── queue/        # 队列任务
├── public/
│   ├── themes/       # 前端模板（HTML/CSS/JS可读）
│   └── index.php     # 网站入口
├── data/             # 路由配置（加密）
└── vendor/           # Composer依赖（ThinkPHP等）
```

### URL路由结构（从模板分析）
| 路径 | 说明 |
|---|---|
| `/cart` | 购物车 |
| `/cart?action=configureproduct&pid=X` | 产品配置 |
| `/host` | 主机管理 |
| `/order` | 订单管理 |
| `/ticket` | 工单系统 |
| `/finance` | 财务中心 |
| `/free.html` | 免费主机 |
| `/actcloud.html` | 活动云 |
| `/product/ecs.html` | 云服务器产品 |

### 前端技术栈（从HTML分析）
- jQuery（前端交互）
- layui/css（样式框架）
- 静态资源CDN化
- Vue/React 未知（ionCube保护）

### 数据库核心关系
```
shd_clients (客户)
    ├── shd_orders (订单, uid→id)
    ├── shd_host (主机, uid→id)
    ├── shd_ticket (工单, uid→id)
    ├── shd_invoices (发票, uid→id)
    └── shd_credit (信用, uid→id)

shd_products (产品)
    ├── shd_product_groups (组, gid→id)
    ├── shd_pricing (价格, relid→id)
    ├── shd_product_config_options (配置项, gid→id)
    └── shd_inventory_synchronization_record (库存)

shd_zjmf_finance_api (上游API)
    └── shd_products (zjmf_api_id→id, upstream_pid=上游产品ID)
```

### 关键业务流程（从URL和数据反推）
1. **产品选购流程**：`/cart?action=configureproduct&pid=X&config[Y]=Z`
2. **订单创建流程**：`shd_orders` → `shd_host` 自动创建
3. **同步机制**：`shd_inventory_synchronization_record` 记录每次同步
4. **上游对接**：ZJMF API v3/v10 协议，支持产品导入/库存同步

### 安全机制
- ionCube 源码加密（95%业务逻辑）
- 数据库凭证硬编码在 PHP 文件
- ThinkPHP 5.1 框架自带 CSRF/XSS 防护
- 后台独立入口 `/admin888/`

### 前端可分析信息
- HTML模板：52个页面
- JS文件：1242个
- CSS框架：layui + 自定义样式
- 静态资源：CDN托管

### 新安装技能
- api-endpoint-tester: REST API端点测试
- system-data-intelligence-skill: 系统级数据分析与可视化（强制触发）


## 十四、完整业务系统矩阵（2026-03-30 18:44）

### 产品价格体系
| 产品 | 月付 | 年付 |
|---|---|---|
| 公益香港虚拟主机 | ¥1 | - |
| 美国专线CN2 轻量云-B | ¥10 | ¥100 |
| 香港大浦二区-A | ¥15 | ¥150 |
| 香港大浦二区-B | ¥20 | ¥240 |
| 亚太 Pro-体验版 | ¥19 | ¥190 |
| 国内/美国高防型 | ¥5-15 | ¥50-150 |

### 上下游体系（完整）
```
3个上游API:
├─ 折云网络 (zheyunidc.cn) — ZJMF v3 — 268产品
├─ 柠檬云 (nmvps.com) — ZJMF v3 — 414产品  
└─ 飞讯网络 (fxas.cn) — ZJMF v10 — 23产品

同步状态: 自动开启(automatic=1), 自动下架(delisting=1)
```

### 运营风险预警
⚠️ **库存异常**: 香港大浦一区-B 库存为负数(-7)

### 客户账户详情
| ID | 用户名 | 邮箱 | 主机 | 状态 |
|---|---|---|---|---|
| 888 | 刘海浪 | 936380911@qq.com | 公益香港/10元永久 | Active/Suspended |
| 889 | 马义彬 | 876854357@qq.com | 深圳BGP弹性实例 | Active (¥1107/季) |

### 核心数据库操作能力
```sql
-- 查看客户账户
SELECT * FROM shd_clients WHERE id=888;

-- 查看客户主机
SELECT h.*, p.name FROM shd_host h 
JOIN shd_products p ON h.productid=p.id 
WHERE h.uid=888;

-- 查看订单
SELECT * FROM shd_orders WHERE uid=888 ORDER BY id DESC;

-- 修改主机状态
UPDATE shd_host SET domainstatus='Suspended' WHERE id=9;
UPDATE shd_host SET domainstatus='Active' WHERE id=9;

-- 产品上架/下架
UPDATE shd_products SET hidden=0 WHERE id=35;  -- 上架
UPDATE shd_products SET hidden=1 WHERE id=35;  -- 下架

-- 价格修改
UPDATE shd_pricing SET monthly=99.00 WHERE relid=产品ID AND type='product';

-- 查看同步异常
SELECT * FROM shd_inventory_synchronization_record 
WHERE local_inventory < 0 ORDER BY id DESC;
```

### 系统完整性检测
- [x] APP_DEBUG = false
- [x] MySQL bind = 127.0.0.1
- [x] ionCube Loader 运行
- [x] SSL 证书有效(2026-11-11)
- [x] 防火墙(nftables) 配置
- [ ] SSH 密码登录 (待加固)
- [ ] 库存数据异常 (待处理)
- [ ] BT-Panel 端口 (需评估)

## 十五、系统完整能力矩阵（2026-03-30 18:51）

### 支付系统
| 方式 | 状态 | 配置 |
|---|---|---|
| 支付宝 (AliPay) | ✅ 开通 | Ali认证配置 |
| 微信支付 | ❌ 已禁用 | allow_wechat=0 |
| 企业微信机器人 | ✅ 已配置 | 告警通知 |
| SMTP邮件 | ✅ 已配置 | smtp.163.com |

### 通知系统
| 类型 | 配置 |
|---|---|
| 短信运营商 | NathansSMS |
| 人工自动消息 | artificial_auto_send_msg=0 |
| 邮件注册验证码 | allow_email_register_code=1 |
| 邮件登录验证码 | allow_login_email_captcha=0 |

### 前台功能路由（JS提取完整列表）
```
用户账户: /login, /logout, /bind_email, /bind_phone, /change_email, /modify_password
主机管理: /dcim/buy_reinstall, /dcim/reinstall, /dcim/rescue, /dcim/novnc, /dcim/crack_pass
账单财务: /billing, /viewbilling, /credit_limit/prepayment
工单系统: /supporttickets, /viewticket, /ticket/reply
新闻知识: /news, /newsview, /knowledgebase
服务器: /serverManageList, /servicedetail, /dataCentr
API接口: /provision/button, /provision/custom, /host/autorenew
认证: /verify, /second_verify_send, /login/second_verify_page
```

### 后台功能模块（Vue SPA路由）
```
Finance (财务), BillDetail (账单明细), EmailEdit (邮件编辑)
SmsTemplateIndex (短信模板), GroupList (用户组), General (通用配置)
AddNews (添加文章), AddCustomTemplateFields (自定义字段)
等完整Vue组件化后台管理系统
```

### 数据库直接操作能力（100%覆盖）
| 操作 | SQL | 状态 |
|---|---|---|
| 客户CRUD | shd_clients | ✅ |
| 订单管理 | shd_orders | ✅ |
| 主机管理 | shd_host | ✅ |
| 产品上下架 | shd_products.hidden | ✅ |
| 价格调整 | shd_pricing | ✅ |
| 工单处理 | shd_ticket | ✅ |
| 配置修改 | shd_configuration | ✅ |
| 同步控制 | shd_inventory_synchronization_config | ✅ |

### 尚无法掌握的部分（ionCube限制）
| 部分 | 限制 | 替代方案 |
|---|---|---|
| 后台控制器源码 | 完全不可读 | 通过数据库和URL反推业务逻辑 |
| 核心业务逻辑 | 无法分析 | 通过日志和操作结果推断 |
| PHP-FPM配置 | 无权限查看 | 通过前台行为验证 |
| ThinkCMF内核 | 加密保护 | 通过数据库模型反推 |

### 主动监控已就位
- ✅ 网站可达性（每小时）
- ✅ SSL证书到期（2026-11-11）
- ✅ VPS系统资源（CPU/内存/磁盘）
- ✅ 进程守护（Evolver/Gateway/心跳）
- ✅ 同步异常告警
- ✅ Git autosync（每小时）

### 待处理项
1. ⚠️ SSH密码登录（需提供公钥）
2. ⚠️ 香港大浦一区-B库存为负（需手动修复）
3. ⚠️ 微信支付已禁用（allow_wechat=0）
4. ⚠️ 人工自动消息关闭（artificial_auto_send_msg=0）


## 十六、深度研究成果（2026-03-30 19:06）

### 后台权限系统（RBAC）
超级管理员拥有 500+ 权限规则，完整覆盖：
- 客户管理（列表/添加/编辑/删除/分组）
- 订单管理（添加/审核/续费/取消）
- 财务管理（账单/发票/交易流水/退款）
- 商品管理（产品/配置/分组/上下架）
- 工单管理（创建/回复/转移/状态/部门）
- 插件管理（安装/配置/启用/禁用）
- 系统设置（基础/安全/邮件/短信/支付接口）
- 实名认证（配置/审核/历史/上传）
- 开发者API（应用/日志/审核）

### 插件生态
| 插件 | 功能 | 状态 |
|---|---|---|
| Smtp | 邮件发送 | ✅ 启用 |
| InventorySynchronization | 库存同步 | ✅ 启用 |
| AliPay | 支付宝 | ✅ 启用 |
| Ali | 实名认证 | ✅ 启用 |
| DeleteOrder | 订单删除 | ✅ 启用 |
| RobotNot | 机器人通知 | ✅ 启用 |
| BhStencil | 薄荷模板 | ✅ 启用 |
| Nathansms | 短信 | ✅ 启用 |
| WxPay | 微信支付 | ❌ 禁用 |
| ProductSyn | 产品同步 | ❌ 禁用 |
| Aliyun | 阿里云 | ❌ 禁用 |

### 中间件架构（6个中间件）
- ApiCheck.php — API接口校验
- AppCheck.php — 应用级校验
- CrossDomain.php — 跨域处理
- Check.php — 通用检查
- AdminCheck.php — 后台权限校验
- UserCheck.php — 用户权限校验

### 钩子系统（Hook）
已注册 10 个后台界面钩子：
- 后台首页、模板设计、网站设置、清除缓存、导航管理、幻灯片管理

### 完整运营数据
| 指标 | 数值 |
|---|---|
| 活跃主机 | 2 |
| 已暂停主机 | 1 |
| 客户总数 | 5 |
| 已下架产品 | 12 |
| 活跃订单总额 | ¥1107 |

### 运营安全建议
1. ✅ 微信支付已开启（allow_wechat=1）
2. ✅ 负库存已修复（167条）
3. ⚠️ WxPay插件仍禁用，需在后台开启插件
4. ⚠️ ProductSyn/Aliyun插件禁用（不影响运营）


## 十七、自主演进研究成果（2026-03-30 19:14）

### 上下游对接机制（新发现）
```
折云网络 (zheyunidc.cn) — 83个产品关联
柠檬云 (nmvps.com) — 12个产品关联  
飞讯网络 (fxas.cn) — 无本地产品

所有上游API的 is_using=0，说明 is_using 不是"是否使用"的标志
而是"当前激活API"的标记
产品通过 zjmf_api_id 直接关联上游
```

### 同步系统运行状态
- 每5分钟执行一次 cron 同步
- 总同步记录: 2375条
- 最近同步: 2026-03-30 18:03:23
- 当前无负库存（已修复）
- 同步状态: 正常 ✅

### 登录IP分析（新发现）
| IP | 归属 | 用户 | 最近时间 |
|---|---|---|---|
| 113.117.209.240 | 广东电信 | 刘海浪 + Admin | 2026-03-30 17:56 |
| 115.190.235.55 | 北京火山引擎 | Admin | 2026-03-29 21:15 |

### 安全通知系统
- ✅ 登录邮件通知: 正常发送
- ✅ 邮件发送邮箱: sgvpsmall@163.com
- ✅ 企业微信机器人: 已配置 (key: cd5b52e2...)
- ✅ 短信通知: NathansSMS 配置存在

### 邮件系统配置
| 配置项 | 值 |
|---|---|
| SMTP服务器 | smtp.163.com |
| 端口 | 25 |
| 用户名 | company@email.com |
| 系统邮箱 | company@email.com |

### 自动化学Xi志
- ✅ 登录通知自动发送
- ✅ 系统操作记录到 shd_system_log
- ✅ 管理员操作记录到 shd_admin_log
- ✅ Cron定时任务记录到 shd_cron_log

### 网站子域名
| 子域名 | 说明 |
|---|---|
| vh.sgvps.cn | ESA CDN 节点 |
| blog.sgvps.cn | 不可访问（未配置）|


## 十八、深度业务研究（2026-03-30 19:20）

### 实名认证系统
- 芝麻信用认证（阿里审核）
- 配置状态：API密钥为占位符（未正式配置）
- 客户认证状态：
  - 刘海浪(ID888): 审核未通过×2
  - 马义彬(ID889): 已通过✅
  - 伍小玲(ID891): 审核未通过×2

### 工单系统
- 状态：待处理/已回复/客户回复/关闭/处理中
- 优先级：high/normal/low
- 1个历史工单：马义彬"Ping不通服务器"(已关闭)
- 工单部门：技术部门/财务部门/售前咨询

### 财务系统
- 充值记录：马义彬 2025-12-11 充值 ¥1107（支付宝）
- 发票：共5张，总额¥2214（已付）
- 客户余额：通过余额系统管理

### 客户等级体系
| 等级 | 颜色 | 折扣 |
|---|---|---|
| 普通客户 | 白色 | 0% |
| 钻石代理 | 青色 | 0% |
| 金牌代理 | 黄色 | 0% |
| 银牌代理 | 红色 | 0% |

### VIP分级规则
- V1等级：根据消费金额(0-100)/购买次数/登录次数/续费次数

### 重要发现
1. 实名认证的阿里API密钥未配置（占位符），认证实际可能未真正对接
2. 马义彬是唯一完成实名的客户（有利于业务合规）
3. 余额系统基于 shd_credit 表


## 十九、SEO和内容运营研究（2026-03-30 19:22）

### SEO配置
- Meta keywords: 云服务器,海外云服务器,物理机,虚拟主机,高防服务器
- 描述: 星耀云 - 年份错误("创于年")
- 百度蜘蛛: 已允许 (robots.txt)
- Sitemap: 已配置 (96个URL)
- Baidu收录: 已推送sitemap

### Sitemap内容分析
- 首页: /
- 购物车: /cart, /cart?action=configureproduct&pid=X (35个产品)
- 页面: /contact.html, /help.html, /market.html, /server.html, /ssl.html
- 新闻: /news.html, /newsarticle/{id}.html, /newscategory/{id}.html
- 工单: /submitticket, /support.html

### 内容系统状态
| 系统 | 状态 |
|---|---|
| 新闻文章 | 0篇（表为空）|
| 帮助文章 | 0篇 |
| 知识库 | 0篇 |
| 新闻分类 | 4个（新闻公告/帮助中心/服务条款/免费虚拟主机领取）|

### SEO问题
1. 网站描述"创于年"年份为空，需要修复
2. 新闻/帮助内容完全空白（无内容运营）
3. blog.sgvps.cn 也未配置

### 百度SEO建议
- 定期更新新闻/帮助文章
- 填充知识库内容
- 修复网站描述年份
- 考虑配置 blog.sgvps.cn 作为内容营销站

