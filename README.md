# Bartosz Łabiszak — academic website

Personal research and teaching website, published through GitHub Pages at https://blabiszak.github.io/.

Plain HTML, CSS and JavaScript. No framework, no external fonts or icon libraries, and every page stays readable without JavaScript.

## Everyday edits

| I want to… | Edit |
|---|---|
| Add or fix a **publication** | `data/publications.yml` — see below |
| Post a **news** item | the `<ul class="news-list">` in `index.html` (newest first, keep 4–6) |
| Add a **student** | the `.mentoring` block in `index.html` |
| Change bio, research themes, teaching, contact | `index.html` |
| Colours, typography, layout | `assets/site.css` (theme tokens are at the top) |

### Adding a publication

1. Open `data/publications.yml` on GitHub and click ✏️.
2. Copy an existing entry, change the fields, commit.
3. The **Build publications** GitHub Action regenerates `publications.html`, the homepage highlights and `assets/publications.bib` within a minute or two.

Field notes are at the top of the YAML file. Useful ones:

- `featured: true` — also show the paper on the homepage (keep this to about five).
- `tldr:` — one plain-language sentence, shown in italics under the title.
- `data:` / `code:` / `pdf:` — add links and badges.
- Wrap Latin names in `*asterisks*` to italicise them.

Do **not** edit the generated parts by hand: everything between `<!-- PUBS:START -->` / `<!-- PUBS:END -->` in `publications.html` and `<!-- FEATURED:START -->` / `<!-- FEATURED:END -->` in `index.html` is overwritten on each build.

To build locally instead: `pip install pyyaml && python3 tools/build_publications.py`.

> The Action needs write access: *Settings → Actions → General → Workflow permissions → Read and write*.

## Files

- `index.html` — homepage (about, research, news, selected papers, teaching & mentoring, contact)
- `publications.html` — full, filterable publication list
- `404.html` — the "lost to genetic drift" page
- `data/publications.yml` — publication data (source of truth)
- `tools/build_publications.py` — renders the YAML into the pages + BibTeX
- `assets/site.css`, `assets/site.js` — styles, theme toggle, mobile menu
- `assets/publications.js` — search, topic filters and copy-BibTeX buttons
- `assets/hero-700.webp`, `hero-1100.{webp,jpg}`, `profile-640.jpg`, `og-image.jpg` — web-sized images
- `sitemap.xml`, `robots.txt` — for search engines

## Images

Only web-sized copies live here; full-resolution originals stay on your computer. To add or replace a photo, export it about 1100 px wide as WebP or JPEG (roughly 150–300 KB) and put it in `assets/`.

## What belongs in this repo

Everything here is public: the repository and the website alike. Only commit material you'd be happy for anyone to read:

- **Yes:** published papers, public datasets and code, teaching materials, photos you're happy to share.
- **No:** manuscripts under review, unpublished results, grant drafts, student data, raw camera photos.

`.gitignore` already excludes `originals/` and `drafts/` folders, so you can keep those next to the site locally without them being pushed.
