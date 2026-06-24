#!/usr/bin/env python3
"""Generate print-ready CV PDFs (FR + EN) from the Hugo resume pages.

Dependencies: hugo, chromium (headless)
Usage: ./scripts/resume-pdf.py
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
LEGACY_CSS = Path.home() / "Repositories" / "piergst" / "resume" / "src" / "style.css"

RESUMES = {
    "fr": {
        "html": PROJECT / "public" / "fr" / "resume" / "index.html",
        "pdf": PROJECT / "resume-fr.pdf",
        "lang": "fr",
    },
    "en": {
        "html": PROJECT / "public" / "resume" / "index.html",
        "pdf": PROJECT / "resume-en.pdf",
        "lang": "en",
    },
}


def build_hugo():
    subprocess.run(["hugo", "--quiet"], cwd=PROJECT, check=True)


def ensure_hugo_built():
    for cfg in RESUMES.values():
        if not cfg["html"].exists():
            print("==> Building Hugo site...")
            build_hugo()
            return


def extract_content(html: str) -> str:
    m = re.search(
        r'<div class="post-content[^"]*">(.*?)</div>\s*<footer',
        html,
        re.DOTALL,
    )
    if not m:
        raise SystemExit('ERROR: could not find <div class="post-content"> in HTML')
    return m.group(1)


def legacy_print_css() -> str:
    """Extract the @media print block from the legacy resume CSS."""
    css = LEGACY_CSS.read_text(encoding="utf-8")
    m = re.search(r"@media print\s*\{(.*?)\n\}", css, re.DOTALL)
    if not m:
        raise SystemExit("ERROR: no @media print block in legacy CSS")
    return m.group(1)


def hugo_additions() -> str:
    """Extra rules for Hugo-specific markup, plus tighter spacing."""
    return """
    /* ---- Hugo additions & print tightening ---- */

    body { font-size: 9.5pt; line-height: 1.4; }

    h1 { font-size: 18pt; margin: 0 0 6pt 0; }

    .resume-h2, h2 {
        font-size: 12pt;
        margin: 14pt 0 5pt 0;
        padding-bottom: 2pt;
    }

    .resume-h3, h3 {
        font-size: 10.5pt;
        margin: 10pt 0 4pt 0;
    }

    p { margin: 0 0 4pt 0; }

    ul, ol { margin: 0 0 5pt 1.2em; }

    li { margin: 1.5pt 0; font-size: 9pt; }

    blockquote p { font-size: 9pt; margin: 3pt 0; }

    .resume-tag {
        display: inline-block;
        color: #1a1a1a;
        font-weight: normal;
        font-style: normal;
        background-color: #eaeaea;
        border-radius: 3px;
        padding: 0px 5px;
        white-space: nowrap;
        font-size: 8.5pt;
    }

    h4 {
        font-size: 9pt;
        font-weight: normal;
        color: #666;
        text-align: center;
        margin: 4pt 0;
        line-height: 1.7;
    }

    h5 {
        font-size: 9pt;
        font-weight: normal;
        color: #555;
        text-align: center;
        margin: 6pt 0;
    }

    blockquote {
        margin: 0;
        padding: 0;
        border: none;
    }

    date { font-size: 8.5pt; }
"""


def render_page(content: str, lang: str, print_css: str) -> str:
    additions = hugo_additions()
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head><meta charset="utf-8"><style>
@media print {{
    @page {{ size: A4; margin: 10mm 16mm 6mm 16mm; }}
{print_css}
{additions}
}}
</style></head>
<body>
{content}
</body>
</html>"""


def generate_pdf(html_path: Path, pdf_path: Path, lang: str) -> None:
    html = html_path.read_text(encoding="utf-8")
    content = extract_content(html)
    print(f"  [{lang.upper()}] Extracted {len(content)} chars")

    page = render_page(content, lang, legacy_print_css())

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False, encoding="utf-8"
    ) as f:
        f.write(page)
        tmp = f.name

    out = str(pdf_path)
    print(f"  [{lang.upper()}] Rendering {out} ...")
    subprocess.run(
        [
            "/usr/bin/chromium",
            "--headless",
            "--no-sandbox",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={out}",
            tmp,
        ],
        check=True,
    )
    os.unlink(tmp)
    size_kb = os.path.getsize(out) / 1024
    print(f"  [{lang.upper()}] Done  ({size_kb:.0f} kB)")


def main():
    ensure_hugo_built()
    pcss = legacy_print_css()
    print(f"==> Loaded {len(pcss)} chars of print CSS from {LEGACY_CSS}")

    for code, cfg in RESUMES.items():
        generate_pdf(cfg["html"], cfg["pdf"], code)

    print("==> All done")


if __name__ == "__main__":
    main()
