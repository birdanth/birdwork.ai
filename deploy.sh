#!/usr/bin/env bash
# Deploy birdwork.ai to Cloudflare Pages via Direct Upload API (v2 manifest format)
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

# Build manifest: hash each file, upload via the newer direct-upload flow
# Step 1: Create hashes for each file
echo "==> Hashing files..."
declare -A FILE_HASHES
MANIFEST="{"
FIRST=true
for f in index.html favicon.ico logo.png logo-white.png logo-dark.png; do
  FILEPATH="${DEPLOY_DIR}/${f}"
  if [ ! -f "$FILEPATH" ]; then
    echo "WARNING: $f not found, skipping"
    continue
  fi
  HASH=$(sha256sum "$FILEPATH" | cut -d' ' -f1)
  FILE_HASHES["$f"]="$HASH"
  if [ "$FIRST" = true ]; then
    FIRST=false
  else
    MANIFEST+=","
  fi
  MANIFEST+="\"/${f}\":\"${HASH}\""
done
MANIFEST+="}"

echo "==> Manifest: $MANIFEST"

# Step 2: Upload files and create deployment with manifest
echo "==> Uploading and deploying..."

# Build the curl command with manifest + all files
CURL_CMD="curl -s -X POST \
  \"https://api.cloudflare.com/client/v4/accounts/${CF_ACCOUNT_ID}/pages/projects/${CF_PROJECT}/deployments\" \
  -H \"Authorization: Bearer ${CF_TOKEN}\" \
  -F \"manifest=${MANIFEST}\""

for f in index.html favicon.ico logo.png logo-white.png logo-dark.png; do
  FILEPATH="${DEPLOY_DIR}/${f}"
  if [ -f "$FILEPATH" ]; then
    HASH="${FILE_HASHES[$f]}"
    CURL_CMD+=" -F \"${HASH}=@${FILEPATH}\""
  fi
done

DEPLOY_RESPONSE=$(eval $CURL_CMD)

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
