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
