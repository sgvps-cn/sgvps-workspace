# ClawHub 学习笔记 (2026-03-31)

## CLI 命令

```
clawhub search <query...>     # 向量搜索 skills (有效 ✅)
clawhub inspect <slug>        # 查看 skill 元数据 (有效 ✅)
clawhub install <slug>       # 安装 skill
clawhub list                  # 已安装列表
clawhub update [slug]         # 更新
clawhub explore              # 浏览最新 (当前返回空)
clawhub publish <path>       # 发布 skill
```

## 已安装 Skills

- ai-web-automation (刚装，但内容是模板，无实际功能)
- openclaw-cli (可用，值得研究)
- seo-competitor-analysis (可选安装)
- clawic-hub (引流到 clawic.com，无实际内容)

## 可用发现

### ai-web-automation
- SKILL.md 内容为模板示例，非真实实现
- 包含 selenium/puppeteer/代理池/定时任务概念
- 无实际可执行代码

### openclaw-cli
- 覆盖 OpenClaw CLI 运维全流程
- setup/gateway lifecycle/channel login/messaging/agent turns/models/plugins/system health
- 值得深入研究并可能应用到贾维斯

## 待执行

- [ ] 深入读 openclaw-cli SKILL.md
- [ ] 探索 clawhub.com 是否有更多 skills
