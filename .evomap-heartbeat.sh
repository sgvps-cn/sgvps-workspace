#!/bin/bash
# EvoMap Node Heartbeat Loop
# Keep node alive with 5-minute heartbeat

NODE_ID="node_d5f7e05f3abbc423"
NODE_SECRET="4bbaad422b71c3c4106dcedb6e7efd1549152bea5ea59d83e32db88c41d49f45"
HEARTBEAT_URL="https://evomap.ai/a2a/heartbeat"
INTERVAL=300  # 5 minutes in seconds

while true; do
  response=$(curl -s -X POST "$HEARTBEAT_URL" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $NODE_SECRET" \
    -d "{\"node_id\": \"$NODE_ID\"}" 2>&1)
  
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Heartbeat: $response"
  
  sleep $INTERVAL
done
