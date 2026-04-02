#!/usr/bin/env bash
# Deploy birdwork.com to Cloudflare Pages via Direct Upload API
set -euo pipefail

CF_ACCOUNT_ID="5fb1be728b47c260542d53c6cb07d7aa"
CF_PROJECT="birdwork"
CF_TOKEN="${CF_API_TOKEN:-$(cat ~/.secrets/cf-pages-token 2>/dev/null || echo '')}"

if [ -z "$CF_TOKEN" ]; then
  echo "ERROR: No CF API token found. Set CF_API_TOKEN env var or create ~/.secrets/cf-pages-token"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEPLOY_DIR="$SCRIPT_DIR"

echo "==> Creating deployment..."
DEPLOY_RESPONSE=$(curl -s -X POST \
  "https://api.cloudflare.com/client/v4/accounts/${CF_ACCOUNT_ID}/pages/projects/${CF_PROJECT}/deployments" \
  -H "Authorization: Bearer ${CF_TOKEN}" \
  -H "Content-Type: multipart/form-data" \
  -F "index.html=@${DEPLOY_DIR}/index.html;type=text/html" \
  -F "favicon.ico=@${DEPLOY_DIR}/favicon.ico;type=image/x-icon" \
  -F "logo.png=@${DEPLOY_DIR}/logo.png;type=image/png" \
  -F "logo-white.png=@${DEPLOY_DIR}/logo-white.png;type=image/png" \
  -F "logo-dark.png=@${DEPLOY_DIR}/logo-dark.png;type=image/png")

SUCCESS=$(echo "$DEPLOY_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('success', False))" 2>/dev/null || echo "parse_error")
URL=$(echo "$DEPLOY_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('result',{}).get('url',''))" 2>/dev/null || echo "")

if [ "$SUCCESS" = "True" ]; then
  echo "==> Deployed successfully!"
  echo "    URL: $URL"
  echo "    Live: https://birdwork.pages.dev"
else
  echo "==> Deploy failed!"
  echo "$DEPLOY_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$DEPLOY_RESPONSE"
  exit 1
fi
