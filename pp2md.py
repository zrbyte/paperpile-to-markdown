"""pp2md.py - Convert Paperpile JSON to Markdown files.

This script searches for a JSON file in the same directory as the
script, loads it and a markdown template, then creates a markdown file
for each entry in the JSON. Each field marked with double braces in the
template is replaced with information from the JSON entry.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


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


def main() -> None:
    here = Path(__file__).resolve().parent

    json_files = list(here.glob("*.json"))
    if not json_files:
        raise FileNotFoundError("No JSON file found next to script.")
    json_path = json_files[0]

    template_path = here / "paper-template.md"
    if not template_path.exists():
        raise FileNotFoundError("Template file not found.")

    data = load_json(json_path)
    template = load_template(template_path)

    for entry in data:
        output = replace_fields(template, entry)
        citekey = entry.get("citekey", "paper")
        filename = f"{citekey[:-2]}.md"
        (here / filename).write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
