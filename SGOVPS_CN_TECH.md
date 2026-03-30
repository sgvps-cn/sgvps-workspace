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

## 七、待处理项

- [ ] **立即修复 APP_DEBUG=true**（`/think` 文件）
- [ ] 升级 PHP 7.2 → 8.x
- [ ] 升级 ThinkCMF 或制定迁移计划
- [ ] 删除 `public/.idea`
- [ ] 数据库远程访问加固
- [ ] 建立自动备份策略
