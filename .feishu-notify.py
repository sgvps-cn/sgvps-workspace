#!/usr/bin/env python3
"""飞书统一通知脚本"""
import subprocess, json, sys

APP_ID = "cli_a943e4427838dcd1"
APP_SECRET = "rnYXkg925E6JQnPjq4splbAA7Q2Lyb5u"
USER_ID = "ou_08ac6d09db0b76c0f90f4ef5e46cff78"

def get_token():
    r = subprocess.run(
        ["/usr/bin/curl", "-s", "-X", "POST",
         "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
         "-H", "Content-Type: application/json",
         "-d", '{"app_id":"cli_a943e4427838dcd1","app_secret":"rnYXkg925E6JQnPjq4splbAA7Q2Lyb5u"}'
        ], capture_output=True, text=True, timeout=10
    )
    try:
        return json.loads(r.stdout).get("tenant_access_token", "")
    except:
        return ""

def send(text):
    token = get_token()
    if not token:
        print("FAIL: token")
        return False
    payload = json.dumps({
        "receive_id": USER_ID,
        "msg_type": "text",
        "content": json.dumps({"text": text})
    })
    r = subprocess.run(
        ["/usr/bin/curl", "-s", "-X", "POST",
         "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
         "-H", "Authorization: Bearer " + token,
         "-H", "Content-Type: application/json",
         "-d", payload
        ], capture_output=True, text=True, timeout=10
    )
    try:
        result = json.loads(r.stdout)
        if result.get("code") == 0:
            print("OK")
            return True
        else:
            print("FAIL: " + str(result.get("msg", "")))
            return False
    except:
        print("FAIL: parse")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 .feishu-notify.py <text>")
        sys.exit(1)
    send(sys.argv[1])
