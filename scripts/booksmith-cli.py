#!/usr/bin/env python3
"""
Booksmith CLI -- Unified entry point for Sloth-BookSmith-Den.
Auto-detects input format (.docx or .md) and routes to the correct pipeline.

Usage:
    python booksmith-cli.py --input book.docx --output book.pdf --theme publishing-classic
    python booksmith-cli.py --input book.md  --output book.pdf --theme academic-serif
"""
import os
import sys
import tempfile
import shutil
import argparse
from pathlib import Path

# Import sibling modules
_SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(_SCRIPT_DIR))

try:
    import booksmith
except ImportError as e:
    print(f"Error: Could not import booksmith module: {e}")
    sys.exit(1)

try:
    import docx2md
except ImportError as e:
    print(f"Error: Could not import docx2md module: {e}")
    sys.exit(1)


def detect_input_format(input_path):
    """Detect input format from file extension."""
    ext = Path(input_path).suffix.lower()
    if ext == '.docx':
        return 'docx'
    elif ext == '.md':
        return 'md'
    else:
        return None


def run_docx_pipeline(args):
    """Pipeline: .docx -> .md -> .pdf"""
    input_docx = Path(args.input).resolve()
    output_pdf = Path(args.output).resolve()

    # Determine work directory for intermediate files
    if args.keep_md:
        # Save .md next to the output PDF
        work_dir = output_pdf.parent
    else:
        # Use a temp directory that we'll clean up
        work_dir = Path(tempfile.mkdtemp(prefix='booksmith_'))

    print(f"[CLI] Detected Word input: {input_docx}")
    print(f"[CLI] Work directory: {work_dir}")

    # Step 1: DOCX -> Markdown
    overrides = {}
    if args.title:
        overrides['title'] = args.title
    if args.author:
        overrides['author'] = args.author
    if args.date:
        overrides['date'] = args.date
    if args.subtitle:
        overrides['subtitle'] = args.subtitle

    try:
        md_path = docx2md.convert(
            input_docx=str(input_docx),
            output_dir=str(work_dir),
            images_dir=str(work_dir / 'images'),
            **overrides
        )
    except Exception as e:
        print(f"[CLI] DOCX conversion failed: {e}")
        if not args.keep_md and work_dir.exists():
            shutil.rmtree(work_dir, ignore_errors=True)
        sys.exit(1)

    # Step 2: Markdown -> PDF
    print(f"\n[CLI] Passing Markdown to booksmith: {md_path}")
    _run_booksmith(md_path, output_pdf, args)

    # Cleanup
    if not args.keep_md and work_dir.exists():
        print(f"[CLI] Cleaning up temp files: {work_dir}")
        shutil.rmtree(work_dir, ignore_errors=True)

    print(f"\n[CLI] Done! PDF: {output_pdf}")


def run_md_pipeline(args):
    """Pipeline: .md -> .pdf (direct)"""
    input_md = Path(args.input).resolve()
    output_pdf = Path(args.output).resolve()

    print(f"[CLI] Detected Markdown input: {input_md}")
    _run_booksmith(input_md, output_pdf, args)
    print(f"\n[CLI] Done! PDF: {output_pdf}")


def _run_booksmith(input_md, output_pdf, args):
    """Call booksmith.generate_pdf with parsed config."""
    config = booksmith.load_preset(args.theme)

    # Apply CLI overrides
    overrides = [
        'title', 'author', 'date', 'isbn', 'publisher',
        'subtitle', 'cover_style', 'cover_image', 'watermark'
    ]
    for opt in overrides:
        val = getattr(args, opt.replace('-', '_'), None)
        if val:
            config[opt] = val

    try:
        booksmith.generate_pdf(str(input_md), str(output_pdf), config)
    except Exception as e:
        print(f"[CLI] PDF generation failed: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Booksmith CLI -- Auto-detect .docx/.md and generate PDF'
    )
    # Input / Output
    parser.add_argument('--input', '-i', required=True,
                        help='Input file (.docx or .md)')
    parser.add_argument('--output', '-o', default='output.pdf',
                        help='Output PDF file (default: output.pdf)')
    parser.add_argument('--theme', '-t', default='publishing-classic',
                        help='Theme preset name (default: publishing-classic)')

    # Metadata overrides (applied to both docx and md)
    parser.add_argument('--title', help='Book title')
    parser.add_argument('--author', help='Book author')
    parser.add_argument('--date', help='Publication date (YYYY-MM-DD)')
    parser.add_argument('--isbn', help='ISBN number')
    parser.add_argument('--publisher', help='Publisher name')
    parser.add_argument('--subtitle', help='Book subtitle')

    # Cover options
    parser.add_argument('--cover-style', default='gradient',
                        choices=['solid', 'gradient', 'image'],
                        help='Cover style (default: gradient)')
    parser.add_argument('--cover-image', help='Cover background image path')

    # Other
    parser.add_argument('--watermark', help='Watermark text')
    parser.add_argument('--keep-md', action='store_true',
                        help='Keep intermediate .md file (for .docx input)')

    args = parser.parse_args()

    # Validate input
    if not os.path.exists(args.input):
        print(f"[CLI] Error: Input file not found: {args.input}")
        sys.exit(1)

    fmt = detect_input_format(args.input)
    if fmt == 'docx':
        run_docx_pipeline(args)
    elif fmt == 'md':
        run_md_pipeline(args)
    else:
        print(f"[CLI] Error: Unsupported input format '{fmt}'. "
              f"Only .docx and .md are supported.")
        sys.exit(1)


if __name__ == '__main__':
    main()
