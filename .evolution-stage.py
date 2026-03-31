#!/usr/bin/env python3
"""
贾维斯阶段汇报 - 重大改进立即推送
触发条件：
  - 新技能安装/卸载
  - 重大bug修复（非例行）
  - 系统架构变更
  - 新增重要能力
  - 错误率显著下降

用法：python3 .evolution-stage.py <类型> <描述>
例：python3 .evolution-stage.py skill "安装SEO skill"
"""
import sys, subprocess
from datetime import datetime

def feishu_card(title, items, footer=""):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"## 🦞 {title}",
        f"",
        "",
    ]
    for item in items:
        lines.append(f"- {item}")
    if footer:
        lines += ["", footer]
    lines.append(f"_{ts}_")
    text = "\n".join(lines)
    try:
        subprocess.run(["python3", "/root/.openclaw/workspace/.feishu-notify.py", text],
                      capture_output=True, timeout=15)
    except: pass
    print(f"[Stage Report] {title}: {len(items)} items")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 .evolution-stage.py <类型> <描述> [项...]")
        sys.exit(1)
    etype = sys.argv[1]
    desc = sys.argv[2]
    items = sys.argv[3:] if len(sys.argv) > 3 else [desc]
    feishu_card(f"🚀 贾维斯进化 [{etype}]", items)
