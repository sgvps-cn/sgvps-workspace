#!/usr/bin/env python3
import subprocess, json, re, sys

GLM_KEY = "45dc8c3daf834606ad863f7d8711fb1e.0oH7HauaYa7K5kDH"
PROXY = "http://127.0.0.1:7890"
API = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

def gen_article(title, prompt, keywords, desc):
    payload = {
        "model": "glm-4-flash",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1200,
        "temperature": 0.7
    }
    result = subprocess.run([
        "curl", "-s", "--max-time", "60", "--proxy", PROXY,
        API,
        "-H", f"Authorization: Bearer {GLM_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload)
    ], capture_output=True, text=True)
    
    try:
        d = json.loads(result.stdout)
        if "choices" in d and d["choices"]:
            c = d["choices"][0]["message"]["content"]
            c = re.sub(r"<html[^>]*>.*?<body[^>]*>", "", c, flags=re.DOTALL)
            c = re.sub(r"</body>.*</html>", "", c, flags=re.DOTALL)
            c = re.sub(r"<!DOCTYPE[^>]*>", "", c)
            c = re.sub(r"<head>.*</head>", "", c, flags=re.DOTALL)
            c = re.sub(r"<title>.*</title>", "", c)
            c = re.sub(r"^\s*```html\s*", "", c)
            c = re.sub(r"^\s*```\s*$", "", c)
            return c.strip()
    except:
        pass
    return None

def sql_escape(s):
    return s.replace("\\", "\\\\").replace("'", "\\'")

def run_sql(sql):
    r = subprocess.run(["mysql", "-u", "www_sgvps_cn", "-pp6dd5z992Bpc8CQR", "-h", "127.0.0.1", "www_sgvps_cn", "-e", sql], capture_output=True, text=True)
    return r.returncode == 0

articles = [
    {
        "title": "香港服务器CN2线路全面解析：如何选择适合自己的线路方案",
        "prompt": "请写一篇600字的SEO文章，标题是《香港服务器CN2线路全面解析：如何选择适合自己的线路方案》，面向需要出海服务器的技术人员和中小企业主。内容：1.CN2线路是什么 2.CN2 GT和CN2 GIA的区别（用表格对比）3.如何判断需要哪种 4.购买注意事项。HTML格式，段落<p>，小标题<h2>，表格<table>。只输出文章内容，不要其他说明。",
        "keywords": "CN2线路,香港服务器,GIA,GT,线路选择",
        "desc": "星耀云详解香港服务器CN2线路，区分CN2 GT与CN2 GIA的区别，帮助企业选择最适合的线路方案。"
    },
    {
        "title": "服务器被DDoS攻击了怎么办？高防服务器选购指南",
        "prompt": "请写一篇600字的SEO文章，标题是《服务器被DDoS攻击了怎么办？高防服务器选购指南》，面向正在使用服务器或即将购买服务器的企业主。内容：1.DDoS攻击的常见类型和危害 2.如何判断自己正在被攻击 3.高防服务器的核心参数（防御量、清洗能力）4.选购建议和避坑指南。HTML格式，段落<p>，小标题<h2>。只输出文章内容，不要其他说明。",
        "keywords": "DDoS攻击,高防服务器,服务器防护,CC攻击",
        "desc": "星耀云介绍DDoS攻击防护知识，帮企业了解高防服务器的核心参数和选购技巧，保障业务稳定运行。"
    },
    {
        "title": "企业上云前必须考虑的5个问题：资深运维经验分享",
        "prompt": "请写一篇600字的SEO文章，标题是《企业上云前必须考虑的5个问题：资深运维经验分享》，面向计划迁移上云的中小企业CTO和技术负责人。内容：1.业务连续性如何保障 2.数据安全与合规要求 3.成本预估（不只是云费用，还有运维和迁移成本）4.供应商锁定风险 5.技术团队能力储备。HTML格式，段落<p>，小标题<h2>。只输出文章内容，不要其他说明。",
        "keywords": "企业上云,云迁移,云计算,运维经验",
        "desc": "资深运维分享企业上云前必须考虑的5个关键问题，帮助中小企业规避云迁移风险，降低上云成本。"
    }
]

for art in articles:
    content = gen_article(art["title"], art["prompt"], art["keywords"], art["desc"])
    if not content or len(content) < 50:
        print(f"❌ 生成失败: {art['title']}")
        continue
    
    # 找新relid
    r = subprocess.run(["mysql", "-u", "www_sgvps_cn", "-pp6dd5z992Bpc8CQR", "-h", "127.0.0.1", "www_sgvps_cn", "-N", "-e", "SELECT MAX(relid) FROM shd_news"], capture_output=True, text=True)
    max_relid = int(r.stdout.strip() or 0)
    new_relid = max_relid + 1
    
    # 写入菜单
    ok1 = run_sql(f"INSERT INTO shd_news_menu (id, admin_id, parent_id, title, keywords, description, hidden, sort, create_time) VALUES ({new_relid}, 1, 1, '{sql_escape(art['title'])}', '{art['keywords']}', '{sql_escape(art['desc'])}', 0, 0, 1774906563)")
    
    # 写入内容
    ok2 = run_sql(f"INSERT INTO shd_news (relid, content) VALUES ({new_relid}, '{sql_escape(content)}')")
    
    if ok1 and ok2:
        print(f"✅ 已生成: {art['title']} (relid={new_relid}, {len(content)}字)")
    else:
        print(f"❌ 写入失败: {art['title']}")

print("完成")
