#!/bin/bash
# Quick Action script for macOS Finder
# Converts Paperpile JSON exports to Markdown using pp2md.py.

# Directory containing this script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Call the converter script once for each selected JSON file
for json_path in "$@"; do
    # Skip empty arguments which Automator might pass
    [ -n "$json_path" ] || continue
    python3 "$SCRIPT_DIR/pp2md.py" "$json_path"
done
