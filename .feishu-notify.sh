#!/bin/bash
# 统一飞书通知脚本 - 所有脚本都调用这个
# 用法: .feishu-notify.sh "消息内容"

TEXT="$1"
[ -z "$TEXT" ] && echo "需要消息内容" && exit 1

TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id":"cli_a943e4427838dcd1","app_secret":"rnYXkg925E6JQnPjq4splbAA7Q2Lyb5u"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('tenant_access_token',''))")

curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"receive_id\":\"ou_08ac6d09db0b76c0f90f4ef5e46cff78\",\"msg_type\":\"text\",\"content\":\"{\\\"text\\":\\"$TEXT\\"}\"}" \
  > /dev/null 2>&1

echo "✅ 已发送飞书通知"
