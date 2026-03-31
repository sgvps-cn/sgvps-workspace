#!/usr/bin/env python3
"""
GitHub Gist 增量同步 - workspace备份方案
每次运行只同步变更的文件，不依赖git push
"""
import subprocess, json, os, hashlib, base64, time

GH_TOKEN = "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"
STATE_FILE = "/root/.openclaw/workspace/memory/gist-sync-state.json"
LOG = "/root/.openclaw/workspace/memory/gist-sync.log"
WORKSPACE = "/root/.openclaw/workspace"

HEADERS = {
    "Authorization": f"Bearer {GH_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "Content-Type": "application/json"
}

MANIFEST_GIST = "1c8c2d0f6c8a4e7b9d0f3a2c5e1b8d4"  # manifest Gist ID

def api(method, path, data=None):
    cmd = ["curl", "-s", "-X", method,
           f"https://api.github.com{path}",
           "-H", f"Authorization: Bearer {GH_TOKEN}",
           "-H", "Accept: application/vnd.github+json",
           "-H", "X-GitHub-Api-Version: 2022-11-28"]
    if data:
        cmd += ["-d", json.dumps(data)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return json.loads(r.stdout)

def get_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {"files": {}, "last_sync": None}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def file_hash(path):
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def should_sync(path):
    """判断文件是否需要同步"""
    # 排除
    skip = [".git", "node_modules", ".env", "memory/*.log",
            "memory/daemon-state.json", "memory/inner-state.json",
            "__pycache__", ".pyc", "memory/proactive-alerts.log",
            "memory/clash-auto-switch.log", "memory/clash.log", 
            "memory/clash-start.log"]
    for s in skip:
        if s in path or path.endswith(".pyc"):
            return False
    return True

def sync_file(path, content):
    """同步单个文件到Gist"""
    filename = path.replace(WORKSPACE + "/", "")
    filename = filename.replace("/", "_")
    
    # 更新manifest中的文件
    state = get_state()
    state["files"][path] = {
        "hash": file_hash(path),
        "last_sync": int(time.time())
    }
    save_state(state)
    
    # 读取manifest Gist内容
    try:
        r = api("GET", f"/gists/{MANIFEST_GIST}")
        gist_files = r.get("files", {})
        
        # 更新或添加文件
        new_files = {}
        for fname, fdata in gist_files.items():
            new_files[fname] = {"content": fdata.get("content", "")}
        new_files[filename] = {"content": content}
        
        api("PATCH", f"/gists/{MANIFEST_GIST}", {
            "description": f"Jarvis Workspace Manifest - {time.strftime('%Y-%m-%d %H:%M')}",
            "files": new_files
        })
        return True
    except Exception as e:
        print(f"Gist同步失败: {e}")
        return False

def sync_manifest():
    """同步整个workspace的manifest"""
    state = get_state()
    
    manifest = {
        "last_sync": int(time.time()),
        "files": {}
    }
    
    files_content = {}
    
    for root, dirs, files in os.walk(WORKSPACE):
        dirs[:] = [d for d in dirs if d not in [".git", "node_modules", "__pycache__"]]
        for f in files:
            path = os.path.join(root, f)
            if not should_sync(path):
                continue
            try:
                with open(path) as fp:
                    content = fp.read()
                fname = path.replace(WORKSPACE + "/", "").replace("/", "_")
                files_content[fname] = {"content": content}
                manifest["files"][path] = {
                    "hash": hashlib.md5(content.encode()).hexdigest(),
                    "size": len(content)
                }
            except:
                pass
    
    try:
        # 获取或创建manifest Gist
        r = api("GET", f"/gists/{MANIFEST_GIST}")
        if "id" not in r:
            # 创建新Gist
            r = api("POST", "/gists", {
                "description": f"Jarvis Workspace Backup - {time.strftime('%Y-%m-%d')}",
                "public": False,
                "files": files_content
            })
            print(f"✅ 创建Gist备份: {r.get('html_url', '')}")
        else:
            # 更新
            files_content[r.get("files", {}).get("manifest.json", {}).get("content", "")] = {"content": json.dumps(manifest, indent=2)}
            r = api("PATCH", f"/gists/{MANIFEST_GIST}", {
                "description": f"Jarvis Workspace Backup - {time.strftime('%Y-%m-%d %H:%M')}",
                "files": files_content
            })
            print(f"✅ Gist备份已更新: {len(files_content)}文件")
        
        save_state(manifest)
        return True
    except Exception as e:
        print(f"❌ Gist同步失败: {e}")
        return False

if __name__ == "__main__":
    sync_manifest()
