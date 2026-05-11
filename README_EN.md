<p align="center">
  <img src="assets/sloth-avatar-round.png" width="120" />
</p>

<h1 align="center">匠书 · 出版排版引擎<br/><sub>Sloth-BookSmith-Den</sub></h1>

<p align="center">
  <strong>Turn Markdown & Word manuscripts into publication-ready ebooks</strong><br/>
  PDF / HTML / ePub / MOBI / AZW3 — one codebase, five formats
</p>

<p align="center">
  <img src="assets/qrcode.jpg" width="140" /><br/>
  <sub>Follow <strong>树懒老K (Sloth-K)</strong> · More AI Skills</sub><br/>
  <em>Slow down, go deeper</em>
</p>

---

## Overview

Sloth-BookSmith-Den is a professional book typesetting engine that converts Markdown and Word (.docx) manuscripts into publication-quality ebooks. It supports five output formats from a single codebase, with typographic precision for CJK (Chinese, Japanese, Korean) languages.

## Features

- **Multi-format Export**: PDF, HTML, ePub, MOBI, AZW3 from one source
- **Dual Input**: Native Markdown + auto-detect Word (.docx) conversion
- **Professional Typography**: First-line indent, proportional margins, running headers, chapter openers, drop caps, widow/orphan control
- **Smart TOC**: Auto-generated three-level table of contents with dynamic page numbers (PDF) and NCX navigation (ePub)
- **Syntax Highlighting**: Pygments integration for fenced code blocks
- **Cross-references**: Auto-link "see / refer to / reference" mentions
- **Sub-chapter Navigation**: H2 anchor injection with direct links and PDF bookmarks
- **Cover System**: 5 cover styles (solid, gradient, image, texture, academic) + dark ebook theme
- **Font Fallback**: Modern CJK font chain (PingFang SC, Hiragino Sans GB, Microsoft YaHei)
- **Metadata Injection**: PDF XMP + info dict, ePub dc:description
- **Watermark Support**: CLI parameter for full-page watermark overlay
- **Image Handling**: Auto paragraph-to-figure conversion, ePub local image bundling

## Supported Formats

| Format | Key Features | Best For |
|--------|-------------|----------|
| PDF | Paginated, bookmarks, headers/footers, watermarks | Print publishing, archiving |
| HTML | Responsive, @media print, syntax highlighting | Web reading, online preview |
| ePub | EPUB 2.0, NCX TOC, cover metadata | General e-readers |
| MOBI | Kindle legacy format | Older Kindle devices |
| AZW3 | Kindle modern format, better typography | Modern Kindle devices |

## Theme Presets

| Theme | Style | Best For |
|-------|-------|----------|
| publishing-classic | Classic serif, Songti/Mingti | Literature, academic works |
| academic-serif | Academic wide-margin footnotes | Papers, research reports |
| tech-modern | Sans-serif, code highlighting | Technical docs, dev manuals |
| consulting-navy | Navy blue, data tables | Business proposals, strategy |
| literary-minimal | Minimalist, generous whitespace | Essays, poetry |
| dark-ebook | Dark mode, amber accents | Night reading, e-ink devices |

## Quick Start

### Install Dependencies

```bash
pip install markdown pygments pymupdf playwright pyyaml python-docx
playwright install chromium
```

> MOBI / AZW3 output requires [Calibre](https://calibre-ebook.com/download).

### Basic Usage

```bash
# PDF output
python scripts/booksmith.py --input manuscript.md --theme dark-ebook --format pdf

# HTML output
python scripts/booksmith.py --input manuscript.md --theme tech-modern --format html

# ePub output
python scripts/booksmith.py --input manuscript.md --theme publishing-classic --format epub

# MOBI / AZW3 (requires Calibre)
python scripts/booksmith.py --input manuscript.md --theme dark-ebook --format mobi
python scripts/booksmith.py --input manuscript.md --theme dark-ebook --format azw3

# Word input (auto-detected)
python scripts/booksmith.py --input manuscript.docx --theme academic-serif --format pdf

# With watermark
python scripts/booksmith.py --input manuscript.md --watermark "Internal Use" --format pdf
```

## Version

Current: **2.0.0**

See [CHANGELOG.md](CHANGELOG.md) for details.

## License

MIT License © 2026 lovstudio (Sloth-Eido family)
