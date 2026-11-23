#!/usr/bin/env python3
"""Apply Tony's micro-edit batch to src/data/site.yaml with per-edit count asserts."""
import sys
p = 'src/data/site.yaml'
s = open(p).read()
edits = [
 # 1 nav brand
 ('  brand_bold: TONY\n  brand_thin: birdwork.ai',
  '  brand_bold: birdwork.ai\n  brand_thin: ""'),
 # 2 hero.tags
 ('  tags: [AI Architecture, Semantic Systems, Technical Enablement]',
  '  tags: [AI Systems, Knowledge Ontologies, Innovation Enablement]'),
 # 3 hero.sub (= "hero.lead")
 ('  sub: I design and build production AI systems, semantic data architectures, and the technical training teams need to use them. Twelve years as a computer engineer, founder, and Fractional CTO. I still write the code and still run the whiteboard.',
  '  sub: I design, build, &amp; rollout production AI systems, knowledge architectures, and train teams who need to use them. Twelve years as a computer engineer, founder, and Fractional CTO. I love to take things from whiteboard to scoreboard.'),
 # 4/5 hero ctas
 ('    - {label: VIEW PRODUCTION CASE STUDIES, href: "#case-studies", class: btn}',
  '    - {label: VIEW CASE STUDIES, href: "#case-studies", class: btn}'),
 ('    - {label: EXPLORE SEMANTICS &amp; R&amp;D, href: "#research", class: btn ghost}',
  '    - {label: EXPLORE SEMANTICS, href: "#research", class: btn ghost}'),
 # 6 work.eyebrow (= work.section_label)
 ('  eyebrow: How It Works', '  eyebrow: Modus Operandi'),
 # 7/8 work card titles
 ('      title: Build — Agentic &amp; Semantic Systems',
  '      title: Design &amp; Build — Agentic &amp; Semantic Systems'),
 ('      title: Harden — Security &amp; Unit Economics',
  '      title: Harden &amp; Rollout — Security &amp; Unit Economics'),
 # 9 rd.eyebrow (= rd.section_label)
 ('  eyebrow: R&amp;D · B.I. R&amp;D LLC', '  eyebrow: R&amp;D · Knowledge Engineering'),
 # 10 rd.lead first sentence
 ('  lead: Long-running AI systems degrade in production. Context windows bloat',
  '  lead: How do you maintain domain-specific context knowledge for your AI Agents in a human-manageable &amp; auditable way? Context windows bloat'),
 # 11 about.label (= about.h2)
 ('  label: Systems, Teaching, and Code.', '  label: Systems, Teaching, and Building.'),
 # 12/13 about.intro (= about.paras[0])
 ('interim CTO, and technical educator.', 'agentic engineer, and experienced educator.'),
 ('as a founder and fractional CTO,', 'as a founder and innovation leader,'),
 # 14 about.background (= about.creds[0].body)
 ('      body: B.S. in Computer Engineering with a Mathematics minor from Michigan State University, where I worked as a College of Engineering Teaching Assistant. I still teach STEM and foundational math independently. Explaining hard systems in plain English is half the job.',
  '      body: Computer Engineering B.S. &amp; Mathematics minor from Michigan State University, where I worked as a College of Engineering TA. I still teach STEM, foundational math, &amp; early childhood literacy independently. Explaining hard systems in plain English is half the job.'),
]
for i, (old, new) in enumerate(edits, 1):
    n = s.count(old)
    if n != 1:
        print('EDIT %d: count %d (want 1) :: %s' % (i, n, old[:60])); sys.exit(1)
    s = s.replace(old, new)
open(p, 'w').write(s)
print('applied %d edits' % len(edits))
