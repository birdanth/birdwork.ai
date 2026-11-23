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
