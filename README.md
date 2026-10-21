# CV – Łukasz Spaczyński

**Download the CV:** [English (PDF)](out/Lukasz-Spaczynski-CV-EN.pdf) · [Polski (PDF)](out/Lukasz-Spaczynski-CV-PL.pdf)

Senior iOS / Mobile Engineer · Swift · React Native. The PDFs in `out/` are always built from the
current `data/*.yaml`, so the files above are the up-to-date CV.

This repository is also the generator: YAML content → Jinja2 HTML → Chromium PDF, two A4 pages,
English and Polish from one template. The generator is MIT-licensed; the CV content is not (see `LICENSE`).

## Layout of the repository

```
data/en.yaml        English content
data/pl.yaml        Polish content
template/cv.html.j2 HTML template (Jinja2)
template/cv.css     styling (A4, single column)
build.py            render YAML → HTML → PDF (Chromium via Playwright)
build/              intermediate HTML and PNG previews (ignored by git)
out/                final PDFs (committed)
assets/             photo used in the Polish version
```

## Building

```sh
python3 build.py        # both languages
python3 build.py pl     # Polish only
```

Output: `out/Lukasz-Spaczynski-CV-EN.pdf` and `out/Lukasz-Spaczynski-CV-PL.pdf`.

PNG previews for a quick visual check:

```sh
pdftoppm -png -r 70 out/Lukasz-Spaczynski-CV-EN.pdf build/preview-EN
```

## Requirements

Python 3.13 with the packages from `requirements.txt` (`pip install -r requirements.txt`) and a downloaded
Chromium (`python3 -m playwright install chromium`). For previews, optionally `poppler` (`brew install poppler`).

The layout is tuned for the Helvetica Neue font (macOS). On a system without it Chromium falls back to
another font and line and page breaks may differ. That is why the finished PDFs in `out/` are committed:
they are the source of truth, not a build from another machine.

## Page layout

Single column, two A4 pages (ATS-friendly). Order: header with contact details, profile, skills
(four competency rows, no version numbers), experience in reverse chronological order, the `ai` section
(work with AI agents, optional), hobby projects (`projects`, optional), education and languages side by side,
and the GDPR consent clause (Polish version only; the `consent` field is empty in EN).
The footer with the name and page number is added by Chromium.

After every content change check the page count: `pdfinfo out/*.pdf | grep Pages` should report 2.
When a page does not close, measure instead of guessing: `pdftotext -f 2 -l 2 -bbox-layout out/<file>.pdf -`
prints line coordinates in points (the bottom of the A4 content area with a 17 mm margin is at ~793.7 pt).

Pitfall: if the header (photo + non-breaking headline + contact block) becomes wider than the page, Chromium
silently scales the whole document down to fit the width. Symptom: a smaller font and more content on page 1
than usual. Safeguards: `.head { overflow: hidden }`, a non-breaking name and headline, and the location with the
work mode (`person.location` · `person.availability`) rendered under the headline on the left, not in the
right-hand contact column, which is too narrow next to the photo.
Second pitfall: experience entries use `break-inside: avoid`, so when the Preglife block does not fit under
the skills it jumps to page 2 as a whole and creates a third page.

## Typography

`build.py` runs a typesetting pass over every text field before rendering: a non-breaking space after Polish
one-letter words (a, i, o, u, w, z), glued `&` and `/`, and hyphenated terms (local-first, server-driven,
Objective-C) wrapped in a `nowrap` span so they never break at the hyphen. Keys such as `url`, `email`, `phone`
and `label` are left untouched. Skills items are joined with a non-breaking space before the `·` separator, so a
separator never starts a line.

## Photo

The optional `person.photo` field (path relative to `build/`, e.g. `../assets/photo.jpg`) places a round photo
on the left of the header. It is used in the Polish version only and deliberately omitted in EN (UK/EU market).
The source photo was cropped to head and shoulders with a Pillow script into `assets/photo.jpg`.

## PDF metadata

After rendering, `build.py` rewrites the PDF information dictionary (pypdf): title, author, subject (the headline),
keywords (the skills without parentheses, always taken from the English data so ATS parsers get English terms),
and the Creator and Producer fields carry the author's name instead of the tool name.

## Editing the content

All content lives in the YAML files. The template contains no text, so changing the content never requires
touching HTML or CSS. Sections are rendered in the order defined in the template.

- `url` on projects and experience entries is optional; when present the company name becomes a link.
- An entry with `compact: true` renders role, company and dates on one line with no bullets (used for the
  PHP period 2008–2012).
- An experience entry may have a list of `phases` instead of `bullets`: sub-blocks with their own `title`,
  `start`, `end`, an optional `note` and `bullets`. Preglife is described this way: the React Native period and
  the native iOS period under one employer heading. A phase may break across pages, but its heading and note
  stay together with the first bullet, so a phase title is never orphaned at the bottom of a page.
- A phase may carry a `links` list (`label`, `url`) appended to its note; this is how the App Store and
  Google Play links are attached to the React Native phase.
