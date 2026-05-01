---
title: Minimal Blog Engine
tagline: A static site generator in 500 lines. No dependencies. No magic.
icon: ⚡
status: Active
version: v1.2.0
url: https://github.com/gagaci/my-website
github: https://github.com/gagaci/my-website
---

# About

Minimal Blog Engine is exactly what it sounds like: a way to turn Markdown files into a website with zero configuration and zero dependencies beyond Python 3.

I built this because every other static site generator I tried was either too complicated, too slow, or required me to learn Yet Another Configuration Language.

# Features

- **500 lines of Python** — Read the entire source in one sitting
- **Zero dependencies** — Just Python 3.8+
- **Markdown to HTML** — With syntax highlighting
- **RSS feed** — Generated automatically
- **Fast** — Builds 1000 posts in under 2 seconds
- **Live reload** — For local development

# Quick Start

Clone the repo and run:

```bash
# Clone the repository
git clone https://github.com/gagaci/my-website
cd my-website

# Create your first post
echo "# Hello World" > posts/hello.md

# Build the site
python blog.py build

# Start local server
python blog.py serve
```

# Why Another SSG?

I was tired of:

- Jekyll's Ruby dependencies breaking after every OS update
- Hugo's Go templates being unreadable
- Gatsby taking 45 seconds to build 10 pages
- Every SSG requiring a config file longer than my actual content

So I wrote my own. It does exactly what I need and nothing more.

# License

MIT — Do whatever you want with it.
