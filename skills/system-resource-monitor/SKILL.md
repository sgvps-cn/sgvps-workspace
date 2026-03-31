---
name: system_resource_monitor
description: 服务器资源监控 - CPU/内存/磁盘/进程状态，输出结构化报告，支持阈值告警。用于主动监控系统健康。
version: 1.1.0
author: Jarvis v3
---

# System Resource Monitor v1.1

服务器资源监控 skill，返回结构化健康报告。

## 触发词
- "系统状态"、"服务器健康"、"资源使用"
- "CPU"、"内存"、"磁盘"
- 主动监控 heartbeat 检查

## 使用方法

### 快速检查（exec 直接调用）
```bash
echo "=== 系统状态 ===" && uptime && free -h && df -h / && ps aux --sort=-%cpu | head -5
```

### 标准报告
```bash
# 返回格式：CPU负载 | 内存% | 磁盘% | 进程数 | 运行时间
uptime | awk -F'load average:' '{print "CPU:" $2}' && \
free | grep Mem | awk '{printf "内存:%d%%\n", $3/$2*100}' && \
df / | awk 'NR==2 {print "磁盘:"$5}' && \
echo "进程:$(ps aux | wc -l)" && \
echo "运行:$(uptime -p)"
```

## 阈值定义

| 指标 | 警告 | 危险 | 说明 |
|---|---|---|---|
| CPU Load (1min) | > 4 | > 8 | 4核CPU 기준 |
| 内存使用率 | > 75% | > 90% | RAM / Total |
| 磁盘使用率 | > 75% | > 90% | / 分区 |
| Swap 使用率 | > 50% | > 80% | 已用/总量 |
| 进程数 | > 500 | > 800 | 普通服务器 |
| PHP/Cron 卡住 | > 300s | > 600s | 单进程运行时间 |

## 阈值告警脚本
```bash
#!/bin/bash
MEM_PCT=$(free | grep Mem | awk '{printf "%d", $3/$2*100}')
DISK_PCT=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
LOAD=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')

[ "$MEM_PCT" -ge 90 ] && echo "危险:内存${MEM_PCT}%"
[ "$DISK_PCT" -ge 90 ] && echo "危险:磁盘${DISK_PCT}%"
```

## 返回格式示例

```
=== 贾维斯系统状态 ===
🖥️  运行时间: up 7 days, 3 users, load average: 0.32, 0.28, 0.25
💾  内存: 1.5Gi / 3.8Gi (39%)
💾  Swap: 0B / 0B (0%)
💾  磁盘: 13G / 40G (33%)
🐘  进程: 87 个
🌐  Gateway: ✅ (200)
🔁  Clash: ✅ (运行中)
```

## 自动监控（心跳模式）
在 HEARTBEAT.md 或定时任务中调用：
```bash
python3 -c "
import subprocess
r = subprocess.run(['bash', '-c', 'free | grep Mem && df / && uptime'], capture_output=True, text=True)
# 分析 r.stdout，超过阈值时告警
"
```

## 健康判断逻辑
```python
def system_healthy():
    mem_pct = int(mem_used / mem_total * 100)
    disk_pct = int(disk_used / disk_total * 100)
    load_1m = float(load_avg_1min)
    
    if mem_pct >= 90 or disk_pct >= 90 or load_1m >= 8:
        return "危险"
    elif mem_pct >= 75 or disk_pct >= 75 or load_1m >= 4:
        return "警告"
    return "正常"
```

## 贾维斯集成
在 `.self-repair.py` 的 `repair_memory()` 中已使用：
- RAM ≥ 90% → 自动杀 top 内存进程
- Swap > 1GB → 自动 swapoff/swapon

---
*最后更新: 2026-03-31 by Jarvis*
