#!/usr/bin/env python3
"""Build CV PDFs (EN + PL) from YAML data and a Jinja2 HTML template.

Usage:
    python3 build.py            # build all languages
    python3 build.py en pl      # build selected languages
    python3 build.py --html     # also keep rendered HTML in build/ (always kept)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter
from markupsafe import Markup, escape
from markupsafe import Markup, escape

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
TEMPLATE = ROOT / "template"
BUILD = ROOT / "build"
OUT = ROOT / "out"

NAME_SLUG = "Lukasz-Spaczynski-CV"


NBSP = "\u00a0"
SKIP_KEYS = {"url", "photo", "email", "phone", "lang", "locale", "file_suffix", "label", "start", "end"}
HYPHENATED = re.compile(r"\b\w+(?:-\w+)+\b")
PL_ONE_LETTER = re.compile(r"(?<![\w-])([aiouwzAIOUWZ]) ")


def typeset(text: str, lang: str) -> Markup:
    """Escape, then apply print typography: no line break after Polish one-letter
    words, inside hyphenated terms, or around '&' and '/'. Returns safe markup."""
    s = str(escape(text))
    if lang == "pl":
        s = PL_ONE_LETTER.sub(lambda m: m.group(1) + NBSP, s)
    s = s.replace(" &amp; ", NBSP + "&amp;" + NBSP).replace(" / ", NBSP + "/" + NBSP)
    s = HYPHENATED.sub(lambda m: f'<span class="nowrap">{m.group(0)}</span>', s)
    return Markup(s)


def typeset_tree(node, lang: str):
    if isinstance(node, dict):
        return {k: (v if k in SKIP_KEYS else typeset_tree(v, lang)) for k, v in node.items()}
    if isinstance(node, list):
        return [typeset_tree(v, lang) for v in node]
    if isinstance(node, str):
        return typeset(node, lang)
    return node


def render_html(lang: str) -> Path:
    raw = yaml.safe_load((DATA / f"{lang}.yaml").read_text(encoding="utf-8"))
    data = typeset_tree(raw, lang)
    env = Environment(
        loader=FileSystemLoader(TEMPLATE),
        autoescape=True,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    css = (TEMPLATE / "cv.css").read_text(encoding="utf-8")
    html = env.get_template("cv.html.j2").render(css=css, **data)
    BUILD.mkdir(exist_ok=True)
    out = BUILD / f"cv-{lang}.html"
    out.write_text(html, encoding="utf-8")
    return out, raw


def html_to_pdf(html_path: Path, pdf_path: Path, footer_name: str) -> None:
    footer = (
        '<div style="width:100%;font-family:Helvetica Neue,Helvetica,Arial,sans-serif;'
        'font-size:7.5pt;color:#8a8f99;padding:0 15mm;display:flex;'
        'justify-content:space-between;">'
        f'<span>{footer_name}</span>'
        '<span><span class="pageNumber"></span> / <span class="totalPages"></span></span>'
        '</div>'
    )
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_path.as_uri(), wait_until="networkidle")
        page.emulate_media(media="print")
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            prefer_css_page_size=True,
            display_header_footer=True,
            header_template="<span></span>",
            footer_template=footer,
        )
        browser.close()


def set_metadata(pdf_path: Path, data: dict) -> None:
    """Rewrite the document info dictionary so the file carries the author's
    name instead of the rendering toolchain."""
    name = data["person"]["name"]
    headline = data["person"]["headline"]
    # Keywords always come from the English data so ATS parsers get English terms.
    en = yaml.safe_load((DATA / "en.yaml").read_text(encoding="utf-8"))
    keywords = ", ".join(
        re.sub(r"\s*\([^)]*\)", "", item).strip()
        for group in en["skills"] for item in group["items"]
    )
    reader = PdfReader(str(pdf_path))
    writer = PdfWriter(clone_from=reader)
    writer.add_metadata({
        "/Title": f"{name} – CV",
        "/Author": name,
        "/Subject": headline,
        "/Keywords": keywords,
        "/Creator": name,
        "/Producer": name,
    })
    with open(pdf_path, "wb") as fh:
        writer.write(fh)


def main(argv: list[str]) -> int:
    langs = [a for a in argv if not a.startswith("-")] or ["en", "pl"]
    OUT.mkdir(exist_ok=True)
    for lang in langs:
        html_path, data = render_html(lang)
        pdf_path = OUT / f"{NAME_SLUG}-{data['file_suffix']}.pdf"
        html_to_pdf(html_path, pdf_path, data["person"]["name"] + " \u2013 CV")
        set_metadata(pdf_path, data)
        print(f"[{lang}] {pdf_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
