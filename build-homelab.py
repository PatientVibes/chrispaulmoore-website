#!/usr/bin/env python3
"""Generate homelab.html from the Docker API. Run on haldev.

The previous homelab.html was hand-written. It claimed "12 services, 12/12
green" and listed wg-easy and homepage for three months after both were
decommissioned. A static page cannot notice that it has gone stale, so this one
is not written by hand any more -- it is generated from the running fleet, and
regenerating it is the only way to change it.

    python3 build-homelab.py            # writes homelab.html
    python3 build-homelab.py --stdout   # print, don't write
    python3 build-homelab.py --check    # non-zero exit if the file is stale

------------------------------------------------------------------------------
WHAT THIS PAGE IS ALLOWED TO SAY
------------------------------------------------------------------------------
chrispaulmoore.com is public and unauthenticated. A generator that faithfully
published everything Docker knows would produce a precise attack plan: image
tags are a vulnerability shopping list, and port bindings plus interface
addresses are the security posture in full.

So the projection is an ALLOWLIST, enforced structurally. `PublicService`
carries a display name, a group and a coarse health state -- and has nowhere to
put anything else. The fields below are read from Docker and deliberately
dropped before the template is ever reached:

    image / tag        a list of exactly which CVEs to try
    host + container   the LAN topology, and which services are worth
      port bindings      reaching for
    HostIp bindings    which interfaces each service answers on; this is
                         the wildcard-vs-loopback distinction that the portal
                         exists to audit, and it is nobody else's business
    cloudflared        the public hostname list; it is already in DNS, but
      ingress            there is no reason to hand over an index of it
    networks,          internal structure that only helps someone already
      depends_on         inside

If you extend this script, extend PublicService deliberately or not at all.
Anything that reaches the template gets published, permanently, to strangers.

Service NAMES are published: they were on the old page, they appear in the
essays, and they describe a fleet with no ports open to the internet. That is a
judgement call, and it is the only one of its kind here.

------------------------------------------------------------------------------
Display names and groups come from ~/homelab/portal/meta.yml -- the same file
the portal uses, so the two cannot drift into disagreeing. Override with
HOMELAB_META. Everything structural comes from Docker.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import subprocess
import sys
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required:  pip install pyyaml")

META_PATH = Path(os.environ.get("HOMELAB_META", Path.home() / "homelab/portal/meta.yml"))
OUTPUT = Path(__file__).resolve().parent / "homelab.html"

# Health states collapsed to three buckets. The exact Docker status string can
# leak detail (and churn constantly, which would make every build a diff).
OK, WARN, DOWN = "ok", "warn", "down"


@dataclass(frozen=True)
class PublicService:
    """Everything that may appear on the public page. Nothing else exists here.

    Frozen and three-field on purpose -- see the module docstring. This is the
    membrane between the Docker API and a page strangers can read.
    """

    name: str
    group: str
    health: str


# --------------------------------------------------------------------------
# Read the running system
# --------------------------------------------------------------------------

def docker_inspect_all() -> list[dict]:
    ids = subprocess.run(
        ["docker", "ps", "--all", "--quiet"],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    if not ids:
        return []
    raw = subprocess.run(
        ["docker", "inspect", *ids],
        capture_output=True, text=True, check=True,
    ).stdout
    return json.loads(raw)


def load_meta() -> tuple[dict, list[str]]:
    """Return {container_name: entry} and the group order meta.yml declares."""
    if not META_PATH.exists():
        sys.exit(
            f"meta.yml not found at {META_PATH}.\n"
            "This script must run on haldev, or HOMELAB_META must point at a copy."
        )
    meta = yaml.safe_load(META_PATH.read_text()) or {}
    entries = meta.get("services") or {}
    groups: list[str] = []
    for entry in entries.values():
        g = entry.get("group")
        if g and g not in groups:
            groups.append(g)
    default_group = (meta.get("defaults") or {}).get("group", "Infrastructure")
    if default_group not in groups:
        groups.append(default_group)
    return entries, groups


def classify_health(container: dict) -> str:
    state = container.get("State") or {}
    status = state.get("Status", "")
    if status != "running":
        return DOWN
    health = (state.get("Health") or {}).get("Status")
    if health in (None, "healthy"):
        return OK
    if health == "starting":
        return WARN
    return WARN if health != "unhealthy" else DOWN


def project(containers: list[dict], entries: dict, default_group: str) -> tuple[list[PublicService], int]:
    """Narrow raw Docker records down to what may be published.

    Returns the services plus the number of compose stacks -- derived from the
    project labels, so adding a fifth stack updates the page by itself.
    """
    services: list[PublicService] = []
    stacks: set[str] = set()

    for c in containers:
        config = c.get("Config") or {}
        labels = config.get("Labels") or {}
        container_name = (c.get("Name") or "").lstrip("/")
        compose_service = labels.get("com.docker.compose.service") or container_name
        stack = labels.get("com.docker.compose.project")
        if stack:
            stacks.add(stack)

        entry = entries.get(container_name) or entries.get(compose_service) or {}
        if entry.get("hidden"):
            continue

        # Not compose-managed and not described in meta.yml: a one-off run, a
        # build helper, a forgotten test. The portal surfaces these because an
        # unexpected container is worth seeing; this page omits them so they
        # cannot pad a public count with something that is not a service.
        if not stack and not entry:
            continue

        services.append(PublicService(
            name=entry.get("name") or compose_service.replace("_", " ").replace("-", " ").title(),
            group=entry.get("group") or default_group,
            health=classify_health(c),
        ))

    services.sort(key=lambda s: s.name.lower())
    return services, len(stacks)


# --------------------------------------------------------------------------
# Render
# --------------------------------------------------------------------------

def group_services(services: list[PublicService], order: list[str]) -> OrderedDict:
    grouped: OrderedDict[str, list[PublicService]] = OrderedDict(
        (g, []) for g in order
    )
    for s in services:
        grouped.setdefault(s.group, []).append(s)
    return OrderedDict((g, v) for g, v in grouped.items() if v)


def render(services: list[PublicService], stack_count: int, order: list[str]) -> str:
    grouped = group_services(services, order)
    total = len(services)
    healthy = sum(1 for s in services if s.health == OK)
    generated = datetime.now(timezone.utc).strftime("%d %B %Y")

    # Only stated when it is not "all of them" -- a green count that is always
    # the same number as the total is noise, and an uptime percentage would be
    # a claim this script has no way to substantiate.
    health_note = (
        "All of them are healthy right now."
        if healthy == total
        else f"{healthy} of {total} are healthy right now."
    )

    blocks = []
    for group, members in grouped.items():
        items = "\n".join(
            f'                <li class="s-{html.escape(m.health)}">{html.escape(m.name)}</li>'
            for m in members
        )
        blocks.append(
            f'            <h2>{html.escape(group)}</h2>\n'
            f'            <ul class="fleet">\n{items}\n            </ul>'
        )
    fleet = "\n\n".join(blocks)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="The services running on my home server, listed by reading the Docker API rather than by hand.">
    <meta name="author" content="Chris Paul Moore">
    <link rel="canonical" href="https://chrispaulmoore.com/homelab.html">
    <meta name="robots" content="noindex, follow">
    <meta name="theme-color" content="#FBF8F3" media="(prefers-color-scheme: light)">
    <meta name="theme-color" content="#16150F" media="(prefers-color-scheme: dark)">
    <title>The homelab — Chris Paul Moore</title>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&display=swap" rel="stylesheet">

    <style>
        /* GENERATED FILE -- do not edit by hand.
           Source: build-homelab.py, run on haldev. Edits here are lost on the
           next build, and hand-editing is exactly what made the old version
           of this page untrue. */

        :root {{
            --paper:  #FBF8F3;
            --ink:    #17150F;
            --soft:   #56514A;
            --dim:    #857E73;
            --rule:   #E2DBCE;
            --accent: #3F5C72;
            --ok:     #4C7A5A;
            --warn:   #B07A2E;
            --down:   #A44A3F;
            --serif: 'Newsreader', Georgia, 'Times New Roman', serif;
        }}

        @media (prefers-color-scheme: dark) {{
            :root {{
                --paper:  #16150F;
                --ink:    #EDE8DE;
                --soft:   #ADA69A;
                --dim:    #7E776C;
                --rule:   #302C24;
                --accent: #93B6CE;
                --ok:     #7FA98B;
                --warn:   #D2A45E;
                --down:   #D08076;
            }}
        }}

        *, *::before, *::after {{ box-sizing: border-box; }}
        html {{ -webkit-text-size-adjust: 100%; }}

        body {{
            margin: 0;
            background: var(--paper);
            color: var(--ink);
            font-family: var(--serif);
            font-size: 19px;
            line-height: 1.62;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            font-variant-numeric: oldstyle-nums;
        }}

        ::selection {{ background: var(--accent); color: var(--paper); }}

        .page {{
            max-width: 34rem;
            margin: 0 auto;
            padding: clamp(2.5rem, 8vh, 5rem) 1.5rem clamp(3rem, 8vh, 5rem);
        }}

        a {{
            color: inherit;
            text-decoration: none;
            border-bottom: 1px solid var(--rule);
            transition: color 90ms linear, border-color 90ms linear;
        }}
        a:hover {{ color: var(--accent); border-bottom-color: var(--accent); }}
        a:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 3px; }}

        .back {{
            display: inline-block;
            margin-bottom: 3rem;
            font-size: 0.9rem;
            font-style: italic;
            color: var(--dim);
            border-bottom: 0;
        }}
        .back:hover {{ color: var(--accent); }}

        h1 {{
            margin: 0 0 1.5rem;
            font-size: clamp(2.1rem, 6.5vw, 2.8rem);
            font-weight: 500;
            line-height: 1.1;
            letter-spacing: -0.02em;
        }}

        .lede p {{ margin: 0 0 1.35rem; color: var(--soft); }}
        .lede p:first-child {{ font-size: 1.2rem; line-height: 1.5; color: var(--ink); }}

        hr {{ border: 0; border-top: 1px solid var(--rule); margin: 3rem 0; }}

        h2 {{
            margin: 2.5rem 0 0.9rem;
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            color: var(--dim);
            font-variant-numeric: normal;
        }}
        h2:first-of-type {{ margin-top: 0; }}

        ul.fleet {{
            margin: 0;
            padding: 0;
            list-style: none;
            columns: 2;
            column-gap: 2rem;
        }}

        ul.fleet li {{
            break-inside: avoid;
            color: var(--soft);
            font-size: 1.02rem;
            line-height: 1.85;
        }}

        ul.fleet li::before {{
            content: '';
            display: inline-block;
            width: 0.42em;
            height: 0.42em;
            border-radius: 50%;
            margin-right: 0.6em;
            vertical-align: 0.12em;
            background: var(--ok);
        }}
        ul.fleet li.s-warn::before {{ background: var(--warn); }}
        ul.fleet li.s-down::before {{ background: var(--down); }}
        ul.fleet li.s-warn, ul.fleet li.s-down {{ color: var(--ink); }}

        .colophon {{
            margin-top: 3.5rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--rule);
            font-size: 0.85rem;
            font-style: italic;
            color: var(--dim);
        }}
        .colophon p {{ margin: 0 0 0.5rem; }}
        .colophon p:last-child {{ margin-bottom: 0; }}

        @media (max-width: 33rem) {{
            body {{ font-size: 18px; }}
            ul.fleet {{ columns: 1; }}
        }}

        @media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; }} }}
    </style>
</head>
<body>
    <main class="page">

        <a class="back" href="/">← chrispaulmoore.com</a>

        <h1>The homelab</h1>

        <section class="lede">
            <p>A mini-PC in my house running {total} containerised services across
            {stack_count} Compose stacks, with nothing forwarded to it from the
            internet.</p>

            <p>Everything reachable from outside arrives through a Cloudflare
            tunnel and lands on an identity provider first. It is far more
            discipline than a house needs. That is the point — the stakes are
            low enough to be honest about, and the feedback is immediate when
            something drifts.</p>

            <p>This list is not typed. It is read from the Docker API on the
            machine itself, because the version of this page that <em>was</em>
            typed spent three months describing two services that no longer
            existed.</p>
        </section>

        <hr>

{fleet}

        <footer class="colophon">
            <p>{total} services · {stack_count} stacks · {health_note}</p>
            <p>Generated from the running fleet on {generated}. Versions, ports
            and addresses are deliberately not published.</p>
        </footer>

    </main>
</body>
</html>
"""


# --------------------------------------------------------------------------

def build() -> str:
    entries, groups = load_meta()
    default_group = groups[-1] if groups else "Infrastructure"
    containers = docker_inspect_all()
    if not containers:
        sys.exit("docker returned no containers -- is this haldev, and is Docker running?")
    services, stacks = project(containers, entries, default_group)
    if not services:
        sys.exit("no publishable services found; refusing to write an empty page")
    return render(services, stacks, groups)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stdout", action="store_true", help="print instead of writing")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if homelab.html differs from the current fleet")
    args = ap.parse_args()

    page = build()

    if args.stdout:
        print(page, end="")
        return 0

    if args.check:
        if not OUTPUT.exists():
            print("homelab.html is missing", file=sys.stderr)
            return 1
        # The generated date changes daily and is not drift, so compare
        # everything except the colophon's date line.
        def strip_date(t: str) -> str:
            return "\n".join(l for l in t.splitlines()
                             if "Generated from the running fleet" not in l)
        if strip_date(OUTPUT.read_text()) != strip_date(page):
            print("homelab.html is stale -- run build-homelab.py", file=sys.stderr)
            return 1
        print("homelab.html matches the running fleet")
        return 0

    OUTPUT.write_text(page)
    print(f"wrote {OUTPUT} ({len(page):,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
