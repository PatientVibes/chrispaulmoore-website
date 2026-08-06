# chrispaulmoore.com

Personal site for Chris Paul Moore — Kansas City, Missouri.

One page: who I am, what I work on, and how to reach me. Not a blog, not a
portfolio, not a pitch.

## Stack

Plain HTML with an inline stylesheet. No build step, no framework, no
JavaScript, no analytics. One webfont (Newsreader) and about 10 KB of markup.

## Local development

```sh
git clone git@github.com:PatientVibes/chrispaulmoore-website.git
cd chrispaulmoore-website
python3 -m http.server 8000    # then open http://localhost:8000
```

Opening `index.html` directly works too, but root-relative links (`/essays/...`)
resolve correctly only when it is served.

## Deployment

Pushing to `main` publishes via GitHub Pages. `CNAME` maps the apex domain.

## Also in here

- `homelab.html` — what my home server is currently running. **Generated, not
  written:** `python3 build-homelab.py` reads the Docker API on the machine
  itself. Don't edit the HTML; it is overwritten on every build.
- `essays/` — two published pieces, kept reachable but no longer linked from the
  homepage. Built from `drafts/*.md` via `python3 build-essays.py`.
- `cloudflare-worker.js` — the `comments.chrispaulmoore.com` Worker, deployed
  separately with `npx wrangler`.

See `CLAUDE.md` for the current direction and open decisions.
