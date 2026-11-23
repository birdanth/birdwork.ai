#!/bin/bash
cd /tmp/bwreview || exit 1
source ~/.nvm/nvm.sh
export PATH="$HOME/.local/bin:$PATH"
git add -A
git -c user.name="T" -c user.email="t@birdwork.ai" commit -q -F - <<'MSG'
content(site): Tony's copy batch — brand, hero, work/rd section labels, about

Micro-edit batch applied to src/data/site.yaml, index.html regenerated.
- nav brand -> birdwork.ai (drop TONY)
- hero tags/lead/CTAs rewritten
- work section label -> Modus Operandi; card 01 Build -> Design & Build, 02 Harden -> Harden & Rollout
- rd section label -> R&D · Knowledge Engineering; rd lead opens on the maintainability question
- about h2 -> Systems, Teaching, and Building.; intro noun swaps; Background body rewritten (MSU, TA, early childhood literacy)
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
P=0; for m in 'Knowledge Ontologies' 'Modus Operandi' 'Design &amp; Build — Agentic' 'Harden &amp; Rollout' 'R&amp;D · Knowledge Engineering' 'Systems, Teaching, and Building.' 'innovation leader,' 'early childhood literacy' 'VIEW CASE STUDIES' 'EXPLORE SEMANTICS' 'class="brand">birdwork.ai'; do
  c=$(curl -s https://birdwork.ai/ | grep -c -- "$m"); P=$((P+c)); done
N=0; for m in 'VIEW PRODUCTION CASE STUDIES' 'EXPLORE SEMANTICS &amp; R&amp;D' 'How It Works' 'B.I. R&amp;D LLC' 'Systems, Teaching, and Code.' 'interim CTO, and technical educator' 'College of Engineering Teaching Assistant'; do
  c=$(curl -s https://birdwork.ai/ | grep -c -- "$m"); N=$((N+c)); done
printf 'LIVE sha=%s run=%s concl=%s pos=%s/11 neg=%s\n' "$SHA" "$RUN" "$CONCL" "$P" "$N"
