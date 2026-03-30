# Errors

Command failures and integration errors.

---

## [ERR-20260331-001] MiniMax API model not supported

**Logged**: 2026-03-31T02:00:00+08:00
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
MiniMax API返回status_code 2061，提示"your current token plan not support model"

### Error
```
status_code: 2061, status_msg: 'your current token plan not support model, MiniMax-Text-01'
```

### Context
- 调用 api.minimaxi.com/v1/text/chatcompletion_v2
- 模型: MiniMax-Text-01, abab6.5s-chat 均不支持
- 可能只有特定模型在token计划内

### Suggested Fix
- 查MiniMax文档确认哪个模型可用
- 用有权限的模型做文字生成
- 备用方案：用IDC知识库直接写文章不入API

---

## [ERR-20260331-002] MiniMax API key权限受限

**Logged**: 2026-03-31T02:25:00+08:00
**Priority**: high
**Status**: wont_fix
**Area**: infra

### Summary
MiniMax API key不支持任何文字/语音/图像生成API，所有模型返回2061

### Error
所有测试均返回: status_code 2061 "your current token plan not support model"

### Context
测试过的模型:
- 文字: MiniMax-Text-01, abab6.5s-chat, abab6-chat, abab5.5s-chat 等全部2061
- 语音: speech-01-turbo, speech-2.8-hd 全部2061
- 图像: image-01 2061
- 视频: video-01 2061

### Resolution
- 这个API key可能是给特定业务用的，不支持标准API
- 文章生成继续用IDC知识库直接写，不依赖API
- 如需MiniMax API做文字生成，需要换一个有权限的key

---

## [ERR-20260331-003] 文章插入失败（learnings已promoted）

**Logged**: 2026-03-31T02:30:00+08:00
**Priority**: critical
**Status**: resolved
**Area**: backend

### Summary
之前声称"文章已写入数据库"是错的。INSERT失败但echo导致误以为成功

### Error
MySQL返回: ERROR 1054 (42S22) Unknown column 'title' in 'field list'

### Root Cause
1. shd_news表只有(relid, content)两个字段，没有title字段
2. ZJMF的shd_news是法律/帮助页面存储，不是博客文章
3. shell脚本中 `mysql && echo "✅"` 导致失败也被认为成功

### Resolution
- ZJMF系统没有博客/新闻文章功能
- 想做SEO需要单独搭建WordPress或其他博客系统
- sgvps.cn的sitemap里126个URL是产品页，不是文章
- 已更新监控脚本：SELECT COUNT(*) FROM shd_news 改为统计正确的表

### Correct Data Model
- shd_news_menu: id, title, keywords, description, head_img, read, hidden, sort, update_time, create_time, push_time
- shd_news: relid, content
- 关系: shd_news.relid = shd_news_menu.id (1:1)

---
