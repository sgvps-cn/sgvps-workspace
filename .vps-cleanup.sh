#!/bin/bash
# 贾维斯 VPS 维护脚本 - 每月执行
# 基于 vps-maintenance skill

WORKSPACE="/root/.openclaw/workspace"
LOG="$WORKSPACE/memory/vps-maintenance.log"

echo "=== VPS 维护 $(date) ===" >> "$LOG"

# 1. 系统状态
echo "[系统状态]" >> "$LOG"
uptime >> "$LOG"
free -h >> "$LOG"
df -h >> "$LOG"

# 2. 清理 apt 缓存
echo "[apt 清理]" >> "$LOG"
apt-get clean 2>/dev/null >> "$LOG"
apt-get autoremove -y 2>/dev/null >> "$LOG"

# 3. 清理日志（保留7天）
echo "[日志清理]" >> "$LOG"
journalctl --vacuum-time=7d 2>/dev/null >> "$LOG"

# 4. fail2ban 状态
echo "[Fail2Ban]" >> "$LOG"
systemctl is-active fail2ban 2>/dev/null >> "$LOG"
echo "Ban计数:" >> "$LOG"
fail2ban-client status sshd 2>/dev/null >> "$LOG" || echo "  sshd jail不存在" >> "$LOG"

# 5. 防火墙状态
echo "[防火墙]" >> "$LOG"
/usr/sbin/nft list ruleset 2>/dev/null >> "$LOG"

# 6. BBR 状态
echo "[BBR]" >> "$LOG"
sysctl net.ipv4.tcp_congestion_control 2>/dev/null >> "$LOG"

echo "---" >> "$LOG"
echo "完成于 $(date)" >> "$LOG"
