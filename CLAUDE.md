# CLAUDE.md

This file provides context for AI assistants working in this repository.

## Project Overview

A personal website for "Khabib" — a static site generator built in pure Python with a retro Windows 95 aesthetic. The site hosts essays and product showcases, deployed to GitHub Pages.

**Key constraint:** Zero external dependencies. No npm, no pip packages, no build tools beyond Python 3.

## Repository Structure

```
my-website/
├── build.py              # The entire build system (~387 lines of Python)
├── essays/               # Markdown essay files (source content)
├── products/             # Markdown product showcase files (source content)
├── templates/            # HTML templates with {{ variable }} placeholders
│   ├── index.html        # Homepage (essays list + products grid)
│   ├── essay.html        # Individual essay page
│   └── product.html      # Individual product page
├── output/               # Generated site (do NOT edit manually; always rebuilt)
├── fonts/                # Local font assets (Silkscreen)
└── .github/workflows/
    └── deploy.yml        # CI: builds & deploys to GitHub Pages on push to main
```

## Build System (`build.py`)

The entire site is driven by a single Python script with no external dependencies.

### Configuration (top of `build.py`)
```python
SITE_NAME = "khabib"
SITE_DESCRIPTION = "Essays, products, and random thoughts"
AUTHOR = "Khabib"
```
Update these constants to change site-wide metadata.

### Build pipeline
1. Deletes and recreates `output/`
2. Loads all `.md` files from `essays/` and `products/`
3. Parses frontmatter + converts Markdown to HTML
4. Renders templates and writes HTML files to `output/`

### Template engine
Templates use `{{ variable_name }}` placeholders. The renderer does a simple string replace — no conditionals, loops, or filters in templates.

### Markdown parser
Custom regex-based parser in `markdown_to_html()`. Supported syntax:
- Headers (`#`, `##`, `###`)
- Bold (`**`), italic (`*`), bold+italic (`***`)
- Links `[text](url)`
- Unordered lists (`-` or `*`), ordered lists (`1.`)
- Blockquotes (`>`)
- Inline code (`` `code` ``) and fenced code blocks (` ``` `)
- Horizontal rules (`---`)
- Paragraphs (blank-line separated)

**Not supported:** tables, images, nested lists, footnotes.

## Content Authoring

### Essays (`essays/*.md`)
Frontmatter fields:
```yaml
---
title: "Your Essay Title"
date: 2026-01-15          # YYYY-MM-DD format; used for sorting (newest first)
tags: [tag1, tag2]
description: "Short summary"
---
```
- Filename becomes the slug: `my-essay.md` → `essay-my-essay.html`
- Essays are sorted by `date` descending on the homepage

### Products (`products/*.md`)
Frontmatter fields:
```yaml
---
title: "Product Name"
tagline: "One-line description"
icon: ⚡                  # Emoji displayed on product card
status: Active            # e.g. Active, Archived, Beta
version: v1.0.0
url: https://...          # Live URL
github: https://...       # GitHub repo URL
---
```
- Filename becomes the slug: `my-product.md` → `product-my-product.html`

## Development Workflow

### Build the site
```bash
python build.py
```
Outputs to `output/`. Always run this after changing any source files.

### Local preview
```bash
python build.py --serve           # Builds then serves at http://localhost:8000
python build.py --serve --port 3000  # Custom port
```

### Deployment
Pushing to `main` triggers `.github/workflows/deploy.yml`, which:
1. Runs `python build.py`
2. Uploads `output/` as a GitHub Pages artifact
3. Deploys to GitHub Pages

The `output/` directory is committed to the repo (it is not gitignored). However, it is always fully regenerated during CI — so local `output/` changes are overwritten on deploy.

## Design System

The site uses a Windows 95 aesthetic. Key design rules:

- **Fonts:** `Press Start 2P` (pixel font, for titles/headers/UI chrome) + `Inter` (body text)
- **Color palette** (CSS variables in every template):
  - `--bg: #008080` — teal desktop background
  - `--blue: #000080` — Windows navy blue (links, accents)
  - `--window-bg: #F0F0F0` — window background
  - `--gray: #A0A0A0` — muted elements
- **Borders:** Win95 bevel effect using `#dfdfdf` (top/left light) and `#404040` (bottom/right dark)
- **Window chrome:** Title bar with gradient `#000035 → #003580`, minimize/maximize/close buttons
- **Taskbar:** Fixed at bottom, includes clock (updated via JS)

All CSS is inlined within each template (no shared stylesheet). If you update styles, you must update them in each affected template file.

## Key Conventions

1. **No dependencies** — Do not add `import` statements for third-party packages. The only stdlib modules used are: `os`, `re`, `json`, `shutil`, `argparse`, `datetime`, `pathlib`, `http.server`.
2. **No build config files** — No `package.json`, `requirements.txt`, `pyproject.toml`, etc.
3. **Output is generated** — Never manually edit files in `output/`. They are overwritten on every build.
4. **CSS is inlined per template** — Each template is self-contained. There is no shared CSS file.
5. **Template variables are positional** — `render_template()` uses exact string matching. Variable names in templates must exactly match the keyword arguments passed in `build.py`.
6. **Slug = filename stem** — Essay slug is derived from the `.md` filename, not the frontmatter title.

## Gotchas

- The Markdown parser does **not** escape raw HTML by default (the escape lines are commented out in `markdown_to_html()`). Raw HTML in `.md` files will pass through to output.
- The frontmatter parser splits on the first `:` only, so values with colons (e.g. URLs) need to be quoted: `url: "https://example.com"`.
- Essay navigation (Prev/Next) is based on sort order by date. Essays without a `date` field sort to the bottom.
- The `fonts/` directory contains `Silkscreen.textClipping` — a macOS artifact, not a usable font file. Actual fonts are loaded from Google Fonts CDN at runtime.
