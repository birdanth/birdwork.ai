#!/bin/bash
cd /tmp/bwreview || exit 1
source ~/.nvm/nvm.sh
export PATH="$HOME/.local/bin:$PATH"
git add -A
git -c user.name="T" -c user.email="t@birdwork.ai" commit -q -F - <<'MSG'
content(site): agent-harness / RBAC positioning pass

Tony's batch 2: hero + work card bodies + lead case body reframed around custom
agent harnesses, RBAC, container isolation and health/redundancy checks; stack
matrix gains Agent harness engineering and OpenClaw (on-prem / always-on) +
failing checks; security lead rewritten to the RBAC/audit-log claim.
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
P=0; for m in 'production AI systems, custom agent harnesses' 'Custom agent harnesses, multi-agent workflows' 'On-prem and always-on OpenClaw fleet deployments' 'Five always-on agents running inside a custom harness' 'Agent harness engineering' 'OpenClaw (on-prem / always-on)' 'RBAC &amp;amp; failover checks' 'Built for HIPAA, SOC 2, and regulated governance.'; do
  c=$(curl -s https://birdwork.ai/ | grep -c -- "$m"); P=$((P+c)); done
N=0; for m in 'Multi-agent workflows, RAG, formal' 'Environment isolation, PII redaction' 'Five coordinated agents on client infrastructure' 'Designed for HIPAA, SOC 2'; do
  c=$(curl -s https://birdwork.ai/ | grep -c -- "$m"); N=$((N+c)); done
printf 'LIVE sha=%s run=%s concl=%s pos=%s/8 neg=%s\n' "$SHA" "$RUN" "$CONCL" "$P" "$N"
