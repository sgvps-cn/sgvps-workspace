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
