# chrispaulmoore.com

Personal site for Chris Paul Moore — Kansas City, Missouri.

One page, drawn as a library catalog card: who I am and where to find the rest
of my things. Writing lives at [patientvibes.io](https://patientvibes.io).

## Stack

Plain HTML with an inline stylesheet. No build step, no framework, no
JavaScript, no analytics. Two webfonts (Courier Prime, Libre Caslon Text).

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

- `essays/` — two published pieces, kept reachable but not linked from the
  homepage. They are moving to patientvibes.io. Built from `drafts/*.md` via
  `python3 build-essays.py`.
- `cloudflare-worker.js` — the `comments.chrispaulmoore.com` Worker, deployed
  separately with `npx wrangler`. Nothing on the site uses it at the moment.

See `CLAUDE.md` for the current direction and open decisions.
