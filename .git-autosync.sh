#!/bin/bash
# Git 自动同步 - 每次触发检查并提交
WORKSPACE="/root/.openclaw/workspace"
cd "$WORKSPACE" || exit 1

# 检查是否有未提交更改
if [ -n "$(git status --short 2>/dev/null)" ]; then
    git add -A
    git commit -m "Auto-sync $(date '+%Y-%m-%d %H:%M')" 2>/dev/null
fi
