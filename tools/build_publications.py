#!/usr/bin/env python3
"""Render data/publications.yml into the site.

Writes:
  publications.html          – full list, between <!-- PUBS:START --> / <!-- PUBS:END -->
  index.html                 – featured papers, between <!-- FEATURED:START --> / <!-- FEATURED:END -->
  assets/publications.bib    – BibTeX for every entry

Run from the repository root:  python3 tools/build_publications.py
Needs PyYAML (pip install pyyaml). Everything else is the standard library.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "publications.yml"
ME = "Łabiszak"

TOPICS = {
    "hybridisation": "Hybridisation",
    "scots-pine": "Scots pine",
    "adaptation": "Adaptation",
    "conservation": "Conservation",
    "phylogeography": "Phylogeography",
    "organellar": "Organellar DNA",
    "methods": "Methods",
    "other": "Beyond pines",
}


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def rich(text: str) -> str:
    """Escape, then turn *Latin names* into <i>."""
    return re.sub(r"\*(.+?)\*", r"<i>\1</i>", esc(text))


def plain(text: str) -> str:
    return re.sub(r"\*(.+?)\*", r"\1", str(text))


def fmt_author(name: str) -> str:
    surname, _, initials = name.strip().partition(" ")
    shown = f"{surname}, {initials}" if initials else surname
    shown = esc(shown)
    return f"<strong>{shown}</strong>" if surname == ME else shown


def fmt_authors(authors: list[str], short: bool = False) -> str:
    parts = [fmt_author(a) for a in authors]
    if len(parts) == 1:
        return parts[0]
    full = ", ".join(parts[:-1]) + " &amp; " + parts[-1]
    if not short or len(parts) <= 7:
        return full
    # Long lists: first four (plus me if I am further down), then a count.
    keep = parts[:4]
    mine = [x for x in parts[4:] if x.startswith("<strong>")]
    keep += mine
    hidden = len(parts) - len(keep)
    return (
        f'<span aria-hidden="true">{", ".join(keep)} <span class="more">+{hidden} more</span></span>'
        f'<span class="visually-hidden">{full}</span>'
    )


def citation_tail(p: dict) -> str:
    vol, iss, pages = str(p.get("volume") or ""), str(p.get("issue") or ""), str(p.get("pages") or "")
    bits = vol + (f"({iss})" if iss else "")
    if pages:
        bits = f"{bits}, {pages}" if bits else pages
    return esc(bits)


def bibtex(p: dict) -> str:
    def latex_authors(a):
        out = []
        for n in a:
            s, _, i = n.partition(" ")
            out.append(f"{s}, {i}".strip(", "))
        return " and ".join(out)

    fields = [
        ("author", latex_authors(p["authors"])),
        ("title", "{" + plain(p["title"]) + "}"),
        ("journal", p.get("journal", "")),
        ("year", p["year"]),
        ("volume", p.get("volume", "")),
        ("number", p.get("issue", "")),
        ("pages", str(p.get("pages", "")).replace("–", "--")),
        ("doi", p.get("doi", "")),
    ]
    body = ",\n".join(f"  {k} = {{{v}}}" for k, v in fields if str(v))
    return f"@article{{{p['id']},\n{body}\n}}"


def doi_url(p: dict) -> str:
    return f"https://doi.org/{p['doi']}" if p.get("doi") else ""


def links_row(p: dict) -> str:
    items = []
    if p.get("doi"):
        items.append(f'<a href="{esc(doi_url(p))}">DOI <span aria-hidden="true">↗</span></a>')
    if p.get("pdf"):
        items.append(f'<a href="{esc(p["pdf"])}">PDF <span aria-hidden="true">↗</span></a>')
    if p.get("data"):
        items.append(f'<a href="{esc(p["data"])}">Data <span aria-hidden="true">↗</span></a>')
    if p.get("code"):
        items.append(f'<a href="{esc(p["code"])}">Code <span aria-hidden="true">↗</span></a>')
    cite = (
        '<details class="cite"><summary>Cite</summary>'
        f'<pre><code>{esc(bibtex(p))}</code></pre></details>'
    )
    items.append(cite)
    return '<div class="pub-links">' + "".join(items) + "</div>"


def flags(p: dict) -> str:
    out = []
    if p["authors"][0].startswith(ME):
        out.append('<span class="flag flag-first">First author</span>')
    if p.get("oa"):
        out.append('<span class="flag">Open access</span>')
    if p.get("data"):
        out.append('<span class="flag">Data</span>')
    if p.get("code"):
        out.append('<span class="flag">Code</span>')
    return "".join(out)


def heading(p: dict) -> str:
    title = rich(p["title"])
    href = doi_url(p)
    return f'<a href="{esc(href)}">{title}</a>' if href else title


def tldr(p: dict) -> str:
    return f'<p class="pub-tldr"><span>TL;DR</span> {rich(p["tldr"])}</p>' if p.get("tldr") else ""


def article(p: dict, full: bool) -> str:
    """Homepage highlight (full=False) or full-list entry (full=True)."""
    tail = citation_tail(p)
    if not full:
        authors = fmt_authors(p["authors"], short=True)
        return (
            f'<article class="highlight"><p class="pub-journal">{p["year"]} · {esc(p.get("journal", ""))}</p>'
            f"<h3>{heading(p)}</h3>{tldr(p)}"
            f'<p class="pub-authors">{authors}</p></article>'
        )
    authors = fmt_authors(p["authors"], short=True) + (f" · {tail}" if tail else "")
    note = f'<span class="pub-note">{esc(p["note"])}</span>' if p.get("note") else ""
    topics = " ".join(p.get("topics", []))
    first = "true" if p["authors"][0].startswith(ME) else "false"
    search = esc(" ".join([plain(p["title"]), p.get("journal", ""), " ".join(p["authors"])]).lower())
    return (
        f'<article class="pub-item" id="{esc(p["id"])}" data-topics="{esc(topics)}" data-first="{first}" data-search="{search}">'
        f'<p class="pub-journal">{esc(p.get("journal", ""))}{flags(p)}</p>'
        f"<h3>{heading(p)}</h3>"
        f'<p class="pub-authors">{authors}{note}</p>'
        f"{tldr(p)}{links_row(p)}</article>"
    )


def year_groups(pubs: list[dict]) -> str:
    out, years = [], []
    for p in pubs:
        if p["year"] not in years:
            years.append(p["year"])
    for y in years:
        items = "\n".join(article(p, full=True) for p in pubs if p["year"] == y)
        out.append(
            f'<section class="year-group" data-year="{y}" aria-label="{y}">'
            f'<h3 class="year-heading">{y}</h3><div class="year-items">\n{items}\n</div></section>'
        )
    return "\n".join(out)


def filters(pubs: list[dict]) -> str:
    used = [t for t in TOPICS if any(t in p.get("topics", []) for p in pubs)]
    chips = "".join(
        f'<button type="button" class="chip" data-topic="{t}" aria-pressed="false">{TOPICS[t]}</button>'
        for t in used
    )
    return (
        '<div class="pub-filters" hidden>'
        '<label class="pub-search"><span class="visually-hidden">Search publications</span>'
        '<input type="search" placeholder="Search title, journal, co-author…" autocomplete="off"></label>'
        f'<div class="chips" role="group" aria-label="Filter by topic">'
        '<button type="button" class="chip" data-topic="" aria-pressed="true">All</button>'
        f"{chips}</div>"
        '<label class="first-toggle"><input type="checkbox"> First-author only</label>'
        '<p class="pub-count" aria-live="polite"></p>'
        "</div>"
    )


def stats(pubs: list[dict]) -> str:
    n = len(pubs)
    first = sum(p["authors"][0].startswith(ME) for p in pubs)
    oa = sum(bool(p.get("oa")) for p in pubs)
    years = sorted({p["year"] for p in pubs})
    return (
        '<dl class="pub-stats">'
        f"<div><dt>Articles</dt><dd>{n}</dd></div>"
        f"<div><dt>First author</dt><dd>{first}</dd></div>"
        f"<div><dt>Open access</dt><dd>{oa}</dd></div>"
        f"<div><dt>Since</dt><dd>{years[0]}</dd></div>"
        "</dl>"
    )


def replace_block(path: Path, name: str, content: str) -> None:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(rf"(<!-- {name}:START -->)(.*?)(<!-- {name}:END -->)", re.S)
    if not pattern.search(text):
        sys.exit(f"Markers <!-- {name}:START/END --> not found in {path.name}")
    new = pattern.sub(lambda m: f"{m.group(1)}\n{content}\n{m.group(3)}", text)
    if new != text:
        path.write_text(new, encoding="utf-8")


def validate(pubs: list[dict]) -> None:
    ids = set()
    for p in pubs:
        for key in ("id", "authors", "year", "title"):
            if not p.get(key):
                sys.exit(f"Entry missing '{key}': {p}")
        if p["id"] in ids:
            sys.exit(f"Duplicate id: {p['id']}")
        ids.add(p["id"])
        for t in p.get("topics", []):
            if t not in TOPICS:
                sys.exit(f"{p['id']}: unknown topic '{t}' (allowed: {', '.join(TOPICS)})")


def main() -> None:
    pubs = yaml.safe_load(DATA.read_text(encoding="utf-8")) or []
    for p in pubs:  # YAML may parse DOIs/years oddly; normalise to strings/ints
        p["year"] = int(p["year"])
        for k in ("doi", "volume", "issue", "pages"):
            if p.get(k) is not None:
                p[k] = str(p[k])
    validate(pubs)
    pubs.sort(key=lambda p: -p["year"])  # stable: YAML order within a year

    full = year_groups(pubs)
    replace_block(
        ROOT / "publications.html",
        "PUBS",
        stats(pubs) + "\n" + filters(pubs) + '\n<div class="publication-list" id="pub-list">\n' + full + "\n</div>",
    )

    featured = [p for p in pubs if p.get("featured")]
    replace_block(ROOT / "index.html", "FEATURED", '<div class="highlights">\n' + "\n".join(article(p, full=False) for p in featured) + "\n</div>")

    bib = "% Generated from data/publications.yml — do not edit by hand.\n\n" + "\n\n".join(bibtex(p) for p in pubs) + "\n"
    (ROOT / "assets" / "publications.bib").write_text(bib, encoding="utf-8")

    missing = [p["id"] for p in pubs if not p.get("doi")]
    print(f"Built {len(pubs)} publications ({len(featured)} featured).")
    if missing:
        print("Missing DOI:", ", ".join(missing))


if __name__ == "__main__":
    main()
