#!/bin/bash
# Quick Action script for macOS Finder
# Converts Paperpile JSON exports to Markdown using pp2md.py.

# Directory containing this script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Call the converter script with all selected JSON files
python3 "$SCRIPT_DIR/pp2md.py" "$@"
