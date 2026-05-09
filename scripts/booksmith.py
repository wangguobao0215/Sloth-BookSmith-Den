#!/usr/bin/env python3
"""
Booksmith v2.0 -- Professional Book Typesetting Engine
Converts Markdown to publication-quality PDF using Playwright + Paged.js.
Features: running headers/footers, drop caps, three-line tables, figure captions,
          sidebars, epigraphs, bookmarks, CJK-optimized typography.
"""
import os
import sys
import re
import argparse
import subprocess
import tempfile
import shutil
from datetime import date
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Error: Playwright is required. Install: pip install playwright")
    print("Then run: playwright install chromium")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install: pip install pyyaml")
    sys.exit(1)

import markdown

# ─── Paths ───────────────────────────────────────────────────────────────
SKILL_DIR = Path(__file__).parent.parent
PRESETS_DIR = SKILL_DIR / "presets"
ASSETS_DIR = SKILL_DIR / "assets"

# ─── Font Detection ───────────────────────────────────────────────────────
def detect_fonts(platform_name=None):
    """Detect available fonts with professional CJK fallback chains."""
    import platform
    plat = platform_name or platform.system()

    if plat == "Darwin":
        return {
            "heading": "'PingFang SC', 'Hiragino Sans GB', 'STZhongsong', 'Heiti SC', 'SimHei', 'Microsoft YaHei', sans-serif",
            "body": "'PingFang SC', 'Songti SC', 'STSong', 'SimSun', 'NSimSun', serif",
            "cjk": "'PingFang SC', 'Songti SC', 'STSong', 'SimSun', 'NSimSun', serif",
            "cjk_bold": "'PingFang SC', 'STHeiti', 'SimHei', 'Heiti SC', 'Microsoft YaHei', sans-serif",
            "kai": "'Kaiti SC', 'STKaiti', 'KaiTi', serif",
            "fang": "'Fangsong SC', 'STFangsong', 'FangSong', serif",
            "mono": "'Menlo', 'Monaco', 'Courier New', monospace",
            "latin": "'Georgia', 'Times New Roman', serif",
        }
    elif plat == "Windows":
        return {
            "heading": "'Microsoft YaHei', 'PingFang SC', 'SimHei', 'STZhongsong', sans-serif",
            "body": "'Microsoft YaHei', 'SimSun', 'NSimSun', 'STSong', 'Songti SC', serif",
            "cjk": "'Microsoft YaHei', 'SimSun', 'NSimSun', 'STSong', 'Songti SC', serif",
            "cjk_bold": "'Microsoft YaHei', 'PingFang SC', 'SimHei', 'STHeiti', sans-serif",
            "kai": "'KaiTi', 'STKaiti', 'Kaiti SC', serif",
            "fang": "'FangSong', 'STFangsong', 'Fangsong SC', serif",
            "mono": "'Consolas', 'Courier New', 'Lucida Console', monospace",
            "latin": "'Georgia', 'Times New Roman', 'Cambria', serif",
        }
    else:
        return {
            "heading": "'Noto Sans CJK SC', 'PingFang SC', 'WenQuanYi Micro Hei', 'SimHei', sans-serif",
            "body": "'Noto Serif CJK SC', 'PingFang SC', 'WenQuanYi Micro Hei', 'SimSun', serif",
            "cjk": "'Noto Serif CJK SC', 'PingFang SC', 'WenQuanYi Micro Hei', 'SimSun', serif",
            "cjk_bold": "'Noto Sans CJK SC Bold', 'PingFang SC', 'WenQuanYi Micro Hei', sans-serif",
            "kai": "'AR PL UKai', 'KaiTi', serif",
            "fang": "'AR PL UMing', 'FangSong', serif",
            "mono": "'DejaVu Sans Mono', 'Consolas', monospace",
            "latin": "'Liberation Serif', 'Georgia', serif",
        }


# ─── Preset Loading ───────────────────────────────────────────────────────
def load_preset(name):
    """Load a theme preset from YAML file."""
    preset_path = PRESETS_DIR / f"{name}.yaml"
    if not preset_path.exists():
        print(f"Error: Preset '{name}' not found at {preset_path}")
        print(f"Available presets: {[f.stem for f in PRESETS_DIR.glob('*.yaml')]}")
        sys.exit(1)

    with open(preset_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ─── Frontmatter ──────────────────────────────────────────────────────────
def extract_frontmatter(md_text):
    """Extract YAML frontmatter from markdown."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', md_text, re.DOTALL)
    if match:
        try:
            fm = yaml.safe_load(match.group(1)) or {}
            body = md_text[match.end():]
            return fm, body
        except yaml.YAMLError:
            return {}, md_text
    return {}, md_text


# ─── Markdown Parsing ─────────────────────────────────────────────────────
def parse_markdown_structure(md_text):
    """Parse markdown into chapters with epigraph and sub-chapter support."""
    lines = md_text.split('\n')
    chapters = []
    current_chapter = None
    current_content = []

    for line in lines:
        if line.startswith('# '):
            if current_chapter is not None:
                current_chapter['content'] = '\n'.join(current_content)
                current_chapter['sub_chapters'] = _extract_sub_chapters(current_content, len(chapters))
                chapters.append(current_chapter)
            current_chapter = {
                'title': line[2:].strip(),
                'content': '',
                'epigraph': None,
                'sub_chapters': [],
            }
            current_content = []
        else:
            # Check for epigraph: > "quote" -- source
            if current_chapter is not None and current_chapter['epigraph'] is None:
                stripped = line.lstrip('>').strip()
                if line.startswith('> ') and ('--' in stripped or '\u2014' in stripped):
                    parts = re.split(r'\s*[-\u2013\u2014]{2,}\s*', stripped, maxsplit=1)
                    if len(parts) == 2:
                        current_chapter['epigraph'] = {
                            'text': parts[0].strip().strip('"').strip("'").strip(),
                            'source': parts[1].strip()
                        }
                        continue
            current_content.append(line)

    if current_chapter is not None:
        current_chapter['content'] = '\n'.join(current_content)
        current_chapter['sub_chapters'] = _extract_sub_chapters(current_content, len(chapters))
        chapters.append(current_chapter)

    return chapters


def _extract_sub_chapters(content_lines, chapter_index=0):
    """Extract H2 headings from chapter content as sub-chapters with anchor IDs."""
    subs = []
    counter = 0
    for line in content_lines:
        if line.startswith('## '):
            counter += 1
            title = line[3:].strip()
            anchor = f'sub-ch{chapter_index}-{counter}'
            subs.append({'title': title, 'anchor': anchor})
    return subs


def convert_markdown_to_html(md_text):
    """Convert markdown text to HTML with extensions."""
    md = markdown.Markdown(extensions=[
        'tables',
        'fenced_code',
        'toc',
        'smarty',
        'nl2br',
        'footnotes',
        'codehilite',
    ])
    return md.convert(md_text)


def process_body_html(html, chapter_index=0):
    """Post-process HTML: figure/table numbering, sidebars, footnotes."""
    # ── Figure numbering ──
    fig_counter = 0

    def replace_figure(m):
        nonlocal fig_counter
        fig_counter += 1
        src = m.group(1)
        alt = m.group(2) if m.group(2) else ''
        return (
            f'<figure><img src="{src}" alt="{alt}"/>'
            f'<figcaption>\u56fe {chapter_index + 1}-{fig_counter}  {alt}</figcaption></figure>'
        )

    # Match any <img> inside <p>...</p> (supports arbitrary attribute order, title, etc.)
    def replace_img_figure(m):
        nonlocal fig_counter
        fig_counter += 1
        tag = m.group(0)
        src_match = re.search(r'src="([^"]+)"', tag)
        src = src_match.group(1) if src_match else ''
        alt_match = re.search(r'alt="([^"]*)"', tag)
        alt = alt_match.group(1) if alt_match else ''
        return (
            f'<figure><img src="{src}" alt="{alt}"/>'
            f'<figcaption>\u56fe {chapter_index + 1}-{fig_counter}  {alt}</figcaption></figure>'
        )

    html = re.sub(r'<p>\s*<img\s+[^>]+/?>\s*</p>', replace_img_figure, html)

    # ── Table numbering (three-line style wrapper) ──
    table_counter = 0

    def replace_table(m):
        nonlocal table_counter
        table_counter += 1
        table_html = m.group(0)
        return (
            f'<div class="table-wrapper">'
            f'<div class="table-caption">\u8868 {chapter_index + 1}-{table_counter}</div>'
            f'{table_html}</div>'
        )

    html = re.sub(r'<table>.*?</table>', replace_table, html, flags=re.DOTALL)

    # ── Sidebar / callout detection ──
    def replace_blockquote(m):
        inner = m.group(1)
        match = re.search(r'<p><strong>([^<]+)</strong>[:\uff1a]?\s*(.*?)</p>', inner)
        if match:
            label = match.group(1)
            rest = match.group(2)
            # Build replacement
            new_inner = inner.replace(
                match.group(0),
                f'<p class="sidebar-title">{label}</p><p>{rest}</p>',
                1
            )
            return f'<aside class="sidebar">{new_inner}</aside>'
        return m.group(0)

    html = re.sub(r'<blockquote>(.*?)</blockquote>', replace_blockquote, html, flags=re.DOTALL)

    # ── Footnote references styling ──
    html = re.sub(
        r'<sup\s+id="fnref:(\d+)">',
        r'<sup class="footnote-ref" id="fnref:\1">',
        html,
    )

    # ── Footnotes section styling ──
    html = html.replace('<div class="footnote">', '<div class="footnotes"><hr/><ol>')
    html = html.replace('</div><!--footnote-->', '</ol></div>')

    # ── Cross-reference auto-linking ──
    # Patterns: "见第3章", "参见第3章", "第3章"
    def xref_replace(m):
        prefix = m.group(1) or ''
        num = m.group(2)
        # Try numeric chapter index (0-based)
        try:
            ch_idx = int(num) - 1
            return f'{prefix}<a href="#ch{ch_idx}">第{num}章</a>'
        except ValueError:
            return m.group(0)

    # Numeric references: 见第3章 / 参见第3章 / 第3章
    # Longer prefixes first to avoid splitting "参见" into "见" + "参"
    html = re.sub(
        r'((?:参见|参阅|参考|见)?)\s*第\s*(\d+)\s*章(?!\d)',
        xref_replace,
        html,
    )

    # ── Add anchor IDs to H2 headings for sub-chapter linking ──
    h2_counter = 0
    def add_h2_id(m):
        nonlocal h2_counter
        h2_counter += 1
        title = m.group(1)
        return f'<h2 id="sub-ch{chapter_index}-{h2_counter}">{title}</h2>'

    html = re.sub(r'<h2>(.*?)</h2>', add_h2_id, html)

    return html


# ─── HTML Generators ──────────────────────────────────────────────────────
def generate_cover_html(config):
    """Generate cover page HTML with decorative elements."""
    title = config.get('title', 'Untitled')
    author = config.get('author', '')
    date_str = config.get('date', str(date.today()))
    subtitle = config.get('subtitle', '')
    publisher = config.get('publisher', '')
    cover_style = config.get('cover_style', 'gradient')
    colors = config['colors']

    if cover_style == 'gradient':
        bg_css = (
            f"background: linear-gradient(160deg, {colors['cover_gradient_start']} 0%, "
            f"{colors['cover_gradient_end']} 50%, {colors['cover_gradient_start']} 100%);"
        )
    elif cover_style == 'solid':
        bg_css = f"background-color: {colors['cover_gradient_start']};"
    elif cover_style == 'image' and config.get('cover_image'):
        bg_css = f"background: url('{config['cover_image']}') center/cover no-repeat;"
    else:
        bg_css = (
            f"background: linear-gradient(160deg, {colors['cover_gradient_start']} 0%, "
            f"{colors['cover_gradient_end']} 50%, {colors['cover_gradient_start']} 100%);"
        )

    # Decorative SVG corner ornaments
    ornament_svg = f'''<svg class="cover-corner top-left" viewBox="0 0 100 100" preserveAspectRatio="none">
<path d="M0,0 L100,0 L0,100 Z" fill="{colors['cover_accent']}" opacity="0.12"/>
</svg>
<svg class="cover-corner bottom-right" viewBox="0 0 100 100" preserveAspectRatio="none">
<path d="M100,100 L0,100 L100,0 Z" fill="{colors['cover_accent']}" opacity="0.12"/>
</svg>'''

    publisher_html = f'<p class="cover-publisher">{publisher}</p>' if publisher else ''
    subtitle_html = f'<p class="cover-subtitle">{subtitle}</p>' if subtitle else ''

    return f'''<div class="cover-page" style="{bg_css}">
{ornament_svg}
<div class="cover-border"><div class="cover-border-inner"></div></div>
<div class="cover-content">
{publisher_html}
<h1 class="cover-title">{title}</h1>
{subtitle_html}
<div class="cover-ornament"></div>
<p class="cover-author">{author}</p>
<p class="cover-date">{date_str}</p>
</div>
</div>'''


def generate_copyright_html(config):
    """Generate copyright page HTML."""
    title = config.get('title', 'Untitled')
    author = config.get('author', '')
    isbn = config.get('isbn', '')
    publisher = config.get('publisher', '')
    date_str = config.get('date', str(date.today()))

    isbn_html = f'<p>ISBN\uff1a{isbn}</p>' if isbn else ''
    publisher_html = f'<p>\u51fa\u7248\uff1a{publisher}</p>' if publisher else ''

    return f'''<div class="copyright-page">
<div class="copyright-content">
<h2 class="copyright-title">{title}</h2>
<p class="copyright-author">{author} \u8457</p>
<div class="copyright-divider"></div>
<div class="copyright-details">
<p>\u51fa\u7248\u65e5\u671f\uff1a{date_str}</p>
{isbn_html}
{publisher_html}
<p class="copyright-notice">\u7248\u6743\u6240\u6709 &copy; {date_str[:4]} {author}</p>
<p class="copyright-notice">\u672a\u7ecf\u8bb8\u53ef\uff0c\u4e0d\u5f97\u4ee5\u4efb\u4f55\u65b9\u5f0f\u590d\u5236\u6216\u6284\u88ad\u672c\u4e66\u4e4b\u90e8\u5206\u6216\u5168\u90e8\u5185\u5bb9\u3002</p>
</div>
</div>
</div>'''


def generate_toc_html(chapters, config):
    """Generate table of contents HTML with hierarchy and dot leaders."""
    items = []
    for i, ch in enumerate(chapters):
        # Main chapter (H1)
        items.append(
            f'<li class="toc-item toc-level-1">'
            f'<a href="#ch{i}"><span class="toc-text">{ch["title"]}</span>'
            f'<span class="toc-dots"></span></a></li>'
        )
        # Sub-chapters (H2) with anchor links
        for sub in ch.get('sub_chapters', []):
            if isinstance(sub, dict):
                sub_title = sub['title']
                sub_anchor = sub.get('anchor', f'ch{i}')
            else:
                sub_title = sub
                sub_anchor = f'ch{i}'
            items.append(
                f'<li class="toc-item toc-level-2">'
                f'<a href="#{sub_anchor}"><span class="toc-text">{sub_title}</span>'
                f'<span class="toc-dots"></span></a></li>'
            )

    return f'''<div class="toc-page">
<h2 class="toc-heading">\u76ee \u5f55</h2>
<div class="toc-divider"></div>
<ul class="toc-list">
{''.join(items)}
</ul>
</div>'''


def generate_chapter_opener(chapter, index, config):
    """Generate chapter opener page with epigraph support."""
    colors = config['colors']
    epigraph_html = ''
    if chapter.get('epigraph'):
        epigraph_html = (
            f'<div class="epigraph">'
            f'<p class="epigraph-text">\u201c{chapter["epigraph"]["text"]}\u201d</p>'
            f'<p class="epigraph-source">\u2014\u2014 {chapter["epigraph"]["source"]}</p>'
            f'</div>'
        )

    return f'''<div class="chapter-opener" id="ch{index}">
<div class="chapter-opener-content">
<p class="chapter-label">\u7b2c {index + 1} \u7ae0</p>
<h2 class="chapter-heading">{chapter['title']}</h2>
<div class="chapter-ornament"></div>
{epigraph_html}
</div>
</div>'''


def generate_body_html(chapters, config):
    """Generate full body HTML with chapters."""
    parts = []
    for i, chapter in enumerate(chapters):
        parts.append(f'<section class="chapter">')
        parts.append(generate_chapter_opener(chapter, i, config))

        chapter_html = convert_markdown_to_html(chapter['content'])
        chapter_html = process_body_html(chapter_html, chapter_index=i)

        # Skip empty body sections (e.g. TOC chapter with only page-break div)
        clean = re.sub(r'<div class="page-break"></div>', '', chapter_html)
        clean = re.sub(r'\s', '', clean)
        if clean:
            parts.append(f'<div class="chapter-body" id="ch-body-{i}">{chapter_html}</div>')

        parts.append('</section>')

    body = '\n'.join(parts)
    # Inject watermark if configured
    watermark = config.get('watermark', '')
    if watermark:
        body += f'\n<div class="watermark">{watermark}</div>'
    return body


# ─── CSS Generator ────────────────────────────────────────────────────────
def generate_css(config):
    """Generate complete CSS with professional book typography."""
    colors = config['colors']
    fonts = config['fonts']
    sizes = config['sizes']
    margins = config['page_margins']
    lh = config['line_height']
    indent = config['first_line_indent']
    para_sp = config['paragraph_spacing']

    # Dynamic line-height based on body size
    body_size = sizes['body']
    if body_size <= 10:
        computed_lh = 1.8
    elif body_size <= 11:
        computed_lh = 1.75
    else:
        computed_lh = 1.65

    top_m = margins.get('top', 28)
    bottom_m = margins.get('bottom', 28)
    # E-book symmetric margins (no binding gutter)
    side_m = margins.get('side', margins.get('inner', 25))
    left_m = side_m
    right_m = side_m

    page_size = config.get('page_size', 'A5')

    return f'''
/* ═══════════════════════════════════════════════════════════════════════
   Booksmith v2.0 -- Professional Book Typography
   ═══════════════════════════════════════════════════════════════════════ */

/* ─── Page Setup ─── */
@page {{
    size: {page_size};
    margin-top: {top_m}mm;
    margin-bottom: {bottom_m}mm;
    margin-left: {left_m}mm;
    margin-right: {right_m}mm;
    @top-center {{
        content: string(chapter-title);
        font-family: {fonts['cjk']};
        font-size: 8.5pt;
        color: {colors['text_faded']};
        border-bottom: 0.5pt solid {colors['border']};
        padding-bottom: 2mm;
    }}
    @bottom-center {{
        content: counter(page);
        font-family: {fonts['cjk']};
        font-size: 9pt;
        color: {colors['text_faded']};
    }}
}}

@page cover {{
    margin: 0;
    @top-center {{ content: none; }}
    @bottom-center {{ content: none; }}
}}

@page copyright, toc {{
    @top-center {{ content: none; }}
}}

@page chapter-opener {{
    @top-center {{ content: none; }}
}}

/* ─── Base ─── */
* {{ margin: 0; padding: 0; box-sizing: border-box; }}

html {{
    font-family: {fonts['body']};
    font-size: {body_size}pt;
    line-height: {computed_lh};
    color: {colors['text']};
    background-color: {colors['page_bg']};
    text-align: justify;
    hyphens: auto;
    -webkit-hyphens: auto;
}}

/* ─── Cover Page ─── */
.cover-page {{
    page: cover;
    break-after: page;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    min-height: 100vh;
    color: {colors['cover_text']};
    overflow: hidden;
}}

.cover-corner {{
    position: absolute;
    width: 100px;
    height: 100px;
    z-index: 1;
}}

.cover-corner.top-left {{ top: 20px; left: 20px; }}
.cover-corner.bottom-right {{ bottom: 20px; right: 20px; transform: rotate(180deg); }}

.cover-border {{
    position: absolute;
    top: 30px;
    left: 30px;
    right: 30px;
    bottom: 30px;
    border: 1px solid rgba(255,255,255,0.12);
    padding: 12px;
    z-index: 1;
}}

.cover-border-inner {{
    width: 100%;
    height: 100%;
    border: 1px solid rgba(255,255,255,0.08);
}}

.cover-content {{
    position: relative;
    z-index: 2;
    max-width: 78%;
}}

.cover-publisher {{
    font-size: 10pt;
    letter-spacing: 0.15em;
    color: {colors['cover_accent']};
    opacity: 0.85;
    margin-bottom: 3em;
}}

.cover-title {{
    font-family: {fonts['heading']};
    font-size: {sizes['cover_title']}pt;
    font-weight: 700;
    letter-spacing: 0.02em;
    line-height: 1.25;
    margin-bottom: 0.6em;
    word-break: keep-all;
    overflow-wrap: break-word;
}}

.cover-subtitle {{
    font-size: 13pt;
    color: {colors['cover_accent']};
    opacity: 0.9;
    font-weight: 400;
    margin-bottom: 1.8em;
    line-height: 1.5;
}}

.cover-ornament {{
    width: 45px;
    height: 2px;
    background: {colors['cover_accent']};
    opacity: 0.6;
    margin: 0 auto;
}}

.cover-author {{
    font-size: 11pt;
    letter-spacing: 0.3em;
    margin-top: 2.5em;
    color: {colors['cover_text']};
    opacity: 0.9;
}}

.cover-date {{
    font-size: 9pt;
    color: {colors['cover_accent']};
    opacity: 0.7;
    margin-top: 0.6em;
}}

/* ─── Copyright Page ─── */
.copyright-page {{
    page: copyright;
    break-after: page;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 80vh;
}}

.copyright-content {{ max-width: 65%; }}

.copyright-title {{
    font-family: {fonts['heading']};
    font-size: 15pt;
    font-weight: 700;
    margin-bottom: 0.3em;
}}

.copyright-author {{
    font-size: 10.5pt;
    color: {colors['text_faded']};
    margin-bottom: 1.8em;
}}

.copyright-divider {{
    width: 30px;
    height: 1px;
    background: {colors['border']};
    margin-bottom: 1.2em;
}}

.copyright-details {{
    font-size: 9pt;
    line-height: 1.9;
    color: {colors['text_faded']};
}}

.copyright-notice {{
    font-size: 8pt;
    font-style: italic;
    margin-top: 0.4em;
}}

/* ─── TOC Page ─── */
.toc-page {{
    page: toc;
    break-after: page;
}}

.toc-heading {{
    font-family: {fonts['heading']};
    font-size: 22pt;
    font-weight: 700;
    text-align: center;
    margin-bottom: 0.4em;
    letter-spacing: 0.15em;
}}

.toc-divider {{
    width: 28px;
    height: 2px;
    background: {colors['accent']};
    margin: 0 auto 2.5em;
}}

.toc-list {{
    list-style: none;
    max-width: 78%;
    margin: 0 auto;
}}

.toc-item {{
    margin-bottom: 0.6em;
    font-size: 10.5pt;
    line-height: 1.5;
    border-bottom: none;
    padding-bottom: 0.2em;
}}

.toc-item.toc-level-1 {{
    font-weight: 600;
    font-size: 11pt;
    margin-top: 1em;
}}

.toc-item.toc-level-1:first-child {{
    margin-top: 0;
}}

.toc-item.toc-level-2 {{
    padding-left: 2em;
    font-size: 10pt;
    font-weight: 400;
}}

.toc-item a {{
    color: {colors['text']};
    text-decoration: none;
    display: flex;
    align-items: baseline;
}}

.toc-text {{
    flex-shrink: 0;
}}

.toc-dots {{
    flex-grow: 1;
    border-bottom: 1px dotted {colors['border']};
    margin: 0 0.5em;
    min-width: 2em;
}}

.toc-item a::after {{
    content: target-counter(attr(href), page);
    font-family: {fonts['cjk']};
    font-size: 9.5pt;
    color: {colors['text_faded']};
    flex-shrink: 0;
    min-width: 1.5em;
    text-align: right;
}}

/* ─── Chapter ─── */
.chapter {{
    page: chapter;
}}

/* ─── Chapter Opener ─── */
.chapter-opener {{
    page: chapter-opener;
    break-before: page;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 50vh;
    text-align: center;
}}

.chapter:first-of-type .chapter-opener {{
    break-before: auto;
}}

.chapter-opener-content {{ max-width: 68%; }}

.chapter-label {{
    font-size: 9.5pt;
    letter-spacing: 0.35em;
    color: {colors['text_faded']};
    margin-bottom: 1.2em;
    text-transform: uppercase;
}}

.chapter-heading {{
    font-family: {fonts['heading']};
    font-size: {sizes['chapter_title']}pt;
    font-weight: 700;
    line-height: 1.25;
    margin-bottom: 0.8em;
    string-set: chapter-title content(text);
}}

.chapter-ornament {{
    width: 32px;
    height: 2px;
    background: {colors['accent']};
    margin: 0 auto;
    opacity: 0.8;
}}

/* ─── Epigraph ─── */
.epigraph {{
    margin-top: 2.5em;
    max-width: 55%;
    text-align: left;
    font-style: italic;
}}

.epigraph-text {{
    font-size: 10.5pt;
    line-height: 1.85;
    color: {colors['text_faded']};
    margin-bottom: 0.4em;
}}

.epigraph-source {{
    font-size: 9pt;
    color: {colors['text_faded']};
    text-align: right;
    font-style: normal;
    opacity: 0.8;
}}

/* ─── Chapter Body ─── */
.chapter-body {{
    page: body;
    text-align: justify;
    break-before: page;
    overflow: hidden;
}}

.chapter:first-of-type .chapter-opener {{
    counter-reset: page 1;
}}

/* ─── Drop Cap ─── */
.chapter-body > p:first-of-type::first-letter {{
    float: left;
    font-family: {fonts['heading']};
    font-size: 3.2em;
    line-height: 0.82;
    padding-right: 0.08em;
    margin-top: 0.06em;
    font-weight: 700;
    color: {colors['text']};
}}

/* ─── Headings ─── */
.chapter-body h1 {{
    font-family: {fonts['heading']};
    font-size: {sizes['h1']}pt;
    font-weight: 700;
    margin: 1.8em 0 0.8em;
    break-after: avoid;
    line-height: 1.3;
}}

.chapter-body h2 {{
    font-family: {fonts['heading']};
    font-size: {sizes['h2']}pt;
    font-weight: 700;
    margin: 1.4em 0 0.7em;
    break-before: page;
    break-after: avoid;
    line-height: 1.35;
}}

.chapter-body h2:first-of-type {{
    break-before: auto;
}}

.chapter-body h3 {{
    font-family: {fonts['heading']};
    font-size: {sizes['h3']}pt;
    font-weight: 700;
    margin: 1.2em 0 0.5em;
    break-after: avoid;
    line-height: 1.4;
}}

.chapter-body h4 {{
    font-family: {fonts['heading']};
    font-size: {sizes['body'] + 1}pt;
    font-weight: 700;
    margin: 1em 0 0.4em;
    break-after: avoid;
}}

/* ─── Paragraphs ─── */
.chapter-body p {{
    text-indent: {indent}em;
    margin-bottom: {para_sp}em;
    orphans: 4;
    widows: 4;
}}

.chapter-body p:first-of-type {{
    text-indent: 0;
}}

.chapter-body h1 + p,
.chapter-body h2 + p,
.chapter-body h3 + p,
.chapter-body h4 + p {{
    text-indent: 0;
}}

/* ─── Lists ─── */
.chapter-body ul, .chapter-body ol {{
    margin: 1em 0;
    padding-left: 2em;
}}

.chapter-body li {{
    margin-bottom: 0.4em;
    text-indent: 0;
}}

/* ─── Blockquote ─── */
.chapter-body blockquote {{
    border-left: 3px solid {colors['blockquote_border']};
    padding-left: 1.5em;
    margin: 1.5em 0;
    color: {colors['text_faded']};
    font-style: italic;
}}

.chapter-body blockquote p {{
    text-indent: 0;
    margin-bottom: 0.4em;
}}

.chapter-body blockquote p:last-child {{
    margin-bottom: 0;
}}

/* ─── Sidebar / Callout ─── */
.chapter-body .sidebar {{
    background: {colors.get('sidebar_bg', '#F5F2ED')};
    border-left: 4px solid {colors['accent']};
    padding: 1em 1.5em;
    margin: 1.5em 0;
    font-style: normal;
    break-inside: avoid;
}}

.chapter-body .sidebar p {{
    text-indent: 0;
    margin-bottom: 0.4em;
}}

.chapter-body .sidebar .sidebar-title {{
    font-weight: 700;
    color: {colors['accent']};
    font-size: {sizes['body']}pt;
    margin-bottom: 0.3em;
}}

/* ─── Code ─── */
.chapter-body pre {{
    background: {colors['code_bg']};
    padding: 1em;
    border-radius: 3px;
    margin: 1.5em 0;
    overflow-x: auto;
    font-size: {sizes['code']}pt;
    line-height: 1.45;
    break-inside: avoid;
}}

.chapter-body code {{
    font-family: {fonts['mono']};
    font-size: {sizes['code']}pt;
    line-height: 1.4;
}}

.chapter-body p code {{
    background: {colors['code_bg']};
    padding: 0.1em 0.35em;
    border-radius: 2px;
    font-size: 0.88em;
}}

/* ─── Code Highlighting (Pygments) ─── */
.chapter-body .codehilite {{
    background: {colors['code_bg']};
    padding: 0;
    border-radius: 3px;
    margin: 1.5em 0;
    overflow-x: auto;
    font-size: {sizes['code']}pt;
    line-height: 1.45;
    break-inside: avoid;
}}
.chapter-body .codehilite pre {{
    background: transparent;
    padding: 1em;
    margin: 0;
    overflow-x: auto;
}}
.chapter-body .codehilite .hll {{ background-color: rgba(0,0,0,0.05); }}
.chapter-body .codehilite .c {{ color: {colors['text_faded']}; font-style: italic; }}
.chapter-body .codehilite .k {{ color: {colors['accent']}; font-weight: bold; }}
.chapter-body .codehilite .o {{ color: {colors['text']}; }}
.chapter-body .codehilite .ch {{ color: {colors['text_faded']}; font-style: italic; }}
.chapter-body .codehilite .cm {{ color: {colors['text_faded']}; font-style: italic; }}
.chapter-body .codehilite .cp {{ color: {colors['text_faded']}; }}
.chapter-body .codehilite .cpf {{ color: {colors['text_faded']}; }}
.chapter-body .codehilite .c1 {{ color: {colors['text_faded']}; font-style: italic; }}
.chapter-body .codehilite .cs {{ color: {colors['text_faded']}; font-weight: bold; }}
.chapter-body .codehilite .gd {{ color: #8B1A1A; }}
.chapter-body .codehilite .ge {{ font-style: italic; }}
.chapter-body .codehilite .gr {{ color: #8B1A1A; }}
.chapter-body .codehilite .gh {{ color: {colors['text_faded']}; font-weight: bold; }}
.chapter-body .codehilite .gi {{ color: #2E8B57; }}
.chapter-body .codehilite .go {{ color: {colors['text_faded']}; }}
.chapter-body .codehilite .gp {{ color: {colors['text_faded']}; font-weight: bold; }}
.chapter-body .codehilite .gs {{ font-weight: bold; }}
.chapter-body .codehilite .gu {{ color: {colors['text_faded']}; font-weight: bold; }}
.chapter-body .codehilite .gt {{ color: #8B1A1A; }}
.chapter-body .codehilite .kc {{ color: {colors['accent']}; font-weight: bold; }}
.chapter-body .codehilite .kd {{ color: {colors['accent']}; font-weight: bold; }}
.chapter-body .codehilite .kn {{ color: {colors['accent']}; font-weight: bold; }}
.chapter-body .codehilite .kp {{ color: {colors['accent']}; }}
.chapter-body .codehilite .kr {{ color: {colors['accent']}; font-weight: bold; }}
.chapter-body .codehilite .kt {{ color: {colors['accent_light']}; font-weight: bold; }}
.chapter-body .codehilite .m {{ color: {colors['accent_light']}; }}
.chapter-body .codehilite .s {{ color: #2E8B57; }}
.chapter-body .codehilite .na {{ color: {colors['text']}; }}
.chapter-body .codehilite .nb {{ color: {colors['accent']}; }}
.chapter-body .codehilite .nc {{ color: {colors['accent']}; font-weight: bold; }}
.chapter-body .codehilite .no {{ color: {colors['accent_light']}; }}
.chapter-body .codehilite .nd {{ color: {colors['text_faded']}; }}
.chapter-body .codehilite .ni {{ color: {colors['text']}; font-weight: bold; }}
.chapter-body .codehilite .ne {{ color: {colors['accent']}; font-weight: bold; }}
.chapter-body .codehilite .nf {{ color: {colors['accent']}; }}
.chapter-body .codehilite .nl {{ color: {colors['text']}; }}
.chapter-body .codehilite .nn {{ color: {colors['accent']}; font-weight: bold; }}
.chapter-body .codehilite .nt {{ color: {colors['accent']}; font-weight: bold; }}
.chapter-body .codehilite .nv {{ color: {colors['text']}; }}
.chapter-body .codehilite .ow {{ color: {colors['accent']}; font-weight: bold; }}
.chapter-body .codehilite .w {{ color: {colors['text_faded']}; }}
.chapter-body .codehilite .mb {{ color: {colors['accent_light']}; }}
.chapter-body .codehilite .mf {{ color: {colors['accent_light']}; }}
.chapter-body .codehilite .mh {{ color: {colors['accent_light']}; }}
.chapter-body .codehilite .mi {{ color: {colors['accent_light']}; }}
.chapter-body .codehilite .mo {{ color: {colors['accent_light']}; }}
.chapter-body .codehilite .sa {{ color: #2E8B57; }}
.chapter-body .codehilite .sb {{ color: #2E8B57; }}
.chapter-body .codehilite .sc {{ color: #2E8B57; }}
.chapter-body .codehilite .dl {{ color: #2E8B57; }}
.chapter-body .codehilite .sd {{ color: {colors['text_faded']}; font-style: italic; }}
.chapter-body .codehilite .s2 {{ color: #2E8B57; }}
.chapter-body .codehilite .se {{ color: {colors['accent_light']}; font-weight: bold; }}
.chapter-body .codehilite .sh {{ color: #2E8B57; }}
.chapter-body .codehilite .si {{ color: {colors['accent_light']}; font-weight: bold; }}
.chapter-body .codehilite .sx {{ color: #2E8B57; }}
.chapter-body .codehilite .sr {{ color: {colors['accent_light']}; }}
.chapter-body .codehilite .s1 {{ color: #2E8B57; }}
.chapter-body .codehilite .ss {{ color: {colors['accent_light']}; }}
.chapter-body .codehilite .bp {{ color: {colors['accent']}; }}
.chapter-body .codehilite .fm {{ color: {colors['accent']}; }}
.chapter-body .codehilite .vc {{ color: {colors['text']}; }}
.chapter-body .codehilite .vg {{ color: {colors['text']}; }}
.chapter-body .codehilite .vi {{ color: {colors['text']}; }}
.chapter-body .codehilite .vm {{ color: {colors['text']}; }}
.chapter-body .codehilite .il {{ color: {colors['accent_light']}; }}

/* ─── Three-line Tables ─── */
.chapter-body .table-wrapper {{
    margin: 1.5em 0;
    break-inside: avoid;
    overflow-x: auto;
    max-width: 100%;
}}

.chapter-body .table-caption {{
    font-size: 9pt;
    color: {colors['text_faded']};
    text-align: center;
    margin-bottom: 0.5em;
    font-family: {fonts['kai']};
}}

.chapter-body table {{
    width: 100%;
    border-collapse: collapse;
    font-size: {sizes.get('table', 9.5)}pt;
    line-height: 1.5;
}}

.chapter-body thead {{
    border-top: 1.5pt solid {colors['text']};
    border-bottom: 0.75pt solid {colors['text']};
}}

.chapter-body tbody {{
    border-bottom: 1.5pt solid {colors['text']};
}}

.chapter-body th, .chapter-body td {{
    padding: 0.45em 0.7em;
    text-align: left;
    vertical-align: top;
    border: none;
}}

.chapter-body th {{
    font-weight: 700;
    background: transparent;
    color: {colors['text']};
    font-family: {fonts['heading']};
}}

/* ─── Figures ─── */
.chapter-body figure {{
    text-align: center;
    margin: 2em 0;
    break-inside: avoid;
}}

.chapter-body figure img {{
    max-width: 100%;
    height: auto;
    display: block;
    margin: 0 auto;
}}

.chapter-body figcaption {{
    font-size: 9pt;
    font-style: normal;
    color: {colors['text_faded']};
    margin-top: 0.5em;
    text-align: center;
    font-family: {fonts['kai']};
}}

/* ─── Horizontal Rule ─── */
.chapter-body hr {{
    border: none;
    border-top: 1px solid {colors['border']};
    margin: 2em auto;
    width: 20%;
}}

/* ─── Links ─── */
.chapter-body a {{
    color: {colors.get('link', colors['accent'])};
    text-decoration: none;
    border-bottom: 1px dotted {colors.get('link', colors['accent'])};
}}

/* ─── Footnotes ─── */
.chapter-body .footnotes {{
    margin-top: 2.5em;
    padding-top: 1em;
    border-top: 0.75pt solid {colors['border']};
    font-size: 8.5pt;
    line-height: 1.55;
}}

.chapter-body .footnotes ol {{
    padding-left: 1.5em;
    margin: 0;
}}

.chapter-body .footnotes li {{
    margin-bottom: 0.25em;
}}

.chapter-body .footnote-ref {{
    font-size: 0.75em;
    vertical-align: super;
    line-height: 0;
}}

/* ─── Table Scrollbar (e-book preview) ─── */
.chapter-body .table-wrapper::-webkit-scrollbar {{
    height: 4px;
}}
.chapter-body .table-wrapper::-webkit-scrollbar-track {{
    background: {colors['page_bg']};
}}
.chapter-body .table-wrapper::-webkit-scrollbar-thumb {{
    background: {colors['border']};
    border-radius: 2px;
}}

/* ─── Watermark ─── */
.watermark {{
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-30deg);
    font-family: {fonts['cjk']};
    font-size: 36pt;
    color: {colors['text_faded']};
    opacity: 0.08;
    pointer-events: none;
    z-index: 1000;
    white-space: nowrap;
    letter-spacing: 0.15em;
}}

/* ─── Page Break Utility ─── */
.page-break {{
    break-after: page;
    page-break-after: always;
    height: 0;
    overflow: hidden;
    visibility: hidden;
}}
'''


def add_bookmarks(pdf_path, chapters, config):
    """Add PDF bookmarks (outline) and XMP metadata using PyMuPDF."""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        toc = []

        # Front matter bookmarks
        toc.append([1, "\u5c01\u9762", 0])
        toc.append([1, "\u7248\u6743\u9875", 1])
        toc.append([1, "\u76ee\u5f55", 2])

        # Find chapter pages by searching for chapter opener text
        for i, ch in enumerate(chapters):
            ch_label = f"\u7b2c{i + 1}\u7ae0 {ch['title']}"
            found = False
            ch_page = None
            for page_num in range(min(3, len(doc)), len(doc)):
                page = doc[page_num]
                text = page.get_text()
                # Look for "第 X 章" followed by chapter title
                if f"\u7b2c {i + 1} \u7ae0" in text and ch['title'][:10] in text:
                    toc.append([1, ch_label, page_num])
                    ch_page = page_num
                    found = True
                    break
            if not found:
                # Fallback: estimate position
                est_page = 3 + i * 10
                if est_page < len(doc):
                    toc.append([1, ch_label, est_page])
                    ch_page = est_page

            # Add sub-chapter (H2) bookmarks under this chapter
            if ch_page is not None:
                for sub in ch.get('sub_chapters', []):
                    sub_title = sub['title'] if isinstance(sub, dict) else sub
                    sub_anchor = sub.get('anchor', '') if isinstance(sub, dict) else ''
                    # Try to find sub-chapter page by searching for its title
                    sub_found = False
                    for page_num in range(ch_page, len(doc)):
                        page = doc[page_num]
                        text = page.get_text()
                        if sub_title[:8] in text:
                            toc.append([2, sub_title, page_num])
                            sub_found = True
                            break
                    if not sub_found:
                        toc.append([2, sub_title, ch_page])

        if toc:
            doc.set_toc(toc)

        # Inject XMP metadata
        title = config.get('title', 'Untitled')
        author = config.get('author', '')
        subject = config.get('subtitle', '')
        desc = config.get('description', '')
        publisher = config.get('publisher', '')
        date_str = config.get('date', str(date.today()))

        xmp = f'''<?xpacket begin="" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
<rdf:Description rdf:about=""
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:xmp="http://ns.adobe.com/xap/1.0/"
  xmlns:pdf="http://ns.adobe.com/pdf/1.3/">
  <dc:title><rdf:Alt><rdf:li xml:lang="zh-CN">{title}</rdf:li></rdf:Alt></dc:title>
  <dc:creator><rdf:Seq><rdf:li>{author}</rdf:li></rdf:Seq></dc:creator>
  <dc:publisher><rdf:Bag><rdf:li>{publisher}</rdf:li></rdf:Bag></dc:publisher>
  <dc:date><rdf:Seq><rdf:li>{date_str}</rdf:li></rdf:Seq></dc:date>
  <dc:description><rdf:Alt><rdf:li xml:lang="zh-CN">{desc or subject}</rdf:li></rdf:Alt></dc:description>
  <pdf:Producer>Booksmith v2.0</pdf:Producer>
</rdf:Description>
</rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>'''

        doc.set_xml_metadata(xmp)
        doc.set_metadata({
            'title': title,
            'author': author,
            'subject': desc or subject,
            'producer': 'Booksmith v2.0',
            'creationDate': date_str,
        })
        doc.save(pdf_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
        doc.close()
        print("PDF bookmarks and XMP metadata added.")
    except ImportError:
        print("Note: PyMuPDF not installed, skipping bookmarks.")
    except Exception as e:
        print(f"Warning: Could not add bookmarks: {e}")


# ─── Common Book Builder ──────────────────────────────────────────────────
def build_book(input_md, config):
    """Parse markdown, apply config, build all book fragments."""
    print(f"Reading: {input_md}")
    with open(input_md, "r", encoding="utf-8") as f:
        md_text = f.read()

    frontmatter, body = extract_frontmatter(md_text)
    for k, v in frontmatter.items():
        if k not in config:
            config[k] = v

    chapters = parse_markdown_structure(body)
    print(f"Found {len(chapters)} chapters")

    # Merge detected system fonts with preset preferences (preset wins)
    detected = detect_fonts()
    preset_fonts = config.get('fonts', {})
    merged_fonts = dict(detected)
    merged_fonts.update(preset_fonts)
    config['fonts'] = merged_fonts

    print("Building layout...")
    cover = generate_cover_html(config)
    copyright_page = generate_copyright_html(config)
    toc = generate_toc_html(chapters, config)
    body_html = generate_body_html(chapters, config)

    return {
        'config': config,
        'chapters': chapters,
        'cover': cover,
        'copyright_page': copyright_page,
        'toc': toc,
        'body_html': body_html,
    }


def assemble_full_html(book, mode='pdf'):
    """Assemble complete HTML for PDF or HTML output."""
    config = book['config']
    page_size = config.get('page_size', 'A5')
    css = generate_css(config)

    if mode == 'pdf':
        paged_js_path = ASSETS_DIR / "paged.polyfill.js"
        paged_js_url = paged_js_path.as_uri() if paged_js_path.exists() else "https://unpkg.com/pagedjs@0.4.3/dist/paged.polyfill.js"
        script_block = f'''<script src="{paged_js_url}"></script>
<script>
document.addEventListener('pagedjs-ready', function() {{
    document.body.classList.add('pagedjs-finished');
}});
setTimeout(function() {{
    document.body.classList.add('pagedjs-finished');
}}, 180000);
</script>'''
        print_css = ''
    else:
        script_block = ''
        # Add @media print for HTML screen viewing with print-like pagination
        print_css = f'''<style>
@media print {{
    body {{ background: white; }}
    .cover-page {{ break-after: page; }}
    .copyright-page {{ break-after: page; }}
    .toc-page {{ break-after: page; }}
    .chapter-opener {{ break-before: page; }}
    .chapter-body {{ break-before: page; }}
    .watermark {{ opacity: 0.04; }}
}}
@media screen {{
    body {{ max-width: 600px; margin: 0 auto; padding: 2em 1em; }}
}}
</style>'''

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{config.get('title', 'Untitled')}</title>
<style>
{css}
</style>
{print_css}
{script_block}
</head>
<body>
{book['cover']}
{book['copyright_page']}
{book['toc']}
{book['body_html']}
</body>
</html>'''


# ─── PDF Generation ───────────────────────────────────────────────────────
def generate_pdf(input_md, output_pdf, config):
    """Generate PDF from markdown via Playwright + Paged.js."""
    print("Booksmith v2.0 -- Professional Book Typesetting Engine")
    print("=" * 50)

    book = build_book(input_md, config)
    full_html = assemble_full_html(book, mode='pdf')

    os.makedirs(os.path.dirname(output_pdf) or '.', exist_ok=True)

    print(f"Rendering PDF: {output_pdf}")
    page_size = config.get('page_size', 'A5')
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(full_html, wait_until="networkidle")

        try:
            page.wait_for_selector("body.pagedjs-finished", timeout=240000)
        except Exception:
            page.wait_for_selector(".pagedjs_page", timeout=240000)
            page.wait_for_timeout(5000)

        page.pdf(
            path=output_pdf,
            format=page_size,
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"},
            print_background=True,
        )
        browser.close()

    add_bookmarks(output_pdf, book['chapters'], book['config'])

    pdf_size = os.path.getsize(output_pdf)
    print(f"Done! {output_pdf}")
    print(f"Size: {pdf_size / 1024 / 1024:.1f} MB")


# ─── HTML Output ──────────────────────────────────────────────────────────
def generate_html_output(input_md, output_html, config):
    """Generate a standalone HTML file (no Paged.js, screen-friendly)."""
    print("Booksmith v2.0 -- HTML Export")
    print("=" * 50)

    book = build_book(input_md, config)
    full_html = assemble_full_html(book, mode='html')

    os.makedirs(os.path.dirname(output_html) or '.', exist_ok=True)
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(full_html)

    html_size = os.path.getsize(output_html)
    print(f"Done! {output_html}")
    print(f"Size: {html_size / 1024:.1f} KB")


# ─── ePub Generation ──────────────────────────────────────────────────────
def generate_epub(input_md, output_epub, config):
    """Generate ePub 2.0 using standard-library zipfile + XML."""
    import zipfile
    import uuid
    import mimetypes
    from xml.sax.saxutils import escape

    print("Booksmith v2.0 -- ePub Export")
    print("=" * 50)

    book = build_book(input_md, config)
    cfg = book['config']
    chapters = book['chapters']
    title = escape(cfg.get('title', 'Untitled'))
    author = escape(cfg.get('author', ''))
    desc = escape(cfg.get('description', cfg.get('subtitle', '')))
    lang = 'zh-CN'
    uid = str(uuid.uuid4())

    os.makedirs(os.path.dirname(output_epub) or '.', exist_ok=True)

    # Build ePub CSS (simplified, no @page, no Paged.js)
    epub_css = generate_css(cfg)
    # Strip @page rules for ePub (readers handle pagination themselves)
    epub_css = re.sub(r'@page[^{]*\{[^}]*\}', '', epub_css, flags=re.DOTALL)
    epub_css = re.sub(r'@page[^{]*\{[^}]*\{[^}]*\}[^}]*\}', '', epub_css, flags=re.DOTALL)
    # Add ePub-friendly base
    epub_css = f'''/* ePub-friendly base */
html {{ -webkit-text-size-adjust: 100%; }}
body {{ margin: 0; padding: 0; }}
'''+ epub_css

    def xhtml_wrapper(content):
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{lang}">
<head>
<meta charset="UTF-8"/>
<title>{title}</title>
<link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
{content}
</body>
</html>'''

    # Collect all image references across all HTML fragments
    all_html_fragments = [
        book['cover'], book['copyright_page'], book['toc'], book['body_html']
    ]
    for ch in chapters:
        ch_body = convert_markdown_to_html(ch['content'])
        ch_body = process_body_html(ch_body, chapter_index=0)
        all_html_fragments.append(ch_body)

    image_map = {}  # original_path -> (epub_path, mime_type)
    img_counter = 0
    for fragment in all_html_fragments:
        for img_match in re.finditer(r'<img[^>]+src="([^"]+)"', fragment):
            src = img_match.group(1)
            if src.startswith(('http://', 'https://', 'data:')):
                continue  # Skip remote and data-URI images
            src_path = Path(src)
            if not src_path.exists():
                # Try resolving relative to markdown file
                md_dir = Path(input_md).parent
                alt_path = md_dir / src
                if alt_path.exists():
                    src_path = alt_path
                else:
                    continue
            img_counter += 1
            img_id = f'img{img_counter:03d}'
            ext = src_path.suffix.lower()
            mime = mimetypes.guess_type(str(src_path))[0] or 'image/jpeg'
            epub_name = f'images/{img_id}{ext}'
            if src not in image_map:
                image_map[src] = (epub_name, mime, src_path)

    def rewrite_img_paths(html_text):
        """Rewrite local image src paths to ePub-relative paths."""
        def repl(m):
            full = m.group(0)
            src = m.group(1)
            if src in image_map:
                return full.replace(f'src="{src}"', f'src="{image_map[src][0]}"')
            return full
        return re.sub(r'<img([^>]+)src="([^"]+)"', repl, html_text)

    with zipfile.ZipFile(output_epub, 'w', zipfile.ZIP_DEFLATED) as zf:
        # mimetype must be first and uncompressed
        zf.writestr('mimetype', 'application/epub+zip', zipfile.ZIP_STORED)

        # META-INF/container.xml
        container = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>'''
        zf.writestr('META-INF/container.xml', container)

        # Write CSS
        zf.writestr('OEBPS/style.css', epub_css)

        # Write images
        for src, (epub_path, mime, src_path) in image_map.items():
            with open(src_path, 'rb') as img_f:
                zf.writestr(f'OEBPS/{epub_path}', img_f.read())

        # Write cover (rewrite image paths)
        cover_html = rewrite_img_paths(book['cover'])
        zf.writestr('OEBPS/cover.xhtml', xhtml_wrapper(cover_html))

        # Write copyright
        copyright_html = rewrite_img_paths(book['copyright_page'])
        zf.writestr('OEBPS/copyright.xhtml', xhtml_wrapper(copyright_html))

        # Write TOC
        toc_html = rewrite_img_paths(book['toc'])
        zf.writestr('OEBPS/toc.xhtml', xhtml_wrapper(toc_html))

        # Write chapters
        manifest_items = [
            ('cover', 'cover.xhtml', 'application/xhtml+xml'),
            ('copyright', 'copyright.xhtml', 'application/xhtml+xml'),
            ('toc', 'toc.xhtml', 'application/xhtml+xml'),
        ]
        spine_items = ['cover', 'copyright', 'toc']
        nav_points = []

        for i, ch in enumerate(chapters):
            ch_id = f'chapter{i+1:03d}'
            ch_file = f'{ch_id}.xhtml'
            opener = generate_chapter_opener(ch, i, cfg)
            body_html = convert_markdown_to_html(ch['content'])
            body_html = process_body_html(body_html, chapter_index=i)
            body_html = rewrite_img_paths(body_html)
            ch_html = xhtml_wrapper(
                f'<section class="chapter">{opener}'
                f'<div class="chapter-body">{body_html}</div></section>'
            )
            zf.writestr(f'OEBPS/{ch_file}', ch_html)
            manifest_items.append((ch_id, ch_file, 'application/xhtml+xml'))
            spine_items.append(ch_id)
            nav_points.append(
                f'    <navPoint id="navpoint-{i+1}" playOrder="{i+1}">\n'
                f'      <navLabel><text>{escape(ch["title"])}</text></navLabel>\n'
                f'      <content src="{ch_file}"/>\n'
                f'    </navPoint>'
            )

        # Add image manifest items
        for src, (epub_path, mime, _) in image_map.items():
            img_id = epub_path.replace('/', '_').replace('.', '_')
            manifest_items.append((img_id, epub_path, mime))

        # content.opf
        manifest_xml = '\n'.join(
            f'    <item id="{item_id}" href="{href}" media-type="{mt}"/>'
            for item_id, href, mt in manifest_items + [('style', 'style.css', 'text/css')]
        )
        spine_xml = '\n'.join(f'    <itemref idref="{sid}"/>' for sid in spine_items)

        cover_meta = '<meta name="cover" content="cover"/>' if cfg.get('cover_image') else ''
        desc_tag = f'<dc:description>{desc}</dc:description>' if desc else ''

        opf = f'''<?xml version="1.0" encoding="UTF-8"?>
<package version="2.0" xmlns="http://www.idpf.org/2007/opf">
  <metadata>
    <dc:title>{title}</dc:title>
    <dc:creator>{author}</dc:creator>
    <dc:language>{lang}</dc:language>
    {desc_tag}
    <dc:identifier id="bookid">urn:uuid:{uid}</dc:identifier>
    {cover_meta}
  </metadata>
  <manifest>
{manifest_xml}
  </manifest>
  <spine toc="ncx">
{spine_xml}
  </spine>
</package>'''
        zf.writestr('OEBPS/content.opf', opf)

        # toc.ncx
        ncx = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx version="2005-1">
  <head>
    <meta name="dtb:uid" content="urn:uuid:{uid}"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle><text>{title}</text></docTitle>
  <navMap>
{chr(10).join(nav_points)}
  </navMap>
</ncx>'''
        zf.writestr('OEBPS/toc.ncx', ncx)

    epub_size = os.path.getsize(output_epub)
    print(f"Done! {output_epub}")
    print(f"Size: {epub_size / 1024:.1f} KB")


# ─── MOBI / AZW3 Export (via Calibre ebook-convert) ───────────────────────
def generate_mobi(input_md, output_path, config, fmt='mobi'):
    """Generate MOBI or AZW3 by first creating an ePub, then converting via Calibre."""
    # Detect Calibre's ebook-convert
    ebook_convert = shutil.which('ebook-convert')
    if not ebook_convert and sys.platform == 'win32':
        # Common Windows Calibre install paths
        for path in [
            r'C:\Program Files\Calibre2\ebook-convert.exe',
            r'C:\Program Files (x86)\Calibre2\ebook-convert.exe',
        ]:
            if os.path.exists(path):
                ebook_convert = path
                break
    if not ebook_convert:
        print("Error: Calibre's ebook-convert not found.")
        print("Please install Calibre (https://calibre-ebook.com/download) and ensure it's in your PATH.")
        sys.exit(1)

    # Create a temporary ePub
    tmpdir = tempfile.mkdtemp(prefix='booksmith_')
    tmp_epub = os.path.join(tmpdir, 'tmp.epub')
    try:
        generate_epub(input_md, tmp_epub, config)
        print(f"Converting to {fmt.upper()} via Calibre...")
        cmd = [
            ebook_convert,
            tmp_epub,
            output_path,
            '--output-profile', 'kindle' if fmt == 'mobi' else 'kindle_dx',
            '--no-inline-toc',
            '--chapter', "//h:h1",
            '--page-breaks-before', "//h:h1",
        ]
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if result.returncode != 0:
            err = result.stderr.decode('utf-8', errors='replace') if result.stderr else ''
            print(f"Warning: ebook-convert returned non-zero exit code.\n{err}")
        else:
            print(f"Done! {output_path}")
            out_size = os.path.getsize(output_path)
            print(f"Size: {out_size / 1024:.1f} KB")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ─── Main ─────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Booksmith v2.0 -- Professional Book Typesetting")
    parser.add_argument("--input", "-i", required=True, help="Input Markdown file")
    parser.add_argument("--output", "-o", default="output.pdf", help="Output file")
    parser.add_argument("--format", "-f", default="pdf", choices=["pdf", "html", "epub", "mobi", "azw3"],
                        help="Output format (pdf, html, epub, mobi, azw3)")
    parser.add_argument("--theme", "-t", default="publishing-classic", help="Theme preset name")
    parser.add_argument("--title", help="Book title")
    parser.add_argument("--author", help="Book author")
    parser.add_argument("--date", help="Publication date")
    parser.add_argument("--isbn", help="ISBN number")
    parser.add_argument("--publisher", help="Publisher name")
    parser.add_argument("--subtitle", help="Book subtitle")
    parser.add_argument("--cover-style", default="gradient", choices=["solid", "gradient", "image"])
    parser.add_argument("--cover-image", help="Cover background image path")
    parser.add_argument("--watermark", help="Watermark text")
    args = parser.parse_args()

    config = load_preset(args.theme)
    overrides = ['title', 'author', 'date', 'isbn', 'publisher', 'subtitle', 'cover_style', 'cover_image', 'watermark']
    for opt in overrides:
        val = getattr(args, opt.replace('-', '_'), None)
        if val:
            config[opt] = val

    if args.format == 'pdf':
        generate_pdf(args.input, args.output, config)
    elif args.format == 'html':
        generate_html_output(args.input, args.output, config)
    elif args.format == 'epub':
        generate_epub(args.input, args.output, config)
    elif args.format in ('mobi', 'azw3'):
        generate_mobi(args.input, args.output, config, fmt=args.format)


if __name__ == "__main__":
    main()
