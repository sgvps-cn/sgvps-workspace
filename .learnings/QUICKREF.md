# 贾维斯速查手册

**每次任务前必查，不要凭感觉。**

---

## 执行前必问

1. 这个任务涉及什么领域？（SEO/数据库/系统/代码/网络）
2. 我有相关的 learnings 吗？
3. 上次做类似任务时有没有犯过错？

---

## 快速索引

### SEO
| 问题 | 查 |
|---|---|
| 标题/H1/Alt | LRN-20260331-004 |
| Canonical标签缺失 | THEME_ANALYSIS.md §9 |
| ZJMF无博客系统 | ERR-20260331-003 |

### 数据库
| 问题 | 查 |
|---|---|
| shd_news表结构 | ERR-20260331-003 |
| shd_news_menu是分类 | THEME_ANALYSIS.md §4 |
| 新闻文章用relid关联 | THEME_ANALYSIS.md §4 |

### 系统/网络
| 问题 | 查 |
|---|---|
| 外部API调用 | 永远加timeout (LRN-20260331-002) |
| MiniMax API 2061 | ERR-20260331-001/002 |
| GLM API端点 | open.bigmodel.cn/api/paas/v4 |
| Clash代理 | 127.0.0.1:7890 |
| 网络受限 | LRN-20260331-001 |

### ZJMF/ThinkCMF
| 问题 | 查 |
|---|---|
| 核心PHP加密 | LRN-20260331-005 |
| SEO标题走seo()函数 | THEME_ANALYSIS.md §2 |
| ymlj字段存完整URL | THEME_ANALYSIS.md §2 |
| 可修改: 模板/CSS/数据库 | THEME_ANALYSIS.md §7 |

### 决策框架
| 原则 | 说明 |
|---|---|
| Two-Way Door | 直接执行，可回滚 |
| One-Way Door | 先汇报再执行 |
| 抗反 | 不要为了"完美方案"而卡住 |

---

## 禁止事项

- ❌ 外部API调用不加timeout
- ❌ 以为执行了就算完成了
- ❌ 学了不用
- ❌ 重复同一个错误

---

## 每次心跳检查

1. learnings 有没有新的待处理项？
2. 正在进行的任务有没有错误模式？
3. 系统有没有新发现的异常？
