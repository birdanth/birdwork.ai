#!/usr/bin/env python3
"""Generate src/template.html from the current index.html.

Mechanical and assert-guarded: every replacement must match exactly the expected
number of times, so a drifted live file fails loudly rather than producing a
silently wrong template.
"""
import re

import sys, os
SRC_FILE = sys.argv[1] if len(sys.argv) > 1 else "index.html"
src = open(SRC_FILE).read()
log = []

def R(old, new, n=1):
    global src
    got = src.count(old)
    assert got == n, f'expected {n} got {got} for: {old[:70]!r}'
    src = src.replace(old, new, n)
    log.append((n, old[:58]))

# ---------------------------------------------------------------- svg -> include ---
for fig in ('01', '02', '03', '04'):
    m = re.search(r'<svg class="diagram diagram-light" data-fig="%sl".*?</svg>\n<svg class="diagram diagram-dark" data-fig="%sd".*?</svg>' % (fig, fig), src, re.S)
    assert m, fig
    R(m.group(0), '{{> diagram-%s}}' % fig)

flows = re.findall(r'<svg class="flow[^"]*"[^>]*>.*?</svg>', src, re.S)
assert len(flows) == 2, len(flows)
R(flows[0] + '\n      ' + flows[1], '{{> rd-flow}}')

# --------------------------------------------------------------------- head / seo ---
DESC = ('I design and build production AI systems, semantic data architectures, and the technical '
        'training teams need to use them. Twelve years as a computer engineer, founder, and '
        'Fractional CTO. I still write the code and still run the whiteboard.')
TITLE = 'Tony Bird | AI Architecture, Semantic Systems &amp; Technical Enablement'

R('<title>%s</title>' % TITLE, '<title>{{seo.title}}</title>')
R('content="%s"' % DESC, 'content="{{seo.description}}"', 3)
R('<meta property="og:site_name" content="Tony Bird">', '<meta property="og:site_name" content="{{site.full_name}}">')
R('<meta name="author" content="Tony Bird">', '<meta name="author" content="{{site.full_name}}">')
R('<link rel="canonical" href="https://birdwork.ai/">', '<link rel="canonical" href="https://{{site.domain}}/">')
R('<meta property="og:title" content="%s">' % TITLE, '<meta property="og:title" content="{{seo.title}}">')
R('<meta property="og:url" content="https://birdwork.ai/">', '<meta property="og:url" content="https://{{site.domain}}/">')
R('<meta property="og:image" content="https://birdwork.ai/og-image.png">', '<meta property="og:image" content="https://{{site.domain}}/og-image.png">')
R('content="Tony Bird — AI Systems Architect, Semantics and Technical Enablement, birdwork.ai"', 'content="{{seo.og_image_alt}}"')
R('<meta name="twitter:title" content="%s">' % TITLE, '<meta name="twitter:title" content="{{seo.title}}">')
R('<meta name="twitter:image" content="https://birdwork.ai/og-image.png">', '<meta name="twitter:image" content="https://{{site.domain}}/og-image.png">')
R('<meta name="twitter:image:alt" content="%s">' % TITLE, '<meta name="twitter:image:alt" content="{{seo.twitter_image_alt}}">')

R('"name": "Tony Bird"', '"name": "{{site.full_name}}"')
R('"url": "https://birdwork.ai/"', '"url": "https://{{site.domain}}/"')
R('"email": "mailto:bird@birdwork.ai"', '"email": "mailto:{{site.email}}"')
R('"jobTitle": "AI Systems Architect, Semantics & Technical Enablement"', '"jobTitle": "{{seo.job_title}}"')
R('"name": "Michigan State University"', '"name": "{{seo.university}}"')
R('"sameAs": ["https://www.linkedin.com/in/anthonymbird/"]', '"sameAs": ["{{site.linkedin_url}}"]')

# -------------------------------------------------------------------------- nav ---
R('<a href="#hero" class="brand">TONY<span>&thinsp;&thinsp;birdwork.ai</span></a>',
  '<a href="#hero" class="brand">{{nav.brand_bold}}<span>&thinsp;&thinsp;{{nav.brand_thin}}</span></a>')

NAVLINKS = ('<a href="#case-studies">Case Studies</a><a href="#operating-model">How I Work</a>'
            '<a href="#context-finops" class="nav-ctx">Context FinOps</a><a href="#security">Security</a>'
            '<a href="#research">R&amp;D</a><a href="#about">About</a>')
NAVLOOP = '{{#each nav.links}}<a href="{{href}}"{{#if class}} class="{{class}}"{{/if}}>{{label}}</a>{{/each}}'
R(NAVLINKS + '<a href="#connect">Connect</a>', NAVLOOP + '<a href="{{nav.connect.href}}">{{nav.connect.label}}</a>')
R(NAVLINKS, NAVLOOP, 2)
R('<a href="#connect">Connect</a>', '<a href="{{nav.connect.href}}">{{nav.connect.label}}</a>')
R('<p class="drawer-meta">bird@birdwork.ai · Grand Rapids, MI</p>', '<p class="drawer-meta">{{nav.drawer_meta}}</p>')

# ------------------------------------------------------------------------- hero ---
R('<p class="hero-eyebrow">AI Architecture · Semantic Systems · Technical Enablement</p>',
  '<p class="hero-eyebrow" data-key="hero.tags">{{join hero.tags " · "}}</p>')
R("<h1>Tony Bird's Work</h1>", '<h1 data-key="hero.h1">{{hero.h1}}</h1>')
R('<p class="sub">%s</p>' % DESC, '<p class="sub" data-key="hero.sub">{{hero.sub}}</p>')
R('      <a href="#case-studies" class="btn">VIEW PRODUCTION CASE STUDIES</a>\n'
  '      <a href="#research" class="btn ghost">EXPLORE SEMANTICS &amp; R&amp;D</a>\n',
  '{{#each hero.ctas}}      <a href="{{href}}" class="{{class}}">{{label}}</a>\n{{/each}}')

# ------------------------------------------------------------------------ stats ---
R('    <div class="stat"><b>30 Days</b><span>Kickoff to 24/7 prod · 5 agents · 5.7M Salesforce records</span></div>\n'
  '    <div class="stat"><b>50%+</b><span>LLM FinOps savings · 68% prompt cache hit rate</span></div>\n'
  '    <div class="stat"><b>97.5%</b><span>Faster enterprise deploy · 480h to 12h</span></div>\n'
  '    <div class="stat"><b>$3.5M</b><span>Direct C-suite SaaS closed · 10K+ DAU</span></div>\n',
  '{{#each stats.items}}    <div class="stat"><b>{{b}}</b><span>{{span}}</span></div>\n{{/each}}')

# ----------------------------------------------------------- operating ("work") ---
R('<p class="section-label">How It Works</p>', '<p class="section-label" data-key="work.eyebrow">{{work.eyebrow}}</p>')
R('<h2>How I Work</h2>', '<h2 data-key="work.label">{{work.label}}</h2>')
R('<p class="lede">Build it cleanly. Make it safe and cheap to run. Teach the team to own it.</p>',
  '<p class="lede" data-key="work.lead">{{work.lead}}</p>')
cards = re.findall(r'      <div class="cell card">.*?</div>\n', src, re.S)
assert len(cards) == 3, len(cards)
R(''.join(cards),
  '{{#each work.cards}}      <div class="cell card"><span class="num">{{num}}</span>'
  '<h3>{{title}}</h3><p>{{body}}</p><div class="card-proof"><ul>'
  '{{#each proof}}<li>{{.}}</li>{{/each}}</ul></div></div>\n{{/each}}')

# ------------------------------------------------------------------------ cases ---
R('<p class="section-label">Selected Enterprise Work</p>',
  '<p class="section-label" data-key="cases.eyebrow">{{cases.eyebrow}}</p>')
R('<h2>Systems in production.</h2>', '<h2 data-key="cases.label">{{cases.label}}</h2>')

lead_old = src[src.index('      <article class="work-card">\n        <p class="client"><span data-site="client.logistics">'):]
lead_old = lead_old[:lead_old.index('\n\n      <article class="work-card">\n        <p class="client"><span data-site="client.peopleAnalytics">')+2]
fulls = re.findall(r'      <article class="work-card">\n        <p class="client">[^\n]*\n        <p class="metric">.*?\n      </article>\n\n', src, re.S)
assert len(fulls) == 3, len(fulls)
wide_old = src[src.index('      <article class="work-card wide">'):]
wide_old = wide_old[:wide_old.index('    </div>')]

CARD_TOP = '      <article class="work-card">\n'
CLIENT = '        <p class="client">{{#if client_key}}<span data-site="{{client_key}}">{{/if}}{{client_fallback}}{{#if client_key}}</span>{{/if}}</p>\n'
METRIC = '        <p class="metric">{{metric}}{{#if metric_tail}} <span class="nw">{{metric_tail}}</span>{{/if}}{{#if metric_tail_2}} <span class="nw">{{metric_tail_2}}</span>{{/if}}</p>\n'

cases_new = (
  '{{#each cases.items}}{{#if is_lead}}' + CARD_TOP + CLIENT
  + '        <p class="role">{{role}}</p>\n        <p class="card-body">{{body}}</p>\n      </article>\n\n{{/if}}'
  + '{{#if is_full}}' + CARD_TOP + CLIENT + METRIC
  + '        <p class="role">{{role}}</p>\n        <ul>\n{{#each bullets}}          <li>{{.}}</li>\n{{/each}}        </ul>\n'
  + '        <p class="tag">{{tag}}</p>\n      </article>\n\n{{/if}}'
  + '{{#if is_wide}}      <article class="work-card wide">\n        <div class="wide-a">\n'
  + '          <p class="client">{{client_fallback}}</p>\n'
  + '          <p class="metric">{{metric}}{{#if metric_tail}} <span class="nw">{{metric_tail}}</span>{{/if}}</p>\n        </div>\n'
  + '        <div class="wide-b">\n          <p class="role">{{role}}</p>\n          <ul>\n'
  + '{{#each bullets}}            <li>{{.}}</li>\n{{/each}}          </ul>\n        </div>\n'
  + '        <p class="tag">{{tag}}</p>\n      </article>\n\n{{/if}}{{/each}}'
)
R(lead_old + ''.join(fulls) + wide_old, cases_new)

# ----------------------------------------------------------------------- finops ---
R('<p class="section-label">Context Engineering</p>', '<p class="section-label" data-key="finops.eyebrow">{{finops.eyebrow}}</p>')
R('<h2>Context Engineering &amp; LLM FinOps</h2>', '<h2 data-key="finops.label">{{finops.label}}</h2>')
R('<p class="lede">Measured production improvements across model routing, context budgets, and prompt caching.</p>',
  '<p class="lede" data-key="finops.lead">{{finops.lead}}</p>')

cols = re.findall(r'      <div class="stack-col"><h4>.*?</div>\n', src, re.S)
assert len(cols) == 3, len(cols)
R(''.join(cols),
  '{{#each stack.columns}}      <div class="stack-col"><h4>{{h4}}</h4><p>{{p}}</p></div>\n{{/each}}')

# --------------------------------------------------------------------- security ---
R('<p class="section-label">Zero-Trust Agentic Security</p>', '<p class="section-label" data-key="security.eyebrow">{{security.eyebrow}}</p>')
R('<h2>Secure by default, governed by policy.</h2>', '<h2 data-key="security.label">{{security.label}}</h2>')
R('<p class="lede">Designed for HIPAA, SOC 2, and regulated governance — every agent capability is scoped, logged, and reversible.</p>',
  '<p class="lede" data-key="security.lead">{{security.lead}}</p>')

# --------------------------------------------------------------------------- rd ---
R('<p class="section-label">R&amp;D · B.I. R&amp;D LLC</p>', '<p class="section-label" data-key="rd.eyebrow">{{rd.eyebrow}}</p>')
R('<h2>Knodes &amp; Kore</h2>', '<h2 data-key="rd.label">{{rd.label}}</h2>')
R('<p class="lede">Long-running AI systems degrade in production. Context windows bloat, reasoning drifts across sessions, and teams lose auditability when schemas or models change. Knodes and Kore solve those long-term system management and performance problems at the data layer.</p>',
  '<p class="lede" data-key="rd.lead">{{rd.lead}}</p>')
R('      <p class="rd-meta"><span>Audit-replayable</span>·<span>Regulated-env shaped</span>·<span>Model-agnostic</span>·<span>Open research</span></p>',
  '      <p class="rd-meta" data-key="rd.meta"><span>{{join rd.meta "</span>·<span>"}}</span></p>')

# ------------------------------------------------------------------------ about ---
R('<p class="section-label">About</p>', '<p class="section-label" data-key="about.eyebrow">{{about.eyebrow}}</p>')
R('<h2>Systems, Teaching, and Code.</h2>', '<h2 data-key="about.label">{{about.label}}</h2>')
R('<p>Enterprise AI architect, interim CTO, and technical educator. Twelve-plus years as a founder and fractional CTO, including a 20-person organization and $3.5M in enterprise SaaS contracts. I rebuild delivery and ship production agent systems.</p>',
  '{{#each about.paras}}<p>{{.}}</p>{{/each}}')
creds = re.findall(r'          <li><strong>.*?</li>\n', src, re.S)
assert len(creds) == 3, len(creds)
R(''.join(creds),
  '{{#each about.creds}}          <li><strong>{{head}}</strong>: {{body}}</li>\n{{/each}}')

# -------------------------------------------------------------- about+connect CTA ---
CTA_ABOUT = ('          <a href="mailto:bird@birdwork.ai" class="btn" data-href="email">Email Tony</a>\n'
             '          <a href="https://www.linkedin.com/in/anthonymbird/" class="btn ghost" data-href="linkedin" target="_blank" rel="noopener noreferrer">Connect on LinkedIn</a>\n')
CTA_CONNECT = ('      <a href="mailto:bird@birdwork.ai" class="btn" data-href="email">Email Tony</a>\n'
               '      <a href="https://www.linkedin.com/in/anthonymbird/" class="btn ghost" data-href="linkedin" target="_blank" rel="noopener noreferrer">Connect on LinkedIn</a>\n')
CTA_TPL = ('<a href="{{href}}" class="{{class}}"{{#if data_href}} data-href="{{data_href}}"{{/if}}'
           '{{#if external}} target="_blank" rel="noopener noreferrer"{{/if}}>{{label}}</a>')
R(CTA_ABOUT, '{{#each about.ctas}}' + '          ' + CTA_TPL + '\n{{/each}}')
R(CTA_CONNECT, '{{#each connect.ctas}}' + '      ' + CTA_TPL + '\n{{/each}}')

# ---------------------------------------------------------------------- connect ---
R('<p class="section-label">Connect</p>', '<p class="section-label" data-key="connect.eyebrow">{{connect.eyebrow}}</p>')
R('<h2>Work Together</h2>', '<h2 data-key="connect.label">{{connect.label}}</h2>')
R('<p>Open to Principal or Founding AI Architecture roles, AI Curriculum and Enablement leadership, and focused fractional advisory work. Remote or West Michigan. Send a note with what you are trying to build or fix.</p>',
  '<p data-key="connect.body">{{connect.body}}</p>')
R('      <span class="nw" data-site="location">Grand Rapids, MI · US &amp; Remote</span> · <span class="nw">© 2026 Tony Bird</span> · <span class="nw">birdwork.ai</span>',
  '      <span class="nw" data-site="location">{{connect.meta.0}}</span> · <span class="nw">{{connect.meta.1}}</span> · <span class="nw">{{connect.meta.2}}</span>')

# ----------------------------------------------------------------------- footer ---
R('<span>Tony Bird — AI Architecture &amp; Technical Enablement · birdwork.ai</span>', '<span>{{footer.blurb}}</span>')
R('<div class="foot-meta"><span>Available for new engagements</span><span>© 2026 Tony Bird</span></div>',
  '<div class="foot-meta"><span>{{footer.meta.0}}</span><span>{{footer.meta.1}}</span></div>')

# --------------------------------------------------------------------- SITE json ---
R(re.search(r'const SITE = \{.*?\n\};', src, re.S).group(0), 'const SITE = {{site_json}};')

# ----------------------------------------------------------------- layout wiring ---
LAYOUT_RULES = """
/* --- layout manifest: every value below is a --prop with the old literal as its
   fallback, so the manifest is additive and nothing shifts until you edit it. --- */
{{layout_css}}
section{padding-top:var(--section-py,8.5rem);padding-bottom:var(--section-py,8.5rem)}
h2{margin-bottom:var(--h2-mb,1.4rem)}
.section-label{margin-bottom:var(--section-label-mb,1.4rem)}
.lede{margin-bottom:var(--lede-mb,0)}
.work-grid{margin-top:var(--work-grid-mt,0)}
.cards-3{margin-top:var(--cards3-mt,0)}
.stack{margin-top:var(--stack-mt,0)}
.stats{padding:var(--stats-py,3.5rem) 0;gap:var(--stats-gap,2rem)}
.rd{margin-top:var(--rd-mt,1.75rem)}
.rd-meta{margin-top:var(--rd-meta-mt,1.4rem)}
.diagram-wrap{margin-top:var(--diagram-wrap-mt,2.6rem)}
.about-wrap{gap:var(--about-wrap-gap,2.75rem)}
.connect{padding-bottom:var(--connect-pb,5.5rem)}
.hero-eyebrow{margin-bottom:var(--hero-eyebrow-mb,1.9rem)}
.hero h1{margin-bottom:var(--hero-h1-mb,1.6rem)}
.hero p.sub{margin-bottom:var(--hero-sub-mb,2.5rem)}
.idbadge{position:absolute;top:0;left:0;transform:translateY(-105%);font-family:'JetBrains Mono',monospace;font-size:9px;line-height:1.6;letter-spacing:.03em;padding:0 5px;background:var(--accent-warm);color:#fff;border-radius:3px;pointer-events:none;z-index:9;white-space:nowrap}
@media(max-width:900px){section{padding-top:var(--section-mobile-py,5rem);padding-bottom:var(--section-mobile-py,5rem)}.stats{gap:var(--stats-mobile-gap,2.25rem)}.about-wrap{gap:var(--about-wrap-mobile-gap,2rem)}}
</style>"""
R('</style>\n</head>', LAYOUT_RULES + '\n</head>')

# -------------------------------------------------------------------- id badges ---
IDS_JS = """<script>
// ?ids=1 paints the YAML key of every editable block (zero effect otherwise)
(function(){
  if(!/[?&]ids=1(?:&|$)/.test(location.search)) return;
  document.querySelectorAll('[data-key]').forEach(function(el){
    if(getComputedStyle(el).position === 'static') el.style.position = 'relative';
    var b = document.createElement('span');
    b.className = 'idbadge'; b.textContent = el.getAttribute('data-key'); b.setAttribute('aria-hidden','true');
    el.appendChild(b);
  });
})();
</script>
</body>"""
R('</body>', IDS_JS)

open('src/template.html', 'w').write(src)
print('template bytes', len(src), '| replacements', len(log))
