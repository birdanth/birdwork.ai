# AGENTS.md — birdwork.ai

Repo-level instructions for agents editing this site.

## Copy & Voice Standard — "The Tony Test" (Mandatory on All Site Copy)
Apply these five rules to every headline, subheadline, card, metadata tag, and UI string:
1. **No clever slogans or antithesis:** Never use SaaS taglines ("X for the part after Y", "Not just A, B", "Built for speed and substance") or quips before technical facts.
2. **No consultant abstractions:** Ban filler like "measurable velocity", "three-pillar discipline", "bridging rigor", "high-impact engagements", "turn AI noise into...", "synergistic", "passionate", "thought leader".
3. **Short declarative sentences:** Write like Hemingway. Cut em-dash chains—split compound thoughts into two plain sentences.
4. **Concrete nouns and active verbs:** Prefer `built`, `cut`, `taught`, `shipped`, `ran`, `compacts`, `catches` over `leveraged`, `spearheaded`, `empowered`, `enabled`, `facilitated`.
5. **Facts carry the claim:** State the engineering problem, the mechanism, and the verified number plainly. Omit overly granular trivia (e.g., college GPA, course numbers) unless explicitly requested.

## Editing Rules
- Single-file static site (`index.html`). No bundler, no npm/npx/pnpm.
- Preserve the design system: fonts (`Cormorant Garamond`, `Inter`, `JetBrains Mono`), color tokens, spacing, layout grids, dark/light toggle.
- Keep head/SEO as literal HTML tags, never JS-injected.
- Client anonymization: `Mid-Size 3PL Brokerage`, `Enterprise People Analytics SaaS`, `Enterprise Communications & Payment Technology`. Never name Ally Logistics, never mention Sacred Spaces, Docere Noscere Universalis, Wyzant, GitHub or a personal phone number.
- Verify with `node --check` on the inline script, JSON-LD parse, tag balance, and width overflow at 320/375/768/1440 before committing.

## Editing content — the manifest refactor

`index.html` is **generated**. Do not hand-edit it: the build overwrites it.

    src/data/site.yaml   all copy, lists, labels, links, and spacing
    src/template.html    page shell — {{tokens}}, {{#each}}, {{#if}}, {{> partials}}
    src/partials/*.html  the four diagram pairs and the R&D flow diagram
    scripts/build.mjs    the build (plain node, no dependencies, no npm)
    index.html           output — committed, deployed

### Loop
    1. edit src/data/site.yaml   (only file needed for copy / list / label / space changes)
    2. node scripts/build.mjs    (or `--check` to validate without writing)
    3. git add src index.html && git commit
    4. push to main -> GitHub Action validates, builds, deploys to Cloudflare Pages
    5. on the live URL append ?ids=1 -> every editable block is badged with its YAML key
       (zero marks when ?ids is absent)

### Revert
    git checkout -- src/data/site.yaml && node scripts/build.mjs && commit
Evaluate `?ids=1` FIRST so a good edit is not lost to a revert. Rollback of a
shipped change is `git revert <sha>` + push (never force-push).

### Rules the build enforces (fatal, named errors)
    * unknown `{{token}}` -> unresolved token error
    * malformed YAML, duplicate keys, bad indentation -> error
    * a missing required field (site.email, hero.h1, cases.items[].client, ...) -> error
    * `layout.<el>.<prop>` with an unknown prop or a value that is neither a
      scale token (0 xs sm md lg xl 2xl) nor a CSS length -> error
    * banned tokens (Sacred Spaces, Docere Noscere, Wyzant, github.com, Ally
      Logistics, GPA) present anywhere -> error

### Labels
`<section>.label` drives BOTH the navbar link and the section heading.
`<section>.nav_label` (optional) overrides the navbar link only.
`<section>.eyebrow` is the small uppercase line above the heading.
Never hardcode a nav label in the template — it resolves from the section.

### Spacing
Micro-layout lives in `layout:` at the bottom of the YAML, one custom property
per entry (`--element-prop`). Prefer a scale token; a raw CSS length is allowed
for values that are already live. Layout is additive: each `var()` carries the
old literal as its fallback, so nothing shifts until a token is edited.

### CLI
    node scripts/build.mjs           # validate + write index.html
    node scripts/build.mjs --check   # validate only, write nothing (exit 1 on error)

## Telegram Micro-Edit Protocol

Tony sends a batch as chat lines; each line is one micro-edit. All target
`src/data/site.yaml` only. Reply is terse: only the diff lines, then
`build: ok | push? (y/n)` — nothing else, max 8 lines.

Grammar:

    key > value                      set scalar
    key: old > new                   surgical substring replace in one value
    key.(mb|mt|pb|pt|py|gap) +/-     step one scale slot  (- - = 1 step, -- = 2)
    + key: item                      append to a list
    - key: item                      remove a list item / section line
    key ~ instruction                freeform; obey The Tony Test (notes/banned a #)

Rules:

    * `key` is a YAML path, dotted (`hero.h1`, `layout.work.lead.mb`, `cases.items[0].metric`).
    * spacing steps walk `[0, xs, sm, md, lg, xl, 2xl]` and write the step name;
      `val` values are read from the built page when quoting a change, never guessed.
    * a line ending in `!` = auto-commit AND push, but only if the build passes;
      if the build fails on a `!` line, stop and wait for `y`/`n`.
    * no `!` = apply, build, report the diff, ask `push? (y/n)`.
    * on `n`: `git checkout -- src/data/site.yaml` and rebuild — nothing else is touched.
    * re-read `src/data/site.yaml` fresh before every batch; never trust a remembered value.
    * verify with `?ids=1` on the live URL to find the exact key for a visual change.
