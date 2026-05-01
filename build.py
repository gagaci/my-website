#!/usr/bin/env python3
"""
Minimal Blog Engine for khabib's Windows 95 Site
================================================
Converts Markdown files to retro-styled HTML pages.

Usage:
    python build.py          # Build the entire site
    python build.py --serve  # Build and start local server

Structure:
    essays/          → Put your .md essay files here
    projects/        → Put your .md project files here
    templates/       → HTML templates (don't edit unless customizing)
    output/          → Generated site (upload this to hosting)
"""

import os
import re
import json
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

# =============================================================================
# CONFIGURATION
# =============================================================================

SITE_NAME = "khabib"
SITE_DESCRIPTION = "Essays, projects, and random thoughts"
AUTHOR = "Khabib"

# Directories
BASE_DIR = Path(__file__).parent
ESSAYS_DIR = BASE_DIR / "essays"
PROJECTS_DIR = BASE_DIR / "projects"
VIDEOS_DIR = BASE_DIR / "videos"
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"

# =============================================================================
# MARKDOWN PARSER (No dependencies!)
# =============================================================================

def parse_frontmatter(content):
    """Extract YAML-like frontmatter from markdown content."""
    if not content.startswith('---'):
        return {}, content
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content
    
    frontmatter = {}
    for line in parts[1].strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            # Handle lists like [tag1, tag2]
            if value.startswith('[') and value.endswith(']'):
                value = [v.strip().strip('"').strip("'") for v in value[1:-1].split(',')]
            frontmatter[key] = value
    
    return frontmatter, parts[2].strip()

def markdown_to_html(text):
    """Convert markdown to HTML (basic but sufficient)."""
    html = text
    
    # Escape HTML entities first (but preserve intentional HTML)
    # html = html.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # Code blocks (``` ... ```)
    def replace_code_block(match):
        code = match.group(1)
        # Escape HTML in code blocks
        code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return f'<pre class="code-block">{code}</pre>'
    html = re.sub(r'```[\w]*\n(.*?)```', replace_code_block, html, flags=re.DOTALL)
    
    # Inline code (`code`)
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # Headers
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Bold and italic
    html = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', html)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    
    # Links [text](url)
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
    
    # Blockquotes
    def replace_blockquote(match):
        content = match.group(0)
        lines = [line.lstrip('> ').strip() for line in content.split('\n')]
        return '<blockquote>' + ' '.join(lines) + '</blockquote>'
    html = re.sub(r'^(?:> .+\n?)+', replace_blockquote, html, flags=re.MULTILINE)
    
    # Unordered lists
    def replace_ul(match):
        items = re.findall(r'^[-*] (.+)$', match.group(0), flags=re.MULTILINE)
        li_items = ''.join(f'<li>{item}</li>' for item in items)
        return f'<ul>{li_items}</ul>'
    html = re.sub(r'(?:^[-*] .+$\n?)+', replace_ul, html, flags=re.MULTILINE)
    
    # Ordered lists
    def replace_ol(match):
        items = re.findall(r'^\d+\. (.+)$', match.group(0), flags=re.MULTILINE)
        li_items = ''.join(f'<li>{item}</li>' for item in items)
        return f'<ol>{li_items}</ol>'
    html = re.sub(r'(?:^\d+\. .+$\n?)+', replace_ol, html, flags=re.MULTILINE)
    
    # Horizontal rules
    html = re.sub(r'^---+$', '<hr>', html, flags=re.MULTILINE)
    
    # Paragraphs (lines separated by blank lines)
    paragraphs = []
    current = []
    for line in html.split('\n'):
        stripped = line.strip()
        if stripped == '':
            if current:
                paragraphs.append('\n'.join(current))
                current = []
        else:
            current.append(line)
    if current:
        paragraphs.append('\n'.join(current))
    
    # Wrap non-block elements in <p> tags
    block_elements = ['<h1', '<h2', '<h3', '<ul', '<ol', '<pre', '<blockquote', '<hr']
    result = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        is_block = any(p.startswith(tag) for tag in block_elements)
        if is_block:
            result.append(p)
        else:
            result.append(f'<p>{p}</p>')
    
    return '\n\n'.join(result)

# =============================================================================
# TEMPLATE ENGINE
# =============================================================================

def render_template(template_name, **context):
    """Simple template rendering with {{ variable }} syntax."""
    template_path = TEMPLATES_DIR / template_name
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Replace {{ variable }} with context values
    for key, value in context.items():
        template = template.replace('{{ ' + key + ' }}', str(value))
    
    return template

# =============================================================================
# BUILD FUNCTIONS
# =============================================================================

def load_essays():
    """Load all essays from the essays directory."""
    essays = []
    if not ESSAYS_DIR.exists():
        return essays
    
    for md_file in ESSAYS_DIR.glob('*.md'):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter, body = parse_frontmatter(content)
        html_body = markdown_to_html(body)
        
        # Generate slug from filename
        slug = md_file.stem
        
        essays.append({
            'slug': slug,
            'title': frontmatter.get('title', slug.replace('-', ' ').title()),
            'date': frontmatter.get('date', ''),
            'tags': frontmatter.get('tags', []),
            'description': frontmatter.get('description', ''),
            'body': html_body,
            'filename': f'essay-{slug}.html'
        })
    
    # Sort by date (newest first)
    essays.sort(key=lambda x: x['date'], reverse=True)
    return essays

def load_projects():
    """Load all projects from the projects directory."""
    projects = []
    if not PROJECTS_DIR.exists():
        return projects
    
    for md_file in PROJECTS_DIR.glob('*.md'):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter, body = parse_frontmatter(content)
        html_body = markdown_to_html(body)
        
        slug = md_file.stem
        
        projects.append({
            'slug': slug,
            'title': frontmatter.get('title', slug.replace('-', ' ').title()),
            'tagline': frontmatter.get('tagline', ''),
            'icon': frontmatter.get('icon', '📦'),
            'status': frontmatter.get('status', 'Active'),
            'version': frontmatter.get('version', ''),
            'url': frontmatter.get('url', ''),
            'github': frontmatter.get('github', ''),
            'body': html_body,
            'filename': f'project-{slug}.html'
        })
    
    projects.sort(key=lambda x: x['title'].lower())
    return projects

def load_videos():
    """Load all videos from the videos directory."""
    videos = []
    if not VIDEOS_DIR.exists():
        return videos

    for md_file in VIDEOS_DIR.glob('*.md'):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        frontmatter, _ = parse_frontmatter(content)
        slug = md_file.stem
        youtube_id = frontmatter.get('youtube_id', '')

        videos.append({
            'slug': slug,
            'title': frontmatter.get('title', slug.replace('-', ' ').title()),
            'youtube_id': youtube_id,
            'youtube_url': f'https://youtu.be/{youtube_id}',
            'thumbnail_url': f'https://img.youtube.com/vi/{youtube_id}/hqdefault.jpg',
            'description': frontmatter.get('description', ''),
            'date': frontmatter.get('date', ''),
        })

    videos.sort(key=lambda x: x['date'], reverse=True)
    return videos

def build_essay_page(essay, essays):
    """Build a single essay HTML page."""
    # Find prev/next essays
    idx = next((i for i, e in enumerate(essays) if e['slug'] == essay['slug']), 0)
    prev_essay = essays[idx + 1] if idx + 1 < len(essays) else None
    next_essay = essays[idx - 1] if idx > 0 else None
    
    prev_link = f'<a href="{prev_essay["filename"]}" class="btn">← Prev</a>' if prev_essay else '<button class="btn" disabled>← Prev</button>'
    next_link = f'<a href="{next_essay["filename"]}" class="btn">Next →</a>' if next_essay else '<button class="btn" disabled>Next →</button>'
    
    # Format date nicely
    date_display = essay['date']
    if date_display:
        try:
            dt = datetime.strptime(date_display, '%Y-%m-%d')
            date_display = dt.strftime('%B %Y')
        except:
            pass
    
    return render_template('essay.html',
        site_name=SITE_NAME,
        title=essay['title'],
        date=date_display,
        body=essay['body'],
        prev_link=prev_link,
        next_link=next_link
    )

def build_project_page(project):
    """Build a single project HTML page."""
    return render_template('project.html',
        site_name=SITE_NAME,
        title=project['title'],
        tagline=project['tagline'],
        icon=project['icon'],
        status=project['status'],
        version=project['version'],
        url=project['url'],
        github=project['github'],
        body=project['body']
    )

def build_index(essays, projects, videos):
    """Build the main index page."""
    # Generate essay list HTML
    essay_items = []
    for essay in essays:
        date_display = essay['date']
        if date_display:
            try:
                dt = datetime.strptime(date_display, '%Y-%m-%d')
                date_display = dt.strftime('%B %Y')
            except:
                pass
        essay_items.append(f'''<li class="essay-item">
            <a href="{essay['filename']}" class="essay-link">{essay['title']}</a>
            <span class="essay-date">{date_display}</span>
        </li>''')
    essays_html = '\n'.join(essay_items) if essay_items else '<li class="essay-item">No essays yet. Add .md files to the essays/ folder.</li>'
    
    # Generate project cards HTML
    project_cards = []
    for project in projects:
        github_link = (
            f'''<a href="{project['github']}" target="_blank" rel="noopener" class="project-repo">GitHub repo</a>'''
            if project['github'] else ''
        )
        project_cards.append(f'''<div class="project-card win95-outset">
            <div class="project-icon">{project['icon']}</div>
            <div class="project-name"><a href="{project['filename']}" class="essay-link">{project['title']}</a></div>
            <div class="project-desc">{project['tagline']}</div>
            {github_link}
        </div>''')
    projects_html = '\n'.join(project_cards) if project_cards else '<p>No projects yet. Add .md files to the projects/ folder.</p>'
    
    # Generate video cards HTML
    video_cards = []
    for video in videos:
        date_display = video['date']
        if date_display:
            try:
                dt = datetime.strptime(str(date_display), '%Y-%m-%d')
                date_display = dt.strftime('%B %Y')
            except:
                pass
        video_cards.append(f'''<div class="video-card">
            <a href="{video['youtube_url']}" target="_blank" rel="noopener" class="video-thumbnail-link">
                <div class="video-thumbnail">
                    <img src="{video['thumbnail_url']}" alt="{video['title']}" loading="lazy">
                    <div class="video-play-overlay">
                        <div class="video-play-btn">&#9654;</div>
                    </div>
                </div>
            </a>
            <div class="video-info">
                <div class="video-title">{video['title']}</div>
                <div class="video-desc">{video['description']}</div>
                <div class="video-date">{date_display}</div>
            </div>
        </div>''')
    videos_html = '\n'.join(video_cards) if video_cards else '<p class="video-empty">No videos yet. Add .md files to the videos/ folder.</p>'

    return render_template('index.html',
        site_name=SITE_NAME,
        site_description=SITE_DESCRIPTION,
        essays_list=essays_html,
        projects_grid=projects_html,
        videos_list=videos_html,
        current_date=datetime.now().strftime('%B %d, %Y')
    )

def build_site():
    """Build the entire site."""
    print(f"\n⚡ Building {SITE_NAME}...")
    print("=" * 40)
    
    # Create output directory
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)
    
    # Load content
    essays = load_essays()
    projects = load_projects()
    videos = load_videos()
    
    print(f"📄 Found {len(essays)} essays")
    print(f"📦 Found {len(projects)} projects")
    print(f"🎬 Found {len(videos)} videos")
    
    # Build essay pages
    for essay in essays:
        html = build_essay_page(essay, essays)
        output_path = OUTPUT_DIR / essay['filename']
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"   ✓ {essay['filename']}")
    
    # Build project pages
    for project in projects:
        html = build_project_page(project)
        output_path = OUTPUT_DIR / project['filename']
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"   ✓ {project['filename']}")
    
    # Build index page
    index_html = build_index(essays, projects,videos )
    with open(OUTPUT_DIR / 'index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)
    print(f"   ✓ index.html")
    
    print("=" * 40)
    print(f"✅ Site built successfully!")
    print(f"📁 Output: {OUTPUT_DIR}/")
    print()

def serve_site(port=8000):
    """Start a local development server."""
    os.chdir(OUTPUT_DIR)
    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(('localhost', port), handler)
    print(f"🌐 Serving at http://localhost:{port}")
    print("   Press Ctrl+C to stop\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f"Build {SITE_NAME}'s website")
    parser.add_argument('--serve', '-s', action='store_true', help='Start local server after build')
    parser.add_argument('--port', '-p', type=int, default=8000, help='Server port (default: 8000)')
    args = parser.parse_args()
    
    # Create directories if they don't exist
    ESSAYS_DIR.mkdir(exist_ok=True)
    PROJECTS_DIR.mkdir(exist_ok=True)
    VIDEOS_DIR.mkdir(exist_ok=True)
    TEMPLATES_DIR.mkdir(exist_ok=True)
    
    # Build the site
    build_site()
    
    # Optionally serve
    if args.serve:
        serve_site(args.port)
