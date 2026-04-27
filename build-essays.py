#!/usr/bin/env python3
"""build-essays.py — drafts/*.md → essays/<slug>.html using essay-template.html.

Reads frontmatter metadata from drafts (YAML-like or inferred), converts the
markdown body to HTML, and substitutes into the template. Mermaid fenced blocks
are converted to <pre class="mermaid"> for client-side rendering by mermaid.js.

Usage:
    python3 build-essays.py            # build all drafts
    python3 build-essays.py one.md     # build a single draft
"""

import html
import re
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
DRAFTS = ROOT / "drafts"
OUT = ROOT / "essays"
TEMPLATE_PATH = ROOT / "essay-template.html"

# Manifest: slug → (number, tag). Drives ordering and metadata in the article header.
MANIFEST = {
    "agent-harness-commitment-curve": ("001", "essay · agents"),
    "karakeep-kindle-pipeline":       ("002", "essay · home ops"),
}


def slugify(stem: str) -> str:
    s = stem.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    return s.strip("-")


def split_title_subtitle_body(md_text: str):
    """Pull the first H1 as title and an italic line directly under it as subtitle."""
    lines = md_text.split("\n")
    title = None
    subtitle = None
    body_start = 0

    for i, line in enumerate(lines):
        if line.startswith("# "):
            title = line[2:].strip()
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                m = re.match(r"^\*([^*].*?)\*\s*$", lines[j].strip())
                if m:
                    subtitle = m.group(1).strip()
                    body_start = j + 1
                else:
                    body_start = i + 1
            else:
                body_start = i + 1
            break

    body = "\n".join(lines[body_start:]).lstrip("\n")
    return title, subtitle, body


def md_to_html(body: str) -> str:
    md = markdown.Markdown(
        extensions=["fenced_code", "tables", "smarty", "attr_list"],
        output_format="html5",
    )
    rendered = md.convert(body)

    def fix_mermaid(match):
        inner = match.group(1)
        # python-markdown HTML-escapes the body; unescape so mermaid sees real chars
        inner = html.unescape(inner)
        return f'<pre class="mermaid">{inner}</pre>'

    rendered = re.sub(
        r'<pre><code class="language-mermaid">(.*?)</code></pre>',
        fix_mermaid,
        rendered,
        flags=re.DOTALL,
    )
    return rendered


def word_count(body: str) -> int:
    text = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    text = re.sub(r"[#*_`>\-\[\]\(\)]", " ", text)
    return len(re.findall(r"\b[\w']+\b", text))


def derive_dek(body: str, max_len: int = 155) -> str:
    """Pick a sentence or two from the first paragraph for use as a meta description."""
    text = re.sub(r"```.*?```", "", body, flags=re.DOTALL).strip()
    paragraph = text.split("\n\n", 1)[0].replace("\n", " ").strip()
    paragraph = re.sub(r"[#*_`>]", "", paragraph)
    paragraph = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", paragraph)
    paragraph = re.sub(r"\s+", " ", paragraph).strip()
    if len(paragraph) <= max_len:
        return paragraph
    cutoff = paragraph[:max_len].rsplit(" ", 1)[0]
    return cutoff.rstrip(",;:") + "…"


def render_essay(md_path: Path, template: str) -> Path:
    md_text = md_path.read_text(encoding="utf-8")
    title, subtitle, body = split_title_subtitle_body(md_text)
    if not title:
        raise SystemExit(f"error: no H1 in {md_path}")

    body_html = md_to_html(body)
    slug = slugify(md_path.stem)
    number, tag = MANIFEST.get(slug, ("---", "essay"))
    dek = subtitle or derive_dek(body)

    subtitle_block = (
        f'<div class="subtitle">{html.escape(subtitle)}</div>' if subtitle else ""
    )

    out_html = template
    replacements = {
        "{{TITLE}}": html.escape(title),
        "{{SUBTITLE}}": html.escape(dek),
        "{{SUBTITLE_BLOCK}}": subtitle_block,
        "{{BODY}}": body_html,
        "{{WORD_COUNT}}": f"{word_count(body):,}",
        "{{NUMBER}}": number,
        "{{TAG}}": tag.upper(),
        "{{SLUG}}": slug,
    }
    for k, v in replacements.items():
        out_html = out_html.replace(k, v)

    OUT.mkdir(exist_ok=True)
    out_path = OUT / f"{slug}.html"
    out_path.write_text(out_html, encoding="utf-8")
    return out_path


def main():
    if not TEMPLATE_PATH.exists():
        raise SystemExit(f"error: template not found at {TEMPLATE_PATH}")
    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    if len(sys.argv) > 1:
        targets = [DRAFTS / arg if not Path(arg).is_absolute() else Path(arg) for arg in sys.argv[1:]]
    else:
        targets = sorted(DRAFTS.glob("*.md"))

    if not targets:
        print("no drafts found", file=sys.stderr)
        return

    print(f"building {len(targets)} essay(s):")
    for md in targets:
        out = render_essay(md, template)
        print(f"  → {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
