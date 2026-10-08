# chrispaulmoore-website

Personal site for Chris Paul Moore. Static HTML, no build step for the homepage.
Deploys via **GitHub Pages** from `main`; `CNAME` points the apex at
`chrispaulmoore.com`. Cloudflare handles DNS.

The `comments.chrispaulmoore.com` Worker was **retired on 2026-10-07**: nothing
used it, it held one test comment, and its public `GET /comments` returned
commenters' IP addresses. The Worker, its route, its DNS record and both KV
namespaces were deleted in Cloudflare, and the source is in git history.

## What this site is now (2026-10-07)

A **personal page drawn as a library catalog card**. One card: name, a short
description, a "subjects" line, and the links as numbered tracings at the
bottom. The user asked for "a nice personal page for myself" that links to
everything else, and picked this look from three mocked-up directions.

It is deliberately **not**:

- a blog or an essay feed. Writing is moving to **patientvibes.io**.
- a list of self-hosted services. Those are reached through one link,
  "III. Restricted — my apps", to `dash.chrispaulmoore.com`. That dashboard
  sits behind Authentik and derives its service list from Docker, so this
  page never has to name a service.
- a dashboard, topology diagram, status page, or AI-agent portal.

### The rule that matters

**Nothing on this page states a number or a list that has to be maintained.**

The 2026-05 version rendered a hand-written homelab topology ("12 services,
12/12 green") listing services that had been decommissioned, and it stayed
wrong for three months. The generated `homelab.html` that replaced it was
removed on 2026-10-07: it was never automated, and a service list doesn't
belong on a personal page. If something here would need updating when the
homelab changes, it should not be here.

The call number (`CPM / KC / 2026`) and the imprint year mark when this design
went up. They are not a counter, so leave them alone.

## Design

- Desk `#4A3B2E`, card `#F1EADB`, ink `#26221C`, catalog red `#B3322A`; a
  full dark variant via `prefers-color-scheme`.
- **Courier Prime** for the card text, **Libre Caslon Text** italic for the
  title line only.
- The card details are real catalog-card conventions: the red rule across the
  top, the rod hole at the bottom, the call number top left, the subject
  headings, and Roman-numeral tracings. Keep it to one card. If the links
  outgrow about six tracings, add a "see also" line, not a second design.
- The "Sign-in" stamp marks links that need an Authentik login.
- Print stylesheet prints the card with URLs written out.
- Subject headings use real Library of Congress forms where one exists
  ("Books and reading", "Kansas City Current (Soccer team)", "KTBG (Radio
  station : Kansas City, Mo.)").
- No scripts, no analytics, no tracking.

## Layout of the repo

| Path | Status |
|---|---|
| `index.html` | **The site.** Includes a CSS-only "View as MARC record" view: the card is `id="marc"`, so `#marc` (`:target`) swaps it for the same record as MARC 21 fields. **Keep the two views in sync**: any change to the card's text, subjects or links needs the matching MARC field (520, 650/610, 856). |
| `404.html` | GitHub Pages' not-found page: a "Card not found" catalog card. Its styles are a copy of `index.html`'s minus the MARC block, so update both when the card design changes. |
| `essays/*.html` | Still served so inbound links keep working, but not linked from the homepage. **Migrating to patientvibes.io.** Once they are live there, replace these with redirects (GitHub Pages: a meta-refresh page per essay) rather than deleting them. |
| `drafts/*.md`, `build-essays.py`, `essay-template.html` | Essay pipeline. Goes with the essays when they move. |
| `CNAME` | DNS. Do not rename or delete. |
| `family-photo.jpg` | Not on the page; still the `og:image`. |

## Open decisions (not actioned — ask first)

1. **Essay migration.** Redirects once patientvibes.io has them (see above).
2. **OG image** is still `family-photo.jpg`. A typographic card in the
   catalog-card style would match the page.

## Conventions

- Vanilla HTML with an inline `<style>`. No framework, no bundler, no CSS file.
- Never hardcode tokens.
- The user manages `gh` / `op` / Cloudflare auth separately.
- Don't state facts about the homelab here at all. Link to the dashboard.
