"""pp2md.py - Convert Paperpile JSON to Markdown files.

The script loads a Paperpile export JSON and a markdown template, then
creates a markdown file for each entry. The template tokens wrapped in
double braces are replaced with the values from the JSON entry.

When executed without arguments the script searches for ``*.json`` next
to itself. File paths passed as arguments are also supported which makes
it easy to use from macOS Quick Actions where the selected file path can
be supplied to the script.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List
import sys


def load_json(path: Path) -> List[Dict[str, Any]]:
    """Load a JSON array from *path* and return it."""
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_template(path: Path) -> str:
    """Return the markdown template contents."""
    return path.read_text(encoding="utf-8")


def format_tags(tags: List[str]) -> str:
    """Return YAML formatted tag lines."""
    if not tags:
        return ""
    lines = [tags[0]]
    for tag in tags[1:]:
        lines.append(tag)
    return "\n  - ".join(lines)


def replace_fields(template: str, entry: Dict[str, Any]) -> str:
    """Replace template placeholders with values from *entry*."""
    published = entry.get("published", {})
    date = f"{published.get('year', '')}-{published.get('month', '')}-{published.get('day', '')}"

    tags_yaml = format_tags(entry.get("labelsNamed", []))

    authors = entry.get("author", [])
    if authors:
        first_author = authors[0]
        last_author = authors[-1]
    else:
        first_author = last_author = {"first": "", "last": ""}

    replacements = {
        "{{year-month-day}}": date,
        "{{title}}": entry.get("title", ""),
        "{{citekey}}": entry.get("citekey", ""),
        "{{journal}}": entry.get("journal", ""),
        "{{year}}": published.get("year", ""),
        "{{tag}}": tags_yaml,
        "{{lead-author}}": f"{last_author.get('first', '')} {last_author.get('last', '')}",
        "{{first-au-lastn}}": first_author.get("first", ""),
        "{{first-au-firstn}}": first_author.get("last", ""),
        "{{volume}}": entry.get("volume", ""),
        "{{number}}": entry.get("number", ""),
    }

    for token, value in replacements.items():
        template = template.replace(token, value)
    return template


def process_json(json_path: Path, template: str) -> None:
    """Create markdown files for the data in *json_path* using *template*."""
    data = load_json(json_path)
    out_dir = json_path.parent
    for entry in data:
        output = replace_fields(template, entry)
        citekey = entry.get("citekey", "paper")
        filename = f"{citekey[:-2]}.md"
        (out_dir / filename).write_text(output, encoding="utf-8")


def main(args: Iterable[str] | None = None) -> None:
    script_dir = Path(__file__).resolve().parent
    template_path = script_dir / "paper-template.md"
    if not template_path.exists():
        raise FileNotFoundError("Template file not found.")

    if args is None:
        args = sys.argv[1:]
    json_paths = [Path(p) for p in args] if args else []
    if not json_paths:
        json_paths = list(script_dir.glob("*.json"))
        if not json_paths:
            raise FileNotFoundError("No JSON file provided or found next to script.")

    template = load_template(template_path)

    for path in json_paths:
        if path.exists():
            process_json(path, template)


if __name__ == "__main__":
    main()
