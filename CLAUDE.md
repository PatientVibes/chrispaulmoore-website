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

## Current progress (2026-04-24)

- **First draft essay:** `drafts/agent-harness-commitment-curve.md` (~2,650 words). Thesis: the 12-component agent-harness taxonomy from [Alex Ker's X post](https://x.com/thealexker/status/2045203785304232162) is better read as a **commitment curve** than a checklist. Components 1–6 are a foundation; 7–12 are discretionary investments justified by the axiom set of the deployment. Applied across two agents — `chorus-agent` (SS&C AI Gateway, enterprise/regulated) and `kindle-pipeline` (local Ollama, personal). Closes on an unresolved tension around token tracking.
- The essay intentionally does **not** pitch, sell, or propose a new framework. It applies Alex Ker's taxonomy honestly and notes where it bends.
- Both case studies draw from `D:\ai-agents\` on `hal-windows` (`chorus-agent/`, `kindle-pipeline/`). Karakeep (on `haldev`) is the article ingestion path feeding kindle-pipeline via nightly SMB export.
- Draft not yet reviewed by Chris. Not linked from the site.

## Next steps (when Chris returns)

1. Fresh-eye review of the draft. Factual corrections on chorus-agent and kindle-pipeline details (inferred from repo READMEs — verify).
2. Decide: ship as-is, trim, expand, or rewrite.
3. Pick the second piece of content. Strong candidates:
   - **Karakeep → Kindle pipeline** as constraint-first engineering (hardware, format, context-window constraints shaping the design).
   - **The homelab as an axiom set** (7 services, zero exposed ports, one shared Postgres — what emerges from that constraint set).
4. Decide publishing venue for the essay. Current default: new blog section on this site once rebuilt. Alternatives: GitHub gist, personal substack, LinkedIn article.
5. Start the `index.html` rebuild only after step 3.

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
