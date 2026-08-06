# chrispaulmoore-website

Personal site for Chris Paul Moore. Static HTML, no build step for the homepage.
Deploys via **GitHub Pages** from `main`; `CNAME` points the apex at
`chrispaulmoore.com`. Cloudflare handles DNS and the `comments.chrispaulmoore.com`
subdomain (Cloudflare Worker in `cloudflare-worker.js` / `wrangler.toml`, deployed
independently with `npx wrangler`).

## What this site is now (2026-08-06)

A **calling card**. One page. Name, a short personal lede, a compact block of
professional facts, and how to reach him.

It is deliberately **not**:

- a blog or an essay feed
- an AI-agent portal
- a dashboard, topology diagram, or status page

### The rule that matters

**Nothing on the homepage states a number that has to be maintained.**

The previous version rendered a hand-written `home.lan` topology — "12 services,
12/12 green, 99.9% uptime" — listing `wg-easy` and `homepage`. Both had been
decommissioned. The page sat unchanged from 2026-05-10 to 2026-08-06 and spent
three months describing infrastructure that no longer existed.

This is the same failure the homelab repo already documents: *prefer deriving
state over hardcoding it — two hand-written service lists drifted apart and
started lying about what was exposed.* A static calling card has no mechanism to
stay true, so it must only assert things that stay true on their own.

If you ever want live counts on this site again, derive them. Do not type them.

## Design

Editorial / typographic. A hard break from the previous "Direction B" look
(dark blueprint grid, IBM Plex, amber accent) — **that brief is retired; do not
restore it on the homepage.**

- Warm paper `#FBF8F3`, ink `#17150F`, cool slate accent `#3F5C72`
- Full dark-mode variant via `prefers-color-scheme`
- One typeface: **Newsreader** (Google Fonts), serif throughout
- Single column, `max-width: 34rem`, generous vertical rhythm
- Near-zero motion; `prefers-reduced-motion` respected
- A real print stylesheet — it is a calling card, so it should print like one
- No scripts, no analytics, no tracking. `index.html` is ~9.7 KB (was ~44 KB)

## Layout of the repo

| Path | Status |
|---|---|
| `index.html` | **The site.** Editorial calling card. |
| `essays/*.html` | Published, still reachable, **not linked from the homepage**. Kept so inbound links don't rot. |
| `drafts/*.md` | Source markdown for the essays. |
| `build-essays.py` + `essay-template.html` | Essay build pipeline. Still works. Run `python3 build-essays.py` after editing a draft. |
| `homelab.html` | **Generated. Do not edit by hand.** Run `python3 build-homelab.py` on haldev. |
| `build-homelab.py` | Generates `homelab.html` from the Docker API. Read its docstring before changing it. |
| `cloudflare-worker.js`, `wrangler.toml` | Comments system. Deploys separately. |
| `CNAME` | DNS. Do not rename or delete. |
| `family-photo.jpg` | No longer on the page; still the `og:image`. |

## homelab.html is generated

`build-homelab.py` reads the Docker API on haldev and writes `homelab.html`.
Display names and groups come from `~/homelab/portal/meta.yml` — the same file
the portal uses, so the page and the dashboard cannot drift into disagreeing.

```sh
python3 build-homelab.py            # write the page
python3 build-homelab.py --check    # exit 1 if it no longer matches the fleet
```

**This page is public and unauthenticated**, so the generator publishes an
allowlist, enforced by the shape of the `PublicService` dataclass: display
name, group, coarse health. Image tags, port bindings, host interfaces,
cloudflared hostnames and internal addresses are read from Docker and dropped
before rendering — publishing them would amount to a vulnerability inventory
and a LAN map. The full reasoning is in the module docstring. **If you extend
that dataclass, you are changing what strangers can read, permanently.**

It is not automated yet. `--check` is designed for a cron or a systemd timer
that regenerates, commits and pushes; that has not been set up, so the page is
accurate as of its last manual build. Until then it can still go stale — just
noisily, because `--check` will say so.

## Open decisions (not actioned — ask first)

1. **Automate the rebuild.** See above. Needs a timer plus deploy credentials
   on haldev, which is the part worth thinking about rather than the script.
2. **OG image** is still `family-photo.jpg`, which no longer matches the site's
   look. Either make a typographic OG card or leave it.

## Conventions

- Vanilla HTML with an inline `<style>`. No framework, no bundler, no CSS file.
- Use `npx wrangler`, never a global install. Never hardcode tokens.
- The user manages `gh` / `op` / Cloudflare auth separately.
- Verify factual claims about the homelab against haldev before publishing them.
  The Docker API is the source of truth, not memory and not this file.
