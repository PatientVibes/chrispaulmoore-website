# chrispaulmoore-website

Personal site for Chris Moore. Deploys via GitHub Pages (CNAME → `chrispaulmoore.com`). Cloudflare handles DNS plus the `comments.chrispaulmoore.com` subdomain (Cloudflare Worker in `cloudflare-worker.js`, `wrangler.toml`). No build step — plain HTML served from root.

## Active project: site refresh

Refresh the site from its current professional-portfolio framing into a **personal hub** built around a **systems-thinker / constraint-based-discovery** positioning.

### Positioning

- **Not a consulting pitch.** No "hire me" CTAs.
- **Not a generic portfolio template** either (avoid Work / About / Contact).
- Chris's worldview, articulated during planning: *pick a constraint set (axioms), follow where they lead, the structure that emerges is the work. Solutions are points on a branch, not destinations.* This comes from his math background (proofs, analysis, abstract algebra) and how he already thinks about Blue Prism Chorus, agent harnesses, his homelab, and D&D.
- The site should **demonstrate** the lens applied to real systems. The homepage frames. The content proves.
- Four surfaces worth covering over time: enterprise / BPM work, agent harness & AI, homelab / home ops, narrative-and-game design.
- Division of domains: **chrispaulmoore.com** is identity / writing / systems thinking; **patientvibes.io** is where project-specific work lives.

### Design reference

- High-fidelity brief lives at `~/Downloads/chrispaulmoore.com.zip` → `design_handoff_chrispaulmoore_homepage/`. Direction B: BPMN-style SVG diagrams, hairline blueprint grid, IBM Plex typography, amber-once-per-viewport, near-zero motion.
- The visual vocabulary fits the systems-thinker positioning. Content needs repositioning from the brief's consulting framing:
  - §01 Practice → the three (or four) axiom systems Chris thinks through, not three consulting pillars.
  - §02 Selected work → case studies framed around constraint → structure, not dollar impact.
  - §03 Outcomes strip (`$15M+` / `40%` etc.) → probably drop. Dollar flex is wrong for a hub.
  - §05 The Lab → grows. Absorbs writing, reading, D&D.
  - §06 Connect → CTA replaced by a link row (GitHub, LinkedIn, patientvibes.io, email).

### Stack

Stay on the current stack. Vanilla HTML + inline `<style>` + inline SVG. The Direction B brief is a static design — no framework needed to render it, and the current GitHub Pages deploy has zero operational overhead.

### Order of operations

1. **Content first, site second.** The homepage is a display case. At least one finished piece of content should exist before the site rebuild starts — otherwise the redesign ships empty.
2. Review and finalize the current draft (see "Current progress" below).
3. Draft a second piece if needed.
4. Rebuild `index.html` using Direction B visual vocabulary with repositioned content.

## Current state (2026-04-27)

- **Direction B rebuild shipped.** `index.html` is the constraint-based-discovery hub: BPMN-style hero diagram (Constraint → Structure), three axiom-system pillars (Enterprise/BPM, Agents/AI, Home Ops), §02 essay cards, §04 homelab topology updated for the current 12-service stack with Karakeep highlighted, §05 Lab cards, link-row footer. §03 Outcomes dropped per the repositioning brief.
- **Two essays published** at `essays/<slug>.html`:
  - `essays/agent-harness-commitment-curve.html` — applies Alex Ker's 12-component taxonomy to `chorus-agent` (regulated) and `kindle-pipeline` (local). Reframes 1–6 as floor and 7–12 as a commitment curve earned by the constraint set.
  - `essays/karakeep-kindle-pipeline.html` — companion piece. Six-axiom derivation of the Karakeep → Kindle Scribe pipeline, with the SMB share as the seam between halves.
  - Both essays passed a 12-agent editorial review (developmental, line, copy, technical fact-check, first reader, headline ×2). Factual claims verified against source repos on hal-windows and haldev.
- **Build pipeline.** `build-essays.py` reads `drafts/*.md` and writes Direction B-styled `essays/<slug>.html` using `essay-template.html`. Mermaid blocks render client-side via mermaid.js v10. Run `python3 build-essays.py` after editing any draft.
- Source-of-truth markdown lives in `drafts/`. `MANIFEST` in the build script controls essay numbering and tag.
- Cross-essay links: each essay's footer links to the other.

## Active backlog

1. **Third piece of content.** Strong candidates per earlier planning: *the homelab as an axiom set* (12-service stack, zero exposed ports, what falls out of those constraints) or *D&D as constraint design* (encounter design as constraint propagation; named in §05 of the homepage).
2. **Distribution / packaging.** Original titles are best for on-post / personal-blog. Per the headline-editor reviews, alternative titles exist for HN and social — keep canonical on-post and use alternates for distribution.
3. **AI-agent harness for the editorial team.** Earlier conversation parked: an AI version of the 6-role review team (developmental / line / copy / technical / first-reader / headline) as a reusable harness for future essays.
4. **OG image.** Currently points at `family-photo.jpg` from the old site. Direction B brief recommends a custom OG image in the same visual vocabulary; not built yet.

## Files not to touch without asking

- `homelab.html` — separate subpage, out of refresh scope
- `wiki.html`, `wiki-viewer.html`, `docsify.html` — separate docsify-powered wiki
- `cloudflare-worker.js`, `wrangler.toml` — comments system, deploys independently
- `CNAME` — DNS config, do not rename or delete
- `family-photo.jpg` — current hero image; may or may not survive the refresh, ask first

## Related context

- Global conventions in `~/CLAUDE.md`: use `npx wrangler` (not global), never hardcode tokens, user manages gh/op/Cloudflare auth separately.
- GitHub MCP server available for repo ops (`mcp__github__*` tools).
- Memory index at `~/.claude/projects/-home-patientvibes/memory/MEMORY.md` has persistent notes on haldev setup, 1Password workflows, and LAN topology.
