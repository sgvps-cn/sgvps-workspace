#!/bin/bash
# sgvps.cn 每周自动生成2篇SEO文章
# 0 10 * * 3,6 /root/.openclaw/workspace/.sgvps-seo-auto-gen.sh

LOG="/root/.openclaw/workspace/memory/seo-auto-gen.log"
DB_HOST="127.0.0.1"
DB_USER="www_sgvps_cn"
DB_PASS="p6dd5z992Bpc8CQR"
DB_NAME="www_sgvps_cn"

echo "[$(date '+%Y-%m-%d %H:%M')] 开始生成SEO文章" >> "$LOG"

NOW=$(date +%s)

# 第一篇
TITLE1="服务器内存不足怎么办？4种排查方法与解决方案"
CONTENT1="<p>服务器内存不足是运维中最常见的问题之一。本文介绍四种实用的排查方法：</p><p><strong>1. 使用free命令查看内存使用</strong><br>执行<code>free -m</code>查看实际可用内存，Mem行显示total/used/free，如果available远小于free，说明内存被缓存占用。</p><p><strong>2. 使用top命令定位高内存进程</strong><br>执行<code>top</code>后按M按内存排序，找到RSS最大的进程。</p><p><strong>3. 检查MySQL配置</strong><br>MySQL默认配置可能占用大量内存，检查<code>innodb_buffer_pool_size</code>是否超过服务器内存的一半。</p><p><strong>4. PHP-FPM进程数过多</strong><br>PHP-FPM的max_children设置过大也会导致内存耗尽，合理设置<code>pm.max_children</code>。</p><p>如果您需要更专业的服务器方案，欢迎了解星耀云的托管服务。</p>"
mysql -u"$DB_USER" -p"$DB_PASS" -h"$DB_HOST" "$DB_NAME" -e "INSERT INTO shd_news (title, type_id, content, create_time, update_time, views, author) VALUES ('$TITLE1', 1, '$CONTENT1', $NOW, $NOW, 0, '星耀云');" 2>/dev/null && echo "[$(date '+%H:%M')] ✅ 已有: $TITLE1" >> "$LOG" || echo "[$(date '+%H:%M')] ❌ 失败: $TITLE1" >> "$LOG"

sleep 1

# 第二篇
TITLE2="CDN加速原理解析：为什么网站用了CDN还是慢？"
CONTENT2="<p>很多网站明明用了CDN加速，打开还是很慢。这是为什么？</p><p><strong>CDN工作原理</strong><br>CDN通过在全球部署边缘节点，让用户访问就近的节点，而不是回源站获取内容。节点会缓存静态资源。</p><p><strong>用了CDN还是慢的常见原因</strong></p><p>1. <strong>缓存未命中</strong>：动态内容无法缓存，每次都回源，源站慢整站就慢<br>2. <strong>源站带宽不足</strong>：CDN回源带宽小，大量并发时源站被打满<br>3. <strong>跨运营商访问</strong>：用户和CDN节点不在同一运营商<br>4. <strong>SSL握手慢</strong>：HTTPS额外握手时间</p><p><strong>正确优化建议</strong><br>启用页面缓存、优化源站性能、选择覆盖用户运营商的CDN节点。</p>"
mysql -u"$DB_USER" -p"$DB_PASS" -h"$DB_HOST" "$DB_NAME" -e "INSERT INTO shd_news (title, type_id, content, create_time, update_time, views, author) VALUES ('$TITLE2', 1, '$CONTENT2', $NOW, $NOW, 0, '星耀云');" 2>/dev/null && echo "[$(date '+%H:%M')] ✅ 已有: $TITLE2" >> "$LOG" || echo "[$(date '+%H:%M')] ❌ 失败: $TITLE2" >> "$LOG"

echo "[$(date '+%Y-%m-%d %H:%M')] 完成" >> "$LOG"
