#!/bin/bash
# 贾维斯每日EvoMap学习脚本
# 每天从 EvoMap ranked assets 学习高价值模式
WORKSPACE="/root/.openclaw/workspace"
LOG="$WORKSPACE/.learnings/EVOMAP_LEARNINGS.md"
ASSETS=$(curl -s "https://evomap.ai/a2a/assets/ranked?limit=5" 2>/dev/null)

echo "=== EvoMap Learning $(date) ===" >> "$LOG"

# 提取 top capsule 的 summary 和 trigger
echo "$ASSETS" | python3 -c "
import sys, json, re
try:
    d = json.loads(sys.stdin.read())
    for a in d.get('assets', [])[:3]:
        p = a.get('payload', {})
        triggers = p.get('trigger', [])
        summary = p.get('summary', '')[:120]
        calls = a.get('call_count', 0)
        conf = a.get('confidence', 0)
        print(f'  Signals: {\", \".join(triggers[:3])}')
        print(f'  Pattern: {summary}')
        print(f'  Used: {calls} times, conf={conf}')
        print()
except: pass
" >> "$LOG" 2>/dev/null

echo "Done at $(date)" >> "$LOG"
echo "---" >> "$LOG"
