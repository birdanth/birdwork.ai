#!/bin/bash
cd /tmp/bwreview || exit 1
source ~/.nvm/nvm.sh
export PATH="$HOME/.local/bin:$PATH"
git add -A
git -c user.name="T" -c user.email="t@birdwork.ai" commit -q -F - <<'MSG'
content(site): card 02 retitled to ROI; OpenClaw -> agentic LLM in card 02 body

Unit Economics -> ROI (matches the s/$ cadence of the other titles) and the
OpenClaw product name generalises to "agentic LLM fleet deployments".
MSG
git push origin main || { echo PUSH-FAILED; exit 1; }
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
H=$(curl -s https://birdwork.ai/)
P=0; for m in 'Harden &amp; Rollout — Security &amp; ROI' 'always-on agentic LLM fleet deployments'; do
  c=$(printf '%s' "$H" | grep -c -- "$m"); P=$((P+c)); done
N=0; for m in 'Unit Economics' 'always-on OpenClaw fleet'; do
  c=$(printf '%s' "$H" | grep -c -- "$m"); N=$((N+c)); done
printf 'LIVE sha=%s run=%s concl=%s pos=%s/2 neg=%s\n' "$SHA" "$RUN" "$CONCL" "$P" "$N"
