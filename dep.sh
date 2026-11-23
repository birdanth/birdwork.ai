#!/bin/bash
# push -> watch CI -> live-verify. prints one line.
cd /tmp/bwreview || exit 1
source ~/.nvm/nvm.sh
export PATH="$HOME/.local/bin:$PATH"
git push origin main || { echo "PUSH-FAILED"; exit 1; }
SHA=$(git rev-parse --short HEAD)
sleep 12
out=""
for i in $(seq 1 30); do
  out=$(gh run list --limit 1 --json databaseId,status,conclusion,headSha -q '.[0]|"\(.databaseId) \(.status) \(.conclusion)"' 2>/dev/null)
  case "$out" in *" completed "*) break;; esac
  sleep 10
done
RUN=$(echo "$out" | awk '{print $1}')
CONCL=$(echo "$out" | awk '{print $3}')
sleep 6
B=$(curl -s https://birdwork.ai/ | wc -c)
K=$(curl -s https://birdwork.ai/ | grep -c 'data-key=')
V=$(curl -s https://birdwork.ai/ | grep -c -- '--section-py')
H=$(curl -sI https://birdwork.ai/ | grep -ci 'content-security-policy\|strict-transport\|x-frame-options\|x-content-type\|referrer-policy\|permissions-policy')
printf 'DEPLOY sha=%s run=%s concl=%s liveBytes=%s dataKeys=%s layoutVar=%s secHeaders=%s\n' "$SHA" "$RUN" "$CONCL" "$B" "$K" "$V" "$H"
