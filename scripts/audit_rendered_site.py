#!/usr/bin/env python3
"""Hard audit for the rendered Quarto site."""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit


REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_SUFFIXES = {".md", ".ipynb"}
ROOT_MARKDOWN_INPUTS = [
    "README.md",
    "EXECUTIVE_SUMMARY.md",
    "RESULTS.md",
    "CHANGELOG.md",
    "WRITEUP.md",
    "READING_GUIDE.md",
    "EVIDENCE.md",
    "SPEC_SHEET.md",
    "SUBMISSION_AUDIT.md",
    "NEXT_STEPS.md",
    "assumptions.md",
    "CLAUDE.md",
    "code_quality.md",
]
NOTEBOOK_INPUTS = [
    "01_canonical_results",
    "02_frozen_vs_lora",
    "03_calibration",
    "04_ood_slate",
]
LINK_RE = re.compile(r"""(?:href|src)=["']([^"']+)["']""")
HTML_TAG_RE = re.compile(r"<[^>]+>")
TABLE_CELL_RE = re.compile(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", re.IGNORECASE | re.DOTALL)
EMBEDDED_SOURCE_MARKERS = (
    'class="btn code-tools-button"',
    'id="quarto-code-tools-source"',
    'id="quarto-embedded-source-code-modal"',
)
MAX_TABLE_CELL_CHARS = 1200


def rel(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def expected_html_paths(site_root: Path) -> list[Path]:
    paths = [site_root / f"{Path(name).stem}.html" for name in ROOT_MARKDOWN_INPUTS]
    paths.extend(
        site_root / "docs" / f"{path.stem}.html" for path in (REPO_ROOT / "docs").glob("*.md")
    )
    paths.extend(site_root / "notebooks" / f"{stem}.html" for stem in NOTEBOOK_INPUTS)
    return sorted(paths)


def raw_sources_under_site(site_root: Path) -> list[Path]:
    return sorted(
        path
        for path in site_root.rglob("*")
        if path.is_file() and path.suffix.lower() in RAW_SUFFIXES
    )


def is_external_or_fragment(link: str) -> bool:
    if not link or link.startswith("#"):
        return True
    parsed = urlsplit(link)
    if parsed.scheme in {"http", "https", "mailto", "tel", "data", "javascript"}:
        return True
    return bool(parsed.netloc)


def rendered_raw_links(site_root: Path) -> list[str]:
    failures: list[str] = []
    for html_path in sorted(site_root.rglob("*.html")):
        text = html_path.read_text(encoding="utf-8", errors="replace")
        for match in LINK_RE.finditer(text):
            link = match.group(1)
            if is_external_or_fragment(link):
                continue
            path_part = urlsplit(link).path
            if Path(path_part).suffix.lower() in RAW_SUFFIXES:
                failures.append(f"{rel(html_path, site_root)} -> {link}")
    return failures


def embedded_source_code_blocks(site_root: Path) -> list[str]:
    failures: list[str] = []
    for html_path in sorted(site_root.rglob("*.html")):
        text = html_path.read_text(encoding="utf-8", errors="replace")
        if any(marker in text for marker in EMBEDDED_SOURCE_MARKERS):
            failures.append(rel(html_path, site_root))
    return failures


def _plain_text_from_html(fragment: str) -> str:
    without_tags = HTML_TAG_RE.sub(" ", fragment)
    return " ".join(html.unescape(without_tags).split())


def long_table_cells(site_root: Path) -> list[str]:
    failures: list[str] = []
    for html_path in sorted(site_root.rglob("*.html")):
        relative = rel(html_path, site_root)
        if relative.startswith("decisions/ADR-"):
            continue
        text = html_path.read_text(encoding="utf-8", errors="replace")
        for index, match in enumerate(TABLE_CELL_RE.finditer(text), start=1):
            cell_text = _plain_text_from_html(match.group(1))
            if len(cell_text) > MAX_TABLE_CELL_CHARS:
                failures.append(f"{relative} cell {index}: {len(cell_text)} chars")
    return failures


def audit(site_root: Path) -> list[str]:
    failures: list[str] = []
    if not site_root.exists():
        return [f"{site_root} does not exist; run `make site` first"]

    raw_files = raw_sources_under_site(site_root)
    if raw_files:
        failures.append(
            "Raw Markdown/notebook files under _site:\n"
            + "\n".join(rel(p, site_root) for p in raw_files)
        )

    missing_html = [path for path in expected_html_paths(site_root) if not path.exists()]
    if missing_html:
        failures.append(
            "Expected rendered HTML outputs are missing:\n"
            + "\n".join(rel(path, site_root) for path in missing_html)
        )

    raw_links = rendered_raw_links(site_root)
    if raw_links:
        failures.append(
            "Rendered internal links still point at raw .md/.ipynb files:\n" + "\n".join(raw_links)
        )

    source_blocks = embedded_source_code_blocks(site_root)
    if source_blocks:
        failures.append(
            "Rendered pages include Quarto embedded source-code blocks:\n"
            + "\n".join(source_blocks)
        )

    long_cells = long_table_cells(site_root)
    if long_cells:
        failures.append(
            f"Rendered non-ADR table cells exceed {MAX_TABLE_CELL_CHARS} characters:\n"
            + "\n".join(long_cells)
        )

    notebook_html = sorted((site_root / "notebooks").glob("*.html"))
    if len(notebook_html) != len(NOTEBOOK_INPUTS):
        failures.append(
            f"Expected {len(NOTEBOOK_INPUTS)} notebook HTML pages, found {len(notebook_html)}:\n"
            + "\n".join(rel(path, site_root) for path in notebook_html)
        )

    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-root", type=Path, default=REPO_ROOT / "_site")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failures = audit(args.site_root.resolve())
    if failures:
        print("Rendered site audit FAILED", file=sys.stderr)
        for failure in failures:
            print(f"\n{failure}", file=sys.stderr)
        return 1
    print("Rendered site audit OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
