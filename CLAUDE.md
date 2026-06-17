# CLAUDE.md

This file provides context for AI assistants working in this repository.

## Project Overview

A personal website for "Khabib" — a static site generator built in pure Python with a retro Windows 95 aesthetic. The whole site is a single page styled as a **Windows 95 file Explorer**: a folder tree, a file view, an address bar, a status bar, and a taskbar with a live clock. Essays, projects, and videos appear as "files" inside Explorer folders; opening an essay or project shows its full content in the file view. Deployed to GitHub Pages.

**Key constraint:** Zero external dependencies. No npm, no pip packages, no build tools beyond Python 3. The front-end is hand-written vanilla JS (no framework).

## Repository Structure

```
my-website/
├── build.py              # The entire build system (pure Python, stdlib only)
├── essays/               # Markdown essay files (source content)
├── projects/             # Markdown project showcase files (source content)
├── videos/               # Markdown video entries (YouTube links)
├── templates/
│   ├── index.html        # The Win95 Explorer single-page app (the whole site)
│   ├── essay.html        # LEGACY — no longer rendered (see note below)
│   └── project.html      # LEGACY — no longer rendered (see note below)
├── output/               # Generated site (do NOT edit manually; always rebuilt)
│   └── index.html        # The only generated file
├── fonts/                # Local font assets (Silkscreen) — not used at runtime
└── .github/workflows/
    └── deploy.yml        # CI: builds & deploys to GitHub Pages on push to main
```

> **Legacy templates:** `templates/essay.html` and `templates/project.html` are from the
> previous multi-page design and are **not** referenced by the build anymore. All content now
> renders inside `index.html`. They are kept only for reference and can be deleted.

## Build System (`build.py`)

The entire site is driven by a single Python script with no external dependencies.

### Configuration (top of `build.py`)
```python
SITE_NAME = "khabib"
SITE_DESCRIPTION = "Essays, projects, and random thoughts"
AUTHOR = "Khabib"
```
Update these constants to change site-wide metadata. `SITE_NAME` is shown as the drive label
(`khabib (C:)`) and in the "Hello, I'm …" heading; `SITE_DESCRIPTION` is the home subtitle.

There are also two editable constants for content the repo doesn't generate from Markdown:
- `ABOUT_BODY` — the paragraphs shown in the **About** document view.
- `BOOKMARKS` — the list shown in the **Bookmarks** folder (name, address, url).

### Build pipeline
1. Deletes and recreates `output/`.
2. Loads all `.md` files from `essays/`, `projects/`, and `videos/`.
3. Parses frontmatter + converts Markdown to HTML.
4. `build_site_data()` assembles a single JSON data model (sections + pages).
5. `build_index()` injects that JSON into `templates/index.html` and writes `output/index.html`.

`index.html` is the **only** file written to `output/`.

### Template engine
`render_template()` does a simple `{{ variable }}` string replace — no conditionals, loops, or
filters. The Explorer template only uses two placeholders: `{{ site_name }}` and `{{ site_data }}`
(the JSON blob). Everything dynamic is rendered client-side from `site_data`.

The injected JSON is made safe for embedding inside a `<script>` tag by replacing `</` with `<\/`.

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

## The Explorer front-end (`templates/index.html`)

The page ships a small vanilla-JS reactive engine (no dependencies). Key pieces:

- **`SITE`** — the injected data model: `{ name, description, sections, pages }`.
- **`sections`** — the home-screen icon grid order. Each has `{ id, icon, name, verb, desc }`.
  `whoami.exe` is decorative (no matching page, so double-clicking does nothing).
- **`pages`** — one entry per navigable folder (`essays`, `projects`, `bookmarks`, `about`,
  `videos`). List folders have `items[]`; `about` has `kind: 'about'` and a `body[]` of paragraphs.
- **State + navigation** mirror a real Explorer: `home` → folder → document, with working
  Back / Forward / Up buttons and history.
- **Opening items:** essays and projects open **in-window** as a document view (full HTML body,
  plus repo/live links for projects). Items with `open: 'external'` (videos, bookmarks) open their
  `url` in a new tab instead of navigating.
- **Icons** are inline SVG `<symbol>`s (`ic-doc`, `ic-folder`, `ic-star`, `ic-person`, `ic-video`,
  `ic-floppy`, etc.). Use these icon ids in `build.py`, not emoji.

When changing the look or behavior, edit `templates/index.html` directly (markup + the inline
`<style>` + the `<script>` engine). When changing what data is shown, edit `build_site_data()`.

## Content Authoring

### Essays (`essays/*.md`)
```yaml
---
title: "Your Essay Title"
date: 2026-01-15          # YYYY-MM-DD; sorted newest-first; shown as the "Modified" column
tags: [tag1, tag2]        # parsed but not currently displayed
description: "Short summary"
---
```
Appears in the **Essays** folder; double-click opens the full text in the file view.

### Projects (`projects/*.md`)
```yaml
---
title: "Project Name"
tagline: "One-line description"
icon: ⚡                  # parsed but NOT shown — the Explorer uses the ic-folder pixel icon
status: Active            # shown in the "Status" column
version: v1.0.0
url: "https://..."        # Live URL — quote values containing colons
github: "https://..."     # GitHub repo URL
---
```
Appears in the **Projects** folder; double-click opens the body plus Visit/GitHub links.

### Videos (`videos/*.md`)
```yaml
---
title: "Video title"
youtube_id: R5Z3OQLln0U   # used to build the youtu.be link
date: 2026-04-19          # shown as the "Published" column
description: "Short summary"
---
```
Appears in the **Videos** folder; double-click opens the YouTube link in a new tab.

## Development Workflow

### Build the site
```bash
python build.py
```
Outputs `output/index.html`. Always run this after changing any source files.

### Local preview
```bash
python build.py --serve              # Builds then serves at http://localhost:8000
python build.py --serve --port 3000  # Custom port
```

### Deployment
Pushing to `main` triggers `.github/workflows/deploy.yml`, which:
1. Runs `python build.py`
2. Uploads `output/` as a GitHub Pages artifact
3. Deploys to GitHub Pages

The `output/` directory is committed to the repo (it is not gitignored). However, it is always
fully regenerated during CI — so local `output/` changes are overwritten on deploy.

## Design System

The site uses a Windows 95 aesthetic, rendered as a desktop + Explorer window.

- **Fonts (Google Fonts CDN):** `Pixelify Sans` (pixel font, for the big headings) + `VT323`
  (monospace, for inline/code blocks in documents). UI chrome uses system `Tahoma`/`Segoe UI`.
- **Color palette:**
  - `#008080` — teal desktop background
  - `#c0c0c0` — window / taskbar gray
  - `#000080` — Windows navy (title bars, selection, links)
  - `#fff` / `#0a0a0a` — pane backgrounds / text
- **Bevels:** Win95 inset/outset effect via layered `box-shadow` using `#fff`/`#dfdfdf` (light,
  top-left) and `#808080`/`#000` (dark, bottom-right). Pressed buttons invert the shadow.
- **Window chrome:** title bar gradient `#000080 → #1066c0`, minimize/maximize/close buttons.
- **Taskbar:** fixed at bottom with a Start button and a clock updated every second via JS.

All CSS is inlined inside `templates/index.html`. There is no shared stylesheet.

## Key Conventions

1. **No dependencies** — Do not add third-party packages. stdlib modules used: `os`, `re`,
   `json`, `shutil`, `argparse`, `datetime`, `pathlib`, `http.server`. The front-end is plain JS.
2. **No build config files** — No `package.json`, `requirements.txt`, `pyproject.toml`, etc.
3. **Output is generated** — Never manually edit `output/`. It is overwritten on every build.
4. **One template, inlined CSS/JS** — `index.html` is self-contained.
5. **Two layers of rendering** — Python builds the JSON data model (`build_site_data`); the
   browser renders the UI from it. Markup/behavior changes go in the template; content/data
   changes go in `build.py`.
6. **Icons are SVG symbol ids**, not emoji — use `ic-*` ids that exist in the template's `<defs>`.

## Gotchas

- The Markdown parser does **not** escape raw HTML by default (the escape lines are commented out
  in `markdown_to_html()`). Raw HTML in `.md` files passes through into the document view.
- The frontmatter parser splits on the first `:` only, so values with colons (e.g. URLs) need to
  be quoted: `url: "https://example.com"`.
- Essays without a `date` sort to the bottom (date is used for descending sort + the Modified column).
- `site_data` is embedded as JSON inside a `<script>`; `build.py` escapes `</` as `<\/` so essay
  or project bodies can't break out of the script tag. Keep that escaping if you touch `build_index`.
- The `fonts/` directory contains `Silkscreen.textClipping` — a macOS artifact, not a usable font.
  Fonts are loaded from the Google Fonts CDN at runtime.
- `templates/essay.html` / `templates/project.html` are legacy and unused — editing them has no effect.
