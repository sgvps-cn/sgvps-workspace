#!/bin/bash
# sgvps.cn 自动生成SEO文章 - GLM-4-Flash驱动
# 每周三、六 11点执行
# 0 11 * * 3,6 /root/.openclaw/workspace/.sgvps-article-gen.sh

GLM_KEY="45dc8c3daf834606ad863f7d8711fb1e.0oH7HauaYa7K5kDH"
PROXY="http://127.0.0.1:7890"
API_HOST="https://open.bigmodel.cn/api/paas/v4"
DB_HOST="127.0.0.1"
DB_USER="www_sgvps_cn"
DB_PASS="p6dd5z992Bpc8CQR"
DB_NAME="www_sgvps_cn"
LOG="/root/.openclaw/workspace/memory/article-gen.log"

echo "[$(date '+%Y-%m-%d %H:%M')] 开始生成SEO文章" >> "$LOG"

gen_article() {
    local topic="$1"
    local prompt="$2"
    local title="$3"
    local keywords="$4"
    local desc="$5"
    
    # 调用GLM API
    local content=$(curl -s --max-time 60 --proxy "$PROXY" \
        "$API_HOST/chat/completions" \
        -H "Authorization: Bearer $GLM_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"glm-4-flash\",
            \"messages\": [{\"role\": \"user\", \"content\": \"$prompt\"}],
            \"max_tokens\": 1200,
            \"temperature\": 0.7
        }" | python3 -c "
import sys,json,re
d=json.load(sys.stdin)
if 'choices' in d and d['choices']:
    c=d['choices'][0]['message']['content']
    c=re.sub(r'<html[^>]*>.*?<body[^>]*>','',c,flags=re.DOTALL)
    c=re.sub(r'</body>.*</html>','',c,flags=re.DOTALL)
    c=re.sub(r'<!DOCTYPE[^>]*>','',c)
    c=re.sub(r'<head>.*</head>','',c,flags=re.DOTALL)
    c=re.sub(r'<title>.*</title>','',c)
    print(c.strip())
else:
    print('ERROR')
" 2>/dev/null)
    
    if [ "$content" = "ERROR" ] || [ ${#content} -lt 100 ]; then
        echo "[$(date '+%H:%M')] ❌ 生成失败: $title" >> "$LOG"
        return 1
    fi
    
    # 转义
    content_esc=$(echo "$content" | sed "s/'/\\\\'/g")
    
    # 找下一个可用relid
    local max_relid=$(mysql -u"$DB_USER" -p"$DB_PASS" -h"$DB_HOST" "$DB_NAME" -N -e "SELECT MAX(relid) FROM shd_news" 2>/dev/null)
    local new_relid=$((max_relid + 1))
    
    # 新建菜单项
    mysql -u"$DB_USER" -p"$DB_PASS" -h"$DB_HOST" "$DB_NAME" << EOF 2>/dev/null
INSERT INTO shd_news_menu (id, admin_id, parent_id, title, keywords, description, hidden, sort, create_time)
VALUES ($new_relid, 1, 1, '$title', '$keywords', '$desc', 0, 0, UNIX_TIMESTAMP());
INSERT INTO shd_news (relid, content) VALUES ($new_relid, '$content_esc');
EOF
    
    if [ $? -eq 0 ]; then
        echo "[$(date '+%H:%M')] ✅ 已生成: $title (${#content}字, relid=$new_relid)" >> "$LOG"
    else
        echo "[$(date '+%H:%M')] ❌ 写入失败: $title" >> "$LOG"
    fi
}

# 两篇不同主题的文章
gen_article \
    "CN2线路" \
    "请写一篇600字的SEO文章，标题是《香港服务器CN2线路全面解析：如何选择适合自己的线路方案》，面向需要出海服务器的技术人员和中小企业主。内容包含：1.CN2线路到底是什么 2.CN2 GT和CN2 GIA的区别 3.如何判断自己需要哪种线路 4.购买时的注意事项。要求：专业实用，有对比表格。用HTML格式，段落用<p>，小标题用<h2>，如有表格用<table>。只输出文章内容，不要任何其他说明。" \
    "香港服务器CN2线路全面解析：如何选择适合自己的线路方案" \
    "CN2线路,香港服务器,GIA,GT,线路选择" \
    "星耀云详解香港服务器CN2线路，区分CN2 GT与CN2 GIA的区别，帮助企业选择最适合的线路方案。"

sleep 5

gen_article \
    "DDoS防护" \
    "请写一篇600字的SEO文章，标题是《服务器被DDoS攻击了怎么办？高防服务器选购指南》，面向正在使用服务器或即将购买服务器的企业主。内容包含：1.DDoS攻击的常见类型和危害 2.如何判断自己正在被攻击 3.高防服务器的核心参数（防御量、清洗能力）4.选购建议和避坑指南。要求：实际可操作，有参考价值。用HTML格式，段落用<p>，小标题用<h2>。只输出文章内容，不要任何其他说明。" \
    "服务器被DDoS攻击了怎么办？高防服务器选购指南" \
    "DDoS攻击,高防服务器,服务器防护,CC攻击" \
    "星耀云介绍DDoS攻击防护知识，帮企业了解高防服务器的核心参数选购技巧，保障业务稳定运行。"

echo "[$(date '+%Y-%m-%d %H:%M')] 完成" >> "$LOG"
