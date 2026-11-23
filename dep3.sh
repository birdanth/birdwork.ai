#!/bin/bash
cd /tmp/bwreview || exit 1
source ~/.nvm/nvm.sh
export PATH="$HOME/.local/bin:$PATH"
node scripts/build.mjs --check || { echo "BUILD-FAIL"; exit 1; }
node scripts/build.mjs >/dev/null || { echo "BUILD-FAIL"; exit 1; }
git add -A
git -c user.name="T" -c user.email="t@birdwork.ai" commit -q -F - <<'MSG'
content(site): work-lead spacing token; layout supports nested paths

Tony: `layout.work.lead.mb +` (0 -> xs, +8px under the operating-model lead).
Engine now walks `layout.<path...>.<prop>` -> `--<path>-<prop>`, so a token can
be scoped to one element instead of the whole class. Documented in AGENTS.md and
the manifest header. Scoped: rd/finops/security leads unchanged.
MSG
git push origin main || { echo "PUSH-FAILED"; exit 1; }
SHA=$(git rev-parse --short HEAD)
sleep 12
out=""
for i in $(seq 1 30); do
  out=$(gh run list --limit 1 --json databaseId,status,conclusion -q '.[0]|"\(.databaseId) \(.status) \(.conclusion)"' 2>/dev/null)
  case "$out" in *" completed "*) break;; esac
  sleep 10
done
RUN=$(echo "$out" | awk '{print $1}'); CONCL=$(echo "$out" | awk '{print $3}')
sleep 6
V=$(curl -s https://birdwork.ai/ | grep -c -- '--work-lead-mb')
S=$(curl -s https://birdwork.ai/ | grep -c -- '#operating-model .lede{margin-bottom:var(--work-lead-mb,0)}')
printf 'LIVE sha=%s run=%s concl=%s varRefs=%s scopedRule=%s\n' "$SHA" "$RUN" "$CONCL" "$V" "$S"
