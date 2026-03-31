---
name: auto_monitor
description: 实时进程级监控 - 进程崩溃/端口down/systemd服务状态/Systemd定时器完整性。与.self-repair.py（每小时故障修复）和.proactive-planner.py（每日业务扫描）互补，专注实时告警。
version: 1.2.0
author: Jarvis v3
---

# Auto Monitor v1.2

**定位：** 实时进程级监控，与 `.self-repair.py`（故障修复）和 `.proactive-planner.py`（业务扫描）三角互补。

| 系统 | 触发 | 职责 |
|---|---|---|
| `.self-repair.py` | 每小时 | 故障修复（进程/内存/git/clash） |
| `.proactive-planner.py` | 每天9点 | 业务扫描（订单/工单/到期/SEO） |
| `auto-monitor` | 实时/5分钟 | 进程崩溃/端口/服务状态/Cron完整性 |

## 核心检查项

### 1. 关键进程存活检测
```bash
# 检查 Nginx / PHP-FPM / MySQL / Clash / OpenClaw 进程
for svc in nginx php-fpm-74 mysql openclaw; do
  pgrep -f "$svc" > /dev/null && echo "$svc:✅" || echo "$svc:❌"
done
```

### 2. 端口监听检测
```bash
# 检查关键端口是否在监听
for port in 80 443 3306 18789 9090; do
  ss -tlnp | grep ":$port " > /dev/null && echo "$port:✅" || echo "$port:❌"
done
```

### 3. systemd 服务状态
```bash
systemctl is-active nginx mysql php-fpm-74 jarvis-daemon 2>/dev/null
```

### 4. Cron 定时器完整性
```bash
# 检测 cron job 是否存在（防丢失）
crontab -l 2>/dev/null | grep -E "self-repair|proactive|evolution"
# 期望至少3个
```

### 5. 最近进程崩溃日志
```bash
# 检查 dmesg / syslog 中的崩溃记录
dmesg | grep -i "oom\|killed\|segfault" | tail -5
```

## 阈值
- 内存 > 90% → 危险
- 磁盘 > 85% → 警告，> 95% → 危险
- CPU Load > 8 → 警告
- 关键端口 down → 立即告警
- Cron job 丢失 → 立即告警并尝试恢复

## 告警格式
```
🚨 [进程告警] Nginx:❌ | MySQL:✅ | PHP:✅ | Gateway:✅
🚨 [端口告警] 80:❌ | 443:❌
🔔 [Cron完整性] self-repair:存在 | proactive:存在 | evolution:存在
```

## 在心跳中使用
```python
# HEARTBEAT.md 中的快速检查
import subprocess
r = subprocess.run(['bash', '-c', 'ss -tlnp | grep ":80 "'], capture_output=True)
if not r.stdout.strip():
    feishu_alert("🚨 Nginx端口80 down!")
```

## 与其他系统的关系
- `.self-repair.py` 负责修复发现的异常
- `auto-monitor` 专注检测，不做修复（检测/告警职责分离）
- 发现问题 → 立即调用 `.self-repair.py` → 记录 → 推送

---
*最后更新: 2026-03-31 by Jarvis*
