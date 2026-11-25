#!/usr/bin/env python3
"""Batch 2: agent-harness / RBAC positioning. Asserts one match per edit."""
import sys
p = 'src/data/site.yaml'
s = open(p).read()
edits = [
 # 1 hero.sub (= hero.lead)
 ('I design, build, &amp; rollout production AI systems, knowledge architectures,',
  'I design, build, &amp; rollout production AI systems, custom agent harnesses, knowledge architectures,'),
 # 2 work.cards[0].body
 ('      body: Multi-agent workflows, RAG,', '      body: Custom agent harnesses, multi-agent workflows, RAG,'),
 # 3 work.cards[1].body
 ('      body: Environment isolation, PII redaction, human-in-the-loop gates, tiered model routing, and context pruning.',
  '      body: On-prem and always-on OpenClaw fleet deployments, RBAC, container isolation, PII redaction, HITL gates, automated health and redundancy checks, tiered model routing, and context pruning.'),
 # 4 cases.items[0].body
 ('      body: Five coordinated agents on client infrastructure, giving',
  '      body: Five always-on agents running inside a custom harness on client infrastructure, with RBAC, automated health and redundancy checks, and giving'),
 # 5 stack.ai (+ = append, " · " separated)
 ('      p: Multi-agent orchestration · context engineering · RAG · GraphRAG · formal ontologies · LLM evaluation · Qwen · HITL',
  '      p: Multi-agent orchestration · context engineering · RAG · GraphRAG · formal ontologies · LLM evaluation · Qwen · HITL · Agent harness engineering'),
 # 6+7 stack.infra (+ x2)
 ('      p: GPU compute · Docker · CI/CD · Salesforce · Slack/Teams · LogRhythm',
  '      p: GPU compute · Docker · CI/CD · Salesforce · Slack/Teams · LogRhythm · OpenClaw (on-prem / always-on) · RBAC &amp; failover checks'),
 # 8 security.lead
 ('  lead: Designed for HIPAA, SOC 2, and regulated governance — every agent capability is scoped, logged, and reversible.',
  '  lead: Built for HIPAA, SOC 2, and regulated governance. Every agent runs with RBAC, scoped permissions, automated health and redundancy checks, and full audit logs.'),
]
for i, (old, new) in enumerate(edits, 1):
    n = s.count(old)
    if n != 1:
        print('EDIT %d: count %d (want 1) :: %s' % (i, n, old[:70])); sys.exit(1)
    s = s.replace(old, new)
open(p, 'w').write(s)
print('applied %d edits' % len(edits))
