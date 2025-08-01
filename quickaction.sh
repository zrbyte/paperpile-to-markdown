#!/bin/zsh
# Quick Action script for macOS Finder
# Converts Paperpile JSON exports to Markdown using pp2md.py.

# Directory containing this script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

run_convert() {
    local json_path="$1"
    [[ -n "$json_path" ]] || return
    python3 "$SCRIPT_DIR/pp2md.py" "$json_path"
}

# Finder may supply paths as arguments or via STDIN depending on the
# Quick Action configuration. Handle both cases.
if [[ $# -gt 0 ]]; then
    for json_path in "$@"; do
        run_convert "$json_path"
    done
else
    while IFS= read -r json_path; do
        run_convert "$json_path"
    done
fi
