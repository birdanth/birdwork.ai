#!/usr/bin/env bash
# Deploy birdwork.ai to Cloudflare Pages via Direct Upload API (v2 manifest format)
# Dynamic: every deployable file is discovered, so new assets (headshot, og-image,
# _redirects, _headers, SEO files) are never silently skipped.
set -euo pipefail

CF_ACCOUNT_ID="5fb1be728b47c260542d53c6cb07d7aa"
CF_PROJECT="birdwork"
CF_TOKEN="${CF_API_TOKEN:-$(cat ~/.secrets/cf-pages-token 2>/dev/null || echo '')}"

if [ -z "$CF_TOKEN" ]; then
  echo "ERROR: No CF API token found. Set CF_API_TOKEN env var or create ~/.secrets/cf-pages-token"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Collect deployable files: everything except VCS/metadata
list_files() {
  find . -type f \
    -not -path './.git/*' \
    -not -path './.github/*' \
    -not -name '.gitignore' \
    -not -name '.gitattributes' \
    -not -name 'deploy.sh' \
    -not -name '.DS_Store' \
    -not -name 'Thumbs.db' \
    -not -name '*.Zone.Identifier' \
    | sed 's|^\./||' | sort
}

mapfile -t FILES < <(list_files)
if [ "${#FILES[@]}" -eq 0 ]; then
  echo "ERROR: no files to deploy"
  exit 1
fi

echo "==> ${#FILES[@]} files to deploy"

declare -A FILE_HASHES
MANIFEST="{"
FIRST=true
for f in "${FILES[@]}"; do
  HASH=$(sha256sum "$f" | cut -d' ' -f1)
  FILE_HASHES["$f"]="$HASH"
  if [ "$FIRST" = true ]; then FIRST=false; else MANIFEST+=","; fi
  MANIFEST+="\"/${f}\":\"${HASH}\""
done
MANIFEST+="}"

echo "==> Manifest built"

CURL_CMD="curl -s -X POST \
  \"https://api.cloudflare.com/client/v4/accounts/${CF_ACCOUNT_ID}/pages/projects/${CF_PROJECT}/deployments\" \
  -H \"Authorization: Bearer ${CF_TOKEN}\" \
  -F \"manifest=${MANIFEST}\""

for f in "${FILES[@]}"; do
  CURL_CMD+=" -F \"${FILE_HASHES[$f]}=@${SCRIPT_DIR}/${f}\""
done

echo "==> Uploading and deploying..."
DEPLOY_RESPONSE=$(eval "$CURL_CMD")

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
