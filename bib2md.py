"""bib2md.py - Create an Obsidian note for a single Paperpile entry by citekey.

Unlike ``pp2md.py`` (which consumes a full Paperpile JSON export), this script
pulls parsed metadata for one entry from the ``paperpile-search`` CLI cache
(which is built from the user's Paperpile BibTeX export URL) and fills the
same ``paper-template.md`` used by the original Quick Action.

Usage:
    python bib2md.py <citekey> [--output-dir DIR]

The default output directory is the user's Obsidian ``work/papers`` folder.
The output filename is ``{citekey[:-3]}.md`` (the last 3 chars are the
Paperpile-assigned random suffix, e.g. ``-gr``).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


DEFAULT_OUTPUT_DIR = Path.home() / "Obsidian Vaults" / "work" / "papers"


def fetch_entry(citekey: str) -> Dict[str, Any]:
    """Return the parsed Paperpile entry for *citekey* via paperpile-search."""
    result = subprocess.run(
        ["paperpile-search", "info", citekey],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"paperpile-search info {citekey} failed: {result.stderr.strip()}"
        )
    return json.loads(result.stdout)


def split_authors(author_field: str) -> List[Tuple[str, str]]:
    """Split a BibTeX-style author string into ``(last, first)`` pairs.

    Handles the ``"Last1, First1 and Last2, First2"`` form returned by
    ``paperpile-search``. Falls back to a single-name parse if no comma is
    present in a segment.
    """
    if not author_field:
        return []
    parts = [p.strip() for p in author_field.split(" and ")]
    out: List[Tuple[str, str]] = []
    for p in parts:
        if "," in p:
            last, first = [x.strip() for x in p.split(",", 1)]
        else:
            # "First Middle Last" fallback
            tokens = p.split()
            last = tokens[-1] if tokens else ""
            first = " ".join(tokens[:-1])
        out.append((last, first))
    return out


def initials(first_name: str) -> str:
    """Return period-separated initials, e.g. ``"Tonghang" -> "T."``."""
    tokens = re.findall(r"[A-Za-z]+", first_name)
    return " ".join(f"{t[0].upper()}." for t in tokens if t)


def format_tags(tags: List[str]) -> str:
    """Return YAML list body for the ``tags:`` frontmatter field."""
    if not tags:
        return ""
    # Template already has the leading "  - " before this token,
    # so only add the separator between items.
    return "\n  - ".join(tags)


def make_date(entry: Dict[str, Any]) -> str:
    """Return an ISO-ish date string using whatever fields are available."""
    year = str(entry.get("year") or "")
    month = str(entry.get("month") or "").strip().rstrip("~")
    if month.isdigit() and 1 <= int(month) <= 12:
        return f"{year}-{int(month):02d}"
    return year


def build_replacements(entry: Dict[str, Any]) -> Dict[str, str]:
    authors = split_authors(entry.get("author", ""))
    if authors:
        first_last, first_first = authors[0]
        last_last, last_first = authors[-1]
    else:
        first_last = first_first = last_last = last_first = ""

    year = str(entry.get("year") or "")
    return {
        "{{year-month-day}}": make_date(entry),
        "{{title}}": entry.get("title", "") or "",
        "{{citekey}}": entry.get("citekey", "") or "",
        "{{journal}}": entry.get("journal", "") or "",
        "{{year}}": year,
        "{{tag}}": format_tags(entry.get("keywords") or []),
        "{{lead-author}}": f"{last_first} {last_last}".strip(),
        "{{first-au-lastn}}": first_last,
        "{{first-au-firstn}}": initials(first_first),
        "{{volume}}": str(entry.get("volume") or ""),
        "{{number}}": str(entry.get("number") or ""),
    }


def render(template: str, entry: Dict[str, Any]) -> str:
    out = template
    for token, value in build_replacements(entry).items():
        out = out.replace(token, value)
    return out


def output_filename(citekey: str) -> str:
    """Strip the 2-char Paperpile suffix (e.g. ``-gr``) to get the stem."""
    stem = citekey[:-3] if len(citekey) > 3 and citekey[-3] == "-" else citekey
    return f"{stem}.md"


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("citekey", help="Paperpile citekey, e.g. Han2026-gr")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to write the .md file into (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite an existing note instead of erroring out.",
    )
    args = parser.parse_args(argv)

    template_path = Path(__file__).resolve().parent / "paper-template.md"
    if not template_path.exists():
        print(f"Template not found: {template_path}", file=sys.stderr)
        return 1

    try:
        entry = fetch_entry(args.citekey)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    args.output_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.output_dir / output_filename(args.citekey)
    if out_path.exists() and not args.overwrite:
        print(f"Refusing to overwrite existing note: {out_path}", file=sys.stderr)
        print("Pass --overwrite to replace it.", file=sys.stderr)
        return 2

    rendered = render(template_path.read_text(encoding="utf-8"), entry)
    out_path.write_text(rendered, encoding="utf-8")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
