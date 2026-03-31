#!/bin/bash
# sgvps.cn SEO文章自动生成 - 基于SEO Skill规范（Python调用GLM）
# 每周三、六 11点执行
# 0 11 * * 3,6 /root/.openclaw/workspace/.sgvps-article-gen.sh

LOG="/root/.openclaw/workspace/memory/article-gen.log"
PYTHON="/usr/bin/python3"

echo "[$(date '+%Y-%m-%d %H:%M')] === SEO文章生成开始 ===" >> "$LOG"

$PYTHON << 'PYEOF' 2>&1 | tee -a "$LOG"
import subprocess, json, re, sys

GLM_KEY = "YOUR_GLM_KEY_HERE"
PROXY = "http://127.0.0.1:7890"
API_HOST = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
DB = {"host":"127.0.0.1","user":"www_sgvps_cn","pass":"p6dd5z992Bpc8CQR","name":"www_sgvps_cn"}

def glm_generate(prompt, max_tokens=1500):
    """调用GLM API生成内容"""
    payload = json.dumps({
        "model": "glm-4-flash",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7
    })
    r = subprocess.run(
        ["/usr/bin/curl", "-s", "--max-time", "90", "--proxy", PROXY,
         API_HOST,
         "-H", f"Authorization: Bearer {GLM_KEY}",
         "-H", "Content-Type: application/json",
         "-d", payload],
        capture_output=True, text=True, timeout=100
    )
    try:
        d = json.loads(r.stdout)
        if "choices" in d and d["choices"]:
            return d["choices"][0]["message"]["content"]
    except:
        pass
    return None

def clean_html(raw):
    """清理API返回的HTML，移除wrapper标签，保留正文结构"""
    # 移除 <html><body> 等包装标签
    raw = re.sub(r'<html[^>]*>.*?<body[^>]*>', '', raw, flags=re.DOTALL)
    raw = re.sub(r'</body>.*?</html>', '', raw, flags=re.DOTALL)
    raw = re.sub(r'<!DOCTYPE[^>]*>', '', raw)
    raw = re.sub(r'<head>.*?</head>', '', raw, flags=re.DOTALL)
    raw = re.sub(r'<title>.*?</title>', '', raw, flags=re.DOTALL)
    
    # 移除代码块标记 ```html ... ```
    raw = re.sub(r'^```html\s*', '', raw, flags=re.MULTILINE)
    raw = re.sub(r'^```\s*$', '', raw, flags=re.MULTILINE)
    
    # 移除行首行尾的空白
    raw = raw.strip()
    
    # 保留 <p> <h2> <h3> <h4> <ul> <ol> <li> <table> <tr> <th> <td> <tbody> <thead> <strong> <b> <a> <br> <blockquote>
    # 其他标签全部移除
    allowed = {'p','h2','h3','h4','ul','ol','li','table','tr','th','td','tbody','thead',
               'strong','b','a','br','blockquote'}
    def replace_tag(m):
        tag = m.group(1).lower().split()[0]
        if tag in allowed:
            return m.group(0)
        return ''
    raw = re.sub(r'<(\w+)[^>]*>', replace_tag, raw)
    
    # 清理多余空白行
    lines = raw.split('\n')
    cleaned = []
    for line in lines:
        line = line.strip()
        if line:
            cleaned.append(line)
    
    result = '\n'.join(cleaned)
    
    # 移除文章内容中的H1（每页只应有一个H1，来自页面标题）
    # 处理 </h1> 后的真实换行（ASCII 10）
    result = re.sub(r'<h1[^>]*>.*?</h1>\s*', '', result, flags=re.DOTALL | re.IGNORECASE)
    
    # 验证基本结构
    if '<p>' not in result and '<h2>' not in result:
        return None
    if len(result) < 300:
        return None
    return result

def mysql_insert(relid, title, keywords, desc, content, cid=1):
    """写入数据库"""
    now_ts = int(__import__('time').time())
    content_esc = content.replace("'", "''")
    title_esc = title.replace("'", "''")
    keywords_esc = keywords.replace("'", "''")
    desc_esc = desc.replace("'", "''")
    
    sql = f"INSERT INTO shd_news_menu (id,admin_id,parent_id,title,keywords,description,hidden,sort,create_time,update_time) VALUES ({relid},1,{cid},'{title_esc}','{keywords_esc}','{desc_esc}',0,0,{now_ts},{now_ts});INSERT INTO shd_news (relid,content) VALUES ({relid},'{content_esc}');"
    
    r = subprocess.run(
        ["/usr/bin/mysql", "-u", DB["user"], f"-p{DB['pass']}", "-h", DB["host"], DB["name"],
         "-e", sql],
        capture_output=True, text=True, timeout=15
    )
    return r.returncode == 0

def get_next_relid():
    r = subprocess.run(
        ["/usr/bin/mysql", "-u", DB["user"], f"-p{DB['pass']}", "-h", DB["host"], DB["name"],
         "-N", "-e", "SELECT IFNULL(MAX(id),0)+1 FROM shd_news_menu"],
        capture_output=True, text=True, timeout=10
    )
    try:
        return int(r.stdout.strip())
    except:
        return 1

# ─── SEO文章主题（基于SEO Skill规范）─────────────────────────────────────────
ARTICLES = [
    {
        "topic": "香港服务器CN2",
        "title": "香港服务器CN2线路全面解析：如何选择适合自己的线路方案",
        "keywords": "CN2线路,香港服务器,GIA,GT,线路选择,服务器租用",
        "desc": "星耀云详解香港服务器CN2线路，区分CN2 GT与CN2 GIA的区别，帮助企业选择最适合的线路方案。",
        "prompt": """请为星耀云官网写一篇600字的SEO文章。

要求：
1. 文章标题：香港服务器CN2线路全面解析：如何选择适合自己的线路方案
2. 文章开头（前100字）必须直接回答：香港服务器CN2线路是什么、为什么重要
3. H2章节（3-4个），包含：CN2线路基本概念、CN2 GT与GIA区别、如何选择线路、购买注意事项
4. 结尾FAQ（3个常见问题）：什么情况需要CN2线路？/ GIA比GT贵多少？/ 如何测试线路质量？
5. 结尾CTA：选择星耀云，体验高速稳定的香港服务器服务
6. 每个章节用<H2>，段落用<P>，列表用<UL><LI>，对比用<TABLE>
7. 文章主体不要使用<H1>标签（标题已在meta中）
8. LSI关键词自然融入：回国线路、163骨干网、网络优化、BGP线路
9. 只输出HTML正文内容，不要任何说明文字，不要代码块标记"""
    },
    {
        "topic": "DDoS防护",
        "title": "服务器被DDoS攻击了怎么办？高防服务器选购指南",
        "keywords": "DDoS攻击,高防服务器,服务器防护,CC攻击,流量清洗",
        "desc": "星耀云介绍DDoS攻击防护知识，帮企业了解高防服务器的核心参数和选购技巧，保障业务稳定运行。",
        "prompt": """请为星耀云官网写一篇600字的SEO文章。

要求：
1. 文章标题：服务器被DDoS攻击了怎么办？高防服务器选购指南
2. 文章开头（前100字）必须直接回答：什么是DDoS攻击、为什么危险
3. H2章节（3-4个），包含：DDoS攻击类型与危害、如何判断正在被攻击、高防服务器核心参数、选购建议
4. 结尾FAQ（3个常见问题）：DDoS攻击能完全防御吗？/ 防御多少G够用？/ 高防服务器价格范围？
5. 结尾CTA：星耀云提供T级DDoS防护，保障业务稳定运行
6. 每个章节用<H2>，段落用<P>，列表用<UL><LI>
7. 文章主体不要使用<H1>标签（标题已在meta中）
8. LSI关键词自然融入：CC攻击、流量清洗、防御峰值、攻击特征、硬防方案
9. 只输出HTML正文内容，不要任何说明文字，不要代码块标记"""
    }
]

# ─── 生成并发布 ────────────────────────────────────────────────────────────────
for article in ARTICLES:
    topic = article["topic"]
    title = article["title"]
    keywords = article["keywords"]
    desc = article["desc"]
    prompt = article["prompt"]
    
    print(f"生成中: {title}", flush=True)
    
    # 调用GLM生成
    raw = glm_generate(prompt, max_tokens=1500)
    if not raw:
        print(f"  ❌ API调用失败", flush=True)
        continue
    
    # 清理HTML
    content = clean_html(raw)
    if not content:
        print(f"  ❌ 内容格式验证失败", flush=True)
        print(f"  原始前100字: {raw[:100]}", flush=True)
        continue
    
    print(f"  生成完成: {len(content)}字节", flush=True)
    
    # 写入数据库
    relid = get_next_relid()
    if mysql_insert(relid, title, keywords, desc, content):
        print(f"  ✅ 已发布: {title} (id={relid})", flush=True)
    else:
        print(f"  ❌ 数据库写入失败", flush=True)

print("全部完成", flush=True)
PYEOF

echo "[$(date '+%Y-%m-%d %H:%M')] === SEO文章生成完成 ===" >> "$LOG"
