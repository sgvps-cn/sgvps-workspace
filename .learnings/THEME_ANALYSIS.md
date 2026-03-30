# ZdsjuM1 主题完整分析
生成时间: 2026-03-31 03:30
分析深度: 全面

---

## 一、主题架构

### 1.1 文件结构
```
/www/wwwroot/www.sgvps.cn/public/themes/web/ZdsjuM1/
├── index.html          # 首页 (Vue组件渲染)
├── about.html         # 关于我们
├── contact.html       # 联系我们
├── service.html       # 产品服务
├── news.html          # 新闻公告
├── newsarticle.html   # 新闻详情
├── newscategory.html  # 新闻分类
├── help.html          # 帮助中心
├── helpcategory.html  # 帮助分类
├── helparticle.html   # 帮助文章
├── support.html       # 服务支持
├── agent.html         # 代理合作
├── cps.html          # CPS推广
├── free.html         # 免费主机
├── baremetal.html    # 物理机
├── actcloud.html     # 活动页
├── links.html        # 友情链接
├── zizhi.html        # 资质证书
├── domain.html       # 域名注册
├── market.html       # 市场/商标
├── bt.html           # 宝塔合作
├── newuser.html      # 新用户
├── sop.html          # (内部工具)
├── ym/               # 营销落地页(域名/虚拟主机)
│   ├── index.html
│   ├── index1.html
│   └── index2.html
├── solution/          # 行业解决方案
│   ├── game.html     # 游戏
│   ├── ecmomerce.html
│   ├── education.html
│   ├── enterprise.html
│   ├── finance.html
│   ├── media.html
│   ├── medical.html
│   └── security.html
├── product/
│   └── ecs.html      # 云服务器产品页
├── common/
│   ├── header.html   # 公共头部 (SEO核心)
│   └── footer.html   # 公共底部
└── style/
    ├── css/          # 41个CSS文件
    └── js/           # JS文件
```

---

## 二、SEO系统

### 2.1 Title标签生成逻辑
位置: `common/header.html` 第22行
```html
<title>{if $seo.ymbt}{$seo.ymbt}{elseif $CartConfig.product.name}[title]_{$CartConfig.product.name}{else /}[title]{/if}_{$setting.company_name}</title>
```

**优先级:**
1. `$seo.ymbt` → seo_settings表对应页面的标题
2. `$CartConfig.product.name` → 产品页专用
3. `[title]` → 后台配置的页面标题

### 2.2 seo()函数工作原理
```php
function seo() {
    return Db::name("seo_settings")->where("ymlj", $bhurl)->select();
}
```
- `$bhurl` = 当前URL路径 (如 `/index`, `/about`)
- `ymlj` = seo_settings表中存储的URL (目前存的是**完整URL**如 `https://www.sgvps.cn`)
- **问题**: 函数用路径匹配完整URL，永远匹配不上 → 走fallback

### 2.3 首页标题问题根因
| 项目 | 值 |
|---|---|
| 数据库title | 星耀云 - 专业云服务器IDC服务商 |
| seo_settings.ymbt | 星耀云首页 |
| seo()匹配 | ❌ 失败 (路径vs完整URL) |
| 实际显示 | 首页_星耀云 |

**解决方案**: 修改 `shd_seo_settings` 的 `ymlj` 字段，把完整URL改成路径 `/`

### 2.4 各页面SEO配置
- 首页: `ymlj=https://www.sgvps.cn` → 需改为 `/`
- 产品页: `ymlj=https://www.sgvps.cn/cart`
- 所有页面的seo字段都在 `shd_seo_settings` 表

---

## 三、模板变量系统

### 3.1 核心函数 (来自zdsju.php, 已加密)
| 函数 | 作用 | 返回 |
|---|---|---|
| `seo()` | SEO设置 | `shd_seo_settings`表 |
| `get_br()` | Banner幻灯片 | 广告设置 |
| `get_all()` | 全局站点设置 | `shd_site`表 |
| `get_keyword()` | 关键词 | 未知 |
| `qqmc()` / `qqzh()` | QQ客服 | QQ号列表 |
| `get_pro()` | 产品列表 | `shd_products`表 |
| `syxl()` | 首页广告双横幅 | 广告配置 |
| `tcgg()` | 弹窗公告 | 广告配置 |

### 3.2 常用模板变量
| 变量 | 来源 | 用途 |
|---|---|---|
| `$setting.company_name` | shd_configuration | 公司名 |
| `$setting.company_qq` | shd_configuration | QQ |
| `$setting.company_email` | shd_configuration | 邮箱 |
| `$setting.company_phone` | shd_configuration | 电话 |
| `$setting.company_profile` | shd_configuration | 公司介绍 |
| `$setting.web_seo_keywords` | shd_configuration | SEO关键词 |
| `$setting.web_seo_desc` | shd_configuration | SEO描述 |
| `$site.xxx` | get_all() | 站点配置 |
| `$newsList` / `$newsContent` | NewsController | 新闻数据 |

---

## 四、新闻/帮助系统

### 4.1 数据表
- `shd_news_menu`: 分类和文章索引 (4条记录)
- `shd_news`: 文章内容 (relid关联)
- `shd_news_type`: 类型 (新闻公告/帮助中心)

### 4.2 现有数据
- 服务条款和隐私条款: 2篇
- 免费主机领取说明: 2篇
- **总计: 4篇**, 全部是帮助/法律文档

### 4.3 注意
这不是博客系统，是ZJMF内置的帮助/公告系统
如需SEO文章营销，需独立搭建WordPress

---

## 五、页面H1标签现状

| 页面 | H1数量 | 问题 |
|---|---|---|
| about.html | 1 | ✅ 正常 |
| actcloud.html | 1 | ✅ 正常 |
| contact.html | 1 | ✅ 正常 |
| index.html | 0 | ❌ Vue渲染,不可见 |
| service.html | 0 | ❌ 无H1 |
| news.html | 2 | ✅ 正常 |
| newsarticle.html | 3 | ⚠️ 多个H1 |
| support.html | 6 | ❌ 太多H1 |
| cps.html | 6 | ❌ 太多H1 |
| free.html | 2 | ⚠️ 多个H1 |
| help*.html | 2-3 | ⚠️ 多个H1 |

---

## 六、CSS架构
共41个CSS文件，按模块分离:
- `global.css` / `header.css` / `index.css` - 基础
- `about.css` / `contact.css` / `news*.css` - 页面专用
- `solution/*.css` - 行业方案页专用
- `cps/*.css` - CPS推广页
- `bt/bt.css` - 宝塔合作

---

## 七、可安全修改范围

✅ **可以修改:**
- 所有HTML模板 (*.html)
- 所有CSS文件 (*.css)
- JS文件 (themes/web/ZdsjuM1/style/js/)
- 数据库 shd_configuration 表
- 数据库 shd_seo_settings 表
- Banner图片 (/upload/banner/)
- 版权/备案信息

❌ **不能修改:**
- app/zdsju.php (加密)
- app/common.php (加密)
- app/home/controller/*.php (加密)
- app/zjmf.php (加密)

---

## 八、首页Vue组件
`index.html` 使用Vue组件系统:
- `@cloud/pep-home-page/pc/index` - 首页主体
- `@cloud/pep-mkp-trademark-cn/pc/index` - 商标页(market.html)

组件在 `public/themes/web/ZdsjuM1/ym/` 有静态版本，但主站用的是外部CDN加载

---

## 九、已知问题汇总

| # | 问题 | 原因 | 修复方式 |
|---|---|---|---|
| 1 | 首页标题"首页_星耀云" | seo()匹配失败+fallback显示 | 修改seo_settings的ymlj为路径 |
| 2 | 首页H1缺失 | Vue组件渲染,模板无H1 | 已加隐藏H1 |
| 3 | 产品页H1缺失 | service.html无H1 | 需在模板加H1 |
| 4 | 多页面H1过多 | support/cps等6个H1 | 需改模板,保留1个主H1 |
| 5 | 7/8图片Alt缺失 | 后台上传时未填 | 后台填写 |
| 6 | Canonical URL缺失 | 模板无canonical标签 | 需在header加 |
| 7 | 无博客系统 | ZJMF只有帮助/公告 | 需装WordPress |

